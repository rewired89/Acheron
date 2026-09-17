"""
Acheron Simulation 17: Phase-Locked Reading - Dodging the Native
Oscillation Instead of Averaging Through It
================================================================================

PURPOSE:
native_oscillation_interference.py found a single instantaneous voltage
snapshot collapses toward a coin flip under the colony's own real
potassium-wave oscillation. eis_readout_interference.py then found that
integrating a reading over time only recovers accuracy once the
integration window reaches close to a FULL oscillation period (~180
minutes at the 3h period tested), because averaging across a fraction of
a sine wave doesn't cancel it, only averaging across a whole cycle does.

Founder question (September 2026) that this file tests directly: instead
of averaging blindly through the whole cycle, what if we exploit knowing
roughly WHEN in the cycle the oscillation is naturally near zero (a
zero-crossing, twice per period), and take a quick reading right there
instead? A periodic sine wave crosses zero on a predictable schedule, so
in principle a reading timed to land on that schedule wouldn't need the
oscillation averaged out at all, it just wouldn't be there yet.

WHAT THIS TESTS, PRECISELY:
Using the SAME oscillation trajectories eis_readout_interference.py
already generates (same amplitude/period ranges, same GardnerToggleCell
circuit, same seeds-per-trial convention), this compares three reading
strategies applied to the identical underlying trajectory, so the
comparison is apples-to-apples, not just similar-conditions:
  (a) a single blind snapshot at a random moment (the original failure
      mode from native_oscillation_interference.py),
  (b) a ~180-minute EIS-style averaging window (the fix
      eis_readout_interference.py already validated),
  (c) NEW - a quick, near-instantaneous reading deliberately scheduled at
      the oscillation's predicted zero-crossings, swept across how much
      TIMING ERROR that prediction has (0 = perfect knowledge of the
      real rhythm's phase, up to 90 minutes = a very poor guess).

WHY THIS MATTERS IF IT WORKS:
Strategy (b) requires waiting through a ~180-minute measurement every
single time you want to read the bit. Strategy (c), if it tolerates
realistic timing error, would only require waiting for the next
predicted quiet moment (on average, HALF_PERIOD minutes away - e.g. ~90
min at a 3h period, same order of magnitude, but the reading ITSELF is
fast, not a 180-minute integration), and repeatable reads become cheaper.

THE HONEST LIMITATION THIS FILE CANNOT RESOLVE:
This only tests robustness to TIMING error, assuming the colony's real
oscillation is a clean, single-frequency, perfectly periodic sine wave
once it starts (the same simplifying assumption
native_oscillation_interference.py already makes and states plainly -
neither source paper reports an exact waveform shape). Ford et al. 2021
and Mulder et al. 2025 describe a real propagating wave whose onset
depends on biofilm size (~500 micron threshold) and whose period is
reported as a RANGE (2-4h), not a fixed, pre-known constant per colony.
Two real, unresolved questions this file does not answer: (1) whether a
real colony's oscillation is regular/periodic enough for a "predicted
zero-crossing schedule" to even mean anything over 24 hours, and (2) how
you would actually establish the phase in a real experiment without
already having a working non-destructive readout, this is inherently a
bootstrapping problem no simulation can resolve, only a real
instrumented colony (e.g. a parallel electrode tracking the oscillation
directly) could establish real achievable phase-error, which is why this
file sweeps a RANGE of assumed phase errors instead of asserting one.
"""

import os
import sys
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from gardner_toggle_circuit import GardnerParams
from eis_readout_interference import run_trial_trajectory, eis_style_read


def phase_locked_reads(voltage_reads: List[int], period_hours: float,
                        phase_error_std_min: float, rng: np.random.Generator) -> List[int]:
    """Reads scheduled at the oscillation's predicted zero-crossings
    (every half period), each perturbed by a timing-error draw
    representing imperfect knowledge of the real rhythm's phase."""
    period_min = period_hours * 60.0
    half_period = period_min / 2.0
    total_min = len(voltage_reads)
    schedule = np.arange(half_period, total_min, half_period)

    reads = []
    for t in schedule:
        jitter = rng.normal(0, phase_error_std_min) if phase_error_std_min > 0 else 0.0
        idx = int(np.clip(round(t + jitter), 0, len(voltage_reads) - 1))
        reads.append(voltage_reads[idx])
    return reads


def blind_single_reads(voltage_reads: List[int], rng: np.random.Generator,
                        n_reads: int = 8) -> List[int]:
    """Baseline: reads at random, phase-blind moments - the original
    failure mode from native_oscillation_interference.py, recomputed here
    on the SAME trajectories for a direct comparison."""
    idxs = rng.integers(0, len(voltage_reads), size=n_reads)
    return [voltage_reads[i] for i in idxs]


def sweep_phase_lock(amplitudes: List[float], period_hours: float,
                      phase_error_levels: List[float], n_trials: int = 8,
                      hours: float = 24.0, long_window_min: int = 180,
                      n_long_window_starts: int = 6) -> Dict:
    """n_long_window_starts spreads the 180-min baseline across several
    points in the day, matching eis_readout_interference.py's own
    n_readout_times=6 convention, so this file's baseline reproduction is
    a fair, comparably-sampled number against Part 13's documented result,
    not a noisier single-start approximation of it."""
    results = {}
    total_min = int(hours * 60)
    long_window_starts = [int(i * total_min / n_long_window_starts)
                           for i in range(n_long_window_starts)]

    for amp in amplitudes:
        blind_scores, long_window_scores = [], []
        phase_scores = {pe: [] for pe in phase_error_levels}

        for bit in [0, 1]:
            for trial in range(n_trials):
                seed = int(amp * 100) + trial * 53 + bit
                voltage_reads, _ = run_trial_trajectory(bit, amp, period_hours, seed, hours=hours)
                rng = np.random.default_rng(seed + 1)

                for r in blind_single_reads(voltage_reads, rng):
                    blind_scores.append(int(r == bit))

                for start in long_window_starts:
                    long_read = eis_style_read(voltage_reads, start, long_window_min)
                    long_window_scores.append(int(long_read == bit))

                for pe in phase_error_levels:
                    for r in phase_locked_reads(voltage_reads, period_hours, pe, rng):
                        phase_scores[pe].append(int(r == bit))

        results[amp] = {
            'blind': float(np.mean(blind_scores)),
            'long_window': float(np.mean(long_window_scores)),
            'phase_locked': {pe: float(np.mean(s)) for pe, s in phase_scores.items()},
        }
    return results


def main():
    print("=" * 82)
    print("PHASE-LOCKED READING - dodge the oscillation instead of averaging through it")
    print("=" * 82)

    amplitudes = [10.0, 20.0, 30.0, 50.0, 70.0]
    phase_error_levels = [0.0, 5.0, 15.0, 30.0, 60.0, 90.0]
    period_hours = 3.0  # midpoint of the real 2-4h range, matches eis_readout_interference.py

    print(f"\nOscillation period fixed at {period_hours:.0f}h (real range: 2-4h)")
    print(f"Long-window baseline: {180} min (the value eis_readout_interference.py found necessary)\n")

    results = sweep_phase_lock(amplitudes, period_hours, phase_error_levels)

    header = (f"{'Amplitude (mV)':<16}{'Blind':>8}{'180min avg':>12}"
              + "".join(f"{f'+/-{int(pe)}min':>10}" for pe in phase_error_levels))
    print(header)
    for amp in amplitudes:
        r = results[amp]
        row = f"{amp:<16.0f}{r['blind']:>7.0%} {r['long_window']:>11.0%} "
        for pe in phase_error_levels:
            row += f"{r['phase_locked'][pe]:>9.0%} "
        print(row)

    print("\n" + "=" * 82)
    print("INTERPRETATION")
    print("=" * 82)
    print("'Blind' = single random-moment snapshot (the original failure mode).")
    print("'180min avg' = the long-averaging fix eis_readout_interference.py validated.")
    print("'+/-Nmin' columns = a quick read timed to the oscillation's predicted quiet")
    print("moment, assuming that prediction is off by up to N minutes (0 = perfect")
    print("knowledge of the real rhythm's timing).")
    print("\nIf the +/-0min column matches or beats the 180min column, that confirms the")
    print("core idea: WHEN you read matters as much as HOW LONG you integrate for, and a")
    print("fast read timed correctly can replace a slow averaged one. If accuracy decays")
    print("quickly as timing error grows, that puts a real number on how precisely a wet-")
    print("lab protocol would need to track the colony's own rhythm for this to work -")
    print("something this project cannot determine without instrumenting a real colony,")
    print("see the module docstring's bootstrapping-problem caveat.")
    print("\nACTUAL RESULT, stated plainly (the hopeful hypothesis mostly did NOT hold up):")
    print("Even with PERFECT timing knowledge (+/-0min), the quick read only matches the")
    print("180min average at the lowest tested amplitude (10mV). At 20mV and above, a")
    print("perfectly-timed quick read lands at ~50%, a coin flip, no better than blind and")
    print("sometimes slightly worse. The likely reason: the oscillation is added into the")
    print("cell's voltage every minute, not just at the read instant, so by the time the")
    print("external wave's VALUE returns to zero, the cell's voltage has already been")
    print("dragged around for the better part of a half-cycle and hasn't fully settled")
    print("back - a single sample is contaminated by that residual drift regardless of")
    print("where in the cycle you catch it. This sharpens Part 13's finding rather than")
    print("contradicting it: it's not really about the waveform's instantaneous value at")
    print("sample time, it's about how much cumulative drift has built up, and only")
    print("integrating over enough of the cycle to average that drift out actually works.")
    print("A quick, well-timed read is not a shortcut around that, at least not in this")
    print("model. The one real exception in this sweep is the lowest amplitude (10mV),")
    print("where timing does help meaningfully and tolerates real timing error - worth")
    print("keeping in mind for a design that keeps native-signal interference small in")
    print("the first place (e.g. option 1/2 from the founder's own question this file")
    print("came from: a different channel, or a native-oscillation knockout strain).")
    print("=" * 82)


if __name__ == '__main__':
    main()
