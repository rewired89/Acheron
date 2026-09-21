"""
Acheron Simulation 18: Does Reducing the Native Signal's Coupling Strength
Help More Than Timing Did?
================================================================================

PURPOSE:
Part 17 (`bsubtilis_11_phase_locked_readout.py`) found that trying to time a quick
read around the native oscillation mostly does not work, at realistic
oscillation strength, a single sample stays contaminated by residual
drift no matter when in the cycle it's taken. That leaves the founder's
other two ideas from the same conversation untested: instead of
outsmarting the interference, remove or shrink it at the source.

TWO REAL-WORLD MECHANISMS THIS MODELS AS ONE GENERIC PARAMETER:
1. Engineer the circuit's voltage output through a DIFFERENT ion channel
   than yugO (the channel Lundberg, Becker & Choe 2013, DOI
   10.1371/journal.pone.0060993, identify as carrying the native
   potassium-wave signal). If the two pathways don't share the same
   channel protein, coupling between them should be weaker, though not
   necessarily zero, they still share the same membrane and cytoplasm.
2. Delete yugO entirely from the engineering chassis strain (a real,
   documented knockout, same paper). This removes the native oscillation
   at its source rather than working around it downstream.

Both mechanisms do the same thing to this project's model: they reduce
how much of the native oscillation's amplitude actually reaches the
engineered circuit's membrane voltage. Neither mechanism has been chosen,
built, or measured, and this project has no citation for exactly how much
coupling reduction either one would achieve in practice (a partial
knockout, incomplete channel segregation, and any biofilm-formation side
effect from losing yugO, per Lundberg et al.'s own finding that yugO also
helps biofilm formation, are all real, wet-lab-only questions). So rather
than assume a number, this file sweeps a RESIDUAL COUPLING FRACTION from
100% (today's assumption, full shared-channel coupling, the baseline
already tested in bsubtilis_08_native_oscillation_interference.py) down to 0% (a
perfect, complete knockout/isolation, the best case), and reports how
much reduction is actually needed before readout recovers, at
realistic-length reading windows.

WHAT THIS TESTS, PRECISELY:
For a set of coupling-reduction levels, the SAME oscillation amplitudes
and period already used in bsubtilis_09_eis_readout_interference.py and
bsubtilis_11_phase_locked_readout.py, scaled down by the coupling fraction, fed into
the same GardnerToggleCell trajectory, read at several window lengths
(a single quick sample up to the full 180-minute average Part 13 already
validated). This directly answers: is it easier to fix this problem by
reducing the interference, or by reading longer? Or does it need both?

WHAT THIS DOES NOT DO:
This does not model yugO knockout's biofilm-formation cost, a different
channel's own expression/noise properties, or partial knockout penetrance
across a population, all real, separate, wet-lab-only questions. It only
answers the narrower, generic question: IF coupling could be reduced by
X%, how much would that help the readout, holding everything else in the
already-validated oscillation/circuit model fixed.
"""

import os
import sys
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from bsubtilis_01_gardner_toggle_circuit import GardnerParams
from bsubtilis_09_eis_readout_interference import run_trial_trajectory, eis_style_read


def sweep_coupling_and_window(base_amplitudes: List[float],
                               coupling_fractions: List[float],
                               window_minutes: List[int],
                               period_hours: float = 3.0,
                               n_trials: int = 8,
                               hours: float = 24.0,
                               n_readout_starts: int = 6) -> Dict:
    results = {}
    total_min = int(hours * 60)
    readout_starts = [int(i * total_min / n_readout_starts) for i in range(n_readout_starts)]

    for base_amp in base_amplitudes:
        for frac in coupling_fractions:
            effective_amp = base_amp * frac
            for window_min in window_minutes:
                scores = []
                for bit in [0, 1]:
                    for trial in range(n_trials):
                        seed = int(base_amp * 100) + trial * 53 + bit
                        voltage_reads, _ = run_trial_trajectory(
                            bit, effective_amp, period_hours, seed, hours=hours)
                        for start in readout_starts:
                            read = eis_style_read(voltage_reads, start, window_min)
                            scores.append(int(read == bit))
                results[(base_amp, frac, window_min)] = float(np.mean(scores))
    return results


def main():
    print("=" * 86)
    print("REDUCING NATIVE-SIGNAL COUPLING (different channel / knockout) vs. READING LONGER")
    print("=" * 86)
    print("\nBase amplitudes are the biofilm's real documented oscillation range (unchanged).")
    print("Coupling fraction = how much of that oscillation actually reaches OUR circuit's")
    print("voltage: 100% = today's worst-case assumption (shared channel), 0% = a perfect")
    print("knockout/isolation (best case, never achieved in practice). Unmeasured, swept.\n")

    base_amplitudes = [30.0, 70.0]   # a moderate and the worst-case real amplitude
    coupling_fractions = [1.0, 0.5, 0.25, 0.1, 0.0]
    window_minutes = [1, 15, 60, 180]
    period_hours = 3.0

    results = sweep_coupling_and_window(base_amplitudes, coupling_fractions, window_minutes,
                                         period_hours=period_hours)

    for base_amp in base_amplitudes:
        print(f"\n--- Base oscillation amplitude = {base_amp:.0f}mV (before any coupling reduction) ---")
        header = f"{'Coupling':<12}" + "".join(f"{f'{w}min':>10}" for w in window_minutes)
        print(header)
        for frac in coupling_fractions:
            row = f"{frac:<12.0%}"
            for w in window_minutes:
                row += f"{results[(base_amp, frac, w)]:>10.0%}"
            print(row)

    print("\n" + "=" * 86)
    print("INTERPRETATION")
    print("=" * 86)
    print("Compare the 1min column (a quick read, no averaging) as coupling fraction drops.")
    print("If 1min accuracy recovers well before coupling hits 0%, that means you don't")
    print("need a perfect knockout, a partial reduction plus a quick read may be enough,")
    print("a real, actionable engineering target instead of an all-or-nothing ask.")
    print("If 1min only recovers near 0% coupling, reducing coupling alone isn't enough")
    print("without also reading longer, meaning both fixes (Part 13's averaging AND a")
    print("lower-coupling design) may be needed together, not either one alone.")
    print("=" * 86)


if __name__ == '__main__':
    main()
