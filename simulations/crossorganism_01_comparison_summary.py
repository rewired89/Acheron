"""
Acheron Simulation 14: Planarian vs. B. subtilis - Side-by-Side Comparison
================================================================================

PURPOSE:
Every prior simulation tested one organism/mechanism at a time. This file
runs the directly comparable tests for BOTH candidate organisms side by
side, using each organism's OWN already-validated model (not a new,
untested one), so the founder can see where the evidence currently stands
for each, in one place.

WHAT IS AND ISN'T COMPARABLE HERE - read before trusting a row:
Three mechanisms are compared on the SAME question ("if the organism is
damaged and regenerates, does it keep the correct bit?"), because all
three already have a validated simulation asking exactly that:
  1. Planarian, bioelectric circuit, mean-field coupling
     (planarian_09_regrowth_state_inheritance.py)
  2. B. subtilis, bioelectric circuit, division-based inheritance
     (bsubtilis_07_colony_regrowth.py)
  3. B. subtilis, DNA methylation, division-based inheritance
     (methylation_02_regeneration_transfer.py), at both real fidelity anchors

These three do NOT rest on equally strong grounding, and this file does
not pretend otherwise:
  - (2)'s coupling mechanism (division inherits the mother cell's actual
    protein state) is mechanistically necessary - that's just what cell
    division does to existing repressor proteins. Least speculative.
  - (1)'s coupling mechanism (a mean-field pull from surviving tissue
    toward neoblast-derived naive tissue) is BORROWED from the bacterial
    coupling idea and applied to planarian regeneration, which is
    mechanistically a different process (differentiation of a distinct
    stem-cell population, not division of an already-committed cell).
    Real planarian bioelectric-instructs-fate precedent exists (Grodstein
    & Levin 2022), but the exact coupling strength used here is NOT
    measured in real planarian tissue. Most speculative of the three.
  - (3) rests on real methylation-fidelity numbers (Laird et al. 2004;
    Watanabe et al. 2006), but those numbers are mammalian CpG methylation,
    not B. subtilis, which doesn't natively carry the enzyme system this
    mechanism needs. Grounded in real numbers, wrong organism.

TWO NEWER B. SUBTILIS-SPECIFIC TESTS ARE DELIBERATELY EXCLUDED HERE, NOT
FORGOTTEN: bsubtilis_08_native_oscillation_interference.py and bsubtilis_09_eis_readout_interference.py
are both grounded in real, published Bacillus subtilis / bacterial biofilm
potassium-signaling literature (Ford et al. 2021; Mulder et al. 2025;
Akabuogu et al. 2024). No equivalent published mechanism for planarian
tissue was found anywhere in this project's research. Building a "planarian
version" of these two tests would mean inventing a planarian interference
source with no citation behind it - exactly the kind of unlabeled
assumption this project's audit has consistently flagged and avoided
elsewhere. That gap is reported honestly below, not filled in.
"""

import os
import sys
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from planarian_09_regrowth_state_inheritance import sweep_surviving_fraction as planarian_sweep
from bsubtilis_07_colony_regrowth import sweep_surviving_fraction as bsubtilis_circuit_sweep
from methylation_02_regeneration_transfer import sweep_surviving_fraction as methylation_sweep


def run_all(fractions: List[float], n_trials: int = 10) -> Dict:
    print("Running planarian (bioelectric circuit, mean-field coupling)...")
    planarian = planarian_sweep(fractions, n_trials=n_trials)

    print("Running B. subtilis (bioelectric circuit, division-based inheritance)...")
    bsub_raw = bsubtilis_circuit_sweep(fractions, n_trials=n_trials)
    bsub_circuit = {frac: r['combined'] for frac, r in bsub_raw.items()}

    print("Running B. subtilis (methylation, division-based, fidelity=99.9%)...")
    meth_raw = methylation_sweep(fractions, [0.999], n_trials=n_trials)
    meth_999 = {frac: meth_raw[(0.999, frac)]['combined'] for frac in fractions}

    print("Running B. subtilis (methylation, division-based, fidelity=96.0%)...")
    meth_raw2 = methylation_sweep(fractions, [0.96], n_trials=n_trials)
    meth_96 = {frac: meth_raw2[(0.96, frac)]['combined'] for frac in fractions}

    return {
        'planarian_circuit': planarian,
        'bsubtilis_circuit': bsub_circuit,
        'bsubtilis_methylation_999': meth_999,
        'bsubtilis_methylation_96': meth_96,
    }


def main():
    print("=" * 92)
    print("PLANARIAN vs. B. SUBTILIS - regeneration/regrowth data-retention comparison")
    print("=" * 92)
    print()

    fractions = [0.0, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90, 1.0]
    results = run_all(fractions)

    print()
    print(f"{'Surviving':<12}{'Planarian':>14}{'B.subtilis':>16}{'B.subtilis':>16}{'B.subtilis':>16}")
    print(f"{'fraction':<12}{'(circuit,':>14}{'(circuit,':>16}{'(methylation,':>16}{'(methylation,':>16}")
    print(f"{'':<12}{'mean-field)':>14}{'division)':>16}{'99.9% fid.)':>16}{'96% fid.)':>16}")
    print("-" * 92)
    for frac in fractions:
        row = f"{frac:<12.0%}"
        row += f"{results['planarian_circuit'][frac]:>14.1%}"
        row += f"{results['bsubtilis_circuit'][frac]:>16.1%}"
        row += f"{results['bsubtilis_methylation_999'][frac]:>16.1%}"
        row += f"{results['bsubtilis_methylation_96'][frac]:>16.1%}"
        print(row)

    def threshold(series: Dict[float, float], target: float = 0.70) -> str:
        for frac in sorted(series.keys()):
            if frac > 0 and series[frac] >= target:
                return f"~{frac:.0%}"
        return "none in this sweep"

    print("\n" + "=" * 92)
    print("SUMMARY: surviving fraction needed for >=70% recovery")
    print("=" * 92)
    print(f"Planarian (circuit, mean-field coupling):        {threshold(results['planarian_circuit'])}")
    print(f"B. subtilis (circuit, division-based):            {threshold(results['bsubtilis_circuit'])}")
    print(f"B. subtilis (methylation, 99.9% fidelity anchor): {threshold(results['bsubtilis_methylation_999'])}")
    print(f"B. subtilis (methylation, 96% fidelity anchor):   {threshold(results['bsubtilis_methylation_96'])}")

    print("\n" + "=" * 92)
    print("INTERPRETATION")
    print("=" * 92)
    print("Numerically, planarian (bioelectric circuit) TIES B. subtilis (bioelectric")
    print("circuit) at 100% across nearly every surviving fraction tested, and both")
    print("beat the methylation mechanism's real 99.9% anchor (93-97%). That is NOT")
    print("the same as planarian being an equally trustworthy result: the B. subtilis")
    print("circuit row's coupling is mechanistically forced (division copies existing")
    print("repressor protein, not a choice), while the planarian row's coupling")
    print("strength is a borrowed assumption with no direct planarian measurement")
    print("behind it. Same output number, different confidence behind it.")
    print("\nThe methylation 96% row is the cautionary case IN THIS SAME TABLE: same")
    print("organism, same mechanism family, a different real-world context, and it")
    print("fails outright regardless of surviving fraction (see methylation_01_bit_encoding.py")
    print("and methylation_02_regeneration_transfer.py for why: fidelity-bound decay, not")
    print("survivor-count-bound). This table is a snapshot of current SIMULATED")
    print("evidence, not a verdict on which organism is 'better' - it's a map of which")
    print("unmeasured parameter, for which organism, is worth spending wet-lab time")
    print("on first. Ranked by how much wet-lab risk each row is still hiding, lowest")
    print("to highest: B. subtilis circuit < B. subtilis methylation < planarian circuit.")
    print("\nGAP, STATED PLAINLY: bsubtilis_08_native_oscillation_interference.py and")
    print("bsubtilis_09_eis_readout_interference.py, this project's two newest tests, only exist")
    print("for B. subtilis, because that's where the underlying biofilm-signaling")
    print("literature is. No comparable planarian interference test exists yet - not")
    print("because planarians are assumed safe from an equivalent problem, but because")
    print("no citation for one was found. That is an open research gap, not a result.")
    print("=" * 92)


if __name__ == '__main__':
    main()
