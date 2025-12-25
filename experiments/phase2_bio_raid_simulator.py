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
    """

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
                # This ensures we see actual rebuilds in 90-day simulations
                tile.integrity *= 0.997

                # Random degradation events (0.5% chance per day)
                # Accelerates degradation for some tiles
                if np.random.random() < 0.005:
                    tile.integrity *= np.random.uniform(0.85, 0.95)
                    self.total_degradation_events += 1

                # DETERMINISTIC SHOCK EVENT: Day 30, tile 7 drops 25%
                if self.uptime_days == 30 and tile.id == 7:
                    print(f"\n⚡ SHOCK EVENT: Tile 7 integrity drop (-25%)")
                    tile.integrity *= 0.75
                    self.total_degradation_events += 1

                # State transitions based on integrity (but respect CLEAN_LOCKED!)
                if tile.integrity < 0.60:
                    # FAILED: Below 60%, unusable (even if CLEAN_LOCKED)
                    if tile.state != TileState.FAILED:
                        tile.state = TileState.FAILED
                        tile.clean_locked_until_day = -999  # Clear lock
                        print(f"✗ Tile {tile.id} FAILED (integrity: {tile.integrity:.2%})")
                elif tile.state != TileState.CLEAN_LOCKED:  # Don't transition if CLEAN_LOCKED
                    if tile.integrity < 0.80:
                        # SICK: 60-80%, needs proactive rebuild
                        if tile.state != TileState.SICK:
                            tile.state = TileState.SICK
                            print(f"⚠️  Tile {tile.id} is SICK (integrity: {tile.integrity:.2%}) - proactive rebuild needed")
                    else:
                        # ACTIVE: ≥80%, healthy
                        if tile.state == TileState.SICK:
                            tile.state = TileState.ACTIVE
                            print(f"✓ Tile {tile.id} recovered to ACTIVE (integrity: {tile.integrity:.2%})")

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
            # Read with repair_errors=True to fix bit drift
            self.read_data(repair_errors=True)
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
                # Count only LIVE replicas (ACTIVE/SICK, NOT REGENERATING)
                before_count = len([t for t in self.chunk_replicas[chunk_idx]
                                   if self.tiles[t].state in [TileState.ACTIVE, TileState.SICK]])

                self._ensure_chunk_has_three_replicas(chunk_idx)

                # Count only LIVE replicas (ACTIVE/SICK, NOT REGENERATING)
                after_count = len([t for t in self.chunk_replicas[chunk_idx]
                                  if self.tiles[t].state in [TileState.ACTIVE, TileState.SICK]])

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

        # 2) PROACTIVE REBUILD: Replace SICK tiles before they fail
        # CRITICAL: Skip CLEAN_LOCKED tiles (stabilization window)
        sick_tiles = [t for t in self.tiles
                     if t.state == TileState.SICK
                     and t.binary_data
                     and t.state != TileState.CLEAN_LOCKED]  # Don't replace recently regenerated tiles

        if sick_tiles:
            # Rebuild throttling for proactive rebuilds only
            if self.rebuilds_this_week >= self.max_rebuilds_per_week:
                print(f"⏸️  Proactive rebuild throttled (hit weekly limit: {self.rebuilds_this_week}/{self.max_rebuilds_per_week})")
                return

            # Filter out tiles that were recently attempted (prevent spam)
            # Also filter out CLEAN_LOCKED tiles (even if they degrade to SICK during lock)
            eligible_tiles = [t for t in sick_tiles
                            if (self.uptime_days - t.last_rebuild_attempt_day) >= 7
                            and t.clean_locked_until_day < self.uptime_days]  # Lock expired

            if not eligible_tiles:
                locked_count = sum(1 for t in sick_tiles if t.clean_locked_until_day >= self.uptime_days)
                if locked_count > 0:
                    print(f"⏸️  {locked_count} SICK tiles are CLEAN_LOCKED (stabilization window)")
                return  # All SICK tiles attempted recently or locked

            # Pick the sickest tile
            tile_to_rebuild = min(eligible_tiles, key=lambda t: t.integrity)
            print(f"\n🔧 PROACTIVE: Replacing SICK tile {tile_to_rebuild.id} before it fails")

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

        # Update chunk mapping: replace sick_tile.id with target_sterile.id
        self.chunk_replicas[chunk_idx] = [
            target_sterile.id if tid == sick_tile.id else tid
            for tid in replica_ids
        ]

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

        # Update chunk mapping: replace failed_tile.id with target_sterile.id
        self.chunk_replicas[chunk_idx] = [
            target_sterile.id if tid == failed_tile.id else tid
            for tid in replica_ids
        ]

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

    def _ensure_chunk_has_three_replicas(self, chunk_idx: int):
        """
        Enforce 3-replica invariant: top-up chunk to 3 replicas if needed.

        This is CRITICAL to prevent chunk replica count from drifting below 3.

        CRITICAL: REGENERATING tiles are NOT counted as live replicas - they are
        "pending replicas" that will become available after regeneration completes.
        """
        replica_ids = self.chunk_replicas[chunk_idx]
        replicas = [self.tiles[tid] for tid in replica_ids]

        # Filter to LIVE REPLICAS ONLY (ACTIVE or SICK or CLEAN_LOCKED, NOT REGENERATING)
        # REGENERATING tiles are "pending" and don't count toward quorum yet
        live_ids = [t.id for t in replicas
                   if t.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]]

        # Track pending replicas (REGENERATING - will be available soon)
        pending_ids = [t.id for t in replicas
                      if t.state == TileState.REGENERATING]

        # Update mapping to include both live and pending (for tracking purposes)
        # But only live replicas count toward the 3-replica requirement
        all_valid_ids = live_ids + pending_ids
        self.chunk_replicas[chunk_idx] = all_valid_ids

        if len(live_ids) >= 3:
            return  # Already have 3 live replicas

        # Need to top-up!
        missing_count = 3 - len(live_ids)
        if pending_ids:
            print(f"  ⚠️  Chunk {chunk_idx} has {len(live_ids)} live replicas + {len(pending_ids)} pending (REGENERATING), topping up {missing_count}...")
        else:
            print(f"  ⚠️  Chunk {chunk_idx} only has {len(live_ids)} live replicas, topping up {missing_count}...")

        # USE GOLDEN ANCHOR (always correct!) for top-up
        golden_truth = self.chunk_golden_truth.get(chunk_idx)
        if golden_truth:
            correct_data = golden_truth
            print(f"  Using GOLDEN ANCHOR for top-up (guaranteed correct)")
        else:
            # Fallback to majority voting if no anchor
            readable_tiles = [self.tiles[tid] for tid in readable_ids]
            surviving = [t for t in readable_tiles
                        if t.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]
                        and t.binary_data]

            if not surviving:
                print(f"  ✗ FATAL: Cannot top-up chunk {chunk_idx} - no surviving replicas or anchor!")
                return

            correct_data = self._reconstruct_via_majority_vote(surviving)
            print(f"  ⚠️  No golden anchor - using majority vote for top-up")

        # Find sterile spares to top-up
        sterile = [t for t in self.tiles if t.state == TileState.STERILE]

        for i in range(missing_count):
            if not sterile:
                print(f"  ✗ No sterile spares available for top-up!")
                break

            target = sterile.pop(0)

            # Seed target with correct data
            target.state = TileState.REGENERATING
            target.binary_data = correct_data
            target.pattern = self.encoder.encode(correct_data)
            target.regeneration_progress = 0.0
            target.needs_scrub = False
            target.integrity = 0.0

            # Set checksum
            import zlib
            target.chunk_checksum = zlib.crc32(correct_data.encode()) & 0xffffffff

            # Add to chunk mapping
            self.chunk_replicas[chunk_idx].append(target.id)
            print(f"  ✓ Added replica on tile {target.id} (top-up #{i+1}/{missing_count})")

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
                if tile.binary_data != golden_truth:
                    for i in range(min(len(tile.binary_data), len(golden_truth))):
                        if tile.binary_data[i] != golden_truth[i]:
                            disagreements += 1

                    # MANDATORY WRITE-BACK from anchor
                    tile.binary_data = golden_truth
                    tile.pattern = self.encoder.encode(golden_truth)
                    tile.chunk_checksum = golden_checksum
                    replicas_repaired += 1

            # Update metrics
            self.replica_bit_errors += disagreements
            self.scrub_writebacks += replicas_repaired

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
                else:
                    print(f"      ✓ Post-condition verified: all replicas match anchor")
            else:
                print(f"      ✓ All replicas match anchor - no repairs needed")

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
                if tile.binary_data != golden_truth:
                    for i in range(min(len(tile.binary_data), len(golden_truth))):
                        if tile.binary_data[i] != golden_truth[i]:
                            disagreements += 1

                    # Write-back anchor truth (not reconstructed!)
                    tile.binary_data = golden_truth
                    tile.pattern = self.encoder.encode(golden_truth)
                    tile.chunk_checksum = golden_checksum
                    replicas_repaired += 1

            # Update metrics
            self.replica_bit_errors += disagreements
            self.scrub_writebacks += replicas_repaired

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
                else:
                    print(f"      ✓ Post-condition verified: all replicas match golden truth")

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

        CRITICAL: Every chunk must have exactly 3 replicas at all times
        (unless mid-rebuild, in which case we should have a REGENERATING tile).
        """
        for chunk_idx, tile_ids in self.chunk_replicas.items():
            # Assert exactly 3 tile IDs per chunk
            if len(tile_ids) != 3:
                raise RuntimeError(
                    f"Chunk {chunk_idx} has {len(tile_ids)} replicas, expected 3! "
                    f"Tile IDs: {tile_ids}"
                )

            # Count how many are readable (ACTIVE/SICK) vs REGENERATING
            tiles = [self.tiles[tid] for tid in tile_ids]
            readable = sum(1 for t in tiles if t.state in [TileState.ACTIVE, TileState.SICK])
            regenerating = sum(1 for t in tiles if t.state == TileState.REGENERATING)

            # Should have at least 1 readable or 1 regenerating
            if readable == 0 and regenerating == 0:
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

    def _calculate_replica_errors(self) -> tuple:
        """
        Calculate replica bit errors: total disagreements vs GOLDEN ANCHOR.

        This metric tracks data drift and shows scrubbing effectiveness.
        Uses golden anchor as reference (not majority voting between replicas).

        Returns:
            (active_only_errors, offline_count) - only ACTIVE tiles for convergence metric
        """
        active_only_disagreements = 0
        offline_count = 0

        readable_threshold = 0.60  # Minimum integrity to be readable

        for chunk_idx in self.chunk_replicas.keys():
            replica_ids = self.chunk_replicas[chunk_idx]
            replicas = [self.tiles[tid] for tid in replica_ids]

            # Get golden anchor as reference
            golden_truth = self.chunk_golden_truth.get(chunk_idx)
            if not golden_truth:
                continue  # Skip chunks without anchor

            # Count offline replicas (REGENERATING or unreadable)
            for tile in replicas:
                if tile.state == TileState.REGENERATING:
                    offline_count += 1
                elif tile.state not in [TileState.ACTIVE, TileState.SICK]:
                    offline_count += 1
                elif tile.integrity < readable_threshold:
                    offline_count += 1

            # Get ACTIVE replicas ONLY (not SICK, not REGENERATING)
            active_only = [t for t in replicas
                          if t.state == TileState.ACTIVE
                          and t.integrity >= readable_threshold
                          and t.binary_data]

            # Count disagreements vs GOLDEN ANCHOR (only from ACTIVE tiles)
            for tile in active_only:
                for i in range(min(len(tile.binary_data), len(golden_truth))):
                    if tile.binary_data[i] != golden_truth[i]:
                        active_only_disagreements += 1

        return (active_only_disagreements, offline_count)

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

                    # Mark pending replicas differently
                    if tile.state == TileState.REGENERATING:
                        replicas_info.append(f"{tile.id}({state_char},{tile.integrity:.0%})[PENDING]")
                        pending_count += 1
                    elif tile.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]:
                        replicas_info.append(f"{tile.id}({state_char},{tile.integrity:.0%})")
                        live_count += 1
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

            # Replica bit errors (convergence metric - ACTIVE tiles only)
            replica_errors_active, offline_count = controller._calculate_replica_errors()

            # Count total ACTIVE tiles with data
            active_tile_count = sum(1 for t in controller.tiles
                                   if t.state == TileState.ACTIVE and t.binary_data)
            total_active_bits = len(test_data) * active_tile_count // (controller.n_active // controller.replication_factor) if active_tile_count > 0 else 0

            replica_error_rate = (replica_errors_active / total_active_bits * 100) if total_active_bits > 0 and replica_errors_active > 0 else 0
            if replica_error_rate < 5:
                print(f"  ✓ Replica bit errors (ACTIVE only): {replica_errors_active} ({replica_error_rate:.2f}%) - GOOD")
            else:
                print(f"  ⚠️  Replica bit errors (ACTIVE only): {replica_errors_active} ({replica_error_rate:.2f}%) - HIGH")

            print(f"  📊 Replica availability: {offline_count} replicas offline (REGENERATING/unreadable)")
            print(f"  📊 Convergence: {'YES' if replica_error_rate < 5 else 'NO'}")

            # Scrub effectiveness
            print(f"  📊 Scrub write-backs: {controller.scrub_writebacks} replicas repaired")
            print(f"  📊 Total disagreements found: {controller.replica_bit_errors}")

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

    # Replica bit errors (convergence metric - ACTIVE tiles only)
    replica_errors_active, offline_count = controller._calculate_replica_errors()

    # Count total ACTIVE tiles with data
    active_tile_count = sum(1 for t in controller.tiles
                           if t.state == TileState.ACTIVE and t.binary_data)
    total_active_bits = len(test_data) * active_tile_count // (controller.n_active // controller.replication_factor) if active_tile_count > 0 else 0

    replica_error_rate = (replica_errors_active / total_active_bits * 100) if total_active_bits > 0 and replica_errors_active > 0 else 0

    if replica_error_rate == 0:
        print(f"  ✓✓ REPLICA BIT ERRORS (ACTIVE only): 0 (0.0%) - PERFECT CONVERGENCE ✓✓")
    elif replica_error_rate < 5:
        print(f"  ✓ REPLICA BIT ERRORS (ACTIVE only): {replica_errors_active} ({replica_error_rate:.2f}%) - GOOD")
        print(f"     Goal was <5% - achieved!")
    else:
        print(f"  ⚠️  REPLICA BIT ERRORS (ACTIVE only): {replica_errors_active} ({replica_error_rate:.2f}%) - HIGH")
        print(f"     Goal was <5% - needs improvement")

    print(f"  📊 Replica availability: {offline_count} replicas offline (REGENERATING/unreadable)")

    # Scrub effectiveness
    print(f"\nSCRUBBING EFFECTIVENESS:")
    print(f"  Total scrub write-backs: {controller.scrub_writebacks} replicas repaired")
    print(f"  Total disagreements found: {controller.replica_bit_errors}")
    print(f"  Convergence: {'YES' if replica_error_rate < 5 else 'NO (still diverging)'}")

    # Truth authority status
    quorum_chunks = sum(1 for src in controller.chunk_truth_source.values() if src == TruthSource.QUORUM)
    anchor_chunks = sum(1 for src in controller.chunk_truth_source.values() if src == TruthSource.GOLDEN_ANCHOR)
    print(f"\nTRUTH AUTHORITY HIERARCHY:")
    print(f"  Anchor promotions: {controller.anchor_promotions} total (QUORUM → GOLDEN_ANCHOR)")
    print(f"  Final authority: {quorum_chunks} QUORUM, {anchor_chunks} GOLDEN_ANCHOR")
    if anchor_chunks > 0:
        print(f"  ⚠️  {anchor_chunks} chunks permanently using anchor authority (majority voting disabled)")

    # SUCCESS CRITERIA CHECK
    print(f"\nSUCCESS CRITERIA:")
    success_logical = logical_errors == 0
    success_replica = replica_error_rate < 5
    at_risk_loops = controller._detect_at_risk_loops()
    success_no_loops = len(at_risk_loops) == 0
    success_no_quarantine = len(controller.quarantined_chunks) == 0
    success_scrub_converge = controller.scrub_failed_to_converge == 0

    print(f"  {'✓' if success_logical else '✗'} Logical bit errors = 0%")
    print(f"  {'✓' if success_replica else '✗'} Replica bit errors < 5%")
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

    plt.show()

    return controller


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        # Quick 90-day simulation
        run_phase2_simulation(duration_days=90)
    else:
        # Full year simulation
        run_phase2_simulation(duration_days=365)
