"""
Acheron Simulation 19: Does the Fluorescent Reporter Still Read Correctly
After Damage and Regrowth?
================================================================================

PURPOSE:
Two things have been validated separately and never combined:
`bacterial_colony_regrowth.py` proved the underlying genetic memory (u/v
repressor state) survives division-based damage/regrowth down to 2%
surviving cells. `gardner_toggle_reporter_readout.py` proved a GFP/RFP
transcriptional reporter tracks that genetic state accurately when
nothing disturbs the colony. Neither file answers the question that
actually matters for a real experiment: after a colony gets smashed down
to a handful of survivors and regrows by ordinary division, does the
GLOWING COLOR still say the right thing, not just the genes underneath
it? This file runs that combined test directly instead of assuming the
two results compose.

WHAT INHERITANCE MEANS HERE, AND WHY IT MATCHES THE EXISTING MODEL:
`bacterial_colony_regrowth.py` has each daughter inherit the MOTHER'S
(u, v) VALUE directly (not half of it), because u and v are modeled as
concentrations, not absolute molecule counts, and a cell dividing into
two daughters of roughly equal size passes on roughly the same
concentration to each (amount and volume both roughly halve, so their
ratio doesn't). This file extends that exact same, already-established
treatment to the reporter pools (GFP/RFP, both dark/immature and
bright/mature), for consistency, not as a new assumption: daughters
inherit the mother's reporter concentrations at division, then continue
maturing/diluting/synthesizing on their own afterward.

WHAT THIS TESTS, PRECISELY:
The same surviving-fraction sweep as `bacterial_colony_regrowth.py`
(0% to 100%), using `GardnerToggleReporterCell` instead of the plain
`GardnerToggleCell`, reporting BOTH the genetic fidelity (the original
file's result, reproduced here as a consistency check) and the reporter
fidelity (new) side by side, so any gap between them is attributable
specifically to the reporter layer surviving regrowth, not the
underlying memory.

WHAT THIS DOES NOT DO:
Same limitation `bacterial_colony_regrowth.py` already states: division
here is deterministic inheritance plus each cell's own ongoing noise, it
does not model stochastic partition noise (unequal splitting of protein
molecules, reporter or repressor, between daughters), a real phenomenon
with no B. subtilis-specific measurement available yet. This file also
does not model photobleaching, autofluorescence, or population-level
imaging noise from actually photographing a regrown colony under a
microscope, all real, separate, wet-lab-only questions.
"""

import os
import sys
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from gardner_toggle_circuit import GardnerParams
from gardner_toggle_reporter_readout import GardnerToggleReporterCell
from bacterial_colony_regrowth import DOUBLING_TIME_MIN, SETTLE_WINDOW_HOURS


def run_colony_trial(surviving_fraction: float, target_bit: int, seed: int,
                      n_cells: int = 64, params: GardnerParams = None) -> Dict[str, float]:
    """One colony regrowth trial, reporter version. Returns the fraction
    of the FINAL colony reading out the correct bit, both genetically and
    through the fluorescent reporter, after regrowth + settling."""
    params = params or GardnerParams()
    rng = np.random.default_rng(seed)

    n_survivors = max(1, int(round(n_cells * surviving_fraction))) if surviving_fraction > 0 else 0
    if n_survivors == 0:
        return {'genetic': 0.0, 'reporter': 0.0}

    cells = []
    for _ in range(n_survivors):
        c = GardnerToggleReporterCell(params, seed=int(rng.integers(0, 2**31)),
                                       transcriptional_noise_std=3.0)
        c.write(target_bit)
        cells.append(c)

    total_minutes = SETTLE_WINDOW_HOURS * 60.0
    elapsed = 0.0

    while len(cells) < n_cells and elapsed < total_minutes:
        for _ in range(int(DOUBLING_TIME_MIN / 1.0)):
            for c in cells:
                c.step(dt=0.02)
        elapsed += DOUBLING_TIME_MIN
        new_cells = []
        for c in cells:
            daughter = GardnerToggleReporterCell(params, seed=int(rng.integers(0, 2**31)),
                                                  transcriptional_noise_std=3.0)
            daughter.u, daughter.v = c.u, c.v
            daughter.gfp_dark, daughter.gfp_bright = c.gfp_dark, c.gfp_bright
            daughter.rfp_dark, daughter.rfp_bright = c.rfp_dark, c.rfp_bright
            new_cells.append(daughter)
            if len(cells) + len(new_cells) >= n_cells:
                break
        cells.extend(new_cells)
        cells = cells[:n_cells]

    remaining_steps = int(max(0.0, total_minutes - elapsed))
    for _ in range(remaining_steps):
        for c in cells:
            c.step(dt=0.02)

    genetic_correct = sum(1 for c in cells if c.read_genetic() == target_bit) / len(cells)
    reporter_correct = sum(1 for c in cells if c.read_reporter() == target_bit) / len(cells)
    return {'genetic': genetic_correct, 'reporter': reporter_correct}


def sweep_surviving_fraction(fractions: List[float], n_trials: int = 12) -> Dict[float, Dict]:
    results = {}
    for frac in fractions:
        genetic_scores, reporter_scores = [], []
        for bit in [0, 1]:
            for trial in range(n_trials):
                seed = int(frac * 10000) + trial * 97 + bit
                r = run_colony_trial(frac, bit, seed)
                genetic_scores.append(r['genetic'])
                reporter_scores.append(r['reporter'])
        results[frac] = {
            'genetic': float(np.mean(genetic_scores)),
            'reporter': float(np.mean(reporter_scores)),
        }
    return results


def main():
    print("=" * 82)
    print("REPORTER READOUT THROUGH DAMAGE + REGROWTH - does the glow survive too?")
    print("=" * 82)

    fractions = [0.0, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90, 1.0]
    print(f"\nDoubling time: {DOUBLING_TIME_MIN:.0f} min | Settle window: {SETTLE_WINDOW_HOURS:.0f}h\n")
    print(f"{'Surviving':<12}{'Genetic':>12}{'Reporter':>12}{'gap':>10}{'status':>10}")
    results = sweep_surviving_fraction(fractions)
    threshold = None
    for frac, r in results.items():
        gap = abs(r['genetic'] - r['reporter'])
        status = "PASS" if r['reporter'] >= 0.70 else "FAIL"
        if status == "PASS" and threshold is None and frac > 0:
            threshold = frac
        print(f"{frac:<12.0%}{r['genetic']:>11.1%}{r['reporter']:>12.1%}"
              f"{gap:>10.1%}{status:>10}")

    print("\n" + "=" * 82)
    print("INTERPRETATION")
    print("=" * 82)
    if threshold is not None:
        print(f"~{threshold:.0%} surviving cells is where the REPORTER readout recovers, not just")
        print("the underlying genetic state - the two columns above should be compared")
        print("directly, since bacterial_colony_regrowth.py already validated the Genetic")
        print("column on its own.")
    else:
        print("No surviving fraction in this sweep reliably preserved a readable reporter signal.")
    print("\nIf Genetic and Reporter track closely at every surviving fraction, that's the")
    print("computational case for treating Stage 2 of the Validation Proposal (damage +")
    print("regrowth) as safe to run with a fluorescent/reporter readout for B. subtilis")
    print("specifically, something the existing staged plan doesn't yet have (its Stage 2")
    print("is planarian-specific). If they diverge, that gap is new information the")
    print("reporter-only test in gardner_toggle_reporter_readout.py couldn't have shown,")
    print("since that file never disturbs the colony.")
    print("=" * 82)


if __name__ == '__main__':
    main()
