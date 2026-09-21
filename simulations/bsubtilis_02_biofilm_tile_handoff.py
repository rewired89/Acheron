"""
Acheron Simulation 6: Bacterial Biofilm Tile Handoff
======================================================

PURPOSE:
The project's real goal (per Aug 2026 direction) is not "hold one bit
forever" — it's: detect that a tile needs to heal, transfer its data to a
fresh tile BEFORE that happens, let the old tile regenerate, and repeat this
cycle indefinitely. Anything beyond 24h single-tile persistence is bonus
margin, not the requirement.

This simulation tests the mechanism unique to bacterial biofilms (vs. every
other organism discussed so far): a self-propagating handoff. Bacillus
subtilis biofilms carry potassium-wave electrical signals between colonies
via a positive-feedback ion-channel mechanism (Prindle et al. 2015, Nature,
DOI 10.1038/nature15709) — meaning a neighboring "tile" could potentially
pick up the source tile's state WITHOUT an external read/write controller
cycle, simply by being close enough for the wave to reach it. That is
architecturally different from planaria, where transfer requires an external
optogenetic write driven by a camera read.

We test two things:
1. Does a single propagation event reliably transfer a bit (vs. controller
   copy, which is organism-agnostic and assumed to work if read+write
   individually work)?
2. Does fidelity degrade over REPEATED handoff cycles (a "telephone game"
   effect across a tile's operational lifetime), or does having a strong
   bistable attractor at the destination act like a digital repeater —
   cleaning up an imperfect handoff pulse instead of accumulating error?

CAVEAT: No literature was found giving bacteria-specific noise-floor
measurements comparable to the planarian epithelial-cell values used
elsewhere in this project. Noise magnitudes here are carried over from the
"realistic biological noise" profile in planarian_02_noise_floor.py as a
placeholder — this needs real patch-clamp/electrophysiology data from an
engineered B. subtilis line before these numbers can be trusted.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class TileNoise:
    channel_noise_std: float = 5.0        # mV, per-step stochastic fluctuation
    metabolic_noise_fraction: float = 0.10
    thermal_noise_std: float = 0.4
    bistable_k: float = 0.20              # from Part 8: minimum value that PASSED


class BacterialTile:
    """
    One colony patch ("tile"). Same bistable+noise physics as
    NoisyPlanarianTissue, collapsed to a single scalar state (a colony is
    modeled as one well-mixed population, not a 2D cell grid) since biofilm
    electrical signaling propagates as a population-level wave, not a
    per-cell pattern (Prindle et al. 2015).
    """
    V_REST = -50.0
    V_HIGH = -10.0
    V_LOW = -80.0
    V_MID = (V_HIGH + V_LOW) / 2.0
    TAU = 60.0     # min — bacterial ion channel dynamics are faster than
                   # planarian tissue; order-of-magnitude assumption, not measured
    C_MEM = 5.0

    def __init__(self, noise: TileNoise, seed: int = None):
        self.rng = np.random.default_rng(seed)
        self.noise = noise
        self.V = self.V_REST
        self.healed = True   # fresh/available tile

    def write(self, bit: int):
        self.V = self.V_HIGH if bit else self.V_LOW
        self.healed = False  # now carrying live data

    def step(self, dt: float, external_drive: float = 0.0):
        """external_drive: coupling current from a propagating wave (mV/min equivalent)."""
        I_leak = (self.V_REST - self.V) / (200.0 * self.TAU)
        I_bistable = self.noise.bistable_k * (self.V - self.V_MID)
        I_metabolic = self.rng.normal(0, abs(I_leak) * self.noise.metabolic_noise_fraction)
        dV = (I_leak + I_bistable + I_metabolic) / self.C_MEM * dt
        dV += self.rng.normal(0, self.noise.channel_noise_std * np.sqrt(dt))
        dV += self.rng.normal(0, self.noise.thermal_noise_std * np.sqrt(dt))
        dV += external_drive * dt
        self.V = np.clip(self.V + dV, -120, 60)

    def read(self) -> int:
        return 1 if self.V > self.V_MID else 0

    def reset_and_heal(self):
        """Old tile clears and returns to baseline — analog of colony
        regrowth after the data-bearing population disperses/dies off."""
        self.V = self.V_REST
        self.healed = True


def propagate_handoff(source: BacterialTile, dest: BacterialTile,
                       duration_min: float = 120.0, dt: float = 1.0,
                       k_couple: float = 0.05):
    """
    Model the K+ wave handoff: destination tile is driven toward source's
    CURRENT voltage via a diffusive coupling term for `duration_min`, then
    decoupled (wave has passed / tiles are no longer in signaling range).
    Source keeps running its own bistable dynamics throughout (it isn't
    instantaneously erased — it degrades/disperses on its own timeline).
    """
    n_steps = int(duration_min / dt)
    for _ in range(n_steps):
        source.step(dt)
        coupling = k_couple * (source.V - dest.V)
        dest.step(dt, external_drive=coupling)


def run_handoff_chain(n_cycles: int, bit: int, noise: TileNoise,
                       hours_before_handoff: float = 24.0,
                       seed: int = 0) -> List[int]:
    """
    Simulate a chain: Tile_0 written -> holds for `hours_before_handoff` ->
    handoff to Tile_1 -> Tile_0 heals -> Tile_1 holds -> handoff to Tile_2 ->
    ... for n_cycles. Returns the bit read at each new tile right after
    handoff (before its own hold period), to isolate handoff fidelity from
    hold-time fidelity.
    """
    rng_seed = seed
    current = BacterialTile(noise, seed=rng_seed)
    current.write(bit)
    reads_after_handoff = []

    for cycle in range(n_cycles):
        # hold period on the current tile before it signals "need to heal"
        n_hold_steps = int(hours_before_handoff * 60 / 1.0)
        for _ in range(n_hold_steps):
            current.step(dt=1.0)

        # spin up a fresh healthy tile and hand off
        rng_seed += 1
        nxt = BacterialTile(noise, seed=rng_seed)
        propagate_handoff(current, nxt)
        reads_after_handoff.append(nxt.read())

        current.reset_and_heal()
        current = nxt

    return reads_after_handoff


def main():
    noise = TileNoise()
    print("=" * 70)
    print("BACTERIAL BIOFILM TILE HANDOFF — bit survives N healing cycles?")
    print("=" * 70)

    for bit in [0, 1]:
        n_trials = 20
        n_cycles = 5
        successes_per_cycle = np.zeros(n_cycles)
        for trial in range(n_trials):
            reads = run_handoff_chain(n_cycles, bit, noise,
                                       hours_before_handoff=24.0,
                                       seed=trial * 1000 + bit)
            successes_per_cycle += (np.array(reads) == bit)
        rates = successes_per_cycle / n_trials
        print(f"\nBit={bit}  (fidelity after each successive handoff, {n_trials} trials)")
        for i, r in enumerate(rates):
            print(f"  Handoff {i+1}: {r:.0%} correct")

    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print("If fidelity stays flat across handoffs -> bistable attractor at each")
    print("new tile acts as a digital repeater (self-cleaning), safe for many")
    print("healing cycles over the product's operational life.")
    print("If fidelity decays across handoffs -> errors compound like a photocopy")
    print("of a photocopy; system needs read-verify-rewrite via external")
    print("controller instead of trusting passive propagation alone.")
    print("=" * 70)


if __name__ == '__main__':
    main()
