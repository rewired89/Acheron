"""
Acheron Simulation 25: What Real Noise Formula Is the tx_noise Placeholder
Standing In For? (Swain, Elowitz & Siggia 2002)
=====================================================================

PURPOSE:
bsubtilis_01_gardner_toggle_circuit.py's `transcriptional_noise_std` is a
flat, uncited Gaussian noise term (default 3.0, applied identically to
both repressor arms every step). docs/SCIENTIFIC_AUDIT_2026.md has
repeatedly flagged this as the project's single largest category of
"we assumed this" caveat, and Stage B1 of the bench protocol exists
specifically to replace it with a measured number.

The founder supplied Swain, Elowitz & Siggia (2002), "Intrinsic and
extrinsic contributions to stochasticity in gene expression," PNAS
99(20):12795-12800, DOI 10.1073/pnas.162041399 -- the theoretical
companion to the two-color Elowitz et al. 2002 Science paper this project
already cites (audit Part 27). It does not give a B. subtilis noise
number (none of this project's promoters have been measured), but it does
give the actual FORMULA that any real measurement would need to fill in,
and states the qualitative dependencies explicitly:

1. Intrinsic noise decomposes into a Poisson term (set by mean protein
   number) plus a transcriptional term set by mean mRNA number and burst
   size (proteins made per transcript). Their Eq. 19 gives the full
   time-dependent form; the well-known asymptotic simplification of this
   same result (also derived independently by Thattai & van Oudenaarden
   2001, PNAS 98:8614-8619, which Swain et al. cite and build on) is
       eta_int^2 ~= (1 + b) / <P>
   where b is burst size and <P> is mean protein number. This file uses
   that simplified form, not Swain's full Phi0/Phi1 machinery, because
   the full form needs time-resolved parameters (f0, k0, b0, td) this
   project does not have for any BBB promoter.
2. Transcription, not translation, dominates intrinsic noise whenever
   b >> 2 (their Eq. 20). The paper states burst size "may be of order
   tens" in E. coli, though individual translation rates vary widely --
   this is an E. COLI literature range, not a B. subtilis measurement,
   and is used below only to bound plausible scenarios, not asserted as
   this project's real value.
3. Noise scales as ~1/n with gene copy number n. This is the quantitative
   backing for a design choice BENCH_PROTOCOL_BSUBTILIS.md Section 2.2
   already makes on qualitative grounds: chromosomal (single-copy)
   integration keeps copy number from drifting during Stage B2's regrowth
   experiment, and this file shows WHY single-copy is also the noisIER
   choice, not noise-neutral, a real, quantified cost of that design
   decision.
4. A steady-state approximation that ignores the cell cycle (treating
   Phi0 = Phi1 = 1 in their notation) can overestimate intrinsic noise by
   as much as 65% (their Eq. 22 discussion). Flagged here as a caveat for
   any future refinement of this noise model's timing, not implemented.

WHAT THIS DOES NOT DO:
This file does not replace bsubtilis_01_gardner_toggle_circuit.py's noise
model. It computes what a range of PLAUSIBLE (burst size, mean protein
level) combinations imply for intrinsic noise magnitude, using the cited
formula, and compares that range against the currently-hardcoded
tx_noise_std=3.0 placeholder, to show how wide the real uncertainty is
and what Stage B1 / wet_lab_experiments/Experiment_2 needs to measure
(burst size and mean expression level for the actual BBB promoter pair)
to collapse that range to one real number. No B. subtilis-specific number
is invented; the swept ranges are explicitly labeled as illustrative or
as the E. coli literature range this paper itself reports.
"""

import os
import sys
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from bsubtilis_01_gardner_toggle_circuit import GardnerParams


def intrinsic_noise_cv(burst_size: float, mean_protein: float) -> float:
    """eta_int^2 ~= (1+b)/<P>, the well-known asymptotic simplification of
    Swain et al. 2002's Eq. 19 (also in Thattai & van Oudenaarden 2001).
    Returns eta_int, the coefficient of variation (std/mean), not the
    variance."""
    return float(np.sqrt((1.0 + burst_size) / mean_protein))


def cv_to_absolute_std(eta: float, mean_value: float) -> float:
    """Converts a coefficient-of-variation noise value into an absolute
    standard deviation on the same numeric scale bsubtilis_01's GardnerParams
    uses (alpha1/alpha2 ~ tens, u/v steady-state values of that same order),
    so it can be compared directly against tx_noise_std."""
    return eta * mean_value


def sweep_burst_size_vs_placeholder(burst_sizes: List[float],
                                     mean_protein_levels: List[float],
                                     current_placeholder: float = 3.0) -> Dict:
    """For each (burst size, mean protein level) combination, computes the
    implied absolute noise std and compares it to the current uncited
    placeholder. mean_protein_levels are expressed on the same numeric
    scale as GardnerParams.alpha1 (dimensionless promoter-strength units,
    not real molecule counts, since no BBB promoter has been converted to
    a measured molecule count yet, see Stage B3 / Experiment 4)."""
    rows = []
    for b in burst_sizes:
        for p_mean in mean_protein_levels:
            eta = intrinsic_noise_cv(b, p_mean)
            abs_std = cv_to_absolute_std(eta, p_mean)
            rows.append({
                'burst_size': b,
                'mean_protein_level': p_mean,
                'eta_int_cv': eta,
                'implied_abs_std': abs_std,
                'ratio_to_placeholder': abs_std / current_placeholder,
            })
    return rows


def copy_number_scaling(copy_numbers: List[int], reference_eta: float = 0.2) -> Dict[int, float]:
    """eta^2 ~ 1/n (Swain et al. 2002): noise scales inversely with gene
    copy number. reference_eta is an arbitrary anchor (illustrative), the
    POINT is the relative scaling across copy numbers, which is what the
    chromosomal-vs-plasmid design choice actually trades on."""
    ref_n = copy_numbers[0]
    return {n: reference_eta * np.sqrt(ref_n / n) for n in copy_numbers}


def main():
    print("=" * 92)
    print("NOISE SCALING (Swain, Elowitz & Siggia 2002) — bounding the tx_noise_std placeholder")
    print("=" * 92)

    print("\nQuestion 1: for plausible (burst size, mean expression level) combinations, how")
    print("does the implied noise magnitude compare to the current tx_noise_std=3.0 placeholder")
    print("(GardnerParams.alpha1/alpha2 default to 50.0, used as the mean-level anchor)?\n")
    burst_sizes = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
    default_alpha = GardnerParams().alpha1
    mean_protein_levels = [default_alpha]
    rows = sweep_burst_size_vs_placeholder(burst_sizes, mean_protein_levels)
    print(f"{'Burst size b':<14}{'eta_int (CV)':>14}{'Implied abs. std':>20}{'x current placeholder':>24}")
    for r in rows:
        print(f"{r['burst_size']:<14}{r['eta_int_cv']:>14.3f}{r['implied_abs_std']:>20.2f}"
              f"{r['ratio_to_placeholder']:>24.2f}")

    print("\nQuestion 2: how much does noise change with gene copy number (n=1, chromosomal,")
    print("vs. a multi-copy plasmid), per eta^2 ~ 1/n?\n")
    copy_numbers = [1, 5, 10, 50]
    scaling = copy_number_scaling(copy_numbers)
    print(f"{'Copy number':<14}{'Relative eta_int':>18}")
    for n, eta in scaling.items():
        print(f"{n:<14}{eta:>18.3f}")

    print("\n" + "=" * 92)
    print("INTERPRETATION")
    print("=" * 92)
    print("Even at the LOWEST burst size tested (b=1), this formula implies noise about 3x the")
    print("current tx_noise_std=3.0 placeholder, and the gap widens to roughly 17x at b=50, the")
    print("high end of the 'order tens' range this paper's own E. coli characterization reports.")
    print("Taken at face value, this suggests the placeholder may be an UNDERESTIMATE across the")
    print("whole plausible range, not just at the high end, which would make the M3 severe-")
    print("mismatch failure mode worse and could erode M1/M2's current 100% fidelity margin.")
    print("This is exactly what wet_lab_experiments/Experiment_2 (Stage B1) is designed to measure:")
    print("real burst size and mean expression level for the ACTUAL promoter pair, which would")
    print("replace this whole table with the one real number that applies. Caveat: this simplified")
    print("(1+b)/<P> form omits Swain et al.'s own cell-cycle correction (their Eq. 22 finding that")
    print("ignoring it can overestimate noise by up to 65%), so treat this as a rough bound, not a")
    print("precise prediction.")
    print("\nThe copy-number result quantifies something BENCH_PROTOCOL_BSUBTILIS.md Section 2.2")
    print("already argues qualitatively: chromosomal (n=1) integration is the noisIER choice")
    print("compared to a multi-copy plasmid, a real, measured cost of the design decision made")
    print("to keep copy number from drifting during Stage B2's regrowth test, not a free choice.")
    print("See docs/SCIENTIFIC_AUDIT_2026.md Part 28.")
    print("=" * 92)


if __name__ == '__main__':
    main()
