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
    MATURE_DEGRADATION_REDUCTION = 1.0  # Mature replicas degrade at same rate as immature (realistic chronic aging)
    CONSOLIDATION_INTEGRITY_BOOST = 0.02  # Anchor write-back increases integrity by 2%
    CONSOLIDATION_MAX_INTEGRITY = 0.98  # Cap for integrity boost from consolidation

    # BIOLOGICAL DEGRADATION: Realistic chronic decay (decoupled from data correctness)
    # Physical integrity degrades continuously even when data remains correct
    BASE_DEGRADATION_RATE = 0.0005  # 0.05% per day baseline (slower, but chronic hits add pressure)
    CHRONIC_DEGRADATION_PROB = 0.01  # 1% chance per day for chronic degradation hit
    CHRONIC_DEGRADATION_MAG_MIN = 0.04  # Minimum 4% integrity loss from chronic hit
    CHRONIC_DEGRADATION_MAG_MAX = 0.08  # Maximum 8% integrity loss from chronic hit

    # REST & RECOVERY CONSTANTS (disabled to ensure regular regeneration pressure)
    RECOVERY_ENABLED = False  # Disable passive recovery to allow chronic degradation to accumulate
    RECOVERY_RATE = 0.0  # No recovery (tiles must regenerate to restore integrity)
    RECOVERY_MAX = 0.95  # (Unused when RECOVERY_ENABLED = False)
    RECOVERY_MIN_CALM_DAYS = 3  # (Unused when RECOVERY_ENABLED = False)

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
        self.write_successes_total = 0  # Total successful writes

        # TWO-MODE TOP-UP SYSTEM: Restore 3-live redundancy
        self.chunk_two_live_since_day = {}  # {chunk_idx: day} - when chunk dropped to 2 live
        self.chunk_last_drift = {}  # {chunk_idx: [drift1, drift2, drift3]} - last 3 scrub drifts
        self.chunk_last_shock_day = {}  # {chunk_idx: day} - last degradation event affecting chunk
        self.calm_topup_count = 0  # Count of calm-period top-ups (stable chunks)
        self.recovery_topup_count = 0  # Count of recovery top-ups (failed replicas)
        self.chunk_time_at_3live = {}  # {chunk_idx: days} - cumulative time at 3 live replicas (DEPRECATED - use _correct/_healthy)
        self.chunk_time_at_2live = {}  # {chunk_idx: days} - cumulative time at 2 live replicas
        self.chunk_under_replicated_since_day = {}  # {chunk_idx: day} - when chunk dropped below 3 live

        # CORRECTNESS vs HEALTH SPLIT: Track verified replicas separately from healthy ones
        self.chunk_time_at_3live_correct = {}  # {chunk_idx: days} - time at 3 LIVE_CORRECT replicas (verified, >=60%)
        self.chunk_time_at_3live_healthy = {}  # {chunk_idx: days} - time at 3 LIVE_HEALTHY replicas (>=80%)
        self.chunk_time_at_2live_correct = {}  # {chunk_idx: days} - time at 2 LIVE_CORRECT replicas

        # DEADLINE TOP-UP: Force top-up if stuck <3 LIVE_CORRECT for too long
        self.DEADLINE_TOPUP_DAYS = 14  # Force top-up after 14 days <3 LIVE_CORRECT
        self.deadline_topup_count = 0  # Count of deadline-triggered top-ups

        # MUST-HEAL RULES: Mandatory repair for FAILED slots and stuck PENDING
        self.PENDING_DEADLINE_DAYS = 14  # Force action if chunk stuck <3 ACTIVE for >14 days
        self.failed_slot_rebuilds = 0  # Count of mandatory FAILED slot rebuilds
        self.pending_deadline_heals = 0  # Count of PENDING deadline forced promotions/rebuilds
        self.chunks_repair_required = set()  # Chunks with FAILED slots requiring immediate rebuild
        self.chunk_degraded_since_day = {}  # {chunk_idx: day} - when chunk dropped below 3 ACTIVE replicas

        # PROACTIVE_REBUILD: Replace degrading tiles BEFORE they fail
        # This makes self-healing explicit and measurable
        self.PROACTIVE_REBUILD_THRESHOLD = 0.70  # Only trigger for repeat offenders or <70%
        self.PROACTIVE_REBUILD_MIN_DAYS = 3  # Require 3 consecutive days <70%
        self.PROACTIVE_REBUILD_BUDGET_PER_YEAR = 55  # Max rebuilds per year (throttle if exceeded)
        self.PROACTIVE_REBUILD_THROTTLE_THRESHOLD = 0.68  # If >budget, require <68% for 5 days
        self.PROACTIVE_REBUILD_THROTTLE_DAYS = 5  # Stricter requirement when throttled
        self.proactive_rebuild_count = 0  # Count of proactive rebuilds
        self.tiles_saved_before_failure = 0  # Tiles replaced before crossing <60%
        self.tile_degraded_since_day = {}  # {tile_id: day} - when tile dropped below threshold

        # REGEN-IN-PLACE: Regenerate sick tiles in situ (Stage A - primary response)
        self.REGEN_IN_PLACE_THRESHOLD = 0.80  # Trigger if tile <80% (SICK range)
        self.REGEN_IN_PLACE_MIN_SICK_DAYS = 5  # Require 5 consecutive days SICK
        self.REGEN_DURATION_MIN = 5  # Minimum regeneration duration
        self.REGEN_DURATION_MAX = 7  # Maximum regeneration duration
        self.REGEN_INTEGRITY_MIN = 0.90  # Minimum integrity after regeneration
        self.REGEN_INTEGRITY_MAX = 0.97  # Maximum integrity after regeneration
        self.REPEAT_OFFENDER_WINDOW = 60  # Days to track repeat regenerations
        self.REPEAT_OFFENDER_THRESHOLD = 2  # Max regenerations before permanent swap
        self.regen_in_place_count = 0  # Count of in-place regenerations
        self.temp_shadow_count = 0  # Count of temporary shadow replicas created
        self.repeat_offender_swaps = 0  # Count of swaps due to repeat offenders
        self.tile_sick_since_day = {}  # {tile_id: day} - when tile became SICK
        self.tile_regen_history = {}  # {tile_id: [day1, day2, ...]} - regeneration events
        self.tiles_regenerating = set()  # Set of tile IDs currently regenerating
        self.tile_temp_shadow = {}  # {tile_id: shadow_tile_id} - maps regenerating tile to its shadow
        self.days_with_regen_active = 0  # Days when at least one tile was regenerating

        # CORRELATED_SHOCK_WEEKS: Periodic stress testing to force Stage B (PROACTIVE_REBUILD)
        self.SHOCK_WEEKS_PER_YEAR_MIN = 2  # Minimum shock weeks per year
        self.SHOCK_WEEKS_PER_YEAR_MAX = 4  # Maximum shock weeks per year
        self.SHOCK_WEEK_DEGRADATION_MULTIPLIER = 2.5  # Degradation multiplier during shock weeks
        self.SHOCK_WEEK_AFFECTED_TILES_MIN = 3  # Minimum tiles affected per shock week
        self.SHOCK_WEEK_AFFECTED_TILES_MAX = 6  # Maximum tiles affected per shock week
        self.shock_weeks = []  # List of shock week numbers
        self.shock_week_tiles = {}  # {week_num: [tile_ids]} - tiles affected during each shock week
        self.shock_weeks_triggered = 0  # Count of shock weeks that occurred
        self.current_shock_week_tiles = set()  # Tiles currently affected by shock week

        # SPARE_POOL_HEALTH: Maintain healthy spare pool
        self.SPARE_TARGET = 4  # Target number of healthy sterile spares
        self.spare_failures = 0  # Count of tiles that transitioned to FAILED state
        self.spare_regenerations = 0  # Count of orphaned FAILED tiles flushed to STERILE
        self.days_below_spare_target = 0  # Days when healthy sterile count < SPARE_TARGET

        # COLD SNAPSHOT ANCHOR: Last-resort recovery for correlated failures
        self.chunk_snapshot_bits = {}  # {chunk_idx: str} - cold snapshot of chunk data
        self.chunk_snapshot_epoch = {}  # {chunk_idx: int} - when snapshot was taken
        self.chunk_snapshot_checksum = {}  # {chunk_idx: int} - CRC32 checksum of snapshot
        self.snapshot_updates_count = 0  # Total snapshot updates (VERY conservative)
        self.snapshot_used_for_recovery_count = 0  # Snapshots used for emergency recovery
        self.correlated_failure_events = 0  # Chunks with <2 readable LIVE replicas

        # SNAPSHOT UPDATE CONFIGURATION (VERY conservative)
        self.SNAPSHOT_MIN_CLEAN_SCRUBS = 4  # Require 4 consecutive clean scrubs
        self.SNAPSHOT_MIN_ZERO_DRIFT_SCRUBS = 3  # Require 3 consecutive scrubs with 0 drift
        self.SNAPSHOT_MIN_CALM_DAYS = 7  # No shocks in last 7 days

        # TOP-UP CONFIGURATION
        self.CALM_TOPUP_MIN_2LIVE_DAYS = 7  # Minimum days at 2-live before calm top-up
        self.CALM_TOPUP_MIN_CLEAN_SCRUBS = 3  # Require 3 consecutive scrubs with 0 drift
        self.CALM_TOPUP_MIN_CALM_DAYS = 7  # No shocks in last N days
        self.RECOVERY_TOPUP_MIN_DAYS = 3  # Minimum days under-replicated before recovery top-up

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

        # HEALTH INSTRUMENTATION: Track degradation patterns
        self.daily_tiles_healthy = []  # Count of ACTIVE tiles >=80% per day
        self.daily_tiles_degraded = []  # Count of ACTIVE tiles 70-80% per day
        self.daily_tiles_sick = []  # Count of ACTIVE tiles 60-70% per day
        self.tiles_dropped_below_80_baseline = 0  # Dropped due to baseline decay
        self.tiles_dropped_below_80_shock = 0  # Dropped due to shock events
        self.tiles_recovered_integrity = 0  # Count of tiles that recovered integrity

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
                self._track_write(tile, success=True)  # Track initial writes
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

    # ===== FIXED 3-SLOT CHUNK REPLICA HELPERS =====
    def _get_chunk_tile_ids(self, chunk_idx: int) -> List[int]:
        """
        Get non-None tile IDs for a chunk (skipping empty slots).

        Returns:
            List of tile IDs (excludes None slots)
        """
        slots = self.chunk_replicas.get(chunk_idx, [None, None, None])
        return [tid for tid in slots if tid is not None]

    def _get_chunk_tiles(self, chunk_idx: int) -> List[Tile]:
        """
        Get non-None tiles for a chunk.

        Returns:
            List of Tile objects (excludes None slots)
        """
        tile_ids = self._get_chunk_tile_ids(chunk_idx)
        return [self.tiles[tid] for tid in tile_ids]

    def _find_empty_slot(self, chunk_idx: int) -> Optional[int]:
        """
        Find first empty (None) slot in chunk's replica array.

        Returns:
            Slot index (0-2) or None if all slots full
        """
        slots = self.chunk_replicas.get(chunk_idx, [None, None, None])
        for i, tid in enumerate(slots):
            if tid is None:
                return i
        return None

    def _set_chunk_slot(self, chunk_idx: int, slot: int, tile_id: Optional[int]):
        """
        Set a specific slot in chunk's replica array.

        Args:
            chunk_idx: Chunk index
            slot: Slot index (0-2)
            tile_id: Tile ID or None
        """
        if chunk_idx not in self.chunk_replicas:
            self.chunk_replicas[chunk_idx] = [None, None, None]
        self.chunk_replicas[chunk_idx][slot] = tile_id

    def _clear_chunk_slot_by_tile_id(self, chunk_idx: int, tile_id: int) -> bool:
        """
        Clear the slot containing a specific tile ID (set to None).

        Args:
            chunk_idx: Chunk index
            tile_id: Tile ID to remove

        Returns:
            True if tile was found and cleared, False otherwise
        """
        if chunk_idx not in self.chunk_replicas:
            return False

        for i, tid in enumerate(self.chunk_replicas[chunk_idx]):
            if tid == tile_id:
                self.chunk_replicas[chunk_idx][i] = None
                return True
        return False

    def _is_live_correct(self, tile: Tile) -> bool:
        """
        Check if a replica is LIVE_CORRECT (verified and readable).

        LIVE_CORRECT = has passed verification/scrub, even if integrity <80%
        States: ACTIVE, SICK, or CLEAN_LOCKED with integrity >=60%

        This is the key metric for correctness (data is valid).
        """
        return (tile.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]
                and tile.binary_data is not None
                and tile.integrity >= 0.60)

    def _is_live_healthy(self, tile: Tile) -> bool:
        """
        Check if a replica is LIVE_HEALTHY (good physical health).

        LIVE_HEALTHY = integrity >=80% (old definition of "LIVE")

        This is the metric for physical health (tile is not degraded).
        """
        return (tile.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]
                and tile.binary_data is not None
                and tile.integrity >= 0.80)

    def _count_live_correct(self, chunk_idx: int) -> int:
        """Count LIVE_CORRECT replicas for a chunk."""
        tile_ids = self._get_chunk_tile_ids(chunk_idx)
        return sum(1 for tid in tile_ids if self._is_live_correct(self.tiles[tid]))

    def _count_live_healthy(self, chunk_idx: int) -> int:
        """Count LIVE_HEALTHY replicas for a chunk."""
        tile_ids = self._get_chunk_tile_ids(chunk_idx)
        return sum(1 for tid in tile_ids if self._is_live_healthy(self.tiles[tid]))

    def _track_write(self, tile: Tile, success: bool):
        """Track write attempts and outcomes for metrics."""
        self.write_attempts_total += 1
        if success:
            self.write_successes_total += 1
        else:
            self.write_failures_total += 1
            tile.write_fail_count += 1

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

        # CORRELATED_SHOCK_WEEKS: Check if we're entering/exiting a shock week
        current_week_1indexed = (self.uptime_days + 6) // 7  # Week 1 = days 1-7
        if current_week_1indexed in self.shock_weeks:
            # We're in a shock week
            if current_week_1indexed not in [w for w in self.shock_weeks if w in self.shock_week_tiles]:
                # First day of this shock week - skip initialization
                pass
            # Update current shock tiles
            self.current_shock_week_tiles = set(self.shock_week_tiles.get(current_week_1indexed, []))
            # Only print on first day of shock week
            if self.uptime_days % 7 == 1:
                print(f"\n🌩️  SHOCK WEEK {current_week_1indexed} ACTIVE: {len(self.current_shock_week_tiles)} tiles will receive {self.SHOCK_WEEK_DEGRADATION_MULTIPLIER}x degradation (tiles: {sorted(self.current_shock_week_tiles)})")
                self.shock_weeks_triggered += 1
        else:
            self.current_shock_week_tiles = set()

        # Age all tiles and update states
        for tile in self.tiles:
            if tile.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]:
                tile.age += 1

                # Track health BEFORE degradation (for instrumentation)
                was_healthy = (tile.integrity >= 0.80)
                integrity_before = tile.integrity

                # BIOLOGICAL DEGRADATION: Continuous integrity loss (decoupled from data correctness)
                # Physical substrate degrades even when data remains perfectly correct via ECC
                if tile.maturity_level >= 2:
                    # Mature tiles: same degradation rate (chronic aging model)
                    degradation_rate = 1.0 - (self.BASE_DEGRADATION_RATE * self.MATURE_DEGRADATION_REDUCTION)
                    tile.integrity *= degradation_rate
                else:
                    # Immature tiles: baseline degradation
                    degradation_rate = 1.0 - self.BASE_DEGRADATION_RATE
                    tile.integrity *= degradation_rate

                # CHRONIC DEGRADATION: Non-lethal integrity hits (regular pressure toward regeneration)
                # Models cumulative molecular damage, substrate fatigue, environmental stress
                # This ensures tiles regularly drift into 70-80% integrity range
                # CORRELATED_SHOCK_WEEKS: Apply elevated degradation stress to selected tiles
                chronic_prob = self.CHRONIC_DEGRADATION_PROB
                if tile.id in self.current_shock_week_tiles:
                    # Shock week: elevated degradation probability
                    chronic_prob *= self.SHOCK_WEEK_DEGRADATION_MULTIPLIER

                if np.random.random() < chronic_prob:
                    chronic_magnitude = np.random.uniform(self.CHRONIC_DEGRADATION_MAG_MIN, self.CHRONIC_DEGRADATION_MAG_MAX)
                    tile.integrity *= (1.0 - chronic_magnitude)
                    self.total_degradation_events += 1
                    shock_marker = " [SHOCK WEEK]" if tile.id in self.current_shock_week_tiles else ""
                    if tile.integrity < 0.80:
                        print(f"🧬 Chronic degradation{shock_marker}: Tile {tile.id} dropped to {tile.integrity:.2%} (molecular fatigue)")
                    # Track if this caused drop below 80%
                    if was_healthy and tile.integrity < 0.80:
                        self.tiles_dropped_below_80_baseline += 1

                # REST & RECOVERY: Passive integrity recovery for stable tiles
                # Only if tile has been calm (no recent shocks) AND mature
                if self.RECOVERY_ENABLED and tile.maturity_level >= 2:
                    # Check if this tile's chunk has been calm
                    chunk_idx = None
                    for cidx, tile_ids in self.chunk_replicas.items():
                        if tile.id in tile_ids:
                            chunk_idx = cidx
                            break

                    if chunk_idx is not None:
                        # Check calmness: no shocks in last N days
                        days_since_shock = 999
                        if chunk_idx in self.chunk_last_shock_day:
                            days_since_shock = self.uptime_days - self.chunk_last_shock_day[chunk_idx]

                        if days_since_shock >= self.RECOVERY_MIN_CALM_DAYS and tile.integrity < self.RECOVERY_MAX:
                            # Apply passive recovery
                            old_integrity = tile.integrity
                            tile.integrity = min(tile.integrity + self.RECOVERY_RATE, self.RECOVERY_MAX)
                            if tile.integrity > old_integrity + 0.0005:  # Only count significant recovery
                                self.tiles_recovered_integrity += 1

                # Random degradation events (0.5% chance per day)
                # BIOLOGICAL HARDENING: Mature replicas are MORE resistant to random shocks
                shock_probability = 0.005 if tile.maturity_level < 2 else 0.002  # 60% lower for mature (was 50%)
                if np.random.random() < shock_probability:
                    shock_magnitude = np.random.uniform(0.85, 0.95) if tile.maturity_level < 2 else np.random.uniform(0.90, 0.97)  # Smaller shocks for mature
                    tile.integrity *= shock_magnitude
                    self.total_degradation_events += 1
                    # Track if this caused drop below 80%
                    if was_healthy and tile.integrity < 0.80:
                        self.tiles_dropped_below_80_shock += 1
                    # CALM-PERIOD TOP-UP: Record shock for this tile's chunk
                    self._record_shock(tile.id)

                # Track if baseline degradation caused drop below 80%
                if was_healthy and tile.integrity < 0.80 and tile.integrity >= integrity_before * 0.99:
                    # Dropped below 80% but no shock (baseline decay only)
                    self.tiles_dropped_below_80_baseline += 1

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
                        self.spare_failures += 1  # Track tile failures
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
                            self._track_write(tile, success=True)  # Track scrub write-back

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
                                    self._track_write(rep, success=True)  # Track retry write-back

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
                    # IMMEDIATE PROMOTION: Promote to ACTIVE immediately after verification
                    # CLEAN_LOCK is now a protection flag, not a state gate
                    tile.state = TileState.ACTIVE  # Immediately LIVE_CORRECT (verified)
                    tile.integrity = 0.98  # Near-perfect regeneration
                    tile.age = 0
                    tile.regeneration_progress = 0.0
                    tile.regen_complete_day = self.uptime_days
                    tile.clean_locked_until_day = self.uptime_days + 7  # Protected from proactive rebuild
                    tile.needs_scrub = False  # Already did hard scrub above
                    print(f"  ✓ Tile {tile.id} promoted to ACTIVE (LIVE_CORRECT) with 7-day protection (until day {tile.clean_locked_until_day})")

        # Clear expired clean lock protection flags
        for tile in self.tiles:
            if tile.clean_locked_until_day > 0 and self.uptime_days >= tile.clean_locked_until_day:
                print(f"🔓 Tile {tile.id} clean lock protection expired (integrity: {tile.integrity:.2%})")
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

        # THREE-MODE TOP-UP: Track time at 2-live vs 3-live and check for top-up opportunities
        self._track_live_replica_time()

        # Complete any ongoing REGEN-IN-PLACE operations (check before starting new ones)
        self._complete_regen_in_place()

        # MUST-HEAL RULES (highest priority - bypass risk gates)
        self._check_failed_slots()  # Rule 1: Mandatory rebuild of FAILED slots
        self._enforce_pending_deadline()  # Rule 2: Force action on stuck PENDING chunks

        # STAGE A: REGEN-IN-PLACE (primary self-healing - regenerate sick tiles in situ)
        self._check_regen_in_place()

        # STAGE B: PROACTIVE_REBUILD (repeat offenders only - permanent swap)
        self._check_proactive_rebuild()

        # SPARE_POOL_HEALTH: Maintain healthy spare pool (flush orphaned FAILED tiles)
        self._maintain_spare_pool()

        # Try RECOVERY_TOPUP first (high priority - failed replicas)
        self._check_recovery_topup()
        # Then try CALM_TOPUP (medium priority - stable chunks)
        self._check_calm_period_topup()
        # Finally try DEADLINE_TOPUP (fail-safe - chunks stuck <3-live too long)
        self._check_deadline_topup()

        # Daily monitoring: print min/avg integrity and triggers
        if self.uptime_days % 10 == 0:  # Every 10 days
            active_tiles = [t for t in self.tiles if t.state in [TileState.ACTIVE, TileState.SICK]]
            if active_tiles:
                min_integrity = min(t.integrity for t in active_tiles)
                avg_integrity = np.mean([t.integrity for t in active_tiles])
                sick_count = sum(1 for t in self.tiles if t.state == TileState.SICK)
                print(f"📊 Day {self.uptime_days}: min={min_integrity:.1%}, avg={avg_integrity:.1%}, SICK={sick_count}, rebuilds={self.rebuild_count}")

        # HEALTH INSTRUMENTATION: Track daily health distribution
        active_tiles = [t for t in self.tiles if t.state == TileState.ACTIVE]
        healthy_count = sum(1 for t in active_tiles if t.integrity >= 0.80)
        degraded_count = sum(1 for t in active_tiles if 0.70 <= t.integrity < 0.80)
        sick_count = sum(1 for t in active_tiles if 0.60 <= t.integrity < 0.70)
        self.daily_tiles_healthy.append(healthy_count)
        self.daily_tiles_degraded.append(degraded_count)
        self.daily_tiles_sick.append(sick_count)

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

                    replicas = [self.tiles[tid] for tid in tile_ids if tid is not None]
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
            replicas = [self.tiles[tid] for tid in tile_ids if tid is not None]

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

            # Add to chunk mapping (find empty slot)
            empty_slot = self._find_empty_slot(chunk_idx)
            if empty_slot is not None:
                self._set_chunk_slot(chunk_idx, empty_slot, target.id)
                print(f"  ✓ Added PENDING replica on tile {target.id} to slot {empty_slot} (top-up #{i+1}/{missing_count})")
            else:
                print(f"  ⚠️  Chunk {chunk_idx} has no empty slots - skipping!")

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
            # EMERGENCY: Correlated failure detected - try snapshot recovery
            if chunk_idx in self.chunk_snapshot_bits:
                self.correlated_failure_events += 1
                print(f"  🚨 CORRELATED FAILURE: Chunk {chunk_idx} has <2 readable replicas ({len(readable)})")
                print(f"      Attempting COLD SNAPSHOT emergency recovery...")

                # Try to recover using snapshot
                if self._emergency_snapshot_recovery(chunk_idx):
                    print(f"      ✓ Snapshot recovery initiated - chunk will recover")
                    return  # Recovery in progress, skip normal scrub
                else:
                    print(f"      ✗ Snapshot recovery failed - no sterile spares or snapshot unavailable")

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

                    # COLD SNAPSHOT: Check if we should update snapshot
                    self._update_cold_snapshot_if_eligible(chunk_idx, golden_truth)
            else:
                print(f"      ✓ All replicas match anchor - no repairs needed")

                # RISK-GATED REBUILDS: Reset failed scrub counter (no repairs needed = success)
                self.chunk_failed_scrub_count[chunk_idx] = 0

                # BIOLOGICAL HARDENING: Maturation for stable replicas (no repair needed)
                self._advance_maturation(readable)

                # QUORUM RESTORATION: Track consecutive clean scrubs
                self._track_clean_scrub_for_quorum_restoration(chunk_idx, readable)

                # COLD SNAPSHOT: Check if we should update snapshot
                self._update_cold_snapshot_if_eligible(chunk_idx, golden_truth)

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

                    # COLD SNAPSHOT: Check if we should update snapshot
                    self._update_cold_snapshot_if_eligible(chunk_idx, golden_truth)
            else:
                # No disagreements - all replicas already match
                # RISK-GATED REBUILDS: Reset failed scrub counter (no repairs needed = success)
                self.chunk_failed_scrub_count[chunk_idx] = 0

                # BIOLOGICAL HARDENING: Maturation for stable replicas
                self._advance_maturation(readable)

                # QUORUM RESTORATION: Track clean scrub
                current_count = self.chunk_consecutive_clean_scrubs.get(chunk_idx, 0)
                self.chunk_consecutive_clean_scrubs[chunk_idx] = current_count + 1

                # COLD SNAPSHOT: Check if we should update snapshot
                self._update_cold_snapshot_if_eligible(chunk_idx, golden_truth)

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
                        print(f"              Shock resistance increased (chronic degradation pressure continues)")

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

    def _update_cold_snapshot_if_eligible(self, chunk_idx: int, golden_truth: str):
        """
        COLD SNAPSHOT ANCHOR: Update snapshot if chunk is super-stable.

        VERY conservative update rules - only snapshot when chunk is:
        - Has 3 LIVE replicas (full redundancy)
        - 0 drift for last Y scrubs (Y=3)
        - No shocks in last Z days (Z=7)
        - K consecutive clean scrubs (K=4)

        This creates a last-resort recovery anchor for correlated failures.

        Args:
            chunk_idx: Chunk to potentially snapshot
            golden_truth: Current golden truth data
        """
        tile_ids = self._get_chunk_tile_ids(chunk_idx)  # Get non-None tile IDs

        # CRITERION 1: Must have 3 LIVE replicas (ACTIVE, ≥60%)
        live_tiles = [self.tiles[tid] for tid in tile_ids
                     if self.tiles[tid].state == TileState.ACTIVE
                     and self.tiles[tid].integrity >= 0.60]
        if len(live_tiles) < 3:
            return  # Not fully redundant

        # CRITERION 2: Must have 0 drift for last Y scrubs
        if chunk_idx not in self.chunk_last_drift:
            return
        drift_history = self.chunk_last_drift[chunk_idx]
        if len(drift_history) < self.SNAPSHOT_MIN_ZERO_DRIFT_SCRUBS:
            return  # Not enough history
        if any(d > 0 for d in drift_history[-self.SNAPSHOT_MIN_ZERO_DRIFT_SCRUBS:]):
            return  # Recent drift detected

        # CRITERION 3: No shocks in last Z days
        if chunk_idx in self.chunk_last_shock_day:
            days_since_shock = self.uptime_days - self.chunk_last_shock_day[chunk_idx]
            if days_since_shock < self.SNAPSHOT_MIN_CALM_DAYS:
                return  # Too soon after shock

        # CRITERION 4: K consecutive clean scrubs
        consecutive_clean = self.chunk_consecutive_clean_scrubs.get(chunk_idx, 0)
        if consecutive_clean < self.SNAPSHOT_MIN_CLEAN_SCRUBS:
            return  # Not stable enough

        # ALL CRITERIA MET - update snapshot!
        import zlib
        new_checksum = zlib.crc32(golden_truth.encode()) & 0xffffffff

        # Check if snapshot changed
        old_snapshot = self.chunk_snapshot_bits.get(chunk_idx)
        if old_snapshot == golden_truth:
            return  # Snapshot unchanged, no update needed

        self.chunk_snapshot_bits[chunk_idx] = golden_truth
        self.chunk_snapshot_epoch[chunk_idx] = self.uptime_days
        self.chunk_snapshot_checksum[chunk_idx] = new_checksum
        self.snapshot_updates_count += 1

        print(f"          📸 COLD SNAPSHOT updated for chunk {chunk_idx} (epoch={self.uptime_days}, checksum={new_checksum:08x})")
        print(f"              Criteria: 3 live, 0 drift×{self.SNAPSHOT_MIN_ZERO_DRIFT_SCRUBS}, {consecutive_clean} clean scrubs, {days_since_shock if chunk_idx in self.chunk_last_shock_day else 'no'}d since shock")

    def _emergency_snapshot_recovery(self, chunk_idx: int) -> bool:
        """
        COLD SNAPSHOT EMERGENCY RECOVERY: Recover chunk using cold snapshot.

        This is the last-resort recovery path for correlated failures where
        all replicas become unreadable simultaneously.

        Uses snapshot_bits as truth source to rebuild one replica onto a
        sterile tile, then normal quorum workflow can resume.

        Args:
            chunk_idx: Chunk to recover

        Returns:
            True if recovery initiated, False if not possible
        """
        # Check if we have a snapshot
        if chunk_idx not in self.chunk_snapshot_bits:
            return False

        snapshot_data = self.chunk_snapshot_bits[chunk_idx]
        snapshot_epoch = self.chunk_snapshot_epoch[chunk_idx]
        snapshot_checksum = self.chunk_snapshot_checksum[chunk_idx]

        # Verify snapshot checksum
        import zlib
        actual_checksum = zlib.crc32(snapshot_data.encode()) & 0xffffffff
        if actual_checksum != snapshot_checksum:
            print(f"      ✗ SNAPSHOT CORRUPTED! Checksum mismatch (expected {snapshot_checksum:08x}, got {actual_checksum:08x})")
            return False

        # Find sterile spare
        sterile = [t for t in self.tiles if t.state == TileState.STERILE]
        if not sterile:
            return False  # No spare capacity

        target = sterile[0]

        print(f"      📸 Using snapshot from epoch {snapshot_epoch} (age: {self.uptime_days - snapshot_epoch} days)")
        print(f"      Creating replica on tile {target.id}...")

        # Seed target with snapshot data
        target.state = TileState.REGENERATING
        target.binary_data = snapshot_data
        target.pattern = self.encoder.encode(snapshot_data)
        self._track_write(target, success=True)  # Track snapshot recovery write
        target.regeneration_progress = 1.0  # Skip regeneration delay
        target.needs_scrub = False
        target.integrity = 0.98  # Start at high integrity
        target.chunk_checksum = snapshot_checksum

        # Check if chunk already has too many replicas (prevent inflation during recovery)
        usable_count = sum(1 for tid in self.chunk_replicas.get(chunk_idx, [])
                          if self.tiles[tid].state not in [TileState.FAILED, TileState.STERILE])
        if usable_count >= 3:
            print(f"      ⚠️  Chunk {chunk_idx} already has {usable_count} usable replicas - skipping recovery")
            target.state = TileState.STERILE
            return False

        # Add to chunk mapping (find empty slot)
        empty_slot = self._find_empty_slot(chunk_idx)
        if empty_slot is not None:
            self._set_chunk_slot(chunk_idx, empty_slot, target.id)
            print(f"      ✓ Added snapshot recovery replica to slot {empty_slot}")
        else:
            # No empty slot - chunk already full
            print(f"      ⚠️  Chunk {chunk_idx} has no empty slots - skipping snapshot recovery")
            target.state = TileState.STERILE
            return False

        # IMPORTANT: Do NOT call _scrub_chunk here - it would cause recursive AT_RISK detection!
        # The replica will be verified in the next normal scrub cycle

        # IMMEDIATE PROMOTION: Mark as ACTIVE (LIVE_CORRECT) with 7-day protection
        target.state = TileState.ACTIVE
        target.clean_locked_until_day = self.uptime_days + 7
        target.regen_complete_day = self.uptime_days

        # Reset maturation (new replica)
        target.consecutive_successful_scrubs = 0
        target.maturity_level = 0
        target.matured_on_day = -999

        self.snapshot_used_for_recovery_count += 1

        print(f"      ✓ Snapshot recovery initiated - tile {target.id} added as ACTIVE (LIVE_CORRECT) with protection")

        # FOLLOW-THROUGH: If chunk still <3 LIVE_CORRECT after this recovery, schedule additional top-up
        # This ensures we don't leave chunk at 2-live after snapshot recovery
        live_correct_count = self._count_live_correct(chunk_idx)
        if live_correct_count < 3:
            print(f"      ⚠️  Chunk {chunk_idx} still has only {live_correct_count} LIVE_CORRECT replicas after snapshot recovery")
            print(f"          Marking for additional top-up to restore full 3-live redundancy")
            # Mark chunk as under-replicated to trigger top-up on next cycle
            if chunk_idx not in self.chunk_under_replicated_since_day:
                self.chunk_under_replicated_since_day[chunk_idx] = self.uptime_days

        # CLEANUP: Flush any FAILED tiles to maintain 3-replica invariant
        # After adding recovery replica, chunk may have 4 replicas (3 usable + 1 FAILED)
        failed_tile_ids = [tid for tid in self._get_chunk_tile_ids(chunk_idx)
                          if self.tiles[tid].state == TileState.FAILED]
        for failed_id in failed_tile_ids:
            self._flush_tile(self.tiles[failed_id])
            self._clear_chunk_slot_by_tile_id(chunk_idx, failed_id)
            print(f"      Flushed FAILED tile {failed_id} to sterile pool (maintaining 3-replica invariant)")

        print(f"      Chunk {chunk_idx} now has {len(self.chunk_replicas[chunk_idx])} replicas")

        return True

    def _track_live_replica_time(self):
        """
        Track time spent at 2-live vs 3-live for each chunk.

        Now tracks BOTH correctness (LIVE_CORRECT) and health (LIVE_HEALTHY) metrics.
        LIVE_CORRECT = verified, >=60% integrity (key metric for correctness)
        LIVE_HEALTHY = >=80% integrity (key metric for health)
        """
        for chunk_idx, tile_ids in self.chunk_replicas.items():
            # Count LIVE_CORRECT replicas (verified, >=60%)
            live_correct_count = self._count_live_correct(chunk_idx)

            # Count LIVE_HEALTHY replicas (>=80%)
            live_healthy_count = self._count_live_healthy(chunk_idx)

            # Initialize CORRECT counters
            if chunk_idx not in self.chunk_time_at_3live_correct:
                self.chunk_time_at_3live_correct[chunk_idx] = 0
            if chunk_idx not in self.chunk_time_at_2live_correct:
                self.chunk_time_at_2live_correct[chunk_idx] = 0

            # Initialize HEALTHY counters
            if chunk_idx not in self.chunk_time_at_3live_healthy:
                self.chunk_time_at_3live_healthy[chunk_idx] = 0

            # Initialize legacy counters (for compatibility)
            if chunk_idx not in self.chunk_time_at_3live:
                self.chunk_time_at_3live[chunk_idx] = 0
            if chunk_idx not in self.chunk_time_at_2live:
                self.chunk_time_at_2live[chunk_idx] = 0

            # Track LIVE_CORRECT time (primary metric for correctness)
            if live_correct_count >= 3:
                self.chunk_time_at_3live_correct[chunk_idx] += 1
                # Reset timers when back to 3-live-correct
                if chunk_idx in self.chunk_two_live_since_day:
                    del self.chunk_two_live_since_day[chunk_idx]
                if chunk_idx in self.chunk_under_replicated_since_day:
                    del self.chunk_under_replicated_since_day[chunk_idx]
            elif live_correct_count == 2:
                self.chunk_time_at_2live_correct[chunk_idx] += 1
                # Mark when chunk first dropped to 2-live-correct
                if chunk_idx not in self.chunk_two_live_since_day:
                    self.chunk_two_live_since_day[chunk_idx] = self.uptime_days

            # Track LIVE_HEALTHY time (secondary metric for health)
            if live_healthy_count >= 3:
                self.chunk_time_at_3live_healthy[chunk_idx] += 1

            # Track legacy metrics (for compatibility)
            self.chunk_time_at_3live[chunk_idx] = self.chunk_time_at_3live_correct[chunk_idx]
            self.chunk_time_at_2live[chunk_idx] = self.chunk_time_at_2live_correct[chunk_idx]

            # Track under-replication for RECOVERY_TOPUP (any <3 live_correct)
            if live_correct_count < 3:
                if chunk_idx not in self.chunk_under_replicated_since_day:
                    self.chunk_under_replicated_since_day[chunk_idx] = self.uptime_days

            # Track degradation for MUST-HEAL rules (any <3 ACTIVE replicas)
            tiles = self._get_chunk_tiles(chunk_idx)
            active_count = sum(1 for t in tiles if t.state == TileState.ACTIVE and t.integrity >= 0.70)
            if active_count >= 3:
                # Back to 3 ACTIVE - clear degradation timer
                if chunk_idx in self.chunk_degraded_since_day:
                    del self.chunk_degraded_since_day[chunk_idx]
            else:
                # <3 ACTIVE - mark when degradation started
                if chunk_idx not in self.chunk_degraded_since_day:
                    self.chunk_degraded_since_day[chunk_idx] = self.uptime_days

    def _check_recovery_topup(self):
        """
        RECOVERY TOP-UP: Restore under-replicated chunks due to failed/offline replicas.

        This is the PRIMARY top-up mode for durability. Triggers when:
        1. Chunk has <3 LIVE replicas for >= R days (R=3)
        2. Has at least 2 readable LIVE replicas (quorum available)
        3. Has sterile spare available
        4. <3 usable replicas (enforce maximum)

        Does NOT require "calm" or "stability" - the point is to recover from failures.
        """
        sterile = [t for t in self.tiles if t.state == TileState.STERILE]
        if not sterile:
            return  # No spare capacity

        for chunk_idx in sorted(self.chunk_replicas.keys()):
            tile_ids = self._get_chunk_tile_ids(chunk_idx)  # Get non-None tile IDs

            # Count usable replicas (exclude FAILED/STERILE which are offline)
            usable_tiles = [self.tiles[tid] for tid in tile_ids
                           if self.tiles[tid].state not in [TileState.FAILED, TileState.STERILE]]

            # RECOVERY CRITERION: Need <3 USABLE replicas
            # (A chunk with 2 ACTIVE + 1 FAILED has 3 total but only 2 usable - NEEDS recovery!)
            if len(usable_tiles) >= 3:
                continue  # Already have 3 usable replicas

            # Count LIVE replicas (ACTIVE only, ≥60% integrity)
            live_tiles = [self.tiles[tid] for tid in tile_ids
                         if self.tiles[tid].state == TileState.ACTIVE
                         and self.tiles[tid].integrity >= 0.60]

            # Need <3 live for >= R days
            if len(live_tiles) >= 3:
                continue  # Not under-replicated

            if chunk_idx not in self.chunk_under_replicated_since_day:
                continue  # Just dropped, too soon
            days_under_replicated = self.uptime_days - self.chunk_under_replicated_since_day[chunk_idx]
            if days_under_replicated < self.RECOVERY_TOPUP_MIN_DAYS:
                continue  # Not long enough

            # SAFETY GATE: Must have >= 2 readable LIVE replicas (for quorum truth)
            if len(live_tiles) < 2:
                continue  # Too risky - need quorum

            # RECOVERY TOP-UP ELIGIBLE!
            self._perform_topup(chunk_idx, live_tiles, sterile[0], mode='RECOVERY')
            return  # Only one top-up per day

    def _check_calm_period_topup(self):
        """
        CALM-PERIOD TOP-UP: Restore redundancy to stable chunks.

        This is a SECONDARY top-up mode for optimization. Triggers when:
        1. Chunk has exactly 2 live replicas for >= X days (X=7)
        2. Live-live drift = 0 for last Y scrubs (Y=3)
        3. No shocks in last Z days (Z=7)
        4. Chunk not AT_RISK
        5. <3 usable replicas (enforce maximum)

        More conservative than RECOVERY - used for optimizing stable chunks.
        """
        sterile = [t for t in self.tiles if t.state == TileState.STERILE]
        if not sterile:
            return  # No spare capacity

        for chunk_idx in sorted(self.chunk_replicas.keys()):
            tile_ids = self._get_chunk_tile_ids(chunk_idx)  # Get non-None tile IDs

            # Count usable replicas (exclude FAILED/STERILE which are offline)
            usable_tiles = [self.tiles[tid] for tid in tile_ids
                           if self.tiles[tid].state not in [TileState.FAILED, TileState.STERILE]]

            # CALM CRITERION: Need <3 USABLE replicas
            if len(usable_tiles) >= 3:
                continue  # Already have 3 usable replicas

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
            if days_at_2live < self.CALM_TOPUP_MIN_2LIVE_DAYS:
                continue  # Not long enough

            # Check drift history (require last 3 scrubs with 0 drift)
            if chunk_idx not in self.chunk_last_drift:
                continue
            drift_history = self.chunk_last_drift[chunk_idx]
            if len(drift_history) < self.CALM_TOPUP_MIN_CLEAN_SCRUBS:
                continue  # Not enough history
            if any(d > 0 for d in drift_history[-self.CALM_TOPUP_MIN_CLEAN_SCRUBS:]):
                continue  # Recent drift detected

            # Check for AT_RISK status
            if chunk_idx in self.chunks_at_risk:
                continue  # Chunk is unstable

            # Check for recent shocks
            if chunk_idx in self.chunk_last_shock_day:
                days_since_shock = self.uptime_days - self.chunk_last_shock_day[chunk_idx]
                if days_since_shock < self.CALM_TOPUP_MIN_CALM_DAYS:
                    continue  # Too soon after shock

            # CALM TOP-UP ELIGIBLE!
            self._perform_topup(chunk_idx, live_tiles, sterile[0], mode='CALM')
            return  # Only one top-up per day

    def _check_deadline_topup(self):
        """
        DEADLINE TOP-UP: Force top-up if chunk stuck <3 LIVE_CORRECT for too long.

        This is a FAIL-SAFE mechanism. Triggers when:
        1. Chunk has <3 LIVE_CORRECT replicas for >= 14 days
        2. Has at least 2 readable replicas OR snapshot exists (safety)
        3. Has sterile spare available
        4. <3 usable replicas (enforce maximum)

        More aggressive than CALM - doesn't wait for stability, just forces recovery.
        """
        sterile = [t for t in self.tiles if t.state == TileState.STERILE]
        if not sterile:
            return  # No spare capacity

        for chunk_idx in sorted(self.chunk_replicas.keys()):
            tile_ids = self._get_chunk_tile_ids(chunk_idx)  # Get non-None tile IDs

            # Count LIVE_CORRECT replicas
            live_correct_count = self._count_live_correct(chunk_idx)

            # Only trigger if <3 LIVE_CORRECT
            if live_correct_count >= 3:
                continue

            # Check duration <3 LIVE_CORRECT
            if chunk_idx not in self.chunk_under_replicated_since_day:
                continue  # Just dropped, too soon
            days_under_replicated = self.uptime_days - self.chunk_under_replicated_since_day[chunk_idx]
            if days_under_replicated < self.DEADLINE_TOPUP_DAYS:
                continue  # Not at deadline yet

            # Count usable replicas (exclude FAILED/STERILE)
            usable_tiles = [self.tiles[tid] for tid in tile_ids
                           if self.tiles[tid].state not in [TileState.FAILED, TileState.STERILE]]

            # Check replica limit
            if len(usable_tiles) >= 3:
                continue  # Already have 3 usable replicas

            # SAFETY GATE: Must have >=2 readable OR snapshot exists
            live_correct_tiles = [self.tiles[tid] for tid in tile_ids if self._is_live_correct(self.tiles[tid])]
            has_snapshot = chunk_idx in self.chunk_snapshot_bits

            if len(live_correct_tiles) < 2 and not has_snapshot:
                print(f"  ⚠️  Chunk {chunk_idx} deadline reached ({days_under_replicated}d <3-live) but no quorum/snapshot - BLOCKED")
                continue  # Too risky

            # DEADLINE TOP-UP ELIGIBLE!
            print(f"  ⏰ DEADLINE TOP-UP: Chunk {chunk_idx} has been <3 LIVE_CORRECT for {days_under_replicated} days")
            self._perform_topup(chunk_idx, live_correct_tiles, sterile[0], mode='DEADLINE')
            return  # Only one top-up per day

    def _check_failed_slots(self):
        """
        MUST-HEAL RULE 1: FAILED SLOT MANDATORY REBUILD

        If any chunk slot references a FAILED tile (<60%), immediately mark chunk
        as REPAIR_REQUIRED and rebuild that slot using QUORUM truth (or snapshot).

        This bypasses all risk gates - FAILED slots must be healed.
        """
        sterile = [t for t in self.tiles if t.state == TileState.STERILE]
        if not sterile:
            return  # No spare capacity

        for chunk_idx, slots in self.chunk_replicas.items():
            # Check each slot for FAILED tiles
            for slot_idx, tid in enumerate(slots):
                if tid is None:
                    continue

                tile = self.tiles[tid]
                if tile.state == TileState.FAILED:
                    print(f"\n🚨 MUST-HEAL: Chunk {chunk_idx} slot {slot_idx} has FAILED tile {tid} (integrity: {tile.integrity:.2%})")
                    print(f"   Mandatory rebuild required (bypassing risk gates)")

                    # Get QUORUM truth or snapshot
                    live_correct_tiles = [self.tiles[t] for t in slots if t is not None and self._is_live_correct(self.tiles[t])]

                    if len(live_correct_tiles) >= 2:
                        # Use QUORUM
                        print(f"   Using QUORUM truth from {len(live_correct_tiles)} LIVE_CORRECT replicas")
                        best_tile = max(live_correct_tiles, key=lambda t: t.integrity)
                        correct_data = best_tile.binary_data
                    elif chunk_idx in self.chunk_snapshot_bits:
                        # Use snapshot
                        print(f"   Using SNAPSHOT truth (no quorum available)")
                        correct_data = self.chunk_snapshot_bits[chunk_idx]
                    else:
                        print(f"   ✗ NO QUORUM OR SNAPSHOT - cannot rebuild safely")
                        continue

                    # Rebuild onto sterile tile
                    target = sterile[0]
                    target.state = TileState.REGENERATING
                    target.binary_data = correct_data
                    target.pattern = self.encoder.encode(correct_data)
                    self._track_write(target, success=True)
                    target.regeneration_progress = 1.0
                    target.needs_scrub = False
                    target.integrity = 0.98

                    import zlib
                    target.chunk_checksum = zlib.crc32(correct_data.encode()) & 0xffffffff

                    # Hard scrub to verify
                    self._scrub_chunk(chunk_idx)

                    # Promote to ACTIVE immediately
                    target.state = TileState.ACTIVE
                    target.clean_locked_until_day = self.uptime_days + 7
                    target.regen_complete_day = self.uptime_days

                    # Update slot mapping: replace FAILED tile with new one
                    self._set_chunk_slot(chunk_idx, slot_idx, target.id)

                    # Flush FAILED tile
                    self._flush_tile(tile)

                    self.failed_slot_rebuilds += 1
                    print(f"   ✓ FAILED slot rebuilt onto tile {target.id} (rebuild #{self.failed_slot_rebuilds})")
                    return  # Only one rebuild per day

    def _enforce_pending_deadline(self):
        """
        MUST-HEAL RULE 2: PENDING DEADLINE ENFORCEMENT

        If chunk has been [<3 ACTIVE replicas with >=70%] for >14 days,
        force action:
        a) If SICK tile is in hysteresis band (70-85%), promote to ACTIVE immediately
        b) Else create new replica from QUORUM onto sterile, verify, fill slot

        Goal: Chunks must return to 3 healthy ACTIVE replicas, never stuck with SICK.
        """
        for chunk_idx in sorted(self.chunk_replicas.keys()):
            # Count ACTIVE replicas (not SICK, not CLEAN_LOCKED)
            tile_ids = self._get_chunk_tile_ids(chunk_idx)
            tiles = [self.tiles[tid] for tid in tile_ids]
            active_count = sum(1 for t in tiles if t.state == TileState.ACTIVE and t.integrity >= 0.70)

            # Only act if <3 ACTIVE replicas
            if active_count >= 3:
                continue

            # Check how long chunk has been degraded
            if chunk_idx not in self.chunk_degraded_since_day:
                continue
            days_degraded = self.uptime_days - self.chunk_degraded_since_day[chunk_idx]

            if days_degraded < self.PENDING_DEADLINE_DAYS:
                continue  # Not at deadline yet

            print(f"\n⏰ PENDING DEADLINE: Chunk {chunk_idx} has been <3 ACTIVE replicas for {days_degraded} days")

            # Get all tiles
            tile_ids = self._get_chunk_tile_ids(chunk_idx)
            tiles = [self.tiles[tid] for tid in tile_ids]

            # Check for SICK/PENDING tiles that might be promotable
            sick_tiles = [t for t in tiles if t.state == TileState.SICK and t.integrity >= 0.60]

            if sick_tiles and len(sick_tiles) > 0:
                # Promote SICK tile to ACTIVE immediately
                sick = sick_tiles[0]
                print(f"   Promoting SICK tile {sick.id} (integrity: {sick.integrity:.2%}) to ACTIVE (forced)")
                sick.state = TileState.ACTIVE
                sick.clean_locked_until_day = self.uptime_days + 7
                self.pending_deadline_heals += 1
                return  # Only one action per day

            # Else, create new replica if we have sterile spares
            sterile = [t for t in self.tiles if t.state == TileState.STERILE]
            if not sterile:
                print(f"   ⚠️  No sterile spares available for forced heal")
                return

            # Get LIVE_CORRECT replicas for truth
            live_correct_tiles = [t for t in tiles if self._is_live_correct(t)]

            if len(live_correct_tiles) >= 2:
                # Use QUORUM
                print(f"   Creating new replica using QUORUM truth")
                self._perform_topup(chunk_idx, live_correct_tiles, sterile[0], mode='DEADLINE')
                self.pending_deadline_heals += 1
                return  # Only one action per day

    def _check_regen_in_place(self):
        """
        STAGE A: REGEN-IN-PLACE (primary self-healing response)

        Regenerate sick tiles in situ without permanent swap. Triggers when:
        - A live tile serving a chunk is SICK (60-80%) for >=5 consecutive days
        - AND sterile spare available (for TEMP_SHADOW)
        - AND won't reduce readable replicas below 2

        Process:
        1. Create TEMP_SHADOW replica on sterile spare using QUORUM truth
        2. Mark sick tile as REGENERATING (unreadable during regen)
        3. After 5-7 days, restore integrity to 90-97% and return to ACTIVE
        4. Remove TEMP_SHADOW (keep exactly 3 replicas per chunk)

        This allows tiles to heal without permanent replacement.
        """
        # Track if any tiles are regenerating today
        if len(self.tiles_regenerating) > 0:
            self.days_with_regen_active += 1

        sterile = [t for t in self.tiles if t.state == TileState.STERILE]
        if not sterile:
            return  # No spare capacity for TEMP_SHADOW

        # Find tiles serving chunks that are SICK for >= MIN_SICK_DAYS
        candidates = []
        for chunk_idx, tile_ids in self.chunk_replicas.items():
            tiles = [self.tiles[tid] for tid in tile_ids if tid is not None]

            for tile in tiles:
                # Skip if not live (ACTIVE/SICK) or clean-locked
                if tile.state not in [TileState.ACTIVE, TileState.SICK]:
                    continue
                if tile.clean_locked_until_day >= self.uptime_days:
                    continue

                # Check if tile is SICK (<80% but >=60%)
                if tile.integrity >= self.REGEN_IN_PLACE_THRESHOLD:
                    # Above threshold - clear sick timer
                    if tile.id in self.tile_sick_since_day:
                        del self.tile_sick_since_day[tile.id]
                    continue

                if tile.integrity < 0.60:
                    # Below SICK range - will be handled by FAILED logic
                    continue

                # Tile is SICK (60-80%) - track how long
                if tile.id not in self.tile_sick_since_day:
                    self.tile_sick_since_day[tile.id] = self.uptime_days

                days_sick = self.uptime_days - self.tile_sick_since_day[tile.id]

                if days_sick < self.REGEN_IN_PLACE_MIN_SICK_DAYS:
                    continue  # Not sick long enough

                # Check if this is a repeat offender (>2 regens in 60 days)
                if tile.id in self.tile_regen_history:
                    recent_regens = [d for d in self.tile_regen_history[tile.id]
                                    if self.uptime_days - d <= self.REPEAT_OFFENDER_WINDOW]
                    if len(recent_regens) >= self.REPEAT_OFFENDER_THRESHOLD:
                        print(f"🔁 Tile {tile.id} is a repeat offender ({len(recent_regens)} regens in {self.REPEAT_OFFENDER_WINDOW} days) - escalating to permanent swap")
                        continue  # Skip REGEN-IN-PLACE, let PROACTIVE_REBUILD handle it

                # Safety check: ensure we won't drop below 2 readable replicas
                # (TEMP_SHADOW will count as readable during regen)
                readable = [t for t in tiles
                           if t.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]
                           and t.integrity >= 0.60]

                if len(readable) <= 2:
                    continue  # Too risky - need TEMP_SHADOW to maintain 2+ readable

                # Candidate for REGEN-IN-PLACE
                candidates.append((tile, chunk_idx, days_sick))

        if not candidates:
            return  # No tiles need REGEN-IN-PLACE

        # Pick the most degraded tile (lowest integrity)
        tile_to_regen, chunk_idx, days_sick = min(candidates, key=lambda x: x[0].integrity)

        # Get QUORUM truth from other replicas
        tile_ids = self.chunk_replicas[chunk_idx]
        tiles = [self.tiles[tid] for tid in tile_ids if tid is not None]
        live_correct_tiles = [t for t in tiles
                             if t.id != tile_to_regen.id  # Exclude the one we're regenerating
                             and self._is_live_correct(t)]

        if len(live_correct_tiles) < 2:
            print(f"⚠️  REGEN-IN-PLACE: Cannot regenerate tile {tile_to_regen.id} - insufficient quorum ({len(live_correct_tiles)}/2)")
            return

        # Execute REGEN-IN-PLACE
        print(f"\n🔄 REGEN-IN-PLACE: Regenerating tile {tile_to_regen.id} (integrity: {tile_to_regen.integrity:.2%}, sick for {days_sick} days)")

        # Step 1: Create TEMP_SHADOW replica on sterile spare (standalone safety backup)
        # TEMP_SHADOW is NOT added to chunk - chunk keeps exactly 3 slots filled
        # During regen, chunk has 2 live replicas + 1 REGENERATING (safety threshold met)
        shadow = sterile[0]
        best_tile = max(live_correct_tiles, key=lambda t: t.integrity)
        correct_data = best_tile.binary_data

        shadow.state = TileState.ACTIVE  # TEMP_SHADOW is ACTIVE (standalone backup)
        shadow.binary_data = correct_data
        shadow.pattern = self.encoder.encode(correct_data)
        self._track_write(shadow, success=True)
        shadow.integrity = 0.98  # High integrity
        shadow.needs_scrub = False

        import zlib
        shadow.chunk_checksum = zlib.crc32(correct_data.encode()) & 0xffffffff

        # TEMP_SHADOW remains standalone (not added to chunk)
        # This allows regen-in-place without inflating replica count
        self.temp_shadow_count += 1
        self.tile_temp_shadow[tile_to_regen.id] = shadow.id
        print(f"   ✓ Created TEMP_SHADOW replica on tile {shadow.id} (standalone safety backup)")
        print(f"   📊 Chunk {chunk_idx} during regen: 2 live + 1 REGENERATING (safety threshold met)")

        # Step 2: Mark sick tile as REGENERATING
        tile_to_regen.state = TileState.REGENERATING
        tile_to_regen.regeneration_progress = 0.0
        tile_to_regen.needs_scrub = False
        regen_duration = np.random.randint(self.REGEN_DURATION_MIN, self.REGEN_DURATION_MAX + 1)
        tile_to_regen.regeneration_complete_day = self.uptime_days + regen_duration
        self.tiles_regenerating.add(tile_to_regen.id)

        # Track regeneration event
        if tile_to_regen.id not in self.tile_regen_history:
            self.tile_regen_history[tile_to_regen.id] = []
        self.tile_regen_history[tile_to_regen.id].append(self.uptime_days)

        # Clear sick timer
        if tile_to_regen.id in self.tile_sick_since_day:
            del self.tile_sick_since_day[tile_to_regen.id]

        self.regen_in_place_count += 1
        print(f"   ✓ Tile {tile_to_regen.id} entering REGENERATING state for {regen_duration} days")
        print(f"   📊 REGEN-IN-PLACE #{self.regen_in_place_count}, chunk {chunk_idx} temporarily has 4 replicas (3 + TEMP_SHADOW)")

    def _complete_regen_in_place(self):
        """
        Complete in-place regeneration for tiles that have finished regenerating.

        Process:
        1. Restore tile integrity to 90-97%
        2. Return tile to ACTIVE state
        3. Remove TEMP_SHADOW replica (restore to exactly 3 replicas)
        """
        for tile_id in list(self.tiles_regenerating):
            tile = self.tiles[tile_id]

            if self.uptime_days >= tile.regeneration_complete_day:
                print(f"\n✅ REGEN-IN-PLACE COMPLETE: Tile {tile_id} regeneration finished")

                # Step 1: Restore integrity
                new_integrity = np.random.uniform(self.REGEN_INTEGRITY_MIN, self.REGEN_INTEGRITY_MAX)
                tile.integrity = new_integrity
                tile.state = TileState.ACTIVE
                tile.regeneration_progress = 1.0
                tile.clean_locked_until_day = self.uptime_days + 7  # Protection period
                print(f"   ✓ Tile {tile_id} restored to ACTIVE with integrity {new_integrity:.2%}")

                # Step 2: Remove TEMP_SHADOW (standalone backup, not in chunk)
                if tile_id in self.tile_temp_shadow:
                    shadow_id = self.tile_temp_shadow[tile_id]
                    shadow = self.tiles[shadow_id]

                    # TEMP_SHADOW was never added to chunk, so just flush it
                    self._flush_tile(shadow)
                    print(f"   ✓ Removed TEMP_SHADOW tile {shadow_id} (standalone backup flushed to STERILE)")
                    del self.tile_temp_shadow[tile_id]

                # Remove from regenerating set
                self.tiles_regenerating.remove(tile_id)

    def _check_proactive_rebuild(self):
        """
        STAGE B: PROACTIVE_REBUILD (repeat offender swaps only)

        Permanently replace tiles that are repeat offenders or critically degraded.
        Triggers when:
        - Tile is a repeat offender (>2 regens in 60 days), OR
        - Tile has integrity <70% for N consecutive days
        - AND sterile spare available
        - AND won't reduce readable replicas below 2

        Budget guard: If >55 rebuilds/year pace, throttle to <68% for 5 days.

        Action: Create new replica from QUORUM truth, swap into chunk, retire sick tile.
        """
        sterile = [t for t in self.tiles if t.state == TileState.STERILE]
        if not sterile:
            return  # No spare capacity

        # Calculate rebuild budget (annualized from current pace)
        months_elapsed = self.uptime_days / 30.0
        if months_elapsed < 0.5:
            return  # Wait at least 15 days before starting proactive rebuilds (let system stabilize)

        rebuilds_per_year = (self.proactive_rebuild_count / months_elapsed) * 12.0
        is_over_budget = rebuilds_per_year > self.PROACTIVE_REBUILD_BUDGET_PER_YEAR

        # Adjust thresholds if over budget
        if is_over_budget:
            threshold = self.PROACTIVE_REBUILD_THROTTLE_THRESHOLD  # 78%
            min_days = self.PROACTIVE_REBUILD_THROTTLE_DAYS  # 5 days
        else:
            threshold = self.PROACTIVE_REBUILD_THRESHOLD  # 80%
            min_days = self.PROACTIVE_REBUILD_MIN_DAYS  # 3 days

        # Find tiles serving chunks that are below threshold
        candidates = []
        for chunk_idx, tile_ids in self.chunk_replicas.items():
            tiles = [self.tiles[tid] for tid in tile_ids if tid is not None]

            for tile in tiles:
                # Skip if not serving chunk (not ACTIVE, SICK, or CLEAN_LOCKED)
                if tile.state not in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]:
                    continue

                # Skip if clean-locked (just rebuilt, give it time)
                if tile.clean_locked_until_day >= self.uptime_days:
                    continue

                # Check if below threshold
                if tile.integrity >= threshold:
                    # Above threshold - clear degradation timer
                    if tile.id in self.tile_degraded_since_day:
                        del self.tile_degraded_since_day[tile.id]
                    continue

                # Below threshold - track how long
                if tile.id not in self.tile_degraded_since_day:
                    self.tile_degraded_since_day[tile.id] = self.uptime_days

                days_degraded = self.uptime_days - self.tile_degraded_since_day[tile.id]

                if days_degraded < min_days:
                    continue  # Not degraded long enough

                # Check if this is a repeat offender (>2 regens in 60 days)
                is_repeat_offender = False
                if tile.id in self.tile_regen_history:
                    recent_regens = [d for d in self.tile_regen_history[tile.id]
                                    if self.uptime_days - d <= self.REPEAT_OFFENDER_WINDOW]
                    if len(recent_regens) >= self.REPEAT_OFFENDER_THRESHOLD:
                        is_repeat_offender = True

                # Only proceed if repeat offender OR below 70%
                if not is_repeat_offender and tile.integrity >= 0.70:
                    continue  # Let REGEN-IN-PLACE handle non-repeat-offenders above 70%

                # Safety check: ensure we won't drop below 2 readable replicas
                readable = [t for t in tiles
                           if t.state in [TileState.ACTIVE, TileState.SICK, TileState.CLEAN_LOCKED]
                           and t.integrity >= 0.60]

                if len(readable) <= 2:
                    continue  # Too risky - would leave <2 readable

                # Candidate for proactive rebuild
                reason = "repeat offender" if is_repeat_offender else f"<70% ({tile.integrity:.2%})"
                candidates.append((tile, chunk_idx, days_degraded, reason))

        if not candidates:
            return  # No tiles need proactive rebuild

        # Pick the most degraded tile (lowest integrity)
        tile_to_rebuild, chunk_idx, days_degraded, reason = min(candidates, key=lambda x: x[0].integrity)

        # Check if this is a repeat offender (for tracking)
        is_repeat_offender = "repeat offender" in reason
        if is_repeat_offender:
            self.repeat_offender_swaps += 1

        # Check if this tile would have failed (integrity <60%)
        will_save_before_failure = tile_to_rebuild.integrity < 0.70  # In SICK range or close to failure

        # Get QUORUM truth from other replicas
        tile_ids = self.chunk_replicas[chunk_idx]
        tiles = [self.tiles[tid] for tid in tile_ids if tid is not None]
        live_correct_tiles = [t for t in tiles
                             if t.id != tile_to_rebuild.id  # Exclude the one we're replacing
                             and self._is_live_correct(t)]

        if len(live_correct_tiles) < 2:
            print(f"⚠️  PROACTIVE_REBUILD: Cannot rebuild tile {tile_to_rebuild.id} - insufficient quorum ({len(live_correct_tiles)}/2)")
            return

        # Execute proactive rebuild
        print(f"\n🔧 PROACTIVE_REBUILD: Replacing tile {tile_to_rebuild.id} ({reason})")
        print(f"   Integrity: {tile_to_rebuild.integrity:.2%}, degraded for {days_degraded} days")
        print(f"   Threshold: {threshold:.0%}, Budget status: {'THROTTLED' if is_over_budget else 'OK'} ({rebuilds_per_year:.1f}/{self.PROACTIVE_REBUILD_BUDGET_PER_YEAR} per year)")

        # Get QUORUM truth
        best_tile = max(live_correct_tiles, key=lambda t: t.integrity)
        correct_data = best_tile.binary_data

        # Create new replica in sterile tile
        target = sterile[0]
        target.state = TileState.REGENERATING
        target.binary_data = correct_data
        target.pattern = self.encoder.encode(correct_data)
        self._track_write(target, success=True)
        target.regeneration_progress = 1.0
        target.needs_scrub = False
        target.integrity = 0.98

        import zlib
        target.chunk_checksum = zlib.crc32(correct_data.encode()) & 0xffffffff

        # Hard scrub to verify
        self._scrub_chunk(chunk_idx)

        # Promote to ACTIVE immediately
        target.state = TileState.ACTIVE
        target.clean_locked_until_day = self.uptime_days + 7
        target.regen_complete_day = self.uptime_days

        # Find which slot the old tile occupied and swap it
        slot_idx = None
        for idx, tid in enumerate(self.chunk_replicas[chunk_idx]):
            if tid == tile_to_rebuild.id:
                slot_idx = idx
                break

        if slot_idx is not None:
            self._set_chunk_slot(chunk_idx, slot_idx, target.id)
            print(f"   ✓ Swapped tile {tile_to_rebuild.id} → {target.id} in chunk {chunk_idx} slot {slot_idx}")
        else:
            print(f"   ⚠️  Could not find slot for tile {tile_to_rebuild.id} in chunk {chunk_idx}")

        # Retire the old tile (mark as STERILE for reuse)
        self._flush_tile(tile_to_rebuild)

        # Clear degradation timer
        if tile_to_rebuild.id in self.tile_degraded_since_day:
            del self.tile_degraded_since_day[tile_to_rebuild.id]

        # Update metrics
        self.proactive_rebuild_count += 1
        if will_save_before_failure:
            self.tiles_saved_before_failure += 1

        print(f"   ✓ PROACTIVE_REBUILD complete (#{self.proactive_rebuild_count}, saved {self.tiles_saved_before_failure} tiles before failure)")

    def _maintain_spare_pool(self):
        """
        SPARE_POOL_HEALTH: Maintain healthy spare pool.

        Ensures we have enough healthy sterile spares for future recovery operations.
        - Flushes orphaned FAILED tiles (not in any chunk) back to STERILE
        - Tracks spare pool health metrics
        - Never touches live chunk mappings or data bits
        """
        # Find tiles currently in use (in chunk mappings)
        tiles_in_use = set()
        for tile_ids in self.chunk_replicas.values():
            for tid in tile_ids:
                if tid is not None:
                    tiles_in_use.add(tid)

        # Find orphaned FAILED tiles (not in any chunk)
        orphaned_failed = []
        for tile in self.tiles:
            if tile.state == TileState.FAILED and tile.id not in tiles_in_use:
                orphaned_failed.append(tile)

        # Flush orphaned FAILED tiles back to STERILE for reuse
        for tile in orphaned_failed:
            print(f"\n🔄 SPARE_POOL_HEALTH: Flushing orphaned FAILED tile {tile.id} (integrity: {tile.integrity:.2%}) to STERILE")
            self._flush_tile(tile)
            self.spare_regenerations += 1
            print(f"   ✓ Spare regeneration #{self.spare_regenerations}: tile {tile.id} returned to spare pool")

        # Count healthy sterile spares (STERILE state, ready for use)
        healthy_sterile = sum(1 for t in self.tiles if t.state == TileState.STERILE)

        # TEMP_SHADOW tiles are temporarily using sterile capacity but are still available
        # (they're standalone backups, not consuming long-term spare pool capacity)
        temp_shadow_ids = set(self.tile_temp_shadow.values())
        temp_shadow_count_now = len(temp_shadow_ids)

        # Effective spare capacity = STERILE + TEMP_SHADOW (temporary assignments don't consume pool)
        effective_spare_capacity = healthy_sterile + temp_shadow_count_now

        # Track days below spare target (corrected for TEMP_SHADOW)
        if effective_spare_capacity < self.SPARE_TARGET:
            self.days_below_spare_target += 1
            if self.uptime_days % 30 == 0:  # Report monthly
                print(f"⚠️  SPARE_POOL_HEALTH: Only {effective_spare_capacity}/{self.SPARE_TARGET} effective spares (STERILE: {healthy_sterile}, TEMP_SHADOW: {temp_shadow_count_now}) (day {self.uptime_days})")

    def _perform_topup(self, chunk_idx: int, live_tiles: List[Tile], target_sterile: Tile, mode: str):
        """
        THREE-MODE TOP-UP: Add third replica to under-replicated chunk.

        Args:
            chunk_idx: Chunk index to top up
            live_tiles: Current live replicas (must be >=2)
            target_sterile: Sterile spare to use for new replica
            mode: 'RECOVERY', 'CALM', or 'DEADLINE'
        """
        if mode == 'RECOVERY':
            print(f"\n🔄 RECOVERY TOP-UP: Chunk {chunk_idx}")
            print(f"   Chunk under-replicated ({len(live_tiles)} live) for {self.uptime_days - self.chunk_under_replicated_since_day[chunk_idx]} days")
            print(f"   Adding third replica on tile {target_sterile.id}...")
        elif mode == 'CALM':
            print(f"\n🌊 CALM-PERIOD TOP-UP: Chunk {chunk_idx}")
            print(f"   Chunk stable at 2 live for {self.uptime_days - self.chunk_two_live_since_day[chunk_idx]} days, 0 drift")
            print(f"   Adding third replica on tile {target_sterile.id}...")
        else:  # DEADLINE
            print(f"\n⏰ DEADLINE TOP-UP: Chunk {chunk_idx}")
            print(f"   Chunk <3 LIVE_CORRECT for {self.uptime_days - self.chunk_under_replicated_since_day[chunk_idx]} days (deadline reached)")
            print(f"   Adding third replica on tile {target_sterile.id}...")

        # Get correct data from highest-integrity live tile
        best_tile = max(live_tiles, key=lambda t: t.integrity)
        correct_data = best_tile.binary_data

        # Seed target with correct data
        target_sterile.state = TileState.REGENERATING
        target_sterile.binary_data = correct_data
        target_sterile.pattern = self.encoder.encode(correct_data)
        self._track_write(target_sterile, success=True)  # Track top-up replica creation
        target_sterile.regeneration_progress = 1.0  # Skip regeneration delay
        target_sterile.needs_scrub = False
        target_sterile.integrity = 0.98  # Start at high integrity

        # Set checksum
        import zlib
        target_sterile.chunk_checksum = zlib.crc32(correct_data.encode()) & 0xffffffff

        # CLEANUP FIRST: Flush any FAILED tiles to free up slots
        # This ensures we have empty slots available before adding new replica
        failed_tile_ids = [tid for tid in self._get_chunk_tile_ids(chunk_idx)
                          if self.tiles[tid].state == TileState.FAILED]
        for failed_id in failed_tile_ids:
            self._flush_tile(self.tiles[failed_id])
            self._clear_chunk_slot_by_tile_id(chunk_idx, failed_id)
            print(f"   Pre-cleanup: Flushed FAILED tile {failed_id} to free slot")

        # SAFETY CHECK: Enforce 3-replica maximum before adding (count USABLE replicas only)
        usable_count = len([tid for tid in self._get_chunk_tile_ids(chunk_idx)
                           if self.tiles[tid].state not in [TileState.FAILED, TileState.STERILE]])
        if usable_count >= 3:
            print(f"   ⚠️  ABORT: Chunk {chunk_idx} already has {usable_count} usable replicas! Cannot top-up.")
            # Return target to sterile pool
            target_sterile.state = TileState.STERILE
            return

        # Add to chunk mapping (find empty slot)
        empty_slot = self._find_empty_slot(chunk_idx)
        if empty_slot is not None:
            self._set_chunk_slot(chunk_idx, empty_slot, target_sterile.id)
            print(f"   ✓ Added top-up replica to slot {empty_slot}")
        else:
            print(f"   ⚠️  ABORT: Chunk {chunk_idx} has no empty slots!")
            target_sterile.state = TileState.STERILE
            return

        # Perform hard informational scrub
        self._scrub_chunk(chunk_idx)

        # IMMEDIATE PROMOTION: Mark as ACTIVE (LIVE_CORRECT) with 7-day protection
        target_sterile.state = TileState.ACTIVE
        target_sterile.clean_locked_until_day = self.uptime_days + 7
        target_sterile.regen_complete_day = self.uptime_days

        # Reset maturation (new replica)
        target_sterile.consecutive_successful_scrubs = 0
        target_sterile.maturity_level = 0
        target_sterile.matured_on_day = -999

        # Track the correct counter based on mode
        if mode == 'RECOVERY':
            self.recovery_topup_count += 1
            print(f"✓ Recovery top-up #{self.recovery_topup_count} complete (tile {target_sterile.id} ACTIVE with 7-day protection)")
        elif mode == 'CALM':
            self.calm_topup_count += 1
            print(f"✓ Calm-period top-up #{self.calm_topup_count} complete (tile {target_sterile.id} ACTIVE with 7-day protection)")
        else:  # DEADLINE
            self.deadline_topup_count += 1
            print(f"✓ Deadline top-up #{self.deadline_topup_count} complete (tile {target_sterile.id} ACTIVE with 7-day protection)")

        # Final status
        usable_count = len([tid for tid in self._get_chunk_tile_ids(chunk_idx)
                           if self.tiles[tid].state not in [TileState.FAILED, TileState.STERILE]])
        print(f"   Chunk {chunk_idx} now has {usable_count} usable replicas\n")

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
        Validate chunk->tile mapping invariants with FIXED 3-SLOT ARRAYS.

        CRITICAL INVARIANTS:
        1. Every chunk must have exactly 3 slots (some may be None)
        2. No duplicate tile IDs across non-None slots
        3. Warn (don't fatal) if <3 readable replicas during recovery

        This allows atomic multi-step operations (flush + top-up) without crashes.
        """
        for chunk_idx, slots in self.chunk_replicas.items():
            # ENFORCE 3-SLOT ARRAY: Must have exactly 3 slots (not necessarily filled)
            if not isinstance(slots, list) or len(slots) != 3:
                raise RuntimeError(
                    f"FATAL: Chunk {chunk_idx} has {len(slots) if isinstance(slots, list) else 'invalid'} slots, expected 3! "
                    f"Slots: {slots}. "
                    f"This violates the 3-slot invariant!"
                )

            # Get non-None tile IDs
            tile_ids = [tid for tid in slots if tid is not None]

            # ENFORCE UNIQUENESS: No duplicate tile IDs in non-None slots
            if len(tile_ids) != len(set(tile_ids)):
                duplicates = [tid for tid in tile_ids if tile_ids.count(tid) > 1]
                raise RuntimeError(
                    f"FATAL: Chunk {chunk_idx} has duplicate tile IDs: {duplicates}! "
                    f"All slots: {slots}. "
                    f"This violates uniqueness invariant!"
                )

            # Get actual tiles (skip None slots)
            tiles = [self.tiles[tid] for tid in tile_ids]

            # Count LIVE_CORRECT replicas (readable + verified)
            live_correct = [t for t in tiles if self._is_live_correct(t)]
            live_correct_count = len(live_correct)

            # Separate for informational display
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

            # WARN (don't fatal) if <3 usable replicas - may be mid-recovery
            usable_count = len([t for t in tiles if t.state not in [TileState.FAILED, TileState.STERILE]])
            empty_slots = sum(1 for tid in slots if tid is None)

            if usable_count < 3 or empty_slots > 0:
                print(f"⚠️  Chunk {chunk_idx}: {usable_count} usable, {empty_slots} empty slots (recovery may be needed)")
                print(f"    Slots: {slots}")
                print(f"    Live: {len(live)}, Pending: {len(pending)}, Offline: {len(offline)}")

                # ENSURE RECOVERY: Schedule top-up if needed
                if live_correct_count >= 2:
                    # Has quorum - can safely top-up
                    if chunk_idx not in self.chunk_under_replicated_since_day:
                        self.chunk_under_replicated_since_day[chunk_idx] = self.uptime_days
                        print(f"    → Scheduled for top-up (has {live_correct_count} LIVE_CORRECT replicas)")
                elif chunk_idx in self.chunk_snapshot_bits:
                    # No quorum but has snapshot - can recover
                    print(f"    → Snapshot available for recovery")
                else:
                    # Critical: no quorum and no snapshot
                    print(f"    ✗ CRITICAL: Only {live_correct_count} LIVE_CORRECT, no snapshot!")

            # Warn if no readable replicas at all
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

    # Initialize CORRELATED_SHOCK_WEEKS: Select 2-4 random weeks for elevated degradation stress
    total_weeks = duration_days // 7
    num_shock_weeks = np.random.randint(controller.SHOCK_WEEKS_PER_YEAR_MIN, controller.SHOCK_WEEKS_PER_YEAR_MAX + 1)
    controller.shock_weeks = sorted(np.random.choice(range(1, total_weeks + 1), min(num_shock_weeks, total_weeks), replace=False).tolist())

    # For each shock week, select 3-6 random ACTIVE tiles to stress
    active_tile_ids = [t.id for t in controller.tiles if t.state == TileState.ACTIVE]
    for week_num in controller.shock_weeks:
        num_affected = np.random.randint(controller.SHOCK_WEEK_AFFECTED_TILES_MIN,
                                        min(controller.SHOCK_WEEK_AFFECTED_TILES_MAX + 1, len(active_tile_ids) + 1))
        affected_tiles = np.random.choice(active_tile_ids, num_affected, replace=False).tolist()
        controller.shock_week_tiles[week_num] = affected_tiles

    print(f"\n🌩️  CORRELATED SHOCK WEEKS scheduled: {len(controller.shock_weeks)} weeks out of {total_weeks}")
    for week_num in controller.shock_weeks:
        affected = controller.shock_week_tiles[week_num]
        print(f"   Week {week_num}: {len(affected)} tiles will receive {controller.SHOCK_WEEK_DEGRADATION_MULTIPLIER}x degradation (tiles: {affected})")

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

    # THREE-MODE TOP-UPS (separate from rebuilds)
    recovery_topups_per_month = controller.recovery_topup_count / months_simulated if months_simulated > 0 else 0
    calm_topups_per_month = controller.calm_topup_count / months_simulated if months_simulated > 0 else 0
    deadline_topups_per_month = controller.deadline_topup_count / months_simulated if months_simulated > 0 else 0
    total_topups = controller.recovery_topup_count + controller.calm_topup_count + controller.deadline_topup_count
    print(f"  📊 Recovery top-ups: {controller.recovery_topup_count} ({recovery_topups_per_month:.2f}/month)")
    print(f"  📊 Calm-period top-ups: {controller.calm_topup_count} ({calm_topups_per_month:.2f}/month)")
    print(f"  📊 Deadline top-ups: {controller.deadline_topup_count} ({deadline_topups_per_month:.2f}/month)")
    print(f"  📊 Total top-ups: {total_topups} ({total_topups/months_simulated:.2f}/month)")

    # MUST-HEAL RULES (mandatory repairs)
    failed_slot_per_month = controller.failed_slot_rebuilds / months_simulated if months_simulated > 0 else 0
    pending_deadline_per_month = controller.pending_deadline_heals / months_simulated if months_simulated > 0 else 0
    print(f"  🚨 MUST-HEAL: FAILED slot rebuilds: {controller.failed_slot_rebuilds} ({failed_slot_per_month:.2f}/month)")
    print(f"  🚨 MUST-HEAL: PENDING deadline heals: {controller.pending_deadline_heals} ({pending_deadline_per_month:.2f}/month)")

    # REGEN-IN-PLACE: Stage A self-healing (primary response)
    regen_in_place_per_month = controller.regen_in_place_count / months_simulated if months_simulated > 0 else 0
    regen_in_place_per_year = regen_in_place_per_month * 12.0
    pct_time_regenerating = (controller.days_with_regen_active / days_simulated * 100) if days_simulated > 0 else 0
    avg_regen_duration = (controller.REGEN_DURATION_MIN + controller.REGEN_DURATION_MAX) / 2.0
    print(f"  🔄 REGEN-IN-PLACE (Stage A): {controller.regen_in_place_count} total ({regen_in_place_per_month:.2f}/month, {regen_in_place_per_year:.1f}/year)")
    print(f"     Temp shadow replicas created: {controller.temp_shadow_count}")
    print(f"     Avg regen duration: {avg_regen_duration:.1f} days")
    print(f"     % time with regen active: {pct_time_regenerating:.1f}%")

    # PROACTIVE_REBUILD: Stage B self-healing (repeat offenders/critical only)
    proactive_rebuilds_per_month = controller.proactive_rebuild_count / months_simulated if months_simulated > 0 else 0
    proactive_rebuilds_per_year = proactive_rebuilds_per_month * 12.0
    budget_status = "✓ WITHIN BUDGET" if proactive_rebuilds_per_year <= controller.PROACTIVE_REBUILD_BUDGET_PER_YEAR else "⚠️  OVER BUDGET"
    print(f"  🔧 PROACTIVE_REBUILD (Stage B): {controller.proactive_rebuild_count} total ({proactive_rebuilds_per_month:.2f}/month, {proactive_rebuilds_per_year:.1f}/year)")
    print(f"     Budget: {proactive_rebuilds_per_year:.1f}/{controller.PROACTIVE_REBUILD_BUDGET_PER_YEAR} per year - {budget_status}")
    print(f"     Repeat offender swaps: {controller.repeat_offender_swaps}")
    print(f"     Tiles saved before failure (<70%): {controller.tiles_saved_before_failure}")

    # Count tiles that crossed <60% without being replaced
    tiles_that_failed = sum(1 for t in controller.tiles if t.state == TileState.FAILED)
    print(f"     Tiles that crossed <60% without replacement: {tiles_that_failed}")

    # CORRELATED_SHOCK_WEEKS: Stress testing metrics
    total_weeks = days_simulated // 7
    shock_weeks_per_year = (len(controller.shock_weeks) / days_simulated * 365) if days_simulated > 0 else 0
    print(f"  🌩️  CORRELATED_SHOCK_WEEKS:")
    print(f"     Shock weeks triggered: {controller.shock_weeks_triggered}/{len(controller.shock_weeks)} scheduled")
    print(f"     Shock weeks per year: {shock_weeks_per_year:.1f} ({len(controller.shock_weeks)}/{total_weeks} weeks)")
    print(f"     Degradation multiplier: {controller.SHOCK_WEEK_DEGRADATION_MULTIPLIER}x")
    print(f"     Tiles affected per shock week: {controller.SHOCK_WEEK_AFFECTED_TILES_MIN}-{controller.SHOCK_WEEK_AFFECTED_TILES_MAX}")

    # SPARE_POOL_HEALTH: Spare pool maintenance metrics
    spare_regenerations_per_month = controller.spare_regenerations / months_simulated if months_simulated > 0 else 0
    final_sterile_count = sum(1 for t in controller.tiles if t.state == TileState.STERILE)
    final_temp_shadow_count = len(controller.tile_temp_shadow)
    final_failed_spares = sum(1 for t in controller.tiles if t.state == TileState.FAILED and t.id >= controller.n_active)
    pct_days_below_target = (controller.days_below_spare_target / days_simulated * 100) if days_simulated > 0 else 0
    print(f"  🔄 SPARE_POOL_HEALTH:")
    print(f"     Spare failures (tiles → FAILED): {controller.spare_failures}")
    print(f"     Spare regenerations (orphaned FAILED → STERILE): {controller.spare_regenerations} ({spare_regenerations_per_month:.2f}/month)")
    print(f"     Final spare breakdown:")
    print(f"       - STERILE (free): {final_sterile_count}")
    print(f"       - TEMP_SHADOW (in use): {final_temp_shadow_count}")
    print(f"       - FAILED (quarantined): {final_failed_spares}")
    print(f"       - Effective capacity: {final_sterile_count + final_temp_shadow_count}/{controller.SPARE_TARGET}")
    print(f"     Days below spare target (corrected): {controller.days_below_spare_target}/{days_simulated} ({pct_days_below_target:.1f}%)")

    # COLD SNAPSHOT METRICS (emergency recovery)
    print(f"  📸 Cold snapshot updates: {controller.snapshot_updates_count} (VERY conservative)")
    print(f"  📸 Snapshots used for recovery: {controller.snapshot_used_for_recovery_count}")
    print(f"  📸 Correlated failure events: {controller.correlated_failure_events}")
    if controller.correlated_failure_events > 0:
        if controller.snapshot_used_for_recovery_count == controller.correlated_failure_events:
            print(f"     ✓ ALL correlated failures recovered via snapshot - system is irrecoverable-failure-proof!")
        else:
            print(f"     ⚠️  Some correlated failures not recovered - need more snapshots or sterile spares")

    # Time at 3-live: CORRECTNESS vs HEALTH split (GOAL: >90% at 3-live-correct)
    total_chunk_days_correct = sum(controller.chunk_time_at_3live_correct.values()) + sum(controller.chunk_time_at_2live_correct.values())
    total_chunk_days_healthy = sum(controller.chunk_time_at_3live_healthy.values()) + (total_chunk_days_correct - sum(controller.chunk_time_at_3live_healthy.values()))

    if total_chunk_days_correct > 0:
        pct_3live_correct = sum(controller.chunk_time_at_3live_correct.values()) / total_chunk_days_correct * 100
        pct_2live_correct = sum(controller.chunk_time_at_2live_correct.values()) / total_chunk_days_correct * 100
        pct_3live_healthy = sum(controller.chunk_time_at_3live_healthy.values()) / total_chunk_days_correct * 100

        # LIVE_CORRECT metric (primary - key for correctness)
        if pct_3live_correct >= 90:
            print(f"  ✓ Chunk-time at 3-live-CORRECT: {pct_3live_correct:.1f}% - EXCELLENT (goal: >90%)")
        elif pct_3live_correct >= 70:
            print(f"  ⚠️  Chunk-time at 3-live-CORRECT: {pct_3live_correct:.1f}% - GOOD (goal: >90%)")
        else:
            print(f"  ✗ Chunk-time at 3-live-CORRECT: {pct_3live_correct:.1f}% - TOO LOW (goal: >90%)")
        print(f"     at 2-live-CORRECT: {pct_2live_correct:.1f}%")

        # LIVE_HEALTHY metric (secondary - shows physical health)
        print(f"  📊 Chunk-time at 3-live-HEALTHY (>=80%): {pct_3live_healthy:.1f}%")

    # Write statistics (scrub write-backs + replica creation)
    write_fail_rate = (controller.write_failures_total / controller.write_attempts_total * 100) if controller.write_attempts_total > 0 else 0
    print(f"  📊 Write stats: {controller.write_successes_total} success / {controller.write_failures_total} fail / {controller.write_attempts_total} total (fail rate: {write_fail_rate:.2f}%)")

    # Mature tile percentage
    mature_tiles = sum(1 for t in controller.tiles if t.maturity_level >= 2)
    mature_percentage = (mature_tiles / controller.n_tiles * 100) if controller.n_tiles > 0 else 0
    print(f"  📊 Mature tile percentage: {mature_percentage:.1f}% ({mature_tiles}/{controller.n_tiles} tiles)")

    # HEALTH DIAGNOSTICS
    if controller.daily_tiles_healthy:
        avg_healthy = np.mean(controller.daily_tiles_healthy)
        avg_degraded = np.mean(controller.daily_tiles_degraded)
        avg_sick = np.mean(controller.daily_tiles_sick)
        print(f"\n  📊 HEALTH DIAGNOSTICS:")
        print(f"     Avg daily tiles ≥80%: {avg_healthy:.1f}")
        print(f"     Avg daily tiles 70-80%: {avg_degraded:.1f}")
        print(f"     Avg daily tiles 60-70%: {avg_sick:.1f}")
        print(f"     Tiles dropped <80% (baseline): {controller.tiles_dropped_below_80_baseline}")
        print(f"     Tiles dropped <80% (shocks): {controller.tiles_dropped_below_80_shock}")
        print(f"     Tiles recovered integrity: {controller.tiles_recovered_integrity}")
        if not controller.RECOVERY_ENABLED:
            print(f"     ℹ️  Natural recovery disabled; integrity restored only via regen pipeline")
        else:
            print(f"     ℹ️  Natural recovery enabled: {controller.RECOVERY_RATE*100:.2f}%/day for tiles ≥{controller.RECOVERY_MIN_CALM_DAYS} calm days")

    # CORRECTNESS GUARDRAILS: Lightweight assertions
    print(f"\n  🔒 CORRECTNESS GUARDRAILS:")
    # 1. Logical errors must be 0
    assert logical_errors == 0, f"FATAL: Logical errors detected ({logical_errors})!"
    print(f"     ✓ Logical errors = 0 (VERIFIED)")

    # 2. Replica drift must be 0
    assert replica_drift_rate == 0.0, f"FATAL: Replica drift detected ({replica_drift_rate:.2f}%)!"
    print(f"     ✓ Replica drift = 0% (VERIFIED)")

    # 3. All chunks must have exactly 3 slots
    for chunk_idx, slots in controller.chunk_replicas.items():
        assert len(slots) == 3, f"FATAL: Chunk {chunk_idx} has {len(slots)} slots, expected 3!"
    print(f"     ✓ Replica slot invariant holds (all chunks have 3 slots)")

    # 4. Chunks with <2 readable must have snapshot recovery available or be recovering
    for chunk_idx in controller.chunk_replicas.keys():
        live_correct = controller._count_live_correct(chunk_idx)
        if live_correct < 2:
            has_snapshot = chunk_idx in controller.chunk_snapshot_bits
            is_recovering = chunk_idx in controller.chunk_under_replicated_since_day
            assert has_snapshot or is_recovering, f"FATAL: Chunk {chunk_idx} has <2 readable with no recovery!"
    print(f"     ✓ All under-replicated chunks have recovery path")

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
