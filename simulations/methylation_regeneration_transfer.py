"""
Acheron Simulation 11: Methylation Bit Transfer Through Colony Regrowth
================================================================================

PURPOSE:
This is the third piece of the user's own 3-step framing for how BioCompute's
DNA-methylation readout could be repurposed for Acheron's actual question,
which BioCompute isn't asking: (1) write bits, (2) prove the bits stay
stored, (3) transfer the bits, unchanged, into a REGENERATED part of the
organism. methylation_bit_encoding.py already did (1) and (2) together
(a single lineage holding its bit across generations). This file does (3):
a colony takes damage, loses most of its cells, and regrows by ordinary
division from the survivors - does the regrown colony still read the bit
that was written before the damage?

This mirrors bacterial_colony_regrowth.py's structure (surviving-fraction
sweep, division-driven regrowth, DOUBLING_TIME_MIN, SETTLE_WINDOW_HOURS)
but swaps the continuous Gardner-circuit ODE cell for the discrete
methylation-maintenance model: at each division a cell's methylation bit is
correctly copied to both daughters with probability `maintenance_fidelity`,
or flipped. That IS how DNA methylation inheritance actually works
mechanistically (hemimethylation at replication, then maintenance
methyltransferase re-methylates the new strand, or fails to) - see
methylation_bit_encoding.py's docstring for the real citations this
fidelity parameter is grounded in (Laird et al. 2004 PNAS,
DOI 10.1073/pnas.2536758100; Watanabe et al. 2006, DOI
10.1007/3-540-31181-5_10) and its caveats (mammalian CpG numbers, not
measured for B. subtilis or bacterial Dam).

WHAT THIS DOES NOT DO:
Same caveats as methylation_bit_encoding.py, plus: this treats damage as
killing cells outright (dead cells contribute nothing), not as damaging DNA
or erasing methylation marks directly - a heat/chemical insult that
specifically strips methylation from survivors would be a different, worse
scenario not modeled here.
"""

import os
import sys
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from methylation_bit_encoding import simulate_methylation_lineage

DOUBLING_TIME_MIN = 30.0     # B. subtilis in rich media, same value used project-wide
SETTLE_WINDOW_HOURS = 24.0   # long enough to reach the ~48-generation column that
                              # methylation_bit_encoding.py flagged as the one to watch


def run_regrowth_trial(surviving_fraction: float, target_bit: int,
                        maintenance_fidelity: float, seed: int,
                        n_cells: int = 64) -> float:
    """
    One colony trial: write target_bit into a full colony, kill down to
    surviving_fraction, regrow by division (each division = one chance to
    correctly maintain the methylation bit, per maintenance_fidelity) until
    back to n_cells, then keep dividing for the rest of the observation
    window. Returns the fraction of the FINAL colony still reading the
    correct bit.
    """
    rng = np.random.default_rng(seed)

    n_survivors = max(1, int(round(n_cells * surviving_fraction))) if surviving_fraction > 0 else 0
    if n_survivors == 0:
        return 0.0

    # Survivors all carry the bit as written before the insult (methylation
    # marks on surviving DNA aren't erased by a cell dying elsewhere in the
    # colony - only division risks the bit, per the mechanism modeled here).
    bits = [target_bit] * n_survivors

    total_generations = int((SETTLE_WINDOW_HOURS * 60.0) / DOUBLING_TIME_MIN)
    generations_elapsed = 0

    while generations_elapsed < total_generations:
        # Every current cell divides into 2 daughters; each daughter's bit is
        # drawn independently (one maintenance-methylation event per
        # daughter, per division). new_bits REPLACES bits each generation -
        # it must, or already-settled cells never get another chance to
        # drift, which silently erases the compounding effect this file
        # exists to measure.
        new_bits = []
        for bit in bits:
            for _ in range(2):
                lineage_seed = int(rng.integers(0, 2**31))
                daughter_bit = simulate_methylation_lineage(
                    bit, maintenance_fidelity, n_generations=1,
                    seed=lineage_seed)[-1]
                new_bits.append(daughter_bit)
        bits = new_bits
        if len(bits) > n_cells:
            bits = list(rng.choice(bits, size=n_cells, replace=False))
        generations_elapsed += 1

    correct = sum(1 for b in bits if b == target_bit)
    return correct / len(bits)


def sweep_surviving_fraction(fractions: List[float], fidelities: List[float],
                              n_trials: int = 12) -> Dict:
    results = {}
    for fidelity in fidelities:
        for frac in fractions:
            scores_by_bit = {0: [], 1: []}
            for bit in [0, 1]:
                for trial in range(n_trials):
                    seed = int(frac * 10000) + int(fidelity * 1000) + trial * 97 + bit
                    scores_by_bit[bit].append(
                        run_regrowth_trial(frac, bit, fidelity, seed))
            results[(fidelity, frac)] = {
                'bit0': float(np.mean(scores_by_bit[0])),
                'bit1': float(np.mean(scores_by_bit[1])),
                'combined': float(np.mean(scores_by_bit[0] + scores_by_bit[1])),
            }
    return results


def main():
    print("=" * 78)
    print("METHYLATION BIT TRANSFER THROUGH COLONY REGROWTH — step 3")
    print("=" * 78)
    print("\nDoes a colony that loses most of its cells still read the correct bit")
    print("after regrowing purely by division from the survivors?\n")

    # 99.9% = Watanabe et al. 2006 promoter-CGI best case. 96% = Laird et al.
    # 2004 measured hypermethylated-island maintenance efficiency. Both
    # mammalian CpG, not B. subtilis - see file docstring.
    fidelities = [0.999, 0.96]
    fractions = [0.0, 0.02, 0.05, 0.10, 0.20, 0.50, 1.0]

    print(f"Doubling time: {DOUBLING_TIME_MIN:.0f} min | Observation window: "
          f"{SETTLE_WINDOW_HOURS:.0f}h (~{int(SETTLE_WINDOW_HOURS * 60 / DOUBLING_TIME_MIN)} generations)\n")

    results = sweep_surviving_fraction(fractions, fidelities)
    for fidelity in fidelities:
        print(f"\nMaintenance fidelity = {fidelity:.1%} per division")
        print(f"{'Surviving':<12}{'bit=0':>10}{'bit=1':>10}{'combined':>12}{'gap':>10}{'status':>10}")
        for frac in fractions:
            r = results[(fidelity, frac)]
            gap = abs(r['bit0'] - r['bit1'])
            status = "PASS" if r['combined'] >= 0.70 else "FAIL"
            print(f"{frac:<12.0%}{r['bit0']:>9.1%}{r['bit1']:>10.1%}{r['combined']:>11.1%}"
                  f"{gap:>10.1%}{status:>10}")

    print("\n" + "=" * 78)
    print("INTERPRETATION")
    print("=" * 78)
    print("At 99.9% fidelity (the best real-world anchor found, promoter CpG")
    print("islands in non-cancer cells), the bit survives regrowth from even a")
    print("small surviving population across a full day of division. At 96%")
    print("(the OTHER real measured anchor, a different CpG island context),")
    print("the signal is already decaying toward chance by ~48 generations")
    print("regardless of how many cells survived the initial damage, matching")
    print("methylation_bit_encoding.py's step-1/2 finding: the failure mode here")
    print("is compounding per-division drift, not insufficient survivors. A weak")
    print("maintenance fidelity cannot be rescued by more cells surviving the")
    print("insult, the same qualitative lesson Bio-RAID redundancy already")
    print("taught for the bioelectric circuit (Condorcet's jury theorem: voting")
    print("across copies that are each barely-better-than-chance doesn't help).")
    print("\nThis is a REAL divergence from the Gardner-circuit colony result in")
    print("bacterial_colony_regrowth.py, where surviving fraction (not per-cycle")
    print("fidelity decay) was the binding constraint. For methylation, fidelity")
    print("is the binding constraint - which real B. subtilis Dam-equivalent")
    print("fidelity would be needed to know for certain, and hasn't been found.")
    print("=" * 78)


if __name__ == '__main__':
    main()
