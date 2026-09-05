"""
Acheron Simulation 12: Does the Bacterium's Own Voltage Oscillator Corrupt
Our Engineered Bit?
================================================================================

PURPOSE:
Reading Ford, Fisher, Prindle & Chopp (2021, Bull Math Biol,
DOI 10.1007/s11538-021-00887-3, PMC8857140) and Mulder, Peters Kostman,
Almodaimegh, Edge & Larkin (2025, PLoS Comput Biol,
DOI 10.1371/journal.pcbi.1013746) surfaced a design consideration nobody
had flagged in this project before: B. subtilis biofilms run a REAL,
independent, endogenous voltage oscillator. Starving interior cells
release potassium and hyperpolarize; that signal propagates outward as a
wave (measured at ~10-50 microns/min, period ~2-4 hours, starting once a
biofilm reaches ~500 microns) that temporarily depolarizes/repolarizes
neighboring cells so nutrients can reach the colony's interior. This
happens whether or not we've engineered anything - it's the bacterium
regulating its own metabolism.

gardner_toggle_circuit.py's engineered toggle switch maps its two-repressor
genetic state onto membrane voltage through a "hypothetical ion-channel
expression link... the part nobody has built yet." If that circuit shares
membrane real estate with the biofilm's own native voltage machinery
(plausible - both are voltage-gated potassium channel activity), the
colony's OWN natural signaling could push a cell's voltage away from
whatever the engineered circuit says it should be, independent of
anything going wrong with the circuit itself.

WHAT THIS TESTS, PRECISELY:
Whether a periodic external voltage perturbation, sized and timed to match
the real ranges reported in the two papers above, corrupts the VOLTAGE
READOUT of an already-written, otherwise-healthy GardnerToggleCell.

WHAT THIS DELIBERATELY DOES NOT TEST:
Whether the native oscillation could flip the underlying GENETIC state
(u, v repressor dominance) itself, not just the voltage readout. That
would require assuming the native potassium/voltage activity feeds back
into the engineered circuit's own regulatory proteins - a real possibility
if the two systems share pathway components, but neither source paper
establishes that feedback exists, and this project's discipline throughout
has been not to assume a mechanism beyond what's cited. This file therefore
adds the oscillation as an external perturbation to V only, leaving u/v
untouched, and explicitly reports the genetic read as a control that should
stay unaffected - if it doesn't, that itself would be worth investigating
as a modeling bug, not a real biological finding, given how this file is
built.

UPDATE (September 2026): a third, separate paper narrows how conservative
that scoping choice actually is. Lundberg, Becker & Choe (2013), "MstX and
a Putative Potassium Channel Facilitate Biofilm Formation in Bacillus
subtilis," PLoS ONE 8(5):e60993, DOI 10.1371/journal.pone.0060993, PMID
23737939, name the channel behind the Prindle-lab potassium wave (yugO)
and show its own operon is repressed by SinR and, once active, drives K+
efflux that activates the histidine kinase KinC, which phosphorylates
Spo0A, which represses SinR - a real, published transcriptional feedback
loop sitting on exactly the SinR/Spo0A regulatory node this project's BBB
chassis promoters are drawn from. That is still not the same citation as
"the native oscillation flips THIS engineered circuit's u/v state" - this
paper describes yugO's own regulation, not a demonstrated link into a
Gardner-topology toggle - so the voltage-only scope below remains the
honest thing to simulate today. But it moves the un-tested genetic-feedback
scenario from "a real possibility, unestablished in the literature" to "a
mechanistically analogous loop is established in the literature, just not
yet for this specific engineered promoter" - worth a follow-up test if the
BBB promoter this project ultimately picks turns out to be SinR/Spo0A-
regulated itself.

GROUNDING FOR THE PERTURBATION PARAMETERS:
- Period: 2-4 hours, real range from both papers (simulated 3-4h, a
  comparison experiment in Martinez-Corral et al. ~2-3h, per Ford et al.
  2021's own text).
- Amplitude: neither paper's full text yielded an exact mV swing (their
  reported quantities were mostly relative fluorescence, ThT/APG, not raw
  millivolts). Rather than invent one true number, this sweeps amplitude
  from small (10 mV) up to a worst-case size comparable to our OWN
  circuit's entire signal range (GardnerToggleCell's V_HIGH=-10mV to
  V_LOW=-80mV is a 70mV spread) - i.e., a native oscillation strong enough
  to rival the engineered signal itself, the most adversarial case worth
  checking.
"""

import os
import sys
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from gardner_toggle_circuit import GardnerParams, GardnerToggleCell


def ambient_oscillation_offset(t_minutes: float, amplitude_mv: float,
                                period_hours: float) -> float:
    """Sinusoidal approximation of the native potassium-wave voltage swing
    reaching a cell. Real swings are wave-like, not perfectly sinusoidal,
    but a sinusoid is the honest minimal choice for an unmeasured waveform
    shape - same treatment as every other unmeasured-shape assumption in
    this project."""
    period_minutes = period_hours * 60.0
    return amplitude_mv * np.sin(2 * np.pi * t_minutes / period_minutes)


def run_interference_trial(bit: int, amplitude_mv: float, period_hours: float,
                            seed: int, hours: float = 24.0,
                            params: GardnerParams = None,
                            tx_noise: float = 3.0,
                            sample_every_min: float = 10.0) -> Dict:
    """One cell, written once, then run for `hours` while an ambient
    oscillation is added directly to its membrane voltage (NOT to u/v -
    see module docstring). Samples the voltage readout periodically to
    catch intermittent corruption, not just the final-time value."""
    params = params or GardnerParams()
    cell = GardnerToggleCell(params, seed=seed, transcriptional_noise_std=tx_noise)
    cell.write(bit)

    n_steps = int(hours * 60 / 1.0)
    samples = []
    for step_i in range(n_steps):
        cell.step(dt=0.02)
        t_minutes = (step_i + 1) * 1.0
        cell.V = float(np.clip(
            cell.V + ambient_oscillation_offset(t_minutes, amplitude_mv, period_hours),
            -120, 60))
        if t_minutes % sample_every_min < 1.0:
            samples.append(cell.read_voltage())

    voltage_samples_correct = np.mean([s == bit for s in samples]) if samples else float('nan')
    return {
        'genetic_correct': int(cell.read_genetic() == bit),
        'voltage_correct_final': int(cell.read_voltage() == bit),
        'voltage_correct_fraction': float(voltage_samples_correct),
    }


def sweep_amplitude(amplitudes: List[float], period_hours: float,
                     n_trials: int = 10) -> Dict[float, Dict]:
    results = {}
    for amp in amplitudes:
        gen_scores, volt_final_scores, volt_frac_scores = [], [], []
        for bit in [0, 1]:
            for trial in range(n_trials):
                seed = int(amp * 100) + trial * 37 + bit
                r = run_interference_trial(bit, amp, period_hours, seed)
                gen_scores.append(r['genetic_correct'])
                volt_final_scores.append(r['voltage_correct_final'])
                volt_frac_scores.append(r['voltage_correct_fraction'])
        results[amp] = {
            'genetic': float(np.mean(gen_scores)),
            'voltage_final': float(np.mean(volt_final_scores)),
            'voltage_time_avg': float(np.mean(volt_frac_scores)),
        }
    return results


def main():
    print("=" * 78)
    print("NATIVE VOLTAGE OSCILLATION vs. ENGINEERED BIT - interference test")
    print("=" * 78)
    print("\nDoes the biofilm's OWN potassium-signaling oscillation (real, measured")
    print("in Ford et al. 2021 / Mulder et al. 2025, not engineered by us) corrupt")
    print("the readout of an already-written toggle-switch bit?\n")

    amplitudes = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 70.0]  # mV

    for period_hours in [2.0, 3.0, 4.0]:
        print(f"\n--- Oscillation period = {period_hours:.0f}h (real range: 2-4h) ---")
        print(f"{'Amplitude (mV)':<18}{'Genetic':>12}{'Voltage(final)':>16}{'Voltage(time-avg)':>20}")
        results = sweep_amplitude(amplitudes, period_hours)
        for amp in amplitudes:
            r = results[amp]
            print(f"{amp:<18.0f}{r['genetic']:>11.0%}{r['voltage_final']:>16.0%}"
                  f"{r['voltage_time_avg']:>20.0%}")

    print("\n" + "=" * 78)
    print("INTERPRETATION")
    print("=" * 78)
    print("Genetic column should stay ~100% throughout (by construction - this file")
    print("does not feed the oscillation back into u/v, see docstring). If it isn't")
    print("~100%, that's this file's bug, not a real biological effect.")
    print("\nVoltage(final) is a single readout at hour 24 - easy to get lucky or")
    print("unlucky depending on where the sine wave happens to be at that instant.")
    print("Voltage(time-avg) is the honest number: the fraction of readouts, sampled")
    print("every 10 minutes across the full day, that would have returned the")
    print("correct bit. That's what a real repeated-reading protocol would see.")
    print("\nIf voltage(time-avg) degrades meaningfully even at amplitudes well below")
    print("our own circuit's 70mV signal range, that means the engineered circuit's")
    print("voltage READOUT layer, not the genetic memory itself, needs to be")
    print("electrically shielded or decoupled from the colony's native signaling -")
    print("a concrete, previously-unflagged wet-lab design requirement.")
    print("=" * 78)


if __name__ == '__main__':
    main()
