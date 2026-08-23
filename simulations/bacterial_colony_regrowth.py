"""
Acheron Simulation 9: Bacterial Colony Regrowth State Inheritance
=====================================================================

PURPOSE:
regrowth_state_inheritance.py asks "does a self-healing organism keep its
data" using PLANARIAN framing (fission, neoblasts) even though its actual
math is the generic Gardner circuit model. That file is left exactly as it
is - planarians are the long-term target and its results are being kept
for wet-lab planning. This file asks the SAME question, honestly framed
for B. subtilis, the organism actually being tested near-term.

The bacterial version of this question is mechanistically CLEANER than the
planarian one, and doesn't need an unvalidated "coupling constant":
bacteria don't have a separate stem-cell population differentiating into
new tissue. A damaged colony regrows by ordinary binary fission of the
survivors. At division, a cell's existing repressor proteins physically
partition into both daughter cells - that IS how state is inherited, it's
not a hypothesis, it's what cell division does to existing protein
contents. So instead of guessing a coupling range (the honest limitation
of the planarian file), this model just runs the same validated
GardnerToggleCell dynamics through actual division events.

SCENARIO:
A colony ("tile") storing one bit is hit by an environmental insult (heat,
cold, chemical stress - whatever "gets hurt" means for a bacterium),
killing a fraction of cells. Survivors regrow the colony via successive
rounds of binary fission (~30 min doubling time, typical for B. subtilis
in rich media) until the colony returns to full size, then the population
settles for the remainder of a realistic post-insult window. Question:
does the regrown colony still read out the correct bit?

WHAT THIS DOES NOT DO:
Division here is deterministic inheritance (daughter starts exactly where
the mother was) plus each cell's own ongoing noise - it does NOT model
stochastic partition noise (unequal splitting of protein molecules between
daughters), which is a real phenomenon with no B. subtilis-specific
measurement available yet. That's a second-order effect on top of the
already-unmeasured noise parameters flagged everywhere else in this
project; it would only make results here somewhat more pessimistic, not
change the qualitative finding.
"""

import os
import sys
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from gardner_toggle_circuit import GardnerParams, GardnerToggleCell

DOUBLING_TIME_MIN = 30.0     # B. subtilis in rich media, typical lab value
SETTLE_WINDOW_HOURS = 6.0    # total post-insult window modeled (regrowth + settling)


def run_colony_trial(surviving_fraction: float, target_bit: int, seed: int,
                      n_cells: int = 64, params: GardnerParams = None) -> float:
    """
    One colony regrowth trial. Returns the fraction of the FINAL colony
    reading out the correct bit after regrowth + settling.
    """
    params = params or GardnerParams()
    rng = np.random.default_rng(seed)

    n_survivors = max(1, int(round(n_cells * surviving_fraction))) if surviving_fraction > 0 else 0
    if n_survivors == 0:
        # Total wipeout: nothing left to regrow from. Colony doesn't exist,
        # so there's no data to read - report as 0 correct by convention.
        return 0.0

    cells = []
    for _ in range(n_survivors):
        c = GardnerToggleCell(params, seed=int(rng.integers(0, 2**31)),
                               transcriptional_noise_std=3.0)
        c.write(target_bit)
        cells.append(c)

    total_minutes = SETTLE_WINDOW_HOURS * 60.0
    elapsed = 0.0

    # Regrowth phase: divide every DOUBLING_TIME_MIN until back to n_cells,
    # each daughter inherits the mother's (u, v) at the moment of division -
    # this is the actual mechanism, not an assumption.
    while len(cells) < n_cells and elapsed < total_minutes:
        for _ in range(int(DOUBLING_TIME_MIN / 1.0)):
            for c in cells:
                c.step(dt=0.02)
        elapsed += DOUBLING_TIME_MIN
        new_cells = []
        for c in cells:
            daughter = GardnerToggleCell(params, seed=int(rng.integers(0, 2**31)),
                                          transcriptional_noise_std=3.0)
            daughter.u, daughter.v = c.u, c.v   # inherited state, not re-written
            new_cells.append(daughter)
            if len(cells) + len(new_cells) >= n_cells:
                break
        cells.extend(new_cells)
        cells = cells[:n_cells]

    # Settling phase: run out the remaining window with the colony at full size.
    # (one step() call = one simulated minute, matching gardner_toggle_circuit.py's
    # convention - dt=0.02 is the internal integration step, not minutes-per-call)
    remaining_steps = int(max(0.0, total_minutes - elapsed))
    for _ in range(remaining_steps):
        for c in cells:
            c.step(dt=0.02)

    # Pad back up to n_cells conceptually if regrowth never finished (colony
    # stayed smaller than target) - fraction correct is still measured over
    # however many cells actually exist, which is the honest readout.
    correct = sum(1 for c in cells if c.read_genetic() == target_bit)
    return correct / len(cells)


def sweep_surviving_fraction(fractions: List[float], n_trials: int = 12) -> Dict[float, Dict]:
    """Sweep surviving fraction, reporting bit=0 and bit=1 SEPARATELY
    (not just averaged) to catch any asymmetry like the one found in
    bit_asymmetry_root_cause.py for the older BacterialTile model."""
    results = {}
    for frac in fractions:
        scores_by_bit = {0: [], 1: []}
        for bit in [0, 1]:
            for trial in range(n_trials):
                seed = int(frac * 10000) + trial * 97 + bit
                scores_by_bit[bit].append(run_colony_trial(frac, bit, seed))
        results[frac] = {
            'bit0': float(np.mean(scores_by_bit[0])),
            'bit1': float(np.mean(scores_by_bit[1])),
            'combined': float(np.mean(scores_by_bit[0] + scores_by_bit[1])),
        }
    return results


def main():
    print("=" * 78)
    print("BACTERIAL COLONY REGROWTH — does the colony keep its data after damage?")
    print("=" * 78)

    fractions = [0.0, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90, 1.0]
    print(f"\nDoubling time: {DOUBLING_TIME_MIN:.0f} min | Settle window: {SETTLE_WINDOW_HOURS:.0f}h\n")
    print(f"{'Surviving':<12}{'bit=0':>10}{'bit=1':>10}{'combined':>12}{'gap':>10}{'status':>10}")
    results = sweep_surviving_fraction(fractions)
    threshold = None
    for frac, r in results.items():
        gap = abs(r['bit0'] - r['bit1'])
        status = "PASS" if r['combined'] >= 0.70 else "FAIL"
        if status == "PASS" and threshold is None and frac > 0:
            threshold = frac
        print(f"{frac:<12.0%}{r['bit0']:>9.1%}{r['bit1']:>10.1%}{r['combined']:>11.1%}"
              f"{gap:>10.1%}{status:>10}")

    print("\n" + "=" * 78)
    print("INTERPRETATION")
    print("=" * 78)
    if threshold is not None:
        print(f"~{threshold:.0%} surviving cells is where colony-level recovery holds, under")
        print("division-based state inheritance - a mechanistically grounded model, not")
        print("an assumed coupling field like the planarian version.")
    else:
        print("No surviving fraction in this sweep reliably preserved the data.")
    print("\nIf the bit=0/bit=1 gap column is large at any surviving fraction, that's")
    print("worth checking against bit_asymmetry_root_cause.py's finding for the older")
    print("BacterialTile model - GardnerToggleCell is a different implementation, so")
    print("an asymmetry here would be a NEW finding, not a repeat of that one.")
    print("=" * 78)


if __name__ == '__main__':
    main()
