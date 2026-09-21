"""
Acheron Simulation 15: Circuit Variant Predictor - Design-Space Prediction
Before the Wet-Lab Damage-Regrowth Test
=====================================================================

PURPOSE:
Throughline item 6 in CLAUDE.md is the one open question everything
currently depends on: does an engineered bistable circuit's state survive
damage-and-regrowth. That is a real ~$10K-$30K, 6-12 month wet-lab
experiment (docs/INVESTOR_PITCH.md Roadmap), and it has to be run on ONE
specific promoter-pairing design, not on "the circuit" in the abstract.

This file does not predict a new organism-level phenomenon. It composes
two simulations this project has already validated separately -
bsubtilis_01_gardner_toggle_circuit.py's promoter-strength-ratio sweep (grounded in
Radeck et al. 2013/2017's characterized BBB promoter range) and
bsubtilis_07_colony_regrowth.py's division-based damage-regrowth mechanism
(mechanistically forced, not assumed, see that file's docstring) - into a
single design-space grid: promoter strength ratio x surviving fraction.
The result is a ranked list of which already-characterized promoter
pairings are predicted to tolerate the LEAST forgiving surviving fraction,
i.e. which designs are worth prioritizing for the actual wet-lab test.

WHAT THIS DOES NOT DO:
This is a search over a design space using parameters already in this
repo, not a new validated result and not a substitute for the wet-lab
test itself. It inherits every caveat already stated in the two files it
composes: the toggle-to-voltage link is still hypothetical
(bsubtilis_01_gardner_toggle_circuit.py), and division-based inheritance here ignores
stochastic partition noise (bsubtilis_07_colony_regrowth.py). No new
promoter-strength numbers are introduced, the ratios swept are the same
ones bsubtilis_01_gardner_toggle_circuit.py already uses to represent BBB's measured
range. If a future session has real per-promoter BBB strength values
(rather than the ratio abstraction used here), replace `RATIOS` below
with those cited values instead of adding new ones without a citation,
per docs/THIRD_PARTY_METHODS.md's no-numeric-invention rule.
"""

import os
import sys
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from bsubtilis_01_gardner_toggle_circuit import GardnerParams
from bsubtilis_07_colony_regrowth import run_colony_trial

PASS_THRESHOLD = 0.70  # same bar bsubtilis_07_colony_regrowth.py and crossorganism_01_comparison_summary.py use


def sweep_design_space(ratios: List[float], fractions: List[float],
                        n_trials: int = 10) -> Dict[Tuple[float, float], Dict]:
    """For each (strength_ratio, surviving_fraction) cell, run both bits and
    report bit=0/bit=1 separately, same convention as the files this composes."""
    results = {}
    for ratio in ratios:
        params = GardnerParams(strength_ratio=ratio)
        for frac in fractions:
            scores = {0: [], 1: []}
            for bit in [0, 1]:
                for trial in range(n_trials):
                    seed = int(ratio * 1000) + int(frac * 10000) + trial * 97 + bit
                    scores[bit].append(run_colony_trial(frac, bit, seed, params=params))
            results[(ratio, frac)] = {
                'bit0': float(np.mean(scores[0])),
                'bit1': float(np.mean(scores[1])),
                'combined': float(np.mean(scores[0] + scores[1])),
            }
    return results


def rank_designs(results: Dict[Tuple[float, float], Dict], ratios: List[float],
                  fractions: List[float], threshold: float = PASS_THRESHOLD) -> List[Dict]:
    """For each promoter-strength ratio, find the worst (lowest) surviving
    fraction at which combined fidelity still clears `threshold`. Lower is
    more robust - that ratio recovers even from more severe damage. Ratios
    that never clear the threshold are ranked last, worst first."""
    ranked = []
    for ratio in ratios:
        worst_passing = None
        for frac in sorted(fractions):
            if frac == 0.0:
                continue
            if results[(ratio, frac)]['combined'] >= threshold:
                worst_passing = frac
                break
        ranked.append({'ratio': ratio, 'min_surviving_fraction': worst_passing})
    ranked.sort(key=lambda r: (r['min_surviving_fraction'] is None, r['min_surviving_fraction']))
    return ranked


def main():
    print("=" * 90)
    print("CIRCUIT VARIANT PREDICTOR - which promoter-strength design to test in the wet lab first")
    print("=" * 90)

    ratios = [1.0, 2.0, 5.0, 10.0, 0.1]  # same BBB-range ratios bsubtilis_01_gardner_toggle_circuit.py sweeps
    fractions = [0.02, 0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90, 1.0]
    n_trials = 10

    print(f"\nSweeping {len(ratios)} promoter-strength ratios x {len(fractions)} surviving fractions "
          f"({n_trials} trials/bit/cell)...\n")
    results = sweep_design_space(ratios, fractions, n_trials=n_trials)

    header = f"{'Ratio':<10}" + "".join(f"{f:>9.0%}" for f in fractions)
    print(header)
    for ratio in ratios:
        row = f"{ratio:<10}"
        for frac in fractions:
            row += f"{results[(ratio, frac)]['combined']:>9.0%}"
        print(row)

    ranked = rank_designs(results, ratios, fractions)

    print("\n" + "=" * 90)
    print("RANKED DESIGN RECOMMENDATION (most damage-tolerant design first)")
    print("=" * 90)
    for r in ranked:
        if r['min_surviving_fraction'] is None:
            print(f"strength_ratio={r['ratio']:<6} never reached {PASS_THRESHOLD:.0%} combined fidelity in this sweep")
        else:
            print(f"strength_ratio={r['ratio']:<6} recovers from as little as "
                  f"{r['min_surviving_fraction']:.0%} surviving cells")

    print("\n" + "=" * 90)
    print("INTERPRETATION")
    print("=" * 90)
    print("This ranks design VARIANTS, all of them already-simulated, real-BBB-range")
    print("promoter pairings, by how much simulated damage they're predicted to tolerate.")
    print("It narrows which specific construct to build for the wet-lab damage-regrowth")
    print("test (CLAUDE.md throughline item 6), it does not answer that test's question.")
    print("Every caveat in bsubtilis_01_gardner_toggle_circuit.py and bsubtilis_07_colony_regrowth.py still")
    print("applies here in full, this file only recombines their already-cited parameters.")
    print("=" * 90)


if __name__ == '__main__':
    main()
