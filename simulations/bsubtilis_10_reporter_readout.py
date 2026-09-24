"""
Acheron Simulation 16: Fluorescent Reporter Readout - Sidestepping the
Voltage Interface
=====================================================================

PURPOSE:
bsubtilis_01_gardner_toggle_circuit.py's own docstring flags the "hypothetical
ion-channel-expression link" (repressor state -> membrane voltage) as
having "no prior art at all - nobody has built or measured it, in any
organism." bsubtilis_08_native_oscillation_interference.py and bsubtilis_09_eis_readout_interference.py
then showed that even if that link is built, the biofilm's own native
potassium-wave signaling (Prindle et al. 2015; Ford, Fisher, Prindle &
Chopp 2021, DOI 10.1007/s11538-021-00887-3; Mulder, Peters Kostman,
Almodaimegh, Edge & Larkin 2025, DOI 10.1371/journal.pcbi.1013746)
corrupts a voltage readout unless it is integrated over close to a full
oscillation cycle (~3 hours).

External review (DeepSeek, brought to this project by the founder,
September 2026; logged in docs/SCIENTIFIC_AUDIT_2026.md Part 15) pointed
out an obvious alternative this project had modeled around but never
directly simulated: read the toggle switch's state through a standard
fluorescent transcriptional reporter (GFP for one arm, RFP for the other)
instead of through membrane voltage at all. Checked against this
project's own docs/pitch/Acheron_Validation_Proposal.docx, this isn't a
new idea to the project, Stage 0 already reads bistability through a
transcriptional reporter assay (lacZ/lux), for the same reason. This file
is the simulation that was missing: a reporter-readout version of
bsubtilis_01_gardner_toggle_circuit.py itself, so the "genetic fidelity" number that
file already reports has a directly comparable "reporter fidelity"
column, the same way it already has a "voltage fidelity" column.

WHY THIS SIDESTEPS THE INTERFERENCE PROBLEM, MECHANISTICALLY, NOT JUST
BY NOT MODELING IT:
The native potassium-wave oscillation acts on membrane voltage because it
IS voltage-gated potassium channel activity (yugO, per Lundberg, Becker &
Choe 2013, DOI 10.1371/journal.pone.0060993). It has no established
mechanism for altering transcription rate, translation rate, or
fluorescent-protein chromophore maturation, the three processes that set
GFP/RFP concentration. This file therefore does not add an oscillation
term to the reporter pathway at all, that would be modeling a coupling
nobody has proposed, the same discipline
bsubtilis_08_native_oscillation_interference.py's own docstring applies to keeping the
oscillation OUT of the genetic (u/v) state. The absence of an
interference test here is the point, not an oversight: the fluorescent
pathway and the native oscillation act on physically different state
variables (protein concentration vs. membrane potential), so there is
nothing analogous to simulate. What IS simulated is the reporter
pathway's own realistic stressors: transcriptional noise, protein
maturation delay, growth dilution, and measurement noise, which is the
correct like-for-like replacement for the voltage-noise sweep in
bsubtilis_01_gardner_toggle_circuit.py.

GROUNDING FOR THE REPORTER-DYNAMICS PARAMETERS:
- Maturation: Balleza, Kim & Cluzel (2018, Nature Methods 15:47-51,
  DOI 10.1038/nmeth.4509, PMID 29320486) systematically measured
  maturation kinetics for 50 fluorescent proteins in E. coli and found
  first-order (single- or two-exponential) kinetics with substantial,
  variant-dependent differences in half-time. Their exact per-variant
  minute values live in that paper's figures/tables, which this project
  could not extract as machine-readable numbers, and none of it was
  measured in B. subtilis specifically. Rather than invent one number,
  per docs/THIRD_PARTY_METHODS.md's no-numeric-invention rule, this file
  sweeps maturation half-time across a broad range (5-60 minutes) and
  reports where the reporter readout is and isn't sensitive to it.
- Degradation vs. dilution: Andersen, Sternberg, Poulsen, Bjorn, Givskov &
  Molin (1998, Appl Environ Microbiol 64(6):2240-2246,
  DOI 10.1128/AEM.64.6.2240-2246.1998, PMID 9603842) built degradation-tagged
  "unstable" GFP variants with measured half-lives of 40 minutes to a few
  hours in E. coli and P. putida (not B. subtilis), specifically so GFP
  could report fast transcriptional dynamics instead of accumulating
  indefinitely. Untagged, wild-type GFP is not a substrate for that
  degradation pathway, so its loss from a growing cell is dominated by
  growth dilution, not active decay. This file therefore models reporter
  loss as growth dilution only (no degradation term), consistent with a
  standard, untagged GFP/RFP reporter, not a destabilized one.
- Growth dilution rate: ~30 minute doubling time, the same typical
  B. subtilis figure already used elsewhere in this project
  (bsubtilis_07_colony_regrowth.py, methylation_01_bit_encoding.py).
- Measurement noise (imaging/segmentation/plate-reader noise on the final
  fluorescence reading): no literature figure was sought or used. This is
  a swept sensitivity parameter, not a claimed real value, same treatment
  as `bistable_k` before Part 9 replaced it and as `tx_noise` in
  bsubtilis_01_gardner_toggle_circuit.py itself.

WHAT THIS DOES NOT DO:
This does not simulate real GFP/RFP spectral crosstalk, photobleaching,
autofluorescence, or population heterogeneity in reporter copy number,
all real second-order effects a wet-lab test would encounter. It also
does not replace the actual measurement Stage 0 of the Validation
Proposal calls for, reporter output (lacZ/lux) has never been measured
for this specific circuit in living B. subtilis. Like every other file in
this project, this is a grounded design/sensitivity tool for deciding
what to build and where to look for trouble before spending wet-lab money,
not a validated result.

MODEL:
Same dimensionless Gardner repressor ODE as bsubtilis_01_gardner_toggle_circuit.py:
    du/dt = alpha1 / (1 + v^beta) - u
    dv/dt = alpha2 / (1 + u^gamma) - v
Reporter layer (real time, per-minute units), one two-stage
(immature -> mature) pool per arm:
    d[GFP_dark]/dt   = promoter1_activity - (k_mat + k_dil) * GFP_dark
    d[GFP_bright]/dt = k_mat * GFP_dark - k_dil * GFP_bright
    d[RFP_dark]/dt   = promoter2_activity - (k_mat + k_dil) * RFP_dark
    d[RFP_bright]/dt = k_mat * RFP_dark - k_dil * RFP_bright
where promoter1_activity / promoter2_activity are the same Hill-function
terms driving du/dt and dv/dt (normalized to 0-1), k_mat = ln(2)/maturation
half-life, k_dil = ln(2)/doubling time. Read bit = whichever mature
reporter pool dominates.
"""

import os
import sys
from dataclasses import dataclass
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from bsubtilis_01_gardner_toggle_circuit import GardnerParams


class GardnerToggleReporterCell:
    """Gardner repressor dynamics identical to GardnerToggleCell (see
    bsubtilis_01_gardner_toggle_circuit.py for the Gardner et al. 2000 citation), read
    out through a two-arm fluorescent transcriptional reporter instead of
    through the hypothetical repressor->ion-channel->voltage link."""

    def __init__(self, params: GardnerParams, seed: int = None,
                 transcriptional_noise_std: float = 0.0,
                 maturation_halflife_min: float = 20.0,
                 doubling_time_min: float = 30.0,
                 reporter_measurement_noise_std: float = 0.05):
        self.p = params
        self.rng = np.random.default_rng(seed)
        self.tx_noise = transcriptional_noise_std
        self.k_mat = np.log(2) / maturation_halflife_min
        self.k_dil = np.log(2) / doubling_time_min
        self.meas_noise = reporter_measurement_noise_std
        self.u, self.v = 0.0, 0.0
        self.gfp_dark, self.gfp_bright = 0.0, 0.0
        self.rfp_dark, self.rfp_bright = 0.0, 0.0

    def write(self, bit: int):
        """Transient induction pulse, identical convention to
        GardnerToggleCell.write()."""
        if bit == 1:
            self.u, self.v = self.p.alpha1, 0.0
        else:
            self.u, self.v = 0.0, self.p.alpha2 * self.p.strength_ratio

    def step(self, dt: float = 0.02, dt_minutes: float = 1.0):
        prom1_raw = self.p.alpha1 / (1 + self.v ** self.p.beta)
        prom2_raw = (self.p.alpha2 * self.p.strength_ratio) / (1 + self.u ** self.p.gamma)

        # repressor ODE - identical dynamics to GardnerToggleCell.step()
        du = prom1_raw - self.u
        dv = prom2_raw - self.v
        if self.tx_noise > 0:
            du += self.rng.normal(0, self.tx_noise)
            dv += self.rng.normal(0, self.tx_noise)
        self.u = max(0.0, self.u + du * dt)
        self.v = max(0.0, self.v + dv * dt)

        # reporter layer, real per-minute units, normalized promoter output
        prom1 = prom1_raw / self.p.alpha1
        prom2 = prom2_raw / (self.p.alpha2 * self.p.strength_ratio)
        d_gfp_dark = prom1 - (self.k_mat + self.k_dil) * self.gfp_dark
        d_gfp_bright = self.k_mat * self.gfp_dark - self.k_dil * self.gfp_bright
        d_rfp_dark = prom2 - (self.k_mat + self.k_dil) * self.rfp_dark
        d_rfp_bright = self.k_mat * self.rfp_dark - self.k_dil * self.rfp_bright
        self.gfp_dark = max(0.0, self.gfp_dark + d_gfp_dark * dt_minutes)
        self.gfp_bright = max(0.0, self.gfp_bright + d_gfp_bright * dt_minutes)
        self.rfp_dark = max(0.0, self.rfp_dark + d_rfp_dark * dt_minutes)
        self.rfp_bright = max(0.0, self.rfp_bright + d_rfp_bright * dt_minutes)

    def read_genetic(self) -> int:
        return 1 if self.u > self.v else 0

    def read_reporter(self) -> int:
        gfp_obs = self.gfp_bright * (1 + self.rng.normal(0, self.meas_noise))
        rfp_obs = self.rfp_bright * (1 + self.rng.normal(0, self.meas_noise))
        return 1 if gfp_obs > rfp_obs else 0


def run_persistence(bit: int, params: GardnerParams, hours: float = 24.0,
                     seed: int = 0, tx_noise: float = 0.0,
                     maturation_halflife_min: float = 20.0,
                     reporter_measurement_noise_std: float = 0.05) -> Dict:
    cell = GardnerToggleReporterCell(
        params, seed=seed, transcriptional_noise_std=tx_noise,
        maturation_halflife_min=maturation_halflife_min,
        reporter_measurement_noise_std=reporter_measurement_noise_std)
    cell.write(bit)
    n_steps = int(hours * 60 / 1.0)
    for _ in range(n_steps):
        cell.step(dt=0.02)
    return {
        'genetic_correct': int(cell.read_genetic() == bit),
        'reporter_correct': int(cell.read_reporter() == bit),
        'final_u': cell.u, 'final_v': cell.v,
        'final_gfp': cell.gfp_bright, 'final_rfp': cell.rfp_bright,
    }


def sweep_ratio_and_noise(ratios: List[float], tx_noise_levels: Dict[str, float],
                           n_trials: int = 15) -> None:
    print(f"{'Promoter strength ratio':<28}{'Genetic fidelity':>18}{'Reporter fidelity':>19}")
    for noise_name, tx_noise in tx_noise_levels.items():
        print(f"\n--- {noise_name} (tx_noise_std={tx_noise}) ---")
        for ratio in ratios:
            params = GardnerParams(strength_ratio=ratio)
            gen_correct, rep_correct = 0, 0
            for bit in [0, 1]:
                for trial in range(n_trials):
                    r = run_persistence(bit, params, hours=24.0,
                                         seed=trial * 100 + bit, tx_noise=tx_noise)
                    gen_correct += r['genetic_correct']
                    rep_correct += r['reporter_correct']
            total = n_trials * 2
            print(f"{ratio:<28}{gen_correct/total:>17.0%}{rep_correct/total:>19.0%}")


def sweep_maturation_and_measurement_noise(n_trials: int = 15) -> None:
    """The reporter pathway's own realistic stressors, the like-for-like
    replacement for bsubtilis_01_gardner_toggle_circuit.py's channel/thermal voltage
    noise sweep. Both axes are explicitly unmeasured-for-this-system
    placeholders (see module docstring), swept rather than assumed."""
    params = GardnerParams(strength_ratio=1.0)
    halflives = [5.0, 10.0, 20.0, 40.0, 60.0]
    meas_noise_levels = [0.0, 0.05, 0.15, 0.30]

    print(f"\n{'Maturation t1/2 (min)':<24}", end="")
    for mn in meas_noise_levels:
        print(f"meas_noise={mn:<10}", end="")
    print()
    for halflife in halflives:
        print(f"{halflife:<24}", end="")
        for meas_noise in meas_noise_levels:
            rep_correct = 0
            for bit in [0, 1]:
                for trial in range(n_trials):
                    r = run_persistence(bit, params, hours=24.0,
                                         seed=trial * 100 + bit, tx_noise=3.0,
                                         maturation_halflife_min=halflife,
                                         reporter_measurement_noise_std=meas_noise)
                    rep_correct += r['reporter_correct']
            total = n_trials * 2
            print(f"{rep_correct/total:>17.0%}   ", end="")
        print()


def main():
    print("=" * 78)
    print("FLUORESCENT REPORTER READOUT - sidestepping the voltage interface")
    print("=" * 78)
    print("\nSame Gardner repressor circuit as bsubtilis_01_gardner_toggle_circuit.py. Read out")
    print("through a GFP/RFP transcriptional reporter instead of a hypothetical")
    print("repressor -> ion-channel -> membrane-voltage link.\n")

    ratios = [1.0, 2.0, 5.0, 10.0, 0.1]
    tx_noise_levels = {"No transcriptional noise": 0.0,
                        "Realistic transcriptional noise": 3.0}
    sweep_ratio_and_noise(ratios, tx_noise_levels)

    print("\n" + "-" * 78)
    print("REPORTER-PATHWAY SENSITIVITY: maturation half-life x measurement noise")
    print("(both axes unmeasured for this system - see module docstring)")
    print("-" * 78)
    sweep_maturation_and_measurement_noise()

    print("\n" + "=" * 78)
    print("INTERPRETATION")
    print("=" * 78)
    print("Compare the Reporter fidelity column above to bsubtilis_01_gardner_toggle_circuit.py's")
    print("Voltage fidelity column at the same promoter ratio / tx_noise combination.")
    print("Both start from the identical repressor circuit, so any gap between them")
    print("is entirely attributable to the readout layer, not the underlying memory.")
    print("\nNo native-oscillation interference sweep is included here on purpose:")
    print("the potassium-wave mechanism that corrupts voltage readout in")
    print("bsubtilis_08_native_oscillation_interference.py acts on membrane voltage specifically")
    print("(it IS voltage-gated channel activity). Nothing in the cited literature")
    print("proposes a mechanism by which it would also alter transcription,")
    print("translation, or chromophore maturation, so adding that coupling here")
    print("would be simulating an unproposed effect, not a documented risk.")
    print("\nIf reporter fidelity tracks genetic fidelity closely across the")
    print("maturation/measurement-noise sweep, that is the computational case for")
    print("doing Stage 0 of the Validation Proposal with a fluorescent reporter")
    print("(or the lacZ/lux reporter it already specifies) before ever attempting")
    print("the harder, EIS-based voltage interface in Stage 3.")
    print("=" * 78)


if __name__ == '__main__':
    main()
