"""
Acheron Simulation 7: Gardner-Topology Toggle Switch in B. subtilis
=====================================================================

PURPOSE:
Every prior simulation used `bistable_k`, a phenomenological linear
feedback strength with no direct biological referent. This replaces that
placeholder with an actual designed genetic circuit, built from two real,
freely-available sources:

1. TOPOLOGY + DYNAMICS: Gardner, Cantor & Collins (2000, Nature,
   DOI 10.1038/35002131) — the original synthetic genetic toggle switch:
   two mutually-repressing promoters, published as a dimensionless ODE
   pair with a demonstrated bistable parameter regime.

2. CHASSIS PARTS: the Bacillus BioBrick Box (Radeck et al. 2013,
   J Biol Eng, DOI 10.1186/1754-1611-7-29; BBB 2.0, Radeck et al. 2017,
   Sci Rep, DOI 10.1038/s41598-017-15107-z) — BioBrick-compatible,
   chromosomally-integrating promoters actually characterized IN
   B. subtilis (not E. coli), spanning >3 orders of magnitude in
   strength. This is the real chassis this project's simulations target,
   so promoter-strength ratios are drawn from their measured range
   instead of assumed.

WHAT THIS DOES NOT DO:
Nobody has built this specific circuit (toggle switch wired to an ion
channel output) in B. subtilis and measured it. The Gardner dynamics were
measured in E. coli; the promoter strengths were measured in B. subtilis
for different (reporter) outputs. Combining them is a grounded design
proposal, not a validated result — same category as the toggle-circuit-
in-planaria design, just with real characterized parts instead of a
literature-adjacent guess for the topology and an organism-matched
source for the parts.

RELATED WORK ON THE ACTUAL "GENETIC CIRCUIT -> PERSISTENT MEMORY" PROBLEM:
Huang, Yu, Lee et al. (2025), "Engineering wetware and software for the
predictive design of compressed genetic circuits for higher-state
decision-making," Nature Communications 16:9414 (DOI
10.1038/s41467-025-64457-0) build and quantitatively validate a
recombinase-based genetic memory circuit (their Fig. 7), hitting a
targeted 70% recombination efficiency via a context-specific expression
cassette (CSEC) lookup-table design workflow, with predictions accurate
to <1.4-fold across >50 test cases — a real, wet-lab-measured version of
exactly the "write a persistent bit via a genetic circuit, predict its
performance before building it" problem this file's ion-channel-output
link is still hypothetical about. Their code (github.com/Jayaos/TPro) has
no published license, so it isn't used here — this is a citation, not an
integration; see docs/THIRD_PARTY_METHODS.md.

MODEL:
Dimensionless Gardner toggle:
    du/dt = alpha1 / (1 + v^beta) - u
    dv/dt = alpha2 / (1 + u^gamma) - v
where u, v are repressor concentrations (normalized), alpha1/alpha2 are
promoter strengths (ratio drawn from BBB's characterized range), beta/gamma
are cooperativity (Gardner's own demonstrated bistable regime: beta=gamma=2).
Output "bit" = whichever repressor dominates -> mapped to membrane voltage
via a hypothetical ion-channel-expression link (not yet built or measured).
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class GardnerParams:
    alpha1: float = 50.0     # promoter 1 max strength (dimensionless)
    alpha2: float = 50.0     # promoter 2 max strength
    beta: float = 2.0        # cooperativity of repressor 2 on promoter 1 (Gardner's bistable regime)
    gamma: float = 2.0       # cooperativity of repressor 1 on promoter 2
    # BBB-derived promoter strength ASYMMETRY: the two promoters in a real
    # construct won't be perfectly matched. BBB's characterized promoters span
    # >3 orders of magnitude, so mismatched-strength designs are a real risk,
    # not a corner case. This ratio scales alpha2 relative to alpha1.
    strength_ratio: float = 1.0


class GardnerToggleCell:
    """One cell/colony running the actual repressor-repressor ODE,
    with noise sources analogous to noise_floor_characterizer.py applied
    to promoter output (transcriptional noise) and to the voltage-mapping
    step (channel/thermal noise), instead of a linear bistable_k."""

    V_REST, V_HIGH, V_LOW = -50.0, -10.0, -80.0
    V_MID = (V_HIGH + V_LOW) / 2.0

    def __init__(self, params: GardnerParams, seed: int = None,
                 transcriptional_noise_std: float = 0.0,
                 channel_noise_std: float = 5.0,
                 thermal_noise_std: float = 0.4):
        self.p = params
        self.rng = np.random.default_rng(seed)
        self.tx_noise = transcriptional_noise_std
        self.channel_noise = channel_noise_std
        self.thermal_noise = thermal_noise_std
        self.u, self.v = 0.0, 0.0   # start at unstable near-symmetric point
        self.V = self.V_REST

    def write(self, bit: int, kick: float = 20.0):
        """Transient induction pulse (xylose/IPTG-style) that pushes the
        circuit into one basin, mimicking the write step."""
        if bit == 1:
            self.u, self.v = self.p.alpha1, 0.0
        else:
            self.u, self.v = 0.0, self.p.alpha2 * self.p.strength_ratio

    def step(self, dt: float = 0.01):
        """dt in dimensionless Gardner time units (~ minutes-scale in practice)."""
        du = self.p.alpha1 / (1 + self.v ** self.p.beta) - self.u
        dv = (self.p.alpha2 * self.p.strength_ratio) / (1 + self.u ** self.p.gamma) - self.v
        if self.tx_noise > 0:
            du += self.rng.normal(0, self.tx_noise)
            dv += self.rng.normal(0, self.tx_noise)
        self.u = max(0.0, self.u + du * dt)
        self.v = max(0.0, self.v + dv * dt)

        # Map repressor dominance -> membrane voltage (hypothetical ion
        # channel expression link — the part nobody has built yet)
        target_V = self.V_HIGH if self.u > self.v else self.V_LOW
        dV = (target_V - self.V) * 0.05 * dt * 100  # fast tracking of genetic state
        dV += self.rng.normal(0, self.channel_noise * np.sqrt(dt))
        dV += self.rng.normal(0, self.thermal_noise * np.sqrt(dt))
        self.V = np.clip(self.V + dV, -120, 60)

    def read_genetic(self) -> int:
        return 1 if self.u > self.v else 0

    def read_voltage(self) -> int:
        return 1 if self.V > self.V_MID else 0


def run_persistence(bit: int, params: GardnerParams, hours: float = 24.0,
                     seed: int = 0, tx_noise: float = 0.0) -> Dict:
    cell = GardnerToggleCell(params, seed=seed, transcriptional_noise_std=tx_noise)
    cell.write(bit)
    n_steps = int(hours * 60 / 1.0)  # 1-min-equivalent steps
    for _ in range(n_steps):
        cell.step(dt=0.02)
    return {
        'genetic_correct': int(cell.read_genetic() == bit),
        'voltage_correct': int(cell.read_voltage() == bit),
        'final_u': cell.u, 'final_v': cell.v, 'final_V': cell.V,
    }


def main():
    print("=" * 72)
    print("GARDNER-TOPOLOGY TOGGLE SWITCH — real circuit vs. placeholder bistable_k")
    print("=" * 72)

    # Strength ratios spanning BBB's characterized >3-orders-of-magnitude range
    # 1.0 = perfectly matched promoters (best case, hard to achieve in practice)
    # 0.1-10x = realistic mismatch given BBB's measured promoter strength spread
    ratios = [1.0, 2.0, 5.0, 10.0, 0.1]
    tx_noise_levels = {"No transcriptional noise": 0.0,
                        "Realistic transcriptional noise": 3.0}

    for noise_name, tx_noise in tx_noise_levels.items():
        print(f"\n--- {noise_name} (tx_noise_std={tx_noise}) ---")
        print(f"{'Promoter strength ratio':<28}{'Genetic fidelity':>18}{'Voltage fidelity':>18}")
        for ratio in ratios:
            params = GardnerParams(strength_ratio=ratio)
            n_trials = 15
            gen_correct, volt_correct = 0, 0
            for bit in [0, 1]:
                for trial in range(n_trials):
                    r = run_persistence(bit, params, hours=24.0,
                                         seed=trial * 100 + bit, tx_noise=tx_noise)
                    gen_correct += r['genetic_correct']
                    volt_correct += r['voltage_correct']
            total = n_trials * 2
            print(f"{ratio:<28}{gen_correct/total:>17.0%}{volt_correct/total:>18.0%}")

    print("\n" + "=" * 72)
    print("INTERPRETATION")
    print("=" * 72)
    print("Genetic fidelity = does the repressor circuit itself stay in the")
    print("  written state (this is what Gardner et al. actually measured, in")
    print("  E. coli, not B. subtilis).")
    print("Voltage fidelity = does the HYPOTHETICAL ion-channel-output link")
    print("  survive too (this half has never been built or measured).")
    print("If genetic fidelity holds but voltage fidelity doesn't: the")
    print("  bottleneck moved from 'circuit exists' to 'the circuit->voltage")
    print("  interface,' which is a different, more specific unknown to test.")
    print("=" * 72)


if __name__ == '__main__':
    main()
