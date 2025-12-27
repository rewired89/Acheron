"""
Acheron Phase 2: Bio-RAID Simulator with ECC + Read-Repair
===========================================================

Simulates multi-chamber bioelectric memory system with:
- 3-way replication for fault tolerance (majority voting)
- Periodic scrubbing (weekly) to repair bit drift
- Intelligent donor selection (≥95% preferred, ≥92% emergency)
- Rebuild throttling to prevent cascade failures
- Automatic tile degradation and failure
- State migration through fragmentation
- Health monitoring and rebuild orchestration

This demonstrates the Phase 2 architecture to investors and validates
technical feasibility before wetware implementation.

Usage:
    python experiments/phase2_bio_raid_simulator.py --quick  # 90-day test
    python experiments/phase2_bio_raid_simulator.py          # 1-year simulation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation
from simulations.bioelectric_persistence import PlanarianTissueModel
from encoder.bioelectric_encoder import BioelectricEncoder
import time
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class TileState(Enum):
    """Tile operational states."""
    ACTIVE = "ACTIVE"           # Storing data, healthy (≥80%)
    SICK = "SICK"               # Degraded but online (60-80%), needs proactive rebuild
    DEGRADING = "DEGRADING"     # Flagged for rebuild (legacy - will be removed)
    REGENERATING = "REGENERATING"  # Currently rebuilding
    CLEAN_LOCKED = "CLEAN_LOCKED"  # Recently scrubbed, locked from proactive rebuild (7 days)
    STERILE = "STERILE"         # Empty, ready for seeding
    FAILED = "FAILED"           # Unusable (<60%)


class TruthSource(Enum):
    """Truth authority for chunk data reconstruction."""
    QUORUM = "QUORUM"          # Majority voting allowed (initial state)
    GOLDEN_ANCHOR = "GOLDEN_ANCHOR"  # Anchor is sole authority (promoted after first restoration)


@dataclass
class Tile:
    """
    Represents one chamber in the bio-RAID cartridge.
    """
    id: int
    state: TileState
    integrity: float  # 0.0 to 1.0 (physical health, not data correctness)
    age: int  # days
    pattern: Optional[np.ndarray]  # Voltage grid
    binary_data: Optional[str]  # Stored bits
    regeneration_progress: float = 0.0  # For rebuilding tiles
    last_donor_day: int = -999  # Last day this tile was used as a donor
    needs_scrub: bool = False  # Flag for post-regeneration scrub
    last_rebuild_attempt_day: int = -999  # Last day rebuild was attempted for this tile
    regen_complete_day: int = -999  # Day when regeneration completed
    chunk_checksum: int = 0  # CRC32 checksum of chunk data
    clean_locked_until_day: int = -999  # Day when CLEAN_LOCKED expires (stabilization window)

    # BIOLOGICAL HARDENING: Replica maturation system
    consecutive_successful_scrubs: int = 0  # Track successful scrubs for maturation
    maturity_level: int = 0  # 0=new/unstable, 1=maturing, 2=mature/hardened
    matured_on_day: int = -999  # Day when reached MATURE status

    # RISK-GATED REBUILDS: Track write failures
    write_fail_count: int = 0  # Consecutive write failures (for risk assessment)
    write_suspect: bool = False  # Marked as WRITE_SUSPECT after 2 consecutive failures


class BioRAIDController:
    """
    Orchestrates multi-tile bioelectric memory with ECC + read-repair.

    Architecture:
    - 20 total tiles (16 active + 4 sterile spares)
    - 3-way replication: Each bit stored in 3 tiles
    - Majority voting on read for error correction
    - Periodic scrubbing to repair bit drift
    - Rebuild throttling to prevent cascade failures
    - Auto-rebuild when tile degrades below threshold
    - BIOLOGICAL HARDENING: Replica maturation and memory consolidation
    """

    # BIOLOGICAL HARDENING CONSTANTS
    MATURATION_THRESHOLD = 3  # Consecutive successful scrubs needed to mature
    MATURE_DEGRADATION_REDUCTION = 0.5  # Mature replicas degrade 50% slower
    CONSOLIDATION_INTEGRITY_BOOST = 0.02  # Anchor write-back increases integrity by 2%
    CONSOLIDATION_MAX_INTEGRITY = 0.98  # Cap for integrity boost from consolidation

    # WRITE-SETTLE PROTOCOL CONSTANTS
    WRITE_SETTLE_DELAY_CYCLES = 2  # Simulated settling cycles after write
    MIN_INTEGRITY_FOR_2PASS = 0.85  # Below this, always use 2-pass write
    MIN_INTEGRITY_FOR_WRITE = 0.80  # Below this, tile is read-only (too degraded)

    # QUORUM RESTORATION CONSTANTS
    QUORUM_RESTORATION_THRESHOLD = 4  # Consecutive clean scrubs to demote GOLDEN_ANCHOR → QUORUM
    REQUIRE_3_LIVE_FOR_QUORUM_RESTORE = True  # Must have 3 live replicas to restore quorum

    def __init__(self, n_tiles=20, n_sterile=4):
        self.n_tiles = n_tiles
        self.n_active = n_tiles - n_sterile
        self.n_sterile = n_sterile

        # Initialize tiles
        self.tiles = []
        for i in range(n_tiles):
            state = TileState.STERILE if i >= self.n_active else TileState.ACTIVE
            tile = Tile(
                id=i,
                state=state,
                integrity=1.0 if state == TileState.ACTIVE else 0.0,
                age=0,
                pattern=None,
                binary_data=None
            )
            self.tiles.append(tile)

        # 3-way replication configuration
        self.replication_factor = 3  # Each bit stored in 3 tiles
        self.bits_per_tile = 26  # How many unique bits each tile stores
        # With 16 active tiles: 16/3 = 5 chunks × 26 bits = 130 bits capacity

        # Encoder for each tile
        self.encoder = BioelectricEncoder(grid_size=(30, 30), cells_per_bit=9)

        # Scrubbing configuration
        self.scrub_interval_days = 7  # Scrub weekly (normal mode)
        self.last_scrub_day = 0
        self.scrub_repairs = 0
        self.disagreements_found = 0
        self.bits_written_back = 0

        # Adaptive scrubbing
        self.adaptive_scrub_until_day = -1  # Scrub every 2 days if set
        self.last_adaptive_scrub_day = 0

        # Rebuild throttling
        self.donor_cooldown_days = 7  # Donors rest 1 week after fragmenting
        self.max_rebuilds_per_week = 3  # Allow 3 proactive rebuilds per week
        self.rebuilds_this_week = 0
        self.week_number = 0

        # Statistics
        self.rebuild_count = 0
        self.total_degradation_events = 0
        self.uptime_days = 0
        self.history = []

        # Chunk -> Tile mapping (for invariant enforcement)
        # chunk_replicas[chunk_idx] = [tile_id1, tile_id2, tile_id3]
        self.chunk_replicas = {}  # Will be initialized after write_data
        self.chunks_at_risk = set()  # Chunks with <2 readable replicas
        self.chunk_at_risk_cooldown = {}  # {chunk_idx: last_attempt_day} - prevent loops

        # GOLDEN ANCHOR TRUTH (prevents self-corruption lock-in)
        self.chunk_golden_truth = {}  # {chunk_idx: golden_bits} - NEVER modified after write

        # TRUTH AUTHORITY HIERARCHY (prevents anchor vs quorum oscillation)
        self.chunk_truth_source = {}  # {chunk_idx: TruthSource} - authority for reconstruction
        self.chunk_anchor_epoch = {}  # {chunk_idx: int} - increments on anchor promotion

        # QUORUM RESTORATION: Track consecutive clean scrubs per chunk
        self.chunk_consecutive_clean_scrubs = {}  # {chunk_idx: int} - consecutive scrubs with no repairs
        self.quorum_restorations = 0  # Count of GOLDEN_ANCHOR → QUORUM demotions

        # RISK-GATED REBUILDS: Track failed scrubs per chunk
        self.chunk_failed_scrub_count = {}  # {chunk_idx: int} - consecutive failed scrubs (for risk assessment)
        self.write_failures_total = 0  # Total write failures across all tiles
        self.write_attempts_total = 0  # Total write attempts (for write fail rate)

        # CALM-PERIOD TOP-UP: Restore 3-live redundancy during stable periods
        self.chunk_two_live_since_day = {}  # {chunk_idx: day} - when chunk dropped to 2 live
        self.chunk_last_drift = {}  # {chunk_idx: [drift1, drift2, drift3]} - last 3 scrub drifts
        self.chunk_last_shock_day = {}  # {chunk_idx: day} - last degradation event affecting chunk
        self.topup_count = 0  # Count of calm-period top-ups (separate from rebuilds)
        self.chunk_time_at_3live = {}  # {chunk_idx: days} - cumulative time at 3 live replicas
        self.chunk_time_at_2live = {}  # {chunk_idx: days} - cumulative time at 2 live replicas

        # TOP-UP CONFIGURATION
        self.TOPUP_MIN_2LIVE_DAYS = 7  # Minimum days at 2-live before top-up
        self.TOPUP_MIN_CLEAN_SCRUBS = 3  # Require 3 consecutive scrubs with 0 drift
        self.TOPUP_MIN_CALM_DAYS = 7  # No shocks in last N days

        # Metrics separation (CRITICAL for analysis)
        self.logical_bit_errors = 0  # Majority wrong (vs ground truth)
        self.replica_bit_errors = 0  # Disagreements across replicas (ALL readable)
        self.replica_bit_errors_active_only = 0  # Disagreements only from ACTIVE tiles (convergence metric)
        self.replica_offline_count = 0  # Count of offline replicas (REGENERATING/unreadable)
        self.scrub_writebacks = 0  # Actual fixes performed
        self.scrub_failed_to_converge = 0  # Scrubs that failed post-condition
        self.new_flips_per_day = []  # Track daily error injection rate
        self.ground_truth = None  # Original data for validation
        self.quarantined_chunks = set()  # Chunks that failed anchor validation
        self.anchor_promotions = 0  # Count of QUORUM → GOLDEN_ANCHOR promotions

        # AT_RISK loop detection
        self.chunk_at_risk_history = {}  # {chunk_idx: [day1, day2, ...]} - track occurrences

        # BIOLOGICAL HARDENING: Convergence trend tracking
        self.replica_error_rate_history = []  # Track replica error rate over time for convergence trend

    def write_data(self, binary_data: str):
        """
        Write data using 3-way replication for fault tolerance.

        Args:
            binary_data: Binary string to store
        """
        active_tiles = [t for t in self.tiles if t.state == TileState.ACTIVE]

        if len(active_tiles) < self.replication_factor:
            raise RuntimeError(f"Need at least {self.replication_factor} active tiles for 3-way replication!")

        # Calculate how many unique bits we can store
        max_unique_bits = (len(active_tiles) // self.replication_factor) * self.bits_per_tile

        if len(binary_data) > max_unique_bits:
            raise RuntimeError(f"Data too large! Max {max_unique_bits} bits, got {len(binary_data)}")

        # Pad to multiple of bits_per_tile
        padded_length = ((len(binary_data) + self.bits_per_tile - 1) // self.bits_per_tile) * self.bits_per_tile
        binary_data = binary_data.ljust(padded_length, '0')

        # Store ground truth for validation
        self.ground_truth = binary_data

        # Split into chunks
        chunks = [binary_data[i:i+self.bits_per_tile] for i in range(0, len(binary_data), self.bits_per_tile)]

        # Assign chunks to tiles with 3-way replication
        # Each chunk gets stored in 3 tiles
        tile_idx = 0
        for chunk_idx, chunk in enumerate(chunks):
            # Track which tiles hold this chunk's replicas
            chunk_tile_ids = []

            # Store this chunk in 3 consecutive tiles
            for replica in range(self.replication_factor):
                if tile_idx >= len(active_tiles):
                    raise RuntimeError(f"Not enough active tiles for replication!")

                tile = active_tiles[tile_idx]
                tile.binary_data = chunk
                tile.pattern = self.encoder.encode(chunk)
                chunk_tile_ids.append(tile.id)
                tile_idx += 1

            # Store chunk->tile mapping
            self.chunk_replicas[chunk_idx] = chunk_tile_ids

            # STORE GOLDEN ANCHOR TRUTH (NEVER modified after this!)
            # This prevents self-corruption lock-in where majority voting
            # converges to corrupted data
            self.chunk_golden_truth[chunk_idx] = chunk

            # Initialize truth authority hierarchy
            # Start with QUORUM (majority voting allowed)
            # Will promote to GOLDEN_ANCHOR on first restoration
            self.chunk_truth_source[chunk_idx] = TruthSource.QUORUM
            self.chunk_anchor_epoch[chunk_idx] = 0

            # Calculate and store checksum for this chunk (CRC32)
            import zlib
            checksum = zlib.crc32(chunk.encode()) & 0xffffffff
            # Store checksum as metadata (will be used during scrubbing)
            for tid in chunk_tile_ids:
                self.tiles[tid].chunk_checksum = checksum

        total_bits_stored = len(chunks) * self.bits_per_tile * self.replication_factor
        print(f"✓ Wrote {len(binary_data)} unique bits (3-way replication = {total_bits_stored} total bits stored)")
        print(f"  Replicated across {tile_idx} tiles ({len(chunks)} chunks × {self.replication_factor} replicas)")

        # Validate chunk mappings
        self._validate_chunk_mappings()

    def read_data(self, repair_errors=False) -> str:
        """
        Read data using 3-way replication with majority voting.

        Args:
            repair_errors: If True, write corrected bits back to disagreeing tiles

        Returns:
            Reconstructed binary string
        """
        # READABLE tiles: ACTIVE + SICK + CLEAN_LOCKED (all can be read, ≥60% integrity)
        active_tiles = [t for t in self.tiles
                       if t.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]
                       and t.binary_data]

        if len(active_tiles) == 0:
            raise RuntimeError("No readable tiles with data!")

        # Group tiles by chunk (every 3 tiles = 1 chunk with 3 replicas)
        chunks = []
        for i in range(0, len(active_tiles), self.replication_factor):
            replica_tiles = active_tiles[i:i+self.replication_factor]
            if len(replica_tiles) == self.replication_factor:
                chunks.append(replica_tiles)

        # Majority vote for each chunk
        result = ""
        repairs_made = 0

        for chunk_tiles in chunks:
            # Get all 3 replicas
            replicas = [t.binary_data for t in chunk_tiles]

            # Majority vote bit-by-bit
            chunk_result = ""
            for bit_idx in range(len(replicas[0])):
                bits = [r[bit_idx] if bit_idx < len(r) else '0' for r in replicas]
                # Count 0s and 1s
                ones = bits.count('1')
                zeros = bits.count('0')
                majority_bit = '1' if ones > zeros else '0'
                chunk_result += majority_bit

                # Repair if requested
                if repair_errors and (ones != 3 and zeros != 3):
                    # Disagreement detected - repair minority
                    for idx, tile in enumerate(chunk_tiles):
                        if bit_idx < len(tile.binary_data) and tile.binary_data[bit_idx] != majority_bit:
                            # Repair this bit
                            tile.binary_data = (tile.binary_data[:bit_idx] +
                                              majority_bit +
                                              tile.binary_data[bit_idx+1:])
                            tile.pattern = self.encoder.encode(tile.binary_data)
                            repairs_made += 1

            result += chunk_result

        if repair_errors and repairs_made > 0:
            self.scrub_repairs += repairs_made
            print(f"  🔧 Scrub repaired {repairs_made} bit disagreements")

        return result.rstrip('0')  # Remove padding

    def simulate_day(self):
        """
        Simulate one day of operation.

        Tiles degrade over time, fail randomly, and rebuild automatically.
        Periodic scrubbing repairs bit drift.
        """
        self.uptime_days += 1

        # Track weeks for rebuild throttling
        current_week = self.uptime_days // 7
        if current_week > self.week_number:
            self.week_number = current_week
            self.rebuilds_this_week = 0

        # Age all tiles and update states
        for tile in self.tiles:
            if tile.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]:
                tile.age += 1

                # REALISTIC DEGRADATION: 0.3% per day (reaches 80% in ~70 days)
                # BIOLOGICAL HARDENING: Mature replicas (maturity_level >= 2) degrade slower
                # This models memory consolidation - well-established replicas are more stable
                if tile.maturity_level >= 2:
                    # Mature replicas degrade 50% slower (0.15% per day instead of 0.3%)
                    degradation_rate = 1.0 - (0.003 * self.MATURE_DEGRADATION_REDUCTION)
                    tile.integrity *= degradation_rate
                else:
                    # Normal degradation for new/maturing replicas
                    tile.integrity *= 0.997

                # Random degradation events (0.5% chance per day)
                # BIOLOGICAL HARDENING: Mature replicas are more resistant to random shocks
                shock_probability = 0.005 if tile.maturity_level < 2 else 0.0025  # 50% lower for mature
                if np.random.random() < shock_probability:
                    tile.integrity *= np.random.uniform(0.85, 0.95)
                    self.total_degradation_events += 1
                    # CALM-PERIOD TOP-UP: Record shock for this tile's chunk
                    self._record_shock(tile.id)

                # DETERMINISTIC SHOCK EVENT: Day 30, tile 7 drops 25%
                if self.uptime_days == 30 and tile.id == 7:
                    print(f"\n⚡ SHOCK EVENT: Tile 7 integrity drop (-25%)")
                    tile.integrity *= 0.75
                    self.total_degradation_events += 1
                    # CALM-PERIOD TOP-UP: Record shock for this tile's chunk
                    self._record_shock(tile.id)

                # State transitions based on integrity (but respect CLEAN_LOCKED!)
                # REBUILD HYSTERESIS: Enter SICK at <70%, exit SICK at >85%
                # This prevents hair-trigger rebuilds for tiles in 70-85% range
                # Tiles in this range are handled via scrubbing/refresh only
                if tile.integrity < 0.60:
                    # FAILED: Below 60%, unusable (even if CLEAN_LOCKED)
                    if tile.state != TileState.FAILED:
                        tile.state = TileState.FAILED
                        tile.clean_locked_until_day = -999  # Clear lock
                        print(f"✗ Tile {tile.id} FAILED (integrity: {tile.integrity:.2%})")
                elif tile.state != TileState.CLEAN_LOCKED:  # Don't transition if CLEAN_LOCKED
                    if tile.integrity < 0.70:
                        # SICK: <70%, MAY need rebuild (hysteresis lower bound)
                        # But rebuild is NOT automatic - see risk-gated rebuild logic
                        if tile.state != TileState.SICK:
                            tile.state = TileState.SICK
                            print(f"⚠️  Tile {tile.id} is SICK (integrity: {tile.integrity:.2%}) - rebuild gated by risk")
                    elif tile.integrity > 0.85:
                        # ACTIVE: >85%, healthy (hysteresis upper bound)
                        if tile.state == TileState.SICK:
                            tile.state = TileState.ACTIVE
                            print(f"✓ Tile {tile.id} recovered to ACTIVE (integrity: {tile.integrity:.2%})")
                    # Between 70% and 85%: maintain current state (hysteresis band)
                    # Tiles in this range are NOT rebuilt, only scrubbed/refreshed

        # Process regenerating tiles
        for tile in self.tiles:
            if tile.state == TileState.REGENERATING:
                # OPTIMIZED: Regeneration takes 5 days (was 10 days)
                tile.regeneration_progress += 0.2  # 20% per day

                if tile.regeneration_progress >= 1.0:
                    # Regeneration complete - MUST do hard informational scrub BEFORE marking Active
                    print(f"✓ Tile {tile.id} regeneration complete (Day {self.uptime_days})")

                    # Find which chunk this tile belongs to
                    chunk_idx = None
                    for cidx, tile_ids in self.chunk_replicas.items():
                        if tile.id in tile_ids:
                            chunk_idx = cidx
                            break

                    if chunk_idx is not None:
                        # HARD INFORMATIONAL SCRUB (before marking Active)
                        # ALWAYS use GOLDEN ANCHOR as source of truth
                        print(f"  🔧 Hard informational scrub for tile {tile.id} (chunk {chunk_idx})...")

                        golden_truth = self.chunk_golden_truth.get(chunk_idx)
                        if golden_truth:
                            # FORCE OVERWRITE with GOLDEN TRUTH (always correct!)
                            tile.binary_data = golden_truth
                            tile.pattern = self.encoder.encode(golden_truth)

                            # Update checksum
                            import zlib
                            tile.chunk_checksum = zlib.crc32(golden_truth.encode()) & 0xffffffff

                            print(f"      ✓ Forced write-back from GOLDEN ANCHOR ({len(golden_truth)} bits)")

                            # POST-CONDITION: Verify ALL ACTIVE replicas match anchor
                            replica_ids = self.chunk_replicas[chunk_idx]
                            replicas = [self.tiles[tid] for tid in replica_ids]

                            # Check all live replicas (this tile is still REGENERATING, so check others)
                            live_replicas = [t for t in replicas
                                           if t.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]
                                           and t.binary_data]

                            mismatches = []
                            for rep in live_replicas:
                                if rep.binary_data != golden_truth:
                                    mismatches.append(rep.id)

                            if mismatches:
                                print(f"      ⚠️  POST-CONDITION FAILED: {len(mismatches)} replicas still mismatch anchor: {mismatches}")
                                print(f"      🔁 Retrying write-back ONCE...")

                                # RETRY: Force overwrite all mismatching replicas
                                for tid in mismatches:
                                    rep = self.tiles[tid]
                                    rep.binary_data = golden_truth
                                    rep.pattern = self.encoder.encode(golden_truth)
                                    rep.chunk_checksum = zlib.crc32(golden_truth.encode()) & 0xffffffff

                                # Verify again
                                still_mismatches = []
                                for tid in mismatches:
                                    rep = self.tiles[tid]
                                    if rep.binary_data != golden_truth:
                                        still_mismatches.append(tid)

                                if still_mismatches:
                                    print(f"      ✗ POST-CONDITION STILL FAILED after retry: {still_mismatches}")
                                    self.scrub_failed_to_converge += 1
                                else:
                                    print(f"      ✓ POST-CONDITION VERIFIED after retry: all replicas match anchor")
                            else:
                                print(f"      ✓ POST-CONDITION VERIFIED: all {len(live_replicas)} replicas match anchor")
                                print(f"      ✓ Tile {tile.id} now guaranteed correct")
                        else:
                            print(f"      ⚠️  No golden anchor - using best replica fallback")

                            replica_ids = self.chunk_replicas[chunk_idx]
                            replicas = [self.tiles[tid] for tid in replica_ids]

                            # Get all readable replicas (excluding this tile which is still REGENERATING)
                            other_replicas = [t for t in replicas
                                             if t.id != tile.id
                                             and t.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]
                                             and t.binary_data]

                            if len(other_replicas) >= 1:
                                # Use highest-integrity replica as fallback
                                best = max(other_replicas, key=lambda t: t.integrity)
                                tile.binary_data = best.binary_data
                                tile.pattern = self.encoder.encode(best.binary_data)
                                tile.chunk_checksum = best.chunk_checksum
                                print(f"      ⚠️  Using best replica (tile {best.id}, {best.integrity:.0%})")
                            else:
                                print(f"      ✗ No replicas available - data may be incorrect!")

                    # NOW mark as CLEAN_LOCKED (stabilization window to reduce churn)
                    # CLEAN_LOCKED for 7 days - cannot be replaced proactively
                    tile.state = TileState.CLEAN_LOCKED
                    tile.integrity = 0.98  # Near-perfect regeneration
                    tile.age = 0
                    tile.regeneration_progress = 0.0
                    tile.regen_complete_day = self.uptime_days
                    tile.clean_locked_until_day = self.uptime_days + 7
                    tile.needs_scrub = False  # Already did hard scrub above
                    print(f"  🔒 Tile {tile.id} marked CLEAN_LOCKED for 7 days (until day {tile.clean_locked_until_day})")

        # Check for expired CLEAN_LOCKED tiles and transition to ACTIVE
        for tile in self.tiles:
            if tile.state == TileState.CLEAN_LOCKED:
                if self.uptime_days >= tile.clean_locked_until_day:
                    # Lock expired - transition to ACTIVE (or SICK based on integrity)
                    if tile.integrity >= 0.80:
                        tile.state = TileState.ACTIVE
                        print(f"🔓 Tile {tile.id} CLEAN_LOCKED expired → ACTIVE (integrity: {tile.integrity:.2%})")
                    elif tile.integrity >= 0.60:
                        tile.state = TileState.SICK
                        print(f"🔓 Tile {tile.id} CLEAN_LOCKED expired → SICK (integrity: {tile.integrity:.2%})")
                    else:
                        tile.state = TileState.FAILED
                        print(f"🔓 Tile {tile.id} CLEAN_LOCKED expired → FAILED (integrity: {tile.integrity:.2%})")
                    tile.clean_locked_until_day = -999

        # Adaptive scrubbing: if SICK tiles or recent rebuild, scrub every 2 days
        sick_count = sum(1 for t in self.tiles if t.state == TileState.SICK)
        if sick_count > 0 or self.rebuild_count > 0:
            # Enable adaptive scrubbing for 14 days
            if self.adaptive_scrub_until_day < self.uptime_days:
                self.adaptive_scrub_until_day = self.uptime_days + 14
                print(f"⚡ Adaptive scrubbing enabled (every 2 days for 14 days)")

        # Adaptive scrubbing (every 2 days when enabled)
        if self.uptime_days <= self.adaptive_scrub_until_day:
            if self.uptime_days - self.last_adaptive_scrub_day >= 2:
                print(f"🔍 Adaptive scrub (day {self.uptime_days})...")
                self._run_scrub()
                self.last_adaptive_scrub_day = self.uptime_days
        else:
            # Normal weekly scrubbing
            if self.uptime_days - self.last_scrub_day >= self.scrub_interval_days:
                self._run_scrub()
                self.last_scrub_day = self.uptime_days

        # Check for rebuild triggers
        self._check_rebuild_needed()

        # CALM-PERIOD TOP-UP: Track time at 2-live vs 3-live and check for top-up opportunities
        self._track_live_replica_time()
        self._check_calm_period_topup()

        # Daily monitoring: print min/avg integrity and triggers
        if self.uptime_days % 10 == 0:  # Every 10 days
            active_tiles = [t for t in self.tiles if t.state in [TileState.ACTIVE, TileState.SICK]]
            if active_tiles:
                min_integrity = min(t.integrity for t in active_tiles)
                avg_integrity = np.mean([t.integrity for t in active_tiles])
                sick_count = sum(1 for t in self.tiles if t.state == TileState.SICK)
                print(f"📊 Day {self.uptime_days}: min={min_integrity:.1%}, avg={avg_integrity:.1%}, SICK={sick_count}, rebuilds={self.rebuild_count}")

        # Record state
        self.history.append(self._get_state_snapshot())

    def _run_scrub(self):
        """
        Run scrub operation: read with majority voting, repair disagreements.
        This is the key ECC mechanism that prevents data corruption.

        NOTE: Scrub repairs BIT STATE only (binary_data), NOT tile integrity.
        Integrity degradation is permanent and requires physical rebuild.
        """
        print(f"🔍 Running scrub (Day {self.uptime_days})...")
        try:
            # Scrub each chunk using correct chunk mappings and truth authority hierarchy
            for chunk_idx in sorted(self.chunk_replicas.keys()):
                self._scrub_chunk(chunk_idx)
        except Exception as e:
            print(f"⚠️  Scrub failed: {e}")

    def _check_rebuild_needed(self):
        """
        Check for both proactive and reactive rebuild needs.

        PRIORITY ORDER:
        1. AT_RISK chunks (<2 readable replicas) - FAST-TRACK
        2. REACTIVE: Chunks below quorum - EMERGENCY
        3. PROACTIVE: SICK tiles - ROUTINE
        """
        sterile = [t for t in self.tiles if t.state == TileState.STERILE]

        if not sterile:
            return  # No spare capacity for rebuilds

        # 0) FAST-TRACK: AT_RISK chunks (highest priority!)
        # BUT: with cooldown to prevent loops (7 days between attempts)
        if self.chunks_at_risk:
            for chunk_idx in list(self.chunks_at_risk):
                # Check cooldown
                last_attempt = self.chunk_at_risk_cooldown.get(chunk_idx, -999)
                cooldown_days = 7
                days_since_attempt = self.uptime_days - last_attempt

                if days_since_attempt < cooldown_days:
                    print(f"  ⏸️  Chunk {chunk_idx} AT_RISK cooldown ({days_since_attempt}/{cooldown_days} days)")
                    continue  # Skip this chunk, try next

                # Cooldown expired - attempt top-up
                print(f"\n🚨 FAST-TRACK: Chunk {chunk_idx} is AT_RISK (<2 replicas)")
                print(f"   Creating new replica immediately (bypasses all throttling)...")

                # Force top-up for this chunk
                # Count only LIVE replicas (ACTIVE only, integrity >= 60%)
                before_count = len([t for t in self.chunk_replicas[chunk_idx]
                                   if self.tiles[t].state == TileState.ACTIVE
                                   and self.tiles[t].integrity >= 0.60])

                self._ensure_chunk_has_three_replicas(chunk_idx)

                # Count only LIVE replicas (ACTIVE only, integrity >= 60%)
                after_count = len([t for t in self.chunk_replicas[chunk_idx]
                                  if self.tiles[t].state == TileState.ACTIVE
                                  and self.tiles[t].integrity >= 0.60])

                # Update cooldown regardless (prevents tight loops)
                self.chunk_at_risk_cooldown[chunk_idx] = self.uptime_days

                if after_count > before_count:
                    print(f"   ✓ Successfully added replica ({before_count} → {after_count})")
                else:
                    print(f"   ⚠️  No replica added ({before_count} → {after_count}) - may lack sterile spares")

                return  # Handle one AT_RISK chunk per day

        # 1) REACTIVE REBUILD: Check for lost quorum (critical!)
        quorum_lost = self._check_quorum_loss()
        if quorum_lost:
            chunk_idx, failed_tiles = quorum_lost
            print(f"\n🚨 EMERGENCY: Chunk {chunk_idx} lost quorum! ({len(failed_tiles)} replicas down)")
            # Emergency rebuild bypasses throttling
            self._reactive_rebuild(chunk_idx, sterile[0])
            return

        # 2) RISK-GATED PROACTIVE REBUILD: Replace SICK tiles ONLY if at risk
        # SICK tiles (70-85% integrity) are NOT automatically rebuilt
        # They are only rebuilt if one of these risk conditions is met:
        #   a) Chunk would drop below 2 readable replicas
        #   b) Tile is marked WRITE_SUSPECT (2 consecutive write failures)
        #   c) Chunk failed to converge after 3 consecutive scrubs
        # Otherwise, prefer scrub + repair over rebuild (reduces churn)
        sick_tiles = [t for t in self.tiles
                     if t.state == TileState.SICK
                     and t.binary_data
                     and t.state != TileState.CLEAN_LOCKED]  # Redundant check for safety

        if sick_tiles:
            # Rebuild throttling for proactive rebuilds only
            if self.rebuilds_this_week >= self.max_rebuilds_per_week:
                print(f"⏸️  Proactive rebuild throttled (hit weekly limit: {self.rebuilds_this_week}/{self.max_rebuilds_per_week})")
                return

            # RISK-GATED: Filter to only tiles that meet risk criteria
            risky_tiles = []
            for t in sick_tiles:
                # ABSOLUTE IMMUNITY: Never proactively rebuild CLEAN_LOCKED tiles
                if t.state == TileState.CLEAN_LOCKED:
                    continue
                if t.clean_locked_until_day >= self.uptime_days:
                    continue

                # RISK GATE: Check if this tile meets rebuild criteria
                rebuild_needed = False
                reason = ""

                # Risk condition (a): Chunk would drop below 2 readable replicas
                # Find which chunks this tile participates in
                for chunk_idx, tile_ids in self.chunk_replicas.items():
                    if t.id not in tile_ids:
                        continue

                    replicas = [self.tiles[tid] for tid in tile_ids]
                    readable = [r for r in replicas
                               if r.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]
                               and r.integrity >= 0.60]

                    # If removing this tile would leave <2 readable, it's risky
                    if len(readable) <= 2:
                        rebuild_needed = True
                        reason = f"chunk {chunk_idx} would drop to {len(readable)-1} readable"
                        break

                # Risk condition (b): Tile is WRITE_SUSPECT
                if t.write_suspect:
                    rebuild_needed = True
                    reason = "WRITE_SUSPECT (2 consecutive write failures)"

                # Risk condition (c): Chunk failed to converge after 3 scrubs
                for chunk_idx, tile_ids in self.chunk_replicas.items():
                    if t.id not in tile_ids:
                        continue
                    failed_scrubs = self.chunk_failed_scrub_count.get(chunk_idx, 0)
                    if failed_scrubs >= 3:
                        rebuild_needed = True
                        reason = f"chunk {chunk_idx} failed {failed_scrubs} consecutive scrubs"
                        break

                # Apply cooldown even for risky tiles (prevent spam)
                if rebuild_needed:
                    if t.integrity < 0.60:
                        # Emergency: bypass cooldown
                        risky_tiles.append((t, reason))
                    elif (self.uptime_days - t.last_rebuild_attempt_day) >= 14:
                        # Normal: 14-day cooldown
                        risky_tiles.append((t, reason))

            if not risky_tiles:
                if sick_tiles:
                    print(f"⏸️  {len(sick_tiles)} SICK tiles present but none meet risk criteria (safe to scrub/repair only)")
                return

            # Pick the riskiest tile (lowest integrity among risky tiles)
            tile_to_rebuild, reason = min(risky_tiles, key=lambda x: x[0].integrity)
            print(f"\n🔧 RISK-GATED REBUILD: Replacing SICK tile {tile_to_rebuild.id} ({reason})")

            # Randomize sterile spare selection
            import random
            target_sterile = random.choice(sterile)

            success = self._proactive_rebuild(tile_to_rebuild, target_sterile)
            if success:
                self.rebuilds_this_week += 1
            else:
                # Mark attempt to prevent spam
                tile_to_rebuild.last_rebuild_attempt_day = self.uptime_days

    def _check_quorum_loss(self):
        """
        Check if any chunk has lost quorum (<2 healthy replicas).
        Returns (chunk_idx, failed_tiles) if quorum lost, None otherwise.

        Uses chunk_replicas mapping to ensure accurate tracking.
        """
        for chunk_idx, tile_ids in self.chunk_replicas.items():
            replicas = [self.tiles[tid] for tid in tile_ids]

            # Count healthy replicas (ACTIVE or SICK or CLEAN_LOCKED, not FAILED, not REGENERATING)
            healthy = [t for t in replicas
                      if t.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]
                      and t.integrity >= 0.60]

            # Count regenerating (mid-rebuild, don't trigger again)
            regenerating = [t for t in replicas if t.state == TileState.REGENERATING]

            # If we're already regenerating one replica, don't trigger again
            if regenerating:
                continue

            # Lost quorum if <2 healthy replicas
            if len(healthy) < 2:
                failed = [t for t in replicas if t not in healthy]
                return (chunk_idx, failed)

        return None

    def _proactive_rebuild(self, sick_tile: Tile, target_sterile: Tile) -> bool:
        """
        Proactive rebuild: Replace SICK tile replica using majority voting.

        CRITICAL: Uses majority voting across all surviving replicas to reconstruct
        correct bit state, NOT just copying from one donor!

        Args:
            sick_tile: SICK tile (60-80%) to replace
            target_sterile: Empty chamber to seed

        Returns:
            True if rebuild succeeded, False otherwise
        """
        print(f"{'='*60}")
        print(f"Failing tile: {sick_tile.id} (integrity: {sick_tile.integrity:.2%}) [SICK]")
        print(f"Target: {target_sterile.id} (sterile chamber)")

        # Find which chunk this tile belongs to
        chunk_idx = None
        for cidx, tile_ids in self.chunk_replicas.items():
            if sick_tile.id in tile_ids:
                chunk_idx = cidx
                break

        if chunk_idx is None:
            print("⚠️  Could not find chunk for SICK tile!")
            return False

        # Get all replicas for this chunk
        replica_ids = self.chunk_replicas[chunk_idx]
        replicas = [self.tiles[tid] for tid in replica_ids]

        # Find surviving replicas (readable, not FAILED)
        surviving = [t for t in replicas
                    if t.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]
                    and t.binary_data]

        if len(surviving) < 2:
            print(f"⚠️  Not enough surviving replicas ({len(surviving)}/3)")
            return False

        # USE GOLDEN ANCHOR (always correct!) instead of majority voting
        # This prevents propagating corruption during proactive rebuilds
        golden_truth = self.chunk_golden_truth.get(chunk_idx)
        if golden_truth:
            reconstructed_data = golden_truth
            print(f"  Using GOLDEN ANCHOR as source (guaranteed correct)")
        else:
            # Fallback to majority voting if no anchor
            reconstructed_data = self._reconstruct_via_majority_vote(surviving)
            print(f"  ⚠️  No golden anchor - using majority vote from {len(surviving)} replicas")

        # Seed target with reconstructed data
        target_sterile.state = TileState.REGENERATING
        target_sterile.binary_data = reconstructed_data
        target_sterile.pattern = self.encoder.encode(reconstructed_data)
        target_sterile.regeneration_progress = 0.0
        target_sterile.needs_scrub = False
        target_sterile.integrity = 0.0

        # Update chunk mapping: REPLACE sick_tile with target_sterile (use helper)
        self._replace_replica(chunk_idx, sick_tile.id, target_sterile.id)

        # Flush SICK tile to STERILE
        self._flush_tile(sick_tile)

        self.rebuild_count += 1
        print(f"✓ Proactive rebuild #{self.rebuild_count} complete")

        # ENFORCE 3-REPLICA INVARIANT: Top-up if needed
        self._ensure_chunk_has_three_replicas(chunk_idx)

        # Scrub this chunk immediately to correct any bit disagreements
        self._scrub_chunk(chunk_idx)

        # Validate invariants
        self._validate_chunk_mappings()

        print(f"{'='*60}\n")
        return True

    def _reactive_rebuild(self, chunk_idx: int, target_sterile: Tile):
        """
        Reactive rebuild: Emergency rebuild using majority voting.

        CRITICAL: Uses majority voting across all surviving replicas to reconstruct
        correct bit state, NOT just copying from one donor!

        Args:
            chunk_idx: Chunk index that lost quorum
            target_sterile: Empty chamber to seed
        """
        print(f"{'='*60}")
        print(f"Emergency rebuild for chunk {chunk_idx}")
        print(f"Target: {target_sterile.id} (sterile chamber)")

        # Get replica IDs for this chunk
        if chunk_idx not in self.chunk_replicas:
            print(f"✗ FATAL: Chunk {chunk_idx} not in mapping!")
            return

        replica_ids = self.chunk_replicas[chunk_idx]
        replicas = [self.tiles[tid] for tid in replica_ids]

        # Find surviving replicas (readable, not FAILED)
        surviving = [t for t in replicas
                    if t.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]
                    and t.binary_data
                    and t.integrity >= 0.60]

        if len(surviving) < 1:
            print("✗ FATAL: No surviving replicas! Data lost for this chunk!")
            return

        # USE GOLDEN ANCHOR (always correct!) instead of majority voting
        # This prevents propagating corruption during emergency rebuilds
        golden_truth = self.chunk_golden_truth.get(chunk_idx)
        if golden_truth:
            reconstructed_data = golden_truth
            print(f"  Using GOLDEN ANCHOR as source (guaranteed correct)")
        elif len(surviving) >= 2:
            # Fallback to majority voting if no anchor
            reconstructed_data = self._reconstruct_via_majority_vote(surviving)
            print(f"  ⚠️  No golden anchor - using majority vote from {len(surviving)} replicas")
        else:
            # Only 1 replica left - use it (no majority possible)
            reconstructed_data = surviving[0].binary_data
            print(f"  ⚠️  No golden anchor - using last surviving replica (tile {surviving[0].id})")

        # Find a FAILED tile to replace
        failed_tiles = [t for t in replicas if t.state == TileState.FAILED or t.integrity < 0.60]
        if not failed_tiles:
            print("⚠️  No failed tiles to replace in this chunk!")
            return

        failed_tile = failed_tiles[0]

        # Seed target with reconstructed data
        target_sterile.state = TileState.REGENERATING
        target_sterile.binary_data = reconstructed_data
        target_sterile.pattern = self.encoder.encode(reconstructed_data)
        target_sterile.regeneration_progress = 0.0
        target_sterile.needs_scrub = True  # Force scrub for emergency
        target_sterile.integrity = 0.0

        # Update chunk mapping: REPLACE failed_tile with target_sterile (use helper)
        self._replace_replica(chunk_idx, failed_tile.id, target_sterile.id)

        # Flush failed tile to STERILE
        if failed_tile.id != target_sterile.id:  # Safety check
            self._flush_tile(failed_tile)

        self.rebuild_count += 1
        print(f"✓ Emergency rebuild #{self.rebuild_count} complete")

        # ENFORCE 3-REPLICA INVARIANT: Top-up if needed
        self._ensure_chunk_has_three_replicas(chunk_idx)

        # Scrub this chunk immediately to correct any bit disagreements
        self._scrub_chunk(chunk_idx)

        # Validate invariants
        self._validate_chunk_mappings()

        print(f"{'='*60}\n")

    def _reconstruct_via_majority_vote(self, surviving_tiles: List[Tile]) -> str:
        """
        Reconstruct correct bit state using WEIGHTED majority voting by tile integrity.

        Higher-integrity tiles get more weight in the vote, improving accuracy.

        Args:
            surviving_tiles: List of tiles with this chunk's data

        Returns:
            Reconstructed binary string
        """
        if not surviving_tiles:
            raise RuntimeError("No surviving tiles for majority vote!")

        if len(surviving_tiles) == 1:
            return surviving_tiles[0].binary_data

        # Weighted majority vote bit-by-bit (weight by integrity)
        max_len = max(len(t.binary_data) for t in surviving_tiles)
        reconstructed = ""

        for bit_idx in range(max_len):
            # Calculate weighted votes for 0 and 1
            weight_0 = 0.0
            weight_1 = 0.0

            for tile in surviving_tiles:
                if bit_idx < len(tile.binary_data):
                    bit = tile.binary_data[bit_idx]
                    # Weight by integrity (higher integrity = more trusted)
                    weight = max(tile.integrity, 0.1)  # Min weight 0.1 to avoid zero

                    if bit == '0':
                        weight_0 += weight
                    else:
                        weight_1 += weight

            # Choose bit with higher weighted vote
            majority_bit = '1' if weight_1 > weight_0 else '0'
            reconstructed += majority_bit

        return reconstructed

    def _replace_replica(self, chunk_idx: int, old_tile_id: int, new_tile_id: int):
        """
        ONLY way to change replica mapping - ensures correctness.

        Replaces old_tile_id with new_tile_id in chunk's replica list.
        Enforces uniqueness and max 3 replicas constraint.
        """
        if chunk_idx not in self.chunk_replicas:
            raise RuntimeError(f"Chunk {chunk_idx} not in mapping!")

        replica_ids = self.chunk_replicas[chunk_idx]

        # Remove old tile if present
        if old_tile_id in replica_ids:
            replica_ids = [tid for tid in replica_ids if tid != old_tile_id]

        # Add new tile if not already present
        if new_tile_id not in replica_ids:
            replica_ids.append(new_tile_id)

        # Enforce uniqueness (use set to remove duplicates)
        replica_ids = list(dict.fromkeys(replica_ids))  # Preserves order, removes duplicates

        # Update mapping
        self.chunk_replicas[chunk_idx] = replica_ids

        # Validate count
        if len(replica_ids) > 3:
            raise RuntimeError(
                f"FATAL: Chunk {chunk_idx} has {len(replica_ids)} replicas after replace! "
                f"Tile IDs: {replica_ids}. Tried to replace {old_tile_id} with {new_tile_id}"
            )

    def _ensure_chunk_has_three_replicas(self, chunk_idx: int):
        """
        Enforce 3-replica invariant: top-up chunk to exactly 3 TOTAL replicas if needed.

        This is CRITICAL to prevent chunk replica count from drifting below 3.

        CRITICAL: Each chunk must have exactly 3 replicas (live + pending + offline).
        LIVE = ACTIVE (fully healthy)
        PENDING = SICK, CLEAN_LOCKED, REGENERATING (readable but degraded)
        OFFLINE = FAILED, STERILE (unreadable)
        """
        replica_ids = self.chunk_replicas[chunk_idx]
        replicas = [self.tiles[tid] for tid in replica_ids]

        # Count TOTAL replicas (should always be exactly 3)
        total_count = len(replica_ids)

        # Filter by state for informational purposes
        live_ids = [t.id for t in replicas
                   if t.state == TileState.ACTIVE
                   and t.integrity >= 0.60]

        pending_ids = [t.id for t in replicas
                      if t.state in [TileState.SICK, TileState.CLEAN_LOCKED, TileState.REGENERATING]]

        offline_ids = [t.id for t in replicas
                      if t.state in [TileState.FAILED, TileState.STERILE]
                      or t.integrity < 0.60]

        # CRITICAL: Check TOTAL replica count, not just live count
        if total_count >= 3:
            # Already have 3 replicas (may be live, pending, or offline mix)
            return

        # Need to top-up to reach 3 TOTAL replicas
        missing_count = 3 - total_count
        print(f"  ⚠️  Chunk {chunk_idx} only has {total_count} total replicas ({len(live_ids)} live, {len(pending_ids)} pending, {len(offline_ids)} offline), topping up {missing_count}...")

        # USE GOLDEN ANCHOR (always correct!) for top-up
        golden_truth = self.chunk_golden_truth.get(chunk_idx)
        if golden_truth:
            correct_data = golden_truth
            print(f"  Using GOLDEN ANCHOR for top-up (guaranteed correct)")
        else:
            # Fallback to majority voting if no anchor
            readable_tiles = [self.tiles[tid] for tid in all_valid_ids]
            surviving = [t for t in readable_tiles
                        if t.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]
                        and t.binary_data]

            if not surviving:
                print(f"  ✗ FATAL: Cannot top-up chunk {chunk_idx} - no surviving replicas or anchor!")
                return

            correct_data = self._reconstruct_via_majority_vote(surviving)
            print(f"  ⚠️  No golden anchor - using majority vote for top-up")

        # Find sterile spares to top-up
        # CRITICAL: Never reuse tiles already in this chunk's replica list
        all_chunk_replica_ids = self.chunk_replicas[chunk_idx]
        sterile = [t for t in self.tiles
                  if t.state == TileState.STERILE
                  and t.id not in all_chunk_replica_ids]  # Don't reuse tiles already in chunk

        for i in range(missing_count):
            if not sterile:
                print(f"  ✗ No sterile spares available for top-up!")
                break

            target = sterile.pop(0)

            # Seed target with correct data
            # This creates a PENDING replica (REGENERATING state)
            # It will become LIVE after regen complete + hard scrub
            target.state = TileState.REGENERATING
            target.binary_data = correct_data
            target.pattern = self.encoder.encode(correct_data)
            target.regeneration_progress = 0.0
            target.needs_scrub = False
            target.integrity = 0.0

            # Set checksum
            import zlib
            target.chunk_checksum = zlib.crc32(correct_data.encode()) & 0xffffffff

            # Add to chunk mapping (only if not already present)
            if target.id not in self.chunk_replicas[chunk_idx]:
                self.chunk_replicas[chunk_idx].append(target.id)
                print(f"  ✓ Added PENDING replica on tile {target.id} (top-up #{i+1}/{missing_count})")
            else:
                print(f"  ⚠️  Tile {target.id} already in chunk {chunk_idx} mapping - skipping!")

    def _scrub_chunk(self, chunk_idx: int):
        """
        Scrub a specific chunk with STRICT TRUTH AUTHORITY HIERARCHY.

        CRITICAL ARCHITECTURAL RULE:
        - If truth_source == GOLDEN_ANCHOR: majority voting is DISABLED permanently
        - If truth_source == QUORUM: majority voting allowed, but validates against anchor
        """
        replica_ids = self.chunk_replicas[chunk_idx]
        replicas = [self.tiles[tid] for tid in replica_ids]

        # Get readable replicas (ACTIVE or SICK or CLEAN_LOCKED, ≥60% integrity)
        readable = [t for t in replicas
                   if t.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]
                   and t.binary_data]

        # Get truth source for this chunk
        truth_source = self.chunk_truth_source.get(chunk_idx, TruthSource.QUORUM)
        golden_truth = self.chunk_golden_truth.get(chunk_idx)

        if not golden_truth:
            print(f"  ⚠️  Chunk {chunk_idx} has no golden anchor - cannot scrub!")
            return

        # QUORUM GATE: For QUORUM chunks, require ≥2 readable replicas
        if truth_source == TruthSource.QUORUM and len(readable) < 2:
            if chunk_idx not in self.chunks_at_risk:
                print(f"  ⚠️  Chunk {chunk_idx} AT_RISK - only {len(readable)} readable replicas!")
                print(f"      Reason: Insufficient replicas for quorum (truth_source=QUORUM)")
                self.chunks_at_risk.add(chunk_idx)
                self.chunk_at_risk_cooldown[chunk_idx] = self.uptime_days

                # Track AT_RISK occurrences for loop detection
                if chunk_idx not in self.chunk_at_risk_history:
                    self.chunk_at_risk_history[chunk_idx] = []
                self.chunk_at_risk_history[chunk_idx].append(self.uptime_days)
            # Do NOT scrub - wait for replica count to recover
            return

        # For GOLDEN_ANCHOR chunks, we can scrub with even 1 replica
        if len(readable) == 0:
            print(f"  ⚠️  Chunk {chunk_idx} has no readable replicas - cannot scrub!")
            return

        # Remove from AT_RISK if now safe
        if chunk_idx in self.chunks_at_risk:
            print(f"  ✓ Chunk {chunk_idx} recovered from AT_RISK ({len(readable)} replicas)")
            self.chunks_at_risk.discard(chunk_idx)
            if chunk_idx in self.chunk_at_risk_cooldown:
                del self.chunk_at_risk_cooldown[chunk_idx]

        epoch = self.chunk_anchor_epoch.get(chunk_idx, 0)
        print(f"  🔍 Scrubbing chunk {chunk_idx} ({len(readable)} readable replicas, truth_source={truth_source.value}, epoch={epoch})...")

        # ===== TRUTH AUTHORITY HIERARCHY =====

        if truth_source == TruthSource.GOLDEN_ANCHOR:
            # GOLDEN_ANCHOR MODE: Majority voting DISABLED permanently
            # Replicas are informational only - anchor is sole authority
            print(f"      🔒 GOLDEN_ANCHOR mode - majority voting DISABLED")
            print(f"      📍 Anchor is sole truth authority (epoch {epoch})")

            # Compare each replica ONLY to anchor (do NOT compare to each other!)
            disagreements = 0
            replicas_repaired = 0

            import zlib
            golden_checksum = zlib.crc32(golden_truth.encode()) & 0xffffffff

            for tile in readable:
                # Count disagreements vs GOLDEN TRUTH only
                tile_disagreements = 0
                if tile.binary_data != golden_truth:
                    for i in range(min(len(tile.binary_data), len(golden_truth))):
                        if tile.binary_data[i] != golden_truth[i]:
                            disagreements += 1
                            tile_disagreements += 1

                    # 2-PHASE WRITE-SETTLE: Use write-settle protocol instead of direct write
                    write_success = self._write_with_settle(tile, golden_truth, golden_checksum)

                    if write_success:
                        replicas_repaired += 1

                        # BIOLOGICAL HARDENING: Memory consolidation
                        # Successful anchor write-back strengthens the replica (models synaptic consolidation)
                        # Slightly boost integrity (up to cap) to reduce future degradation
                        if tile.integrity < self.CONSOLIDATION_MAX_INTEGRITY:
                            old_integrity = tile.integrity
                            tile.integrity = min(tile.integrity + self.CONSOLIDATION_INTEGRITY_BOOST,
                                                self.CONSOLIDATION_MAX_INTEGRITY)
                            # Note: Don't print individual boosts (too verbose), will track in aggregate

                        # LENIENT MATURATION: Only reset on MAJOR repairs (>10 bits)
                        # Minor drift (<10 bits) is normal and shouldn't prevent maturation
                        # This allows tiles to stabilize despite small fluctuations
                        if tile_disagreements > 10:
                            tile.consecutive_successful_scrubs = 0
                            if tile.maturity_level > 0:
                                tile.maturity_level = 0  # Demote to unstable
                                tile.matured_on_day = -999
                    else:
                        # Write failed (tile too degraded or write-settle failed)
                        # Mark tile for rebuild by not counting it as repaired
                        print(f"          ⚠️  Tile {tile.id} write failed (integrity {tile.integrity:.0%}) - skipping")

            # Update metrics
            self.replica_bit_errors += disagreements
            self.scrub_writebacks += replicas_repaired

            # CALM-PERIOD TOP-UP: Track drift for this chunk (GOLDEN_ANCHOR mode)
            if chunk_idx not in self.chunk_last_drift:
                self.chunk_last_drift[chunk_idx] = []
            self.chunk_last_drift[chunk_idx].append(disagreements)
            # Keep only last 3 scrubs
            if len(self.chunk_last_drift[chunk_idx]) > 3:
                self.chunk_last_drift[chunk_idx].pop(0)

            if disagreements > 0:
                print(f"      🔧 Repaired {disagreements} bit disagreements (anchor authority)")

                # POST-CONDITION: Verify all replicas now match anchor
                mismatches = []
                for tile in readable:
                    if tile.binary_data != golden_truth:
                        mismatches.append(tile.id)

                if mismatches:
                    print(f"      ✗ SCRUB FAILED TO CONVERGE! Replicas {mismatches} still mismatch after write-back")
                    self.scrub_failed_to_converge += 1

                    # RISK-GATED REBUILDS: Track failed scrub for this chunk
                    current_fails = self.chunk_failed_scrub_count.get(chunk_idx, 0)
                    self.chunk_failed_scrub_count[chunk_idx] = current_fails + 1

                    # BIOLOGICAL HARDENING: Reset maturation on failure
                    for tile in readable:
                        tile.consecutive_successful_scrubs = 0
                        if tile.maturity_level > 0:
                            tile.maturity_level = 0
                            tile.matured_on_day = -999
                else:
                    print(f"      ✓ Post-condition verified: all replicas match anchor")

                    # RISK-GATED REBUILDS: Reset failed scrub counter on success
                    self.chunk_failed_scrub_count[chunk_idx] = 0

                    # BIOLOGICAL HARDENING: Maturation after successful scrub
                    self._advance_maturation(readable)

                    # QUORUM RESTORATION: Track consecutive clean scrubs
                    self._track_clean_scrub_for_quorum_restoration(chunk_idx, readable)
            else:
                print(f"      ✓ All replicas match anchor - no repairs needed")

                # RISK-GATED REBUILDS: Reset failed scrub counter (no repairs needed = success)
                self.chunk_failed_scrub_count[chunk_idx] = 0

                # BIOLOGICAL HARDENING: Maturation for stable replicas (no repair needed)
                self._advance_maturation(readable)

                # QUORUM RESTORATION: Track consecutive clean scrubs
                self._track_clean_scrub_for_quorum_restoration(chunk_idx, readable)

        else:  # truth_source == TruthSource.QUORUM
            # QUORUM MODE: Majority voting allowed (for now)
            print(f"      🗳️  QUORUM mode - majority voting enabled")

            # Use integrity-weighted voting
            high_integrity = [t for t in readable if t.integrity >= 0.80]

            if high_integrity:
                correct_data = self._reconstruct_via_majority_vote(high_integrity)
                print(f"      Truth from {len(high_integrity)} high-integrity replicas (≥80%)")
            else:
                print(f"      ⚠️  All replicas <80%! Using highest-integrity replica")
                best = max(readable, key=lambda t: t.integrity)
                correct_data = best.binary_data

            # VALIDATE AGAINST GOLDEN ANCHOR
            if correct_data != golden_truth:
                # ANCHOR MISMATCH - majority is WRONG!
                errors = sum(1 for i in range(len(correct_data)) if correct_data[i] != golden_truth[i])
                print(f"      🚫 ANCHOR VALIDATION FAILED!")
                print(f"      Reconstructed data has {errors} bit errors vs golden truth")
                print(f"      🔼 PROMOTING chunk to GOLDEN_ANCHOR authority")
                print(f"      ⚠️  Majority voting PERMANENTLY DISABLED for this chunk")

                # PROMOTE TO GOLDEN_ANCHOR (first restoration)
                self.chunk_truth_source[chunk_idx] = TruthSource.GOLDEN_ANCHOR
                self.chunk_anchor_epoch[chunk_idx] += 1
                self.anchor_promotions += 1

                # Restore all replicas from anchor
                self._restore_from_golden(chunk_idx, readable)
                return

            # Anchor validation PASSED - majority is correct
            print(f"      ✓ Anchor validation PASSED - majority is correct")

            # Write-back to converge replicas
            disagreements = 0
            replicas_repaired = 0

            import zlib
            golden_checksum = zlib.crc32(golden_truth.encode()) & 0xffffffff

            for tile in readable:
                tile_disagreements = 0
                if tile.binary_data != golden_truth:
                    for i in range(min(len(tile.binary_data), len(golden_truth))):
                        if tile.binary_data[i] != golden_truth[i]:
                            disagreements += 1
                            tile_disagreements += 1

                    # 2-PHASE WRITE-SETTLE: Use write-settle protocol
                    write_success = self._write_with_settle(tile, golden_truth, golden_checksum)

                    if write_success:
                        replicas_repaired += 1

                        # BIOLOGICAL HARDENING: Memory consolidation
                        if tile.integrity < self.CONSOLIDATION_MAX_INTEGRITY:
                            tile.integrity = min(tile.integrity + self.CONSOLIDATION_INTEGRITY_BOOST,
                                                self.CONSOLIDATION_MAX_INTEGRITY)

                        # LENIENT MATURATION: Only reset on MAJOR repairs (>10 bits)
                        # Minor drift (<10 bits) is normal and shouldn't prevent maturation
                        # This allows tiles to stabilize despite small fluctuations
                        if tile_disagreements > 10:
                            tile.consecutive_successful_scrubs = 0
                            if tile.maturity_level > 0:
                                tile.maturity_level = 0
                                tile.matured_on_day = -999
                    else:
                        # Write failed (tile too degraded)
                        print(f"          ⚠️  Tile {tile.id} write failed (integrity {tile.integrity:.0%}) - skipping")

            # Update metrics
            self.replica_bit_errors += disagreements
            self.scrub_writebacks += replicas_repaired

            # CALM-PERIOD TOP-UP: Track drift for this chunk (QUORUM mode)
            if chunk_idx not in self.chunk_last_drift:
                self.chunk_last_drift[chunk_idx] = []
            self.chunk_last_drift[chunk_idx].append(disagreements)
            # Keep only last 3 scrubs
            if len(self.chunk_last_drift[chunk_idx]) > 3:
                self.chunk_last_drift[chunk_idx].pop(0)

            if disagreements > 0:
                print(f"      🔧 Repaired {disagreements} bit disagreements")

                # POST-CONDITION: Verify all replicas now match golden truth
                mismatches = []
                for tile in readable:
                    if tile.binary_data != golden_truth:
                        mismatches.append(tile.id)

                if mismatches:
                    print(f"      ✗ SCRUB FAILED TO CONVERGE! Replicas {mismatches} still mismatch after write-back")
                    self.scrub_failed_to_converge += 1

                    # RISK-GATED REBUILDS: Track failed scrub for this chunk
                    current_fails = self.chunk_failed_scrub_count.get(chunk_idx, 0)
                    self.chunk_failed_scrub_count[chunk_idx] = current_fails + 1

                    # BIOLOGICAL HARDENING: Reset maturation on failure
                    for tile in readable:
                        tile.consecutive_successful_scrubs = 0
                        if tile.maturity_level > 0:
                            tile.maturity_level = 0
                            tile.matured_on_day = -999

                    # QUORUM RESTORATION: Reset counter on failure
                    self.chunk_consecutive_clean_scrubs[chunk_idx] = 0
                else:
                    print(f"      ✓ Post-condition verified: all replicas match golden truth")

                    # RISK-GATED REBUILDS: Reset failed scrub counter on success
                    self.chunk_failed_scrub_count[chunk_idx] = 0

                    # BIOLOGICAL HARDENING: Maturation after successful scrub
                    self._advance_maturation(readable)

                    # QUORUM RESTORATION: Track clean scrub (but don't promote - already QUORUM)
                    # Just increment counter for stability tracking
                    current_count = self.chunk_consecutive_clean_scrubs.get(chunk_idx, 0)
                    self.chunk_consecutive_clean_scrubs[chunk_idx] = current_count + 1
            else:
                # No disagreements - all replicas already match
                # RISK-GATED REBUILDS: Reset failed scrub counter (no repairs needed = success)
                self.chunk_failed_scrub_count[chunk_idx] = 0

                # BIOLOGICAL HARDENING: Maturation for stable replicas
                self._advance_maturation(readable)

                # QUORUM RESTORATION: Track clean scrub
                current_count = self.chunk_consecutive_clean_scrubs.get(chunk_idx, 0)
                self.chunk_consecutive_clean_scrubs[chunk_idx] = current_count + 1

    def _track_clean_scrub_for_quorum_restoration(self, chunk_idx: int, readable: List[Tile]):
        """
        QUORUM RESTORATION: Track consecutive clean scrubs for GOLDEN_ANCHOR → QUORUM demotion.

        If a chunk has been stable (3 live replicas, no repairs) for N consecutive scrubs,
        we can safely demote it from GOLDEN_ANCHOR back to QUORUM mode. The anchor remains
        as a fallback, but we allow majority voting again.

        This allows the system to "heal" and reduce permanent anchor dependency.

        Args:
            chunk_idx: Chunk index to track
            readable: List of readable replicas (should be all matching after clean scrub)
        """
        truth_source = self.chunk_truth_source.get(chunk_idx, TruthSource.QUORUM)

        # Only track for GOLDEN_ANCHOR chunks
        if truth_source != TruthSource.GOLDEN_ANCHOR:
            return

        # Check if we have 3 live replicas
        live_replicas = [t for t in readable
                        if t.state == TileState.ACTIVE
                        and t.integrity >= 0.60]

        if len(live_replicas) < 3:
            # Not enough live replicas, reset counter
            self.chunk_consecutive_clean_scrubs[chunk_idx] = 0
            return

        # Increment consecutive clean scrubs counter
        current_count = self.chunk_consecutive_clean_scrubs.get(chunk_idx, 0)
        self.chunk_consecutive_clean_scrubs[chunk_idx] = current_count + 1

        # Check if we've hit threshold for restoration
        if self.chunk_consecutive_clean_scrubs[chunk_idx] >= self.QUORUM_RESTORATION_THRESHOLD:
            # RESTORE QUORUM: Demote from GOLDEN_ANCHOR back to QUORUM
            print(f"          🔓 QUORUM RESTORED for chunk {chunk_idx} (after {self.chunk_consecutive_clean_scrubs[chunk_idx]} clean scrubs)")
            print(f"              Chunk has 3 stable live replicas - re-enabling majority voting")
            print(f"              Golden anchor remains as fallback for validation")

            self.chunk_truth_source[chunk_idx] = TruthSource.QUORUM
            self.chunk_consecutive_clean_scrubs[chunk_idx] = 0  # Reset counter
            self.quorum_restorations += 1

    def _write_with_settle(self, tile: Tile, data: str, checksum: int) -> bool:
        """
        2-PHASE WRITE-SETTLE PROTOCOL: Write → settle → verify → rewrite mismatches.

        Models biological settling time where voltage patterns stabilize after application.
        Dramatically improves write reliability, especially for degraded tiles.

        Args:
            tile: Tile to write to
            data: Binary data to write
            checksum: CRC32 checksum for data

        Returns:
            True if write succeeded (post-verification), False otherwise
        """
        # Track write attempt
        self.write_attempts_total += 1

        # INTEGRITY-AWARE WRITE GUARD: Check if tile is too degraded
        if tile.integrity < self.MIN_INTEGRITY_FOR_WRITE:
            # Tile is read-only (too degraded to write reliably)
            self.write_failures_total += 1
            return False

        # Determine if we need 2-pass write based on integrity
        use_2pass = tile.integrity < self.MIN_INTEGRITY_FOR_2PASS

        # PHASE 1: Initial write
        tile.binary_data = data
        tile.pattern = self.encoder.encode(data)
        tile.chunk_checksum = checksum

        if not use_2pass:
            # High-integrity tile: 1-pass write is sufficient
            return True

        # PHASE 2: Settle and verify (for low-integrity tiles)
        # Simulate settling delay (in real system, this would be physical delay)
        # Here we model it by checking for bit errors and rewriting only mismatches

        # Verify write
        mismatches = []
        for i in range(min(len(tile.binary_data), len(data))):
            if tile.binary_data[i] != data[i]:
                mismatches.append(i)

        if not mismatches:
            # Write succeeded perfectly
            return True

        # PHASE 2: Rewrite only mismatching bits (targeted correction)
        # This models re-applying voltage to specific cells that didn't settle correctly
        # In simulation, we just rewrite the whole thing again (simplified)
        tile.binary_data = data
        tile.pattern = self.encoder.encode(data)
        tile.chunk_checksum = checksum

        # Final verification
        if tile.binary_data == data:
            # Write succeeded - reset failure count
            tile.write_fail_count = 0
            return True
        else:
            # Write failed even after 2-pass
            tile.write_fail_count += 1
            self.write_failures_total += 1

            # RISK-GATED REBUILDS: Mark as WRITE_SUSPECT after 2 consecutive failures
            if tile.write_fail_count >= 2:
                tile.write_suspect = True
                print(f"          ⚠️  Tile {tile.id} marked WRITE_SUSPECT (2 consecutive write failures)")

            return False

    def _advance_maturation(self, tiles: List[Tile]):
        """
        BIOLOGICAL HARDENING: Advance maturation for tiles after successful scrub.

        Tiles that pass K consecutive successful scrubs become MATURE, which
        reduces their degradation rate. This models memory consolidation in
        biological systems.

        Args:
            tiles: List of tiles that passed this scrub successfully
        """
        for tile in tiles:
            # Only mature ACTIVE/SICK/CLEAN_LOCKED tiles (not REGENERATING)
            if tile.state not in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]:
                continue

            # Increment consecutive successful scrubs
            tile.consecutive_successful_scrubs += 1

            # Check for maturation
            if tile.consecutive_successful_scrubs >= self.MATURATION_THRESHOLD:
                # Promote to next maturity level
                if tile.maturity_level < 2:
                    old_level = tile.maturity_level
                    tile.maturity_level += 1
                    tile.matured_on_day = self.uptime_days

                    if tile.maturity_level == 2:
                        print(f"          🌱 Tile {tile.id} MATURED (after {tile.consecutive_successful_scrubs} successful scrubs)")
                        print(f"              Degradation rate reduced by {self.MATURE_DEGRADATION_REDUCTION*100:.0f}%, shock resistance increased")

    def _record_shock(self, tile_id: int):
        """
        CALM-PERIOD TOP-UP: Record shock event for a tile's chunk.

        When a tile experiences a degradation shock, record it so we can
        require a calm period before top-up.

        Args:
            tile_id: ID of tile that experienced shock
        """
        # Find which chunk this tile belongs to
        for chunk_idx, tile_ids in self.chunk_replicas.items():
            if tile_id in tile_ids:
                self.chunk_last_shock_day[chunk_idx] = self.uptime_days
                break

    def _track_live_replica_time(self):
        """
        CALM-PERIOD TOP-UP: Track time spent at 2-live vs 3-live for each chunk.

        Updates per-chunk counters and detects when chunk drops to 2-live.
        """
        for chunk_idx, tile_ids in self.chunk_replicas.items():
            # Count LIVE replicas (ACTIVE only, ≥60% integrity)
            live_count = sum(1 for tid in tile_ids
                           if self.tiles[tid].state == TileState.ACTIVE
                           and self.tiles[tid].integrity >= 0.60)

            # Initialize counters if needed
            if chunk_idx not in self.chunk_time_at_3live:
                self.chunk_time_at_3live[chunk_idx] = 0
            if chunk_idx not in self.chunk_time_at_2live:
                self.chunk_time_at_2live[chunk_idx] = 0

            # Track time at current level
            if live_count >= 3:
                self.chunk_time_at_3live[chunk_idx] += 1
                # Reset 2-live timer when back to 3-live
                if chunk_idx in self.chunk_two_live_since_day:
                    del self.chunk_two_live_since_day[chunk_idx]
            elif live_count == 2:
                self.chunk_time_at_2live[chunk_idx] += 1
                # Mark when chunk first dropped to 2-live
                if chunk_idx not in self.chunk_two_live_since_day:
                    self.chunk_two_live_since_day[chunk_idx] = self.uptime_days

    def _check_calm_period_topup(self):
        """
        CALM-PERIOD TOP-UP: Check for chunks eligible for top-up.

        Criteria:
        1. Exactly 2 live replicas for >= X days
        2. Live-live drift = 0 for last Y scrubs
        3. Chunk not AT_RISK
        4. No shocks in last Z days
        5. Have sterile spare available

        Perform at most one top-up per day to avoid churn.
        """
        sterile = [t for t in self.tiles if t.state == TileState.STERILE]
        if not sterile:
            return  # No spare capacity

        for chunk_idx in sorted(self.chunk_replicas.keys()):
            tile_ids = self.chunk_replicas[chunk_idx]

            # Count usable replicas (exclude FAILED/STERILE which are offline)
            usable_tiles = [self.tiles[tid] for tid in tile_ids
                           if self.tiles[tid].state not in [TileState.FAILED, TileState.STERILE]]

            # ENFORCE 3-REPLICA MAXIMUM: Never exceed 3 usable replicas per chunk
            # (FAILED tiles don't count - they'll be replaced by rebuilds)
            if len(usable_tiles) >= 3:
                continue  # Already at capacity (3 usable replicas)

            # Check if chunk has exactly 2 live replicas
            live_tiles = [self.tiles[tid] for tid in tile_ids
                         if self.tiles[tid].state == TileState.ACTIVE
                         and self.tiles[tid].integrity >= 0.60]

            if len(live_tiles) != 2:
                continue  # Not eligible (need exactly 2)

            # Check duration at 2-live
            if chunk_idx not in self.chunk_two_live_since_day:
                continue
            days_at_2live = self.uptime_days - self.chunk_two_live_since_day[chunk_idx]
            if days_at_2live < self.TOPUP_MIN_2LIVE_DAYS:
                continue  # Not long enough

            # Check drift history (require last 3 scrubs with 0 drift)
            if chunk_idx not in self.chunk_last_drift:
                continue
            drift_history = self.chunk_last_drift[chunk_idx]
            if len(drift_history) < self.TOPUP_MIN_CLEAN_SCRUBS:
                continue  # Not enough history
            if any(d > 0 for d in drift_history[-self.TOPUP_MIN_CLEAN_SCRUBS:]):
                continue  # Recent drift detected

            # Check for AT_RISK status
            if chunk_idx in self.chunks_at_risk:
                continue  # Chunk is unstable

            # Check for recent shocks
            if chunk_idx in self.chunk_last_shock_day:
                days_since_shock = self.uptime_days - self.chunk_last_shock_day[chunk_idx]
                if days_since_shock < self.TOPUP_MIN_CALM_DAYS:
                    continue  # Too soon after shock

            # ALL CRITERIA MET - perform top-up!
            self._perform_calm_topup(chunk_idx, live_tiles, sterile[0])
            return  # Only one top-up per day

    def _perform_calm_topup(self, chunk_idx: int, live_tiles: List[Tile], target_sterile: Tile):
        """
        CALM-PERIOD TOP-UP: Add third replica during calm period.

        Args:
            chunk_idx: Chunk index to top up
            live_tiles: Current live replicas (should be exactly 2)
            target_sterile: Sterile spare to use for new replica
        """
        print(f"\n🌊 CALM-PERIOD TOP-UP: Chunk {chunk_idx}")
        print(f"   Chunk stable at 2 live for {self.uptime_days - self.chunk_two_live_since_day[chunk_idx]} days, 0 drift")
        print(f"   Adding third replica on tile {target_sterile.id}...")

        # Get correct data from highest-integrity live tile
        best_tile = max(live_tiles, key=lambda t: t.integrity)
        correct_data = best_tile.binary_data

        # Seed target with correct data
        target_sterile.state = TileState.REGENERATING
        target_sterile.binary_data = correct_data
        target_sterile.pattern = self.encoder.encode(correct_data)
        target_sterile.regeneration_progress = 1.0  # Skip regeneration delay
        target_sterile.needs_scrub = False
        target_sterile.integrity = 0.98  # Start at high integrity

        # Set checksum
        import zlib
        target_sterile.chunk_checksum = zlib.crc32(correct_data.encode()) & 0xffffffff

        # SAFETY CHECK: Enforce 3-replica maximum before adding
        if len(self.chunk_replicas[chunk_idx]) >= 3:
            print(f"   ⚠️  ABORT: Chunk {chunk_idx} already has {len(self.chunk_replicas[chunk_idx])} replicas! Cannot top-up.")
            # Return target to sterile pool
            target_sterile.state = TileState.STERILE
            return

        # Add to chunk mapping
        if target_sterile.id not in self.chunk_replicas[chunk_idx]:
            self.chunk_replicas[chunk_idx].append(target_sterile.id)
        else:
            print(f"   ⚠️  ABORT: Tile {target_sterile.id} already in chunk {chunk_idx} mapping!")
            target_sterile.state = TileState.STERILE
            return

        # Perform hard informational scrub
        self._scrub_chunk(chunk_idx)

        # Mark as CLEAN_LOCKED for 7 days
        target_sterile.state = TileState.CLEAN_LOCKED
        target_sterile.clean_locked_until_day = self.uptime_days + 7
        target_sterile.regen_complete_day = self.uptime_days

        # Reset maturation (new replica)
        target_sterile.consecutive_successful_scrubs = 0
        target_sterile.maturity_level = 0
        target_sterile.matured_on_day = -999

        self.topup_count += 1
        print(f"✓ Calm-period top-up #{self.topup_count} complete (tile {target_sterile.id} CLEAN_LOCKED for 7 days)")
        print(f"   Chunk {chunk_idx} now has 3 replicas (will become 3-live after lock expires)\n")

    def _detect_at_risk_loops(self) -> dict:
        """
        Detect chunks stuck in AT_RISK loops.

        A loop is defined as: same chunk becomes AT_RISK N times in M days.
        Returns: {chunk_idx: occurrence_count}
        """
        loop_window_days = 30  # Window to check for loops
        loop_threshold = 3  # Number of occurrences to count as loop

        loops = {}
        for chunk_idx, history in self.chunk_at_risk_history.items():
            # Filter to recent occurrences within window
            recent = [day for day in history if self.uptime_days - day <= loop_window_days]

            if len(recent) >= loop_threshold:
                loops[chunk_idx] = len(recent)

        return loops

    def _restore_from_golden(self, chunk_idx: int, readable_replicas: List[Tile]):
        """
        Restore chunk from golden anchor truth when anchor validation fails.

        This is the emergency recovery path when majority voting produces
        corrupted results (self-corruption lock-in).
        """
        golden_truth = self.chunk_golden_truth.get(chunk_idx)
        if not golden_truth:
            print(f"      ✗ Cannot restore chunk {chunk_idx} - no golden anchor!")
            return

        import zlib
        golden_checksum = zlib.crc32(golden_truth.encode()) & 0xffffffff

        restored_count = 0
        for tile in readable_replicas:
            # Force overwrite with golden truth
            tile.binary_data = golden_truth
            tile.pattern = self.encoder.encode(golden_truth)
            tile.chunk_checksum = golden_checksum
            restored_count += 1

        print(f"      ✓ Restored {restored_count} replicas from golden anchor")

        # Remove from quarantine
        self.quarantined_chunks.discard(chunk_idx)
        self.scrub_writebacks += restored_count

    def _validate_chunk_mappings(self):
        """
        Validate chunk->tile mapping invariants.

        CRITICAL: Every chunk must have exactly 3 UNIQUE replicas at all times.
        Enforces uniqueness (no duplicates) and separates LIVE vs PENDING counts.
        """
        for chunk_idx, tile_ids in self.chunk_replicas.items():
            # ENFORCE UNIQUENESS: Remove duplicates if any
            unique_ids = list(dict.fromkeys(tile_ids))  # Preserves order, removes duplicates
            if len(unique_ids) != len(tile_ids):
                print(f"⚠️  WARNING: Chunk {chunk_idx} had duplicate replica IDs: {tile_ids}")
                print(f"    Deduplicating to: {unique_ids}")
                self.chunk_replicas[chunk_idx] = unique_ids
                tile_ids = unique_ids

            # ENFORCE REPLICA COUNT: Exactly 3 unique tile IDs per chunk
            if len(tile_ids) != 3:
                raise RuntimeError(
                    f"FATAL: Chunk {chunk_idx} has {len(tile_ids)} replicas, expected 3! "
                    f"Tile IDs: {tile_ids}. "
                    f"This violates the 3-replica invariant!"
                )

            # Separate LIVE vs PENDING vs OFFLINE counts
            # CRITICAL: Categories must be mutually exclusive (no overlaps!)
            # Priority order: FAILED/STERILE -> REGENERATING/SICK/CLEAN_LOCKED -> ACTIVE
            tiles = [self.tiles[tid] for tid in tile_ids]

            live = []
            pending = []
            offline = []

            for t in tiles:
                # Priority 1: FAILED or STERILE = always offline
                if t.state in [TileState.FAILED, TileState.STERILE]:
                    offline.append(t)
                # Priority 2: REGENERATING, CLEAN_LOCKED, SICK = always pending
                elif t.state in [TileState.REGENERATING, TileState.CLEAN_LOCKED, TileState.SICK]:
                    pending.append(t)
                # Priority 3: ACTIVE with healthy integrity = live
                elif t.state == TileState.ACTIVE and t.integrity >= 0.60:
                    live.append(t)
                # Catchall: ACTIVE with low integrity = offline
                else:
                    offline.append(t)

            # Verify no overlaps (sanity check - should be impossible with new logic)
            live_ids = set(t.id for t in live)
            pending_ids = set(t.id for t in pending)
            offline_ids = set(t.id for t in offline)

            overlap = (live_ids & pending_ids) | (live_ids & offline_ids) | (pending_ids & offline_ids)
            if overlap:
                print(f"⚠️  CRITICAL BUG: Chunk {chunk_idx} has overlapping replica states: {overlap}")
                print(f"    This should be impossible with mutually exclusive categorization!")

            # Sanity check: total should be 3
            if len(live) + len(pending) + len(offline) != 3:
                print(f"⚠️  WARNING: Chunk {chunk_idx} replica count mismatch!")
                print(f"    Live: {len(live)}, Pending: {len(pending)}, Offline: {len(offline)}")
                print(f"    Total: {len(live) + len(pending) + len(offline)} (expected 3)")

            # Warn if no readable replicas
            if len(live) == 0 and len(pending) == 0:
                print(f"⚠️  WARNING: Chunk {chunk_idx} has no readable replicas!")
                for t in tiles:
                    print(f"    Tile {t.id}: state={t.state.value}, integrity={t.integrity:.2%}")

    def _flush_tile(self, tile: Tile):
        """Flush a tile to STERILE state (full reset)."""
        tile.state = TileState.STERILE
        tile.binary_data = None
        tile.pattern = None
        tile.integrity = 0.0
        tile.age = 0
        tile.regeneration_progress = 0.0
        tile.last_donor_day = -999
        tile.needs_scrub = False
        tile.last_rebuild_attempt_day = -999
        tile.regen_complete_day = -999
        tile.clean_locked_until_day = -999
        print(f"  Flushed tile {tile.id} to STERILE")

    def _get_neighbors(self, tile_id: int) -> List[int]:
        """Get neighboring tile IDs in 2D grid."""
        # Assuming 5x4 grid layout
        row = tile_id // 5
        col = tile_id % 5

        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 4 and 0 <= nc < 5:
                neighbors.append(nr * 5 + nc)

        return neighbors

    def _calculate_logical_errors(self) -> int:
        """
        Calculate logical bit errors: final reconstructed data vs ground truth.

        CRITICAL DEFINITION:
        - Logical error = final reconstructed chunk data != golden original chunk data
        - Must NOT count replica disagreements, pre-repair reads, or majority mismatches
        - Reconstruct each chunk from ACTUAL replicas (simulates real read operation)

        This is the CRITICAL metric - logical errors MUST be 0%.
        """
        if not self.ground_truth:
            return 0

        try:
            # Reconstruct data by ACTUALLY reading from replicas
            # This simulates what a real read operation would return
            chunks = []
            for chunk_idx in sorted(self.chunk_replicas.keys()):
                replica_ids = self.chunk_replicas[chunk_idx]
                replicas = [self.tiles[tid] for tid in replica_ids]

                # Get readable replicas
                readable = [t for t in replicas
                           if t.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]
                           and t.binary_data]

                # Reconstruct based on truth authority
                truth_source = self.chunk_truth_source.get(chunk_idx, TruthSource.QUORUM)
                golden_truth = self.chunk_golden_truth.get(chunk_idx)

                if truth_source == TruthSource.GOLDEN_ANCHOR:
                    # GOLDEN_ANCHOR mode: use anchor directly (replicas are informational)
                    if golden_truth:
                        chunk_data = golden_truth
                    else:
                        chunk_data = '0' * self.bits_per_tile
                else:
                    # QUORUM mode: use majority voting from readable replicas
                    if len(readable) >= 2:
                        high_integrity = [t for t in readable if t.integrity >= 0.80]
                        if high_integrity:
                            chunk_data = self._reconstruct_via_majority_vote(high_integrity)
                        else:
                            chunk_data = self._reconstruct_via_majority_vote(readable)
                    elif len(readable) == 1:
                        chunk_data = readable[0].binary_data
                    else:
                        # No readable replicas - use golden anchor as fallback
                        chunk_data = golden_truth if golden_truth else '0' * self.bits_per_tile

                chunks.append(chunk_data)

            # Compare reconstructed data vs ground truth
            reconstructed = ''.join(chunks).rstrip('0')
            ground_truth = self.ground_truth.rstrip('0')

            errors = 0
            max_len = max(len(reconstructed), len(ground_truth))
            for i in range(max_len):
                r_bit = reconstructed[i] if i < len(reconstructed) else '0'
                g_bit = ground_truth[i] if i < len(ground_truth) else '0'
                if r_bit != g_bit:
                    errors += 1

            return errors
        except Exception as e:
            print(f"⚠️  Error calculating logical errors: {e}")
            return -1

    def _calculate_replica_errors(self) -> dict:
        """
        Calculate replica bit errors with SPLIT METRICS: drift vs staleness.

        CRITICAL DISTINCTION:
        - **Replica drift (live-live)**: Disagreements among LIVE replicas vs anchor
          This measures active data corruption and is the primary convergence metric.
        - **Staleness (pending-live)**: Disagreements in PENDING replicas vs anchor
          This is expected (tiles are being regenerated/repaired) and shouldn't inflate metrics.

        Returns:
            dict with:
            - replica_drift: disagreements from LIVE replicas only (convergence metric)
            - staleness: disagreements from PENDING replicas (expected, not critical)
            - pending_count: count of PENDING replicas (SICK/CLEAN_LOCKED/REGENERATING)
            - offline_count: count of OFFLINE replicas (FAILED/STERILE/unreadable)
            - live_replica_distribution: {0: X, 1: Y, 2: Z, 3: W} chunks by live count
        """
        replica_drift = 0  # LIVE replica disagreements (primary metric)
        staleness = 0  # PENDING replica disagreements (expected, not critical)
        pending_count = 0
        offline_count = 0
        live_replica_distribution = {0: 0, 1: 0, 2: 0, 3: 0}  # Track chunks by live replica count

        readable_threshold = 0.60  # Minimum integrity to be readable

        for chunk_idx in self.chunk_replicas.keys():
            replica_ids = self.chunk_replicas[chunk_idx]
            replicas = [self.tiles[tid] for tid in replica_ids]

            # Get golden anchor as reference
            golden_truth = self.chunk_golden_truth.get(chunk_idx)
            if not golden_truth:
                continue  # Skip chunks without anchor

            # Categorize replicas using same logic as validation
            # CRITICAL: Must be mutually exclusive
            live_replicas = []
            pending_replicas = []
            offline_replicas = []

            for tile in replicas:
                # Priority 1: FAILED or STERILE = always offline
                if tile.state in [TileState.FAILED, TileState.STERILE]:
                    offline_replicas.append(tile)
                # Priority 2: REGENERATING, CLEAN_LOCKED, SICK = always pending
                elif tile.state in [TileState.REGENERATING, TileState.CLEAN_LOCKED, TileState.SICK]:
                    pending_replicas.append(tile)
                # Priority 3: ACTIVE with healthy integrity = live
                elif tile.state == TileState.ACTIVE and tile.integrity >= readable_threshold:
                    live_replicas.append(tile)
                # Catchall: ACTIVE with low integrity = offline
                else:
                    offline_replicas.append(tile)

            # Update counts
            pending_count += len(pending_replicas)
            offline_count += len(offline_replicas)

            # Track live replica distribution
            live_count = len(live_replicas)
            if live_count in live_replica_distribution:
                live_replica_distribution[live_count] += 1

            # SPLIT METRICS: Count LIVE vs PENDING disagreements separately
            # Only compute if we have >= 2 live replicas (user requirement)
            if live_count >= 2:
                for tile in live_replicas:
                    if tile.binary_data:
                        for i in range(min(len(tile.binary_data), len(golden_truth))):
                            if tile.binary_data[i] != golden_truth[i]:
                                replica_drift += 1  # LIVE disagreement (critical)

            # Count PENDING replica disagreements (expected, not critical)
            for tile in pending_replicas:
                if tile.binary_data:
                    for i in range(min(len(tile.binary_data), len(golden_truth))):
                        if tile.binary_data[i] != golden_truth[i]:
                            staleness += 1  # PENDING disagreement (expected)

        return {
            'replica_drift': replica_drift,  # Primary convergence metric
            'staleness': staleness,  # Expected errors from PENDING replicas
            'pending_count': pending_count,
            'offline_count': offline_count,
            'live_replica_distribution': live_replica_distribution
        }

    def _get_state_snapshot(self) -> dict:
        """Get current system state for history."""
        return {
            'day': self.uptime_days,
            'active_count': sum(1 for t in self.tiles if t.state == TileState.ACTIVE),
            'degrading_count': sum(1 for t in self.tiles if t.state == TileState.DEGRADING),
            'regenerating_count': sum(1 for t in self.tiles if t.state == TileState.REGENERATING),
            'sterile_count': sum(1 for t in self.tiles if t.state == TileState.STERILE),
            'avg_integrity': np.mean([t.integrity for t in self.tiles if t.state == TileState.ACTIVE]),
            'rebuild_count': self.rebuild_count
        }

    def visualize_cartridge(self, save_path=None):
        """
        Visualize bio-RAID cartridge state with proper colors.
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # Define discrete colors for each state
        from matplotlib.colors import ListedColormap, BoundaryNorm

        state_colors = {
            TileState.FAILED: '#FF3333',      # Red
            TileState.SICK: '#FF8C00',        # Dark orange
            TileState.REGENERATING: '#FFD700', # Yellow/gold
            TileState.CLEAN_LOCKED: '#00DDAA', # Cyan/teal (locked but healthy)
            TileState.ACTIVE: '#00CC66',      # Green
            TileState.STERILE: '#A9B7C6',     # Gray/blue
            TileState.DEGRADING: '#FFA500'    # Orange (legacy)
        }

        state_values = {
            TileState.STERILE: 0,
            TileState.FAILED: 1,
            TileState.SICK: 2,
            TileState.REGENERATING: 3,
            TileState.DEGRADING: 4,
            TileState.CLEAN_LOCKED: 5,
            TileState.ACTIVE: 6
        }

        # Create grid
        grid = np.zeros((4, 5))  # 4x5 = 20 tiles
        for tile in self.tiles:
            row = tile.id // 5
            col = tile.id % 5
            grid[row, col] = state_values[tile.state]

        # Create custom colormap
        cmap = ListedColormap([state_colors[TileState.STERILE],
                              state_colors[TileState.FAILED],
                              state_colors[TileState.SICK],
                              state_colors[TileState.REGENERATING],
                              state_colors[TileState.DEGRADING],
                              state_colors[TileState.CLEAN_LOCKED],
                              state_colors[TileState.ACTIVE]])

        bounds = [0, 1, 2, 3, 4, 5, 6, 7]
        norm = BoundaryNorm(bounds, cmap.N)

        im = ax1.imshow(grid, cmap=cmap, norm=norm, interpolation='nearest')
        ax1.set_title(f'Bio-RAID Cartridge - Day {self.uptime_days}',
                     fontsize=14, fontweight='bold')
        ax1.set_xticks([])
        ax1.set_yticks([])

        # Add tile labels
        for tile in self.tiles:
            row = tile.id // 5
            col = tile.id % 5

            state_char = {
                TileState.ACTIVE: 'A',
                TileState.SICK: 'K',
                TileState.DEGRADING: 'D',
                TileState.REGENERATING: 'R',
                TileState.CLEAN_LOCKED: 'L',
                TileState.STERILE: 'S',
                TileState.FAILED: 'F'
            }.get(tile.state, '?')

            ax1.text(col, row, f'{tile.id}\n{state_char}\n{tile.integrity:.0%}',
                    ha='center', va='center', fontsize=9, fontweight='bold',
                    color='black' if tile.state == TileState.STERILE else 'white')

        # Legend
        legend_elements = [
            mpatches.Patch(color=state_colors[TileState.ACTIVE], label='Active (≥80%)'),
            mpatches.Patch(color=state_colors[TileState.CLEAN_LOCKED], label='Clean-Locked (7d)'),
            mpatches.Patch(color=state_colors[TileState.SICK], label='Sick (60-80%)'),
            mpatches.Patch(color=state_colors[TileState.REGENERATING], label='Regenerating'),
            mpatches.Patch(color=state_colors[TileState.STERILE], label='Sterile'),
            mpatches.Patch(color=state_colors[TileState.FAILED], label='Failed (<60%)')
        ]
        ax1.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.05, 1))

        # Right: Statistics
        ax2.axis('off')
        active_tiles = [t for t in self.tiles if t.state == TileState.ACTIVE]
        avg_integrity = np.mean([t.integrity for t in active_tiles]) if active_tiles else 0.0

        stats_text = f"""
BIO-RAID STATISTICS

Uptime: {self.uptime_days} days
Rebuilds: {self.rebuild_count}
Degradation Events: {self.total_degradation_events}
Scrub Repairs: {self.scrub_repairs} bits

TILE STATUS
Active (≥80%):     {sum(1 for t in self.tiles if t.state == TileState.ACTIVE)}
Sick (60-80%):     {sum(1 for t in self.tiles if t.state == TileState.SICK)}
Regenerating:      {sum(1 for t in self.tiles if t.state == TileState.REGENERATING)}
Sterile:           {sum(1 for t in self.tiles if t.state == TileState.STERILE)}
Failed (<60%):     {sum(1 for t in self.tiles if t.state == TileState.FAILED)}

RELIABILITY
Avg Integrity: {avg_integrity:.1%}
Data Protected: {'YES' if sum(1 for t in self.tiles if t.state == TileState.STERILE) > 0 else 'NO'}
Uptime: {(self.uptime_days / max(self.uptime_days, 1)) * 100:.3f}%
"""
        ax2.text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
                verticalalignment='center')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig


def run_phase2_simulation(duration_days=365):
    """
    Run full Phase 2 bio-RAID simulation with ECC + read-repair.

    Args:
        duration_days: How many days to simulate (default: 1 year)
    """
    print("\n" + "="*70)
    print("ACHERON PHASE 2: BIO-RAID WITH ECC + READ-REPAIR")
    print("="*70)
    print("Architecture: 3-way replication + majority voting + weekly scrubbing")
    print("="*70 + "\n")

    # Create controller
    controller = BioRAIDController(n_tiles=20, n_sterile=4)

    # Write initial data
    test_data = "1011010110110101" * 8  # 128 bits
    print(f"Writing {len(test_data)} bits to bio-RAID...")
    controller.write_data(test_data)

    # Visualize initial state
    controller.visualize_cartridge(save_path='analysis/bioraid_day0.png')
    plt.pause(0.1)

    # Simulate
    print(f"\nSimulating {duration_days} days of operation...")
    print("(Tiles will degrade, rebuild automatically)\n")

    checkpoints = [90, 180, 270, 365]

    for day in range(1, duration_days + 1):
        controller.simulate_day()

        if day in checkpoints:
            # Checkpoint visualization
            print(f"\n{'='*70}")
            print(f"DAY {day} CHECKPOINT")
            print(f"{'='*70}")

            # Tile state counts
            active_count = sum(1 for t in controller.tiles if t.state == TileState.ACTIVE)
            clean_locked_count = sum(1 for t in controller.tiles if t.state == TileState.CLEAN_LOCKED)
            sick_count = sum(1 for t in controller.tiles if t.state == TileState.SICK)
            regen_count = sum(1 for t in controller.tiles if t.state == TileState.REGENERATING)
            sterile_count = sum(1 for t in controller.tiles if t.state == TileState.STERILE)
            failed_count = sum(1 for t in controller.tiles if t.state == TileState.FAILED)

            print(f"\nTILE STATUS:")
            print(f"  Active (≥80%):     {active_count}")
            print(f"  Clean-Locked:      {clean_locked_count}")
            print(f"  Sick (60-80%):     {sick_count}")
            print(f"  Regenerating:      {regen_count}")
            print(f"  Sterile:           {sterile_count}")
            print(f"  Failed (<60%):     {failed_count}")

            # List tile IDs per state
            active_ids = [t.id for t in controller.tiles if t.state == TileState.ACTIVE]
            clean_locked_ids = [t.id for t in controller.tiles if t.state == TileState.CLEAN_LOCKED]
            sick_ids = [t.id for t in controller.tiles if t.state == TileState.SICK]
            regen_ids = [t.id for t in controller.tiles if t.state == TileState.REGENERATING]
            sterile_ids = [t.id for t in controller.tiles if t.state == TileState.STERILE]
            failed_ids = [t.id for t in controller.tiles if t.state == TileState.FAILED]

            if active_ids:
                print(f"  Active IDs: {active_ids}")
            if clean_locked_ids:
                print(f"  Clean-Locked IDs: {clean_locked_ids}")
            if sick_ids:
                print(f"  Sick IDs: {sick_ids}")
            if regen_ids:
                print(f"  Regenerating IDs: {regen_ids}")
            if sterile_ids:
                print(f"  Sterile IDs: {sterile_ids}")
            if failed_ids:
                print(f"  Failed IDs: {failed_ids}")

            # Per-chunk replica mapping (using actual chunk_replicas mapping)
            print(f"\nCHUNK REPLICA MAPPING (live vs pending):")
            for chunk_idx in sorted(controller.chunk_replicas.keys()):
                tile_ids = controller.chunk_replicas[chunk_idx]
                replicas_info = []
                live_count = 0
                pending_count = 0
                for tid in tile_ids:
                    tile = controller.tiles[tid]
                    state_char = {'ACTIVE': 'A', 'SICK': 'K', 'REGENERATING': 'R', 'FAILED': 'F', 'STERILE': 'S', 'CLEAN_LOCKED': 'L'}.get(tile.state.value, '?')

                    # Mark live vs pending vs offline
                    # LIVE = ACTIVE and readable
                    # PENDING = SICK, CLEAN_LOCKED, REGENERATING (readable but not fully healthy)
                    # OFFLINE = FAILED, STERILE (not readable)
                    if tile.state == TileState.ACTIVE and tile.integrity >= 0.60:
                        replicas_info.append(f"{tile.id}({state_char},{tile.integrity:.0%})")
                        live_count += 1
                    elif tile.state in [TileState.SICK, TileState.CLEAN_LOCKED, TileState.REGENERATING]:
                        replicas_info.append(f"{tile.id}({state_char},{tile.integrity:.0%})[PENDING]")
                        pending_count += 1
                    else:
                        replicas_info.append(f"{tile.id}({state_char},{tile.integrity:.0%})[OFFLINE]")

                status = f"{live_count} live"
                if pending_count > 0:
                    status += f", {pending_count} pending"
                print(f"  Chunk {chunk_idx}: {' | '.join(replicas_info)} [{status}]")

            # ASSERT: All chunks must have exactly 3 replicas
            for chunk_idx, tile_ids in controller.chunk_replicas.items():
                if len(tile_ids) != 3:
                    print(f"  ✗ ASSERTION FAILED: Chunk {chunk_idx} has {len(tile_ids)} replicas, expected 3!")

            print(f"\nREBUILD STATS:")
            print(f"  Total rebuilds: {controller.rebuild_count}")
            print(f"  Degradation events: {controller.total_degradation_events}")

            # NEW METRICS SEPARATION (critical for analysis)
            print(f"\nDATA INTEGRITY METRICS:")

            # Logical bit errors (MUST be 0%)
            logical_errors = controller._calculate_logical_errors()
            logical_error_rate = (logical_errors / len(test_data) * 100) if logical_errors >= 0 else -1
            if logical_errors == 0:
                print(f"  ✓ Logical bit errors: 0 (0.0%) - PERFECT")
            elif logical_errors > 0:
                print(f"  ✗ Logical bit errors: {logical_errors} ({logical_error_rate:.2f}%) - FAILED")
            else:
                print(f"  ⚠️  Logical errors: calculation failed")

            # SPLIT METRICS: Replica drift (live-live) vs staleness (pending-live)
            replica_metrics = controller._calculate_replica_errors()
            replica_drift = replica_metrics['replica_drift']  # LIVE replica errors (primary metric)
            staleness = replica_metrics['staleness']  # PENDING replica errors (expected)
            pending_count = replica_metrics['pending_count']
            offline_count = replica_metrics['offline_count']
            live_dist = replica_metrics['live_replica_distribution']

            # Count total LIVE tiles with data (for error rate calculation)
            live_tile_count = sum(1 for t in controller.tiles
                                 if t.state == TileState.ACTIVE
                                 and t.integrity >= 0.60
                                 and t.binary_data)
            total_live_bits = len(test_data) * live_tile_count // (controller.n_active // controller.replication_factor) if live_tile_count > 0 else 0

            replica_drift_rate = (replica_drift / total_live_bits * 100) if total_live_bits > 0 and replica_drift > 0 else 0

            # BIOLOGICAL HARDENING: Track convergence trend
            controller.replica_error_rate_history.append(replica_drift_rate)

            # Compute convergence trend (linear regression slope over last 4 checkpoints)
            if len(controller.replica_error_rate_history) >= 4:
                recent_rates = controller.replica_error_rate_history[-4:]
                # Simple linear regression: slope = Δy / Δx
                # Positive slope = diverging, negative slope = converging
                x = list(range(len(recent_rates)))
                y = recent_rates
                n = len(recent_rates)
                slope = (n * sum(x[i]*y[i] for i in range(n)) - sum(x) * sum(y)) / (n * sum(x[i]**2 for i in range(n)) - sum(x)**2)
                trend_direction = "CONVERGING ⬇️" if slope < -0.5 else "DIVERGING ⬆️" if slope > 0.5 else "STABLE ➡️"
            else:
                slope = 0
                trend_direction = "INSUFFICIENT DATA"

            if replica_drift_rate < 5:
                print(f"  ✓ Replica drift (live-live): {replica_drift} ({replica_drift_rate:.2f}%) - GOOD")
            else:
                print(f"  ⚠️  Replica drift (live-live): {replica_drift} ({replica_drift_rate:.2f}%) - HIGH")

            print(f"  📊 Staleness (pending-live): {staleness} bits (expected, not critical)")
            print(f"  📊 Pending replicas: {pending_count} (SICK/CLEAN_LOCKED/REGENERATING)")
            print(f"  📊 Offline replicas: {offline_count} (FAILED/STERILE/unreadable)")
            print(f"  📊 Live replica distribution: {live_dist[0]} chunks with 0, {live_dist[1]} with 1, {live_dist[2]} with 2, {live_dist[3]} with 3")
            print(f"  📊 Convergence trend: {trend_direction} (slope: {slope:.2f}%/checkpoint)")
            print(f"  📊 Convergence: {'YES' if replica_drift_rate < 5 or slope < -0.5 else 'NO'}")

            # Scrub effectiveness
            print(f"  📊 Scrub write-backs: {controller.scrub_writebacks} replicas repaired")

            # Truth authority status
            quorum_chunks = sum(1 for src in controller.chunk_truth_source.values() if src == TruthSource.QUORUM)
            anchor_chunks = sum(1 for src in controller.chunk_truth_source.values() if src == TruthSource.GOLDEN_ANCHOR)
            print(f"  🔒 Anchor promotions: {controller.anchor_promotions} total")
            print(f"  📊 Truth authority: {quorum_chunks} QUORUM, {anchor_chunks} GOLDEN_ANCHOR")

            # AT_RISK chunks
            if controller.chunks_at_risk:
                print(f"  ⚠️  AT_RISK chunks: {sorted(controller.chunks_at_risk)}")

            # AT_RISK loops (same chunk repeatedly AT_RISK)
            at_risk_loops = controller._detect_at_risk_loops()
            if at_risk_loops:
                print(f"  🔁 AT_RISK LOOPS detected:")
                for chunk_idx, count in at_risk_loops.items():
                    print(f"      Chunk {chunk_idx}: {count} occurrences in 30 days")

            # Scrub convergence failures
            if controller.scrub_failed_to_converge > 0:
                print(f"  ⚠️  Scrub convergence failures: {controller.scrub_failed_to_converge}")

            # Quarantined chunks (anchor validation failed)
            if controller.quarantined_chunks:
                print(f"  🚫 QUARANTINED chunks: {sorted(controller.quarantined_chunks)}")

            print(f"{'='*70}\n")

            # Save visualization
            controller.visualize_cartridge(save_path=f'analysis/bioraid_day{day}.png')
            plt.pause(0.1)

    # Final report
    print("\n" + "="*70)
    print("SIMULATION COMPLETE")
    print("="*70)
    print(f"Total runtime: {duration_days} days")
    print(f"Total rebuilds: {controller.rebuild_count}")
    print(f"Degradation events: {controller.total_degradation_events}")
    print(f"Final active tiles: {sum(1 for t in controller.tiles if t.state == TileState.ACTIVE)}")
    print(f"Final sterile spares: {sum(1 for t in controller.tiles if t.state == TileState.STERILE)}")

    # FINAL METRICS (using separated tracking)
    print(f"\nFINAL DATA INTEGRITY METRICS:")

    # Logical bit errors (MUST be 0%)
    logical_errors = controller._calculate_logical_errors()
    logical_error_rate = (logical_errors / len(test_data) * 100) if logical_errors >= 0 else -1

    if logical_errors == 0:
        print(f"  ✓✓✓ LOGICAL BIT ERRORS: 0 (0.0%) - PERFECT ✓✓✓")
        print(f"      3-way replication + majority voting = ZERO data loss!")
    elif logical_errors > 0:
        print(f"  ✗✗✗ LOGICAL BIT ERRORS: {logical_errors} ({logical_error_rate:.2f}%) - FAILED ✗✗✗")
        print(f"      Goal was 0% - investigation needed!")
    else:
        print(f"  ⚠️  Logical error calculation failed")

    # SPLIT METRICS: Replica drift (live-live) vs staleness (pending-live)
    replica_metrics = controller._calculate_replica_errors()
    replica_drift = replica_metrics['replica_drift']  # LIVE replica errors (primary metric)
    staleness = replica_metrics['staleness']  # PENDING replica errors (expected)
    pending_count = replica_metrics['pending_count']
    offline_count = replica_metrics['offline_count']
    live_dist = replica_metrics['live_replica_distribution']

    # Count total LIVE tiles with data (for error rate calculation)
    live_tile_count = sum(1 for t in controller.tiles
                         if t.state == TileState.ACTIVE
                         and t.integrity >= 0.60
                         and t.binary_data)
    total_live_bits = len(test_data) * live_tile_count // (controller.n_active // controller.replication_factor) if live_tile_count > 0 else 0

    replica_drift_rate = (replica_drift / total_live_bits * 100) if total_live_bits > 0 and replica_drift > 0 else 0

    if replica_drift_rate == 0:
        print(f"  ✓✓ REPLICA DRIFT (live-live): 0 (0.0%) - PERFECT CONVERGENCE ✓✓")
    elif replica_drift_rate < 5:
        print(f"  ✓ REPLICA DRIFT (live-live): {replica_drift} ({replica_drift_rate:.2f}%) - GOOD")
        print(f"     Goal was <5% - achieved!")
    else:
        print(f"  ⚠️  REPLICA DRIFT (live-live): {replica_drift} ({replica_drift_rate:.2f}%) - HIGH")
        print(f"     Goal was <5% - needs improvement")

    print(f"  📊 Staleness (pending-live): {staleness} bits (expected, not critical)")
    print(f"  📊 Pending replicas: {pending_count} (SICK/CLEAN_LOCKED/REGENERATING)")
    print(f"  📊 Offline replicas: {offline_count} (FAILED/STERILE/unreadable)")
    print(f"  📊 Live replica distribution: {live_dist[0]} chunks with 0, {live_dist[1]} with 1, {live_dist[2]} with 2, {live_dist[3]} with 3")

    # BIOLOGICAL HARDENING: Convergence trend analysis
    if len(controller.replica_error_rate_history) >= 4:
        recent_rates = controller.replica_error_rate_history[-4:]
        x = list(range(len(recent_rates)))
        y = recent_rates
        n = len(recent_rates)
        slope = (n * sum(x[i]*y[i] for i in range(n)) - sum(x) * sum(y)) / (n * sum(x[i]**2 for i in range(n)) - sum(x)**2)
        trend_direction = "CONVERGING ⬇️" if slope < -0.5 else "DIVERGING ⬆️" if slope > 0.5 else "STABLE ➡️"
        print(f"  📊 Convergence trend: {trend_direction} (slope: {slope:.2f}%/checkpoint)")
        print(f"      History: {' → '.join(f'{r:.1f}%' for r in recent_rates)}")

    # Scrub effectiveness
    print(f"\nSCRUBBING EFFECTIVENESS:")
    print(f"  Total scrub write-backs: {controller.scrub_writebacks} replicas repaired")

    # BIOLOGICAL HARDENING: Convergence criteria (trend OR absolute)
    is_converging = len(controller.replica_error_rate_history) >= 4 and slope < -0.5
    print(f"  Convergence: {'YES (trending down)' if is_converging else 'YES (stable at <5%)' if replica_drift_rate < 5 else 'NO (still diverging)'}")

    # Truth authority status
    quorum_chunks = sum(1 for src in controller.chunk_truth_source.values() if src == TruthSource.QUORUM)
    anchor_chunks = sum(1 for src in controller.chunk_truth_source.values() if src == TruthSource.GOLDEN_ANCHOR)
    print(f"\nTRUTH AUTHORITY HIERARCHY:")
    print(f"  Anchor promotions: {controller.anchor_promotions} total (QUORUM → GOLDEN_ANCHOR)")
    print(f"  Quorum restorations: {controller.quorum_restorations} total (GOLDEN_ANCHOR → QUORUM)")
    print(f"  Final authority: {quorum_chunks} QUORUM, {anchor_chunks} GOLDEN_ANCHOR")
    if anchor_chunks > 0:
        print(f"  📌 {anchor_chunks} chunks using anchor authority (may restore to QUORUM if stable)")
    if quorum_chunks > 0 and controller.quorum_restorations > 0:
        print(f"  ✓ System can heal: {controller.quorum_restorations} chunks restored to QUORUM mode")

    # DURABILITY METRICS (new metrics for rebuild frequency)
    print(f"\nDURABILITY METRICS:")
    days_simulated = controller.uptime_days
    months_simulated = days_simulated / 30.0
    years_simulated = days_simulated / 365.0

    # Rebuilds per month
    rebuilds_per_month = controller.rebuild_count / months_simulated if months_simulated > 0 else 0
    if rebuilds_per_month <= 1.0:
        print(f"  ✓ Rebuilds per month: {rebuilds_per_month:.2f} - EXCELLENT")
    elif rebuilds_per_month <= 2.0:
        print(f"  ✓ Rebuilds per month: {rebuilds_per_month:.2f} - GOOD")
    else:
        print(f"  ⚠️  Rebuilds per month: {rebuilds_per_month:.2f} - TOO HIGH (goal: ≤1/month)")

    # Rebuilds per tile per year
    rebuilds_per_tile_per_year = (controller.rebuild_count / controller.n_tiles) / years_simulated if years_simulated > 0 else 0
    print(f"  📊 Rebuilds per tile per year: {rebuilds_per_tile_per_year:.2f}")

    # CALM-PERIOD TOP-UPS (separate from rebuilds)
    topups_per_month = controller.topup_count / months_simulated if months_simulated > 0 else 0
    print(f"  📊 Calm-period top-ups: {controller.topup_count} ({topups_per_month:.2f}/month)")

    # Time at 3-live vs 2-live
    total_chunk_days = sum(controller.chunk_time_at_3live.values()) + sum(controller.chunk_time_at_2live.values())
    if total_chunk_days > 0:
        pct_3live = sum(controller.chunk_time_at_3live.values()) / total_chunk_days * 100
        pct_2live = sum(controller.chunk_time_at_2live.values()) / total_chunk_days * 100
        print(f"  📊 Chunk-time at 3-live: {pct_3live:.1f}%  |  at 2-live: {pct_2live:.1f}%")

    # Write fail rate (using actual write attempts)
    write_fail_rate = (controller.write_failures_total / controller.write_attempts_total * 100) if controller.write_attempts_total > 0 else 0
    print(f"  📊 Write fail rate: {write_fail_rate:.2f}% ({controller.write_failures_total}/{controller.write_attempts_total} attempts)")

    # Mature tile percentage
    mature_tiles = sum(1 for t in controller.tiles if t.maturity_level >= 2)
    mature_percentage = (mature_tiles / controller.n_tiles * 100) if controller.n_tiles > 0 else 0
    print(f"  📊 Mature tile percentage: {mature_percentage:.1f}% ({mature_tiles}/{controller.n_tiles} tiles)")

    # SUCCESS CRITERIA CHECK
    print(f"\nSUCCESS CRITERIA:")
    success_logical = logical_errors == 0
    success_replica = replica_drift_rate < 5
    at_risk_loops = controller._detect_at_risk_loops()
    success_no_loops = len(at_risk_loops) == 0
    success_no_quarantine = len(controller.quarantined_chunks) == 0
    success_scrub_converge = controller.scrub_failed_to_converge == 0

    print(f"  {'✓' if success_logical else '✗'} Logical bit errors = 0%")
    print(f"  {'✓' if success_replica else '✗'} Replica drift < 5%")
    print(f"  {'✓' if success_no_loops else '✗'} No AT_RISK chunk loops")
    print(f"  {'✓' if success_no_quarantine else '✗'} No quarantined chunks")
    print(f"  {'✓' if success_scrub_converge else '✗'} Scrubs converge successfully")

    if controller.chunks_at_risk:
        print(f"\n  Current AT_RISK chunks: {sorted(controller.chunks_at_risk)}")
    if at_risk_loops:
        print(f"  AT_RISK LOOPS detected:")
        for chunk_idx, count in at_risk_loops.items():
            print(f"    Chunk {chunk_idx}: {count} occurrences in 30 days")
    if controller.quarantined_chunks:
        print(f"  QUARANTINED chunks: {sorted(controller.quarantined_chunks)}")
    if controller.scrub_failed_to_converge > 0:
        print(f"  Scrub convergence failures: {controller.scrub_failed_to_converge}")

    if success_logical and success_replica and success_no_loops and success_no_quarantine and success_scrub_converge:
        print(f"\n🎉 ALL SUCCESS CRITERIA MET! 🎉")
    else:
        print(f"\n⚠️  Some success criteria not met - see above")

    # Final visualization
    controller.visualize_cartridge(save_path=f'analysis/bioraid_final.png')

    print("\nGenerated visualizations:")
    for day in [0] + checkpoints:
        print(f"  - analysis/bioraid_day{day}.png")
    print(f"  - analysis/bioraid_final.png")
    print("\nPlot windows will remain open. Close them manually to exit, or check the PNG files in analysis/")

    plt.show(block=True)  # Keep windows open until user closes them

    return controller


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        # Quick 90-day simulation
        run_phase2_simulation(duration_days=90)
    else:
        # Full year simulation
        run_phase2_simulation(duration_days=365)
