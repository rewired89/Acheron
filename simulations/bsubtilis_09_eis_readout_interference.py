"""
Acheron Simulation 13: Does EIS Readout Survive the Native Oscillation
That Breaks Single-Snapshot Voltage Reading?
================================================================================

PURPOSE:
bsubtilis_08_native_oscillation_interference.py found that a single instantaneous
voltage snapshot, corrupted by the colony's own real potassium-signaling
oscillation (Ford et al. 2021; Mulder et al. 2025), collapses toward a
coin flip at oscillation amplitudes well below the biofilm's documented
real range. That file's own interpretation flagged electrical impedance
spectroscopy (EIS - Akabuogu, Zhang, Krašovec, Roberts & Waigh 2024,
Nano Letters 24(7):2234-2241, DOI 10.1021/acs.nanolett.3c04446) as a
candidate fix, since it measures something structurally different from a
single voltage value. This file tests that candidate fix directly, on the
SAME oscillation, instead of asserting it would help.

WHY EIS MIGHT BE DIFFERENT, MECHANISTICALLY (not just "it's a different
method" - the actual physical reason):
A real EIS measurement is not an instantaneous voltage sample. It applies
a small sinusoidal perturbation and sweeps it across a wide frequency
range (Akabuogu et al. swept ~0.2-10 Hz, taking real measurement time),
building an impedance spectrum from many perturbation cycles. That is
inherently a TIME-INTEGRATED measurement of the channel population's
response, not a snapshot of resting membrane potential at one instant.
This file models that difference directly: instead of reading the
membrane voltage once, it takes a majority vote of the voltage state
across a sweep window of realistic duration, and asks how long that
window needs to be before the ambient oscillation stops corrupting the
reading.

WHAT THIS DOES NOT DO:
This is NOT a literal electrochemical model of impedance spectra,
negative capacitance, or the Kch channel's gating kinetics - building
that would require modeling the actual equivalent-circuit elements
(R_ct, R_Kch, inductance L_Kch) Akabuogu et al. measured, which is a
real, separate research task. This file tests the SPECIFIC, more general
mechanistic claim that a time-integrated measurement outperforms a
single-instant one under this exact oscillation - a necessary condition
for EIS to help, not a full electrochemical simulation of EIS itself.
"""

import os
import sys
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from bsubtilis_01_gardner_toggle_circuit import GardnerParams, GardnerToggleCell
from bsubtilis_08_native_oscillation_interference import ambient_oscillation_offset


def run_trial_trajectory(bit: int, amplitude_mv: float, period_hours: float,
                          seed: int, hours: float = 24.0,
                          params: GardnerParams = None,
                          tx_noise: float = 3.0) -> Tuple[List[int], bool]:
    """One cell, written once, run for `hours` under the ambient oscillation.
    Returns a per-minute voltage-readout trace plus whether the genetic
    state stayed correct (control, same as bsubtilis_08_native_oscillation_interference.py)."""
    params = params or GardnerParams()
    cell = GardnerToggleCell(params, seed=seed, transcriptional_noise_std=tx_noise)
    cell.write(bit)

    n_steps = int(hours * 60 / 1.0)
    voltage_reads = []
    for step_i in range(n_steps):
        cell.step(dt=0.02)
        t_minutes = (step_i + 1) * 1.0
        cell.V = float(np.clip(
            cell.V + ambient_oscillation_offset(t_minutes, amplitude_mv, period_hours),
            -120, 60))
        voltage_reads.append(cell.read_voltage())

    return voltage_reads, cell.read_genetic() == bit


def eis_style_read(voltage_reads: List[int], readout_start_min: int,
                    window_min: int) -> int:
    """Simulates one EIS-style measurement taken starting at readout_start_min,
    integrating (majority vote) over window_min minutes of the trajectory -
    the discrete-time stand-in for sweeping a frequency range that takes
    real measurement time, instead of sampling one instant."""
    window = voltage_reads[readout_start_min: readout_start_min + max(1, window_min)]
    if not window:
        window = [voltage_reads[-1]]
    return 1 if np.mean(window) > 0.5 else 0


def sweep_windows(amplitudes: List[float], period_hours: float,
                   window_minutes: List[int], n_trials: int = 8,
                   n_readout_times: int = 6, hours: float = 24.0) -> Dict:
    """For each amplitude and window size, average accuracy across many
    trials AND many readout times spread through the day (a real reading
    could happen at any point in the colony's oscillation phase)."""
    results = {}
    readout_starts = [int(i * (hours * 60) / n_readout_times) for i in range(n_readout_times)]

    for amp in amplitudes:
        for window_min in window_minutes:
            scores = []
            for bit in [0, 1]:
                for trial in range(n_trials):
                    seed = int(amp * 100) + trial * 53 + bit
                    voltage_reads, _ = run_trial_trajectory(bit, amp, period_hours, seed, hours=hours)
                    for start in readout_starts:
                        read = eis_style_read(voltage_reads, start, window_min)
                        scores.append(int(read == bit))
            results[(amp, window_min)] = float(np.mean(scores))
    return results


def main():
    print("=" * 78)
    print("EIS-STYLE (TIME-INTEGRATED) READOUT vs. THE SAME NATIVE OSCILLATION")
    print("=" * 78)
    print("\nSame ambient oscillation that broke single-snapshot voltage reading in")
    print("bsubtilis_08_native_oscillation_interference.py. Question: does integrating the")
    print("readout over a realistic EIS sweep duration recover accuracy?\n")

    amplitudes = [10.0, 20.0, 30.0, 50.0, 70.0]
    # 1 min ~= single-snapshot baseline. 90-360 min added after the first pass
    # showed no recovery at realistic EIS-sweep durations (minutes) - these
    # test whether recovery ever happens, at windows approaching/exceeding
    # the oscillation's own period (180 min at the fixed 3h period below).
    window_minutes = [1, 5, 15, 30, 60, 90, 180, 360]
    period_hours = 3.0   # midpoint of the real 2-4h range

    print(f"Oscillation period fixed at {period_hours:.0f}h (real range: 2-4h)\n")
    results = sweep_windows(amplitudes, period_hours, window_minutes)

    header = f"{'Amplitude (mV)':<18}" + "".join(f"{f'{w}min':>10}" for w in window_minutes)
    print(header)
    for amp in amplitudes:
        row = f"{amp:<18.0f}"
        for w in window_minutes:
            row += f"{results[(amp, w)]:>10.0%}"
        print(row)

    print("\n" + "=" * 78)
    print("INTERPRETATION - the hopeful hypothesis did NOT hold up as expected")
    print("=" * 78)
    print("The 1-60 minute columns, which cover the realistic duration of an actual")
    print("EIS frequency sweep (Akabuogu et al. swept ~0.2-10 Hz, a measurement of")
    print("seconds to a few minutes in practice), stay just as degraded as the")
    print("single-snapshot baseline - sometimes slightly WORSE, since a short")
    print("majority-vote window can lock in confidently on whatever side of the")
    print("oscillation it happened to land on. Accuracy only recovers once the")
    print("integration window reaches ~180 minutes, which is exactly ONE FULL")
    print("PERIOD of this run's 3-hour oscillation - averaging across a complete")
    print("cycle cancels the sine wave; averaging across a fraction of one does not.")
    print("\nHONEST CONCLUSION: a single real-world EIS measurement, which takes")
    print("minutes, would NOT be immune to this interference - it inherits the same")
    print("readout corruption single-snapshot voltage reading has, because the")
    print("oscillation's ~2-4 hour period is far slower than any one EIS sweep.")
    print("EIS's real advantage here isn't that one measurement 'sees through' the")
    print("oscillation - it's that EIS is cheap and non-destructive enough to")
    print("repeat MANY times across a multi-hour window and combine those readings")
    print("(explicitly not modeled in this file), which single-shot destructive")
    print("sequencing could never do. That's a genuine advantage, but a different,")
    print("more specific one than 'EIS averages it out in one sweep' - the initial")
    print("hypothesis this file was built to check.")
    print("=" * 78)


if __name__ == '__main__':
    main()
