"""
Acheron Simulation 18: Intrinsic vs. Extrinsic Noise in the Engineered Toggle Circuit
=====================================================================

PURPOSE:
docs/SCIENTIFIC_AUDIT_2026.md Part 27 flags a real modeling gap in
bsubtilis_01_gardner_toggle_circuit.py: its `transcriptional_noise_std` applies two
INDEPENDENT random draws each step, one to each repressor. In the terms
Elowitz, Levine, Siggia & Swain (2002), "Stochastic gene expression in a
single cell," Science 297(5584):1183-1186, DOI 10.1126/science.1070919,
PMID 12183631, established with a real two-color-reporter experiment in
E. coli, that is INTRINSIC noise only: randomness inherent to each gene's
own expression machinery, uncorrelated between two genes in the same cell.
Their experiment found a second, often-dominant source: EXTRINSIC noise,
fluctuations in something shared across the whole cell (e.g. the total
RNA polymerase or ribosome pool available at that moment), which moves
every gene in that cell together, correlated, not independently.

This matters more here than for a single reporter gene, because the
Gardner circuit is a MUTUAL-REPRESSION pair. Two independent random nudges
(intrinsic-style) tend to partially cancel and roughly preserve the
balance between the two repressors, which is exactly what
bsubtilis_01_gardner_toggle_circuit.py's own noise sweep already shows (tx_noise_std up
to 3.0 barely moves genetic fidelity at matched promoter strengths). A
single correlated nudge (extrinsic-style) pushes both repressors the same
direction at once and does NOT cancel the same way, this file tests
whether that changes the picture.

WHAT THIS DOES:
Subclasses GardnerToggleCell (imported, never modified) to add one
additional shared random draw per timestep, applied to both repressors'
derivatives together, on top of the existing independent per-gene noise.
Runs the same promoter-ratio sweep bsubtilis_01_gardner_toggle_circuit.py already runs,
with extrinsic noise added, so the two results are directly comparable
line for line.

WHAT THIS DOES NOT DO:
The extrinsic_noise_std values swept below are NOT measured B. subtilis
numbers. Nobody has run the actual two-color-reporter assay on the BBB
promoters this project would use, that is precisely the low-cost wet-lab
experiment Part 27 recommends running before the larger damage-and-
regrowth test. Values here are chosen to span the same range already used
for tx_noise_std (0 to 3.0), for a like-for-like structural comparison,
not because that range is known to be correct for these organisms/parts.
"""

import os
import sys
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from bsubtilis_01_gardner_toggle_circuit import GardnerParams, GardnerToggleCell


class ExtrinsicNoiseToggleCell(GardnerToggleCell):
    """GardnerToggleCell plus one shared random draw per step, applied to
    both repressors together (extrinsic-style), on top of the existing
    independent per-gene draws (intrinsic-style, unchanged from the parent
    class). Everything else is inherited, not reimplemented, so any future
    fix to the parent's core dynamics is picked up automatically."""

    def __init__(self, *args, extrinsic_noise_std: float = 0.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.extrinsic_noise = extrinsic_noise_std

    def step(self, dt: float = 0.01):
        du = self.p.alpha1 / (1 + self.v ** self.p.beta) - self.u
        dv = (self.p.alpha2 * self.p.strength_ratio) / (1 + self.u ** self.p.gamma) - self.v
        if self.tx_noise > 0:
            du += self.rng.normal(0, self.tx_noise)
            dv += self.rng.normal(0, self.tx_noise)
        if self.extrinsic_noise > 0:
            shared = self.rng.normal(0, self.extrinsic_noise)
            du += shared
            dv += shared
        self.u = max(0.0, self.u + du * dt)
        self.v = max(0.0, self.v + dv * dt)

        target_V = self.V_HIGH if self.u > self.v else self.V_LOW
        dV = (target_V - self.V) * 0.05 * dt * 100
        dV += self.rng.normal(0, self.channel_noise * np.sqrt(dt))
        dV += self.rng.normal(0, self.thermal_noise * np.sqrt(dt))
        self.V = np.clip(self.V + dV, -120, 60)


def run_persistence(bit: int, params: GardnerParams, hours: float = 24.0,
                     seed: int = 0, tx_noise: float = 0.0,
                     extrinsic_noise: float = 0.0) -> Dict:
    cell = ExtrinsicNoiseToggleCell(params, seed=seed, transcriptional_noise_std=tx_noise,
                                     extrinsic_noise_std=extrinsic_noise)
    cell.write(bit)
    n_steps = int(hours * 60 / 1.0)
    for _ in range(n_steps):
        cell.step(dt=0.02)
    return {
        'genetic_correct': int(cell.read_genetic() == bit),
        'voltage_correct': int(cell.read_voltage() == bit),
    }


def sweep(ratios: List[float], tx_noise: float, extrinsic_noise: float,
          n_trials: int = 15) -> Dict[float, Dict]:
    results = {}
    for ratio in ratios:
        params = GardnerParams(strength_ratio=ratio)
        gen_correct, volt_correct = 0, 0
        for bit in [0, 1]:
            for trial in range(n_trials):
                r = run_persistence(bit, params, hours=24.0, seed=trial * 100 + bit,
                                     tx_noise=tx_noise, extrinsic_noise=extrinsic_noise)
                gen_correct += r['genetic_correct']
                volt_correct += r['voltage_correct']
        total = n_trials * 2
        results[ratio] = {
            'genetic_fidelity': gen_correct / total,
            'voltage_fidelity': volt_correct / total,
        }
    return results


def main():
    print("=" * 88)
    print("INTRINSIC vs. EXTRINSIC NOISE — does a shared, correlated noise source change")
    print("the Gardner toggle's promoter-mismatch picture?")
    print("=" * 88)

    ratios = [1.0, 2.0, 5.0, 10.0, 0.1]
    scenarios = [
        ("Intrinsic only (existing sweep, tx=3.0, extrinsic=0)", 3.0, 0.0),
        ("Intrinsic + extrinsic (tx=3.0, extrinsic=1.5)", 3.0, 1.5),
        ("Intrinsic + extrinsic (tx=3.0, extrinsic=3.0)", 3.0, 3.0),
    ]

    for label, tx_noise, extrinsic_noise in scenarios:
        print(f"\n--- {label} ---")
        print(f"{'Promoter strength ratio':<28}{'Genetic fidelity':>18}{'Voltage fidelity':>18}")
        results = sweep(ratios, tx_noise, extrinsic_noise)
        for ratio in ratios:
            r = results[ratio]
            print(f"{ratio:<28}{r['genetic_fidelity']:>17.0%}{r['voltage_fidelity']:>18.0%}")

    print("\n" + "=" * 88)
    print("INTERPRETATION")
    print("=" * 88)
    print("bsubtilis_01_gardner_toggle_circuit.py's own sweep already shows intrinsic-only noise barely")
    print("moves fidelity at matched promoter strengths (ratio=1.0), the failure mode there")
    print("is promoter mismatch, not noise. If adding an equal-magnitude EXTRINSIC (shared,")
    print("correlated) term meaningfully drops fidelity at ratio=1.0 where intrinsic-only")
    print("noise did not, that confirms Elowitz et al. 2002's finding matters here: this")
    print("circuit's real weak point may be correlated whole-cell noise, not independent")
    print("per-gene noise, a distinction the project's existing sweep cannot see because it")
    print("never modeled a correlated term. Values used are illustrative, not measured, see")
    print("docs/SCIENTIFIC_AUDIT_2026.md Part 27 and this file's own docstring.")
    print("=" * 88)


if __name__ == '__main__':
    main()
