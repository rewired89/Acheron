"""
Acheron Simulation 21: The Electrical Reader, Damage/Regrowth, and the
Native Oscillation - All Three Combined
================================================================================

PURPOSE:
Three results have existed separately and never been run together:
`bsubtilis_07_colony_regrowth.py` (genetic memory survives division-based
damage/regrowth down to 2% survivors), `bsubtilis_08_native_oscillation_interference.py`
(a single voltage snapshot collapses toward chance under the biofilm's
own real potassium-wave signaling), and `bsubtilis_09_eis_readout_interference.py`
(averaging the voltage read over ~180 minutes, close to a full
oscillation period, recovers accuracy). This file runs all three
mechanisms on the SAME simulated colony at once: damage it, let it
regrow by division while the native oscillation is running throughout
(not just after regrowth finishes), then read the result both ways, a
single instantaneous snapshot and a long, EIS-style averaged window, and
reports whether the already-validated 180-minute fix still works once
real damage and regrowth are also in the picture, not just an
undisturbed, already-written cell.

WHY THIS ISN'T JUST "THE SAME TWO RESULTS ADDED TOGETHER":
A badly damaged colony (very few survivors) takes longer to regrow back
to full size (more doubling rounds needed) than a lightly damaged one.
`bsubtilis_07_colony_regrowth.py` runs everything inside one fixed
real-world window (SETTLE_WINDOW_HOURS = 6h). If regrowth eats further
into that budget for worse damage, there is less time left afterward for
a long EIS-style average, a real, previously-untested interaction
between how much damage happened and how much clean reading time is left
before this project's own recovery deadline. This file measures that
directly (`settle_minutes_available`) instead of assuming the two
results simply compose.

WHAT THIS DOES NOT DO:
Same limitations already stated in the three files this combines:
deterministic (not stochastic) partition inheritance at division
(`bsubtilis_07_colony_regrowth.py`), a sinusoidal approximation of the real
oscillation's shape since neither source paper reports the true waveform
(`bsubtilis_08_native_oscillation_interference.py`), and a majority-vote stand-in for
a real EIS frequency sweep rather than a literal electrochemical model
(`bsubtilis_09_eis_readout_interference.py`). All three caveats carry over unchanged.
"""

import os
import sys
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from bsubtilis_01_gardner_toggle_circuit import GardnerParams, GardnerToggleCell
from bsubtilis_07_colony_regrowth import DOUBLING_TIME_MIN, SETTLE_WINDOW_HOURS
from bsubtilis_08_native_oscillation_interference import ambient_oscillation_offset
from bsubtilis_09_eis_readout_interference import eis_style_read


def run_colony_trial(surviving_fraction: float, target_bit: int, seed: int,
                      amplitude_mv: float, period_hours: float,
                      n_cells: int = 64, params: GardnerParams = None,
                      long_window_min: int = 180) -> Dict[str, float]:
    """One colony regrowth trial under continuous native-oscillation
    interference. Returns genetic fidelity (control, should stay ~100%
    per bsubtilis_08_native_oscillation_interference.py's own scoping choice), a
    single-snapshot voltage read, and a long-window (EIS-style) voltage
    read, plus how many minutes were actually available for that window
    after regrowth finished within the fixed settle budget."""
    params = params or GardnerParams()
    rng = np.random.default_rng(seed)

    n_survivors = max(1, int(round(n_cells * surviving_fraction))) if surviving_fraction > 0 else 0
    if n_survivors == 0:
        return {'genetic': 0.0, 'voltage_snapshot': 0.0, 'voltage_window': 0.0,
                'settle_minutes_available': 0.0}

    cells = []
    for _ in range(n_survivors):
        c = GardnerToggleCell(params, seed=int(rng.integers(0, 2**31)),
                               transcriptional_noise_std=3.0)
        c.write(target_bit)
        cells.append(c)

    total_minutes = SETTLE_WINDOW_HOURS * 60.0
    elapsed = 0.0
    t_abs = 0.0

    while len(cells) < n_cells and elapsed < total_minutes:
        for _ in range(int(DOUBLING_TIME_MIN / 1.0)):
            t_abs += 1.0
            for c in cells:
                c.step(dt=0.02)
                c.V = float(np.clip(
                    c.V + ambient_oscillation_offset(t_abs, amplitude_mv, period_hours),
                    -120, 60))
        elapsed += DOUBLING_TIME_MIN
        new_cells = []
        for c in cells:
            daughter = GardnerToggleCell(params, seed=int(rng.integers(0, 2**31)),
                                          transcriptional_noise_std=3.0)
            daughter.u, daughter.v = c.u, c.v
            daughter.V = c.V
            new_cells.append(daughter)
            if len(cells) + len(new_cells) >= n_cells:
                break
        cells.extend(new_cells)
        cells = cells[:n_cells]

    remaining_minutes = int(max(0.0, total_minutes - elapsed))
    histories: List[List[int]] = [[] for _ in cells]
    for _ in range(remaining_minutes):
        t_abs += 1.0
        for i, c in enumerate(cells):
            c.step(dt=0.02)
            c.V = float(np.clip(
                c.V + ambient_oscillation_offset(t_abs, amplitude_mv, period_hours),
                -120, 60))
            histories[i].append(c.read_voltage())

    genetic_correct = sum(1 for c in cells if c.read_genetic() == target_bit) / len(cells)

    if remaining_minutes > 0:
        snapshot_correct = sum(1 for h in histories if h[-1] == target_bit) / len(histories)
        window = min(long_window_min, remaining_minutes)
        window_correct = sum(
            1 for h in histories if eis_style_read(h, len(h) - window, window) == target_bit
        ) / len(histories)
    else:
        snapshot_correct = sum(1 for c in cells if c.read_voltage() == target_bit) / len(cells)
        window_correct = snapshot_correct

    return {'genetic': genetic_correct, 'voltage_snapshot': snapshot_correct,
            'voltage_window': window_correct,
            'settle_minutes_available': float(remaining_minutes)}


def sweep_surviving_fraction(fractions: List[float], amplitude_mv: float,
                              period_hours: float, n_trials: int = 8) -> Dict[float, Dict]:
    results = {}
    for frac in fractions:
        genetic, snap, window, settle_min = [], [], [], []
        for bit in [0, 1]:
            for trial in range(n_trials):
                seed = int(frac * 10000) + trial * 97 + bit
                r = run_colony_trial(frac, bit, seed, amplitude_mv, period_hours)
                genetic.append(r['genetic'])
                snap.append(r['voltage_snapshot'])
                window.append(r['voltage_window'])
                settle_min.append(r['settle_minutes_available'])
        results[frac] = {
            'genetic': float(np.mean(genetic)),
            'voltage_snapshot': float(np.mean(snap)),
            'voltage_window': float(np.mean(window)),
            'settle_minutes_available': float(np.mean(settle_min)),
        }
    return results


def main():
    print("=" * 86)
    print("DAMAGE + REGROWTH + NATIVE OSCILLATION, ALL THREE AT ONCE (electrical readout)")
    print("=" * 86)

    fractions = [0.02, 0.05, 0.10, 0.20, 0.50, 1.0]
    period_hours = 3.0

    for amplitude_mv in [30.0, 70.0]:
        print(f"\n--- Oscillation amplitude = {amplitude_mv:.0f}mV, period = {period_hours:.0f}h ---")
        print(f"{'Surviving':<12}{'Genetic':>10}{'V-snapshot':>12}{'V-window':>10}{'Settle min avail':>18}")
        results = sweep_surviving_fraction(fractions, amplitude_mv, period_hours)
        for frac, r in results.items():
            print(f"{frac:<12.0%}{r['genetic']:>9.0%} {r['voltage_snapshot']:>11.0%} "
                  f"{r['voltage_window']:>9.0%} {r['settle_minutes_available']:>17.0f}")

    print("\n" + "=" * 86)
    print("INTERPRETATION")
    print("=" * 86)
    print("Genetic should stay ~100% throughout (matches bsubtilis_07_colony_regrowth.py,")
    print("the oscillation is only ever added to voltage, never fed into u/v).")
    print("V-snapshot should degrade toward a coin flip, matching")
    print("bsubtilis_08_native_oscillation_interference.py's original finding, now shown surviving")
    print("through actual damage and regrowth, not just an undisturbed cell.")
    print("V-window should recover close to the level bsubtilis_09_eis_readout_interference.py found")
    print("(92-100% at 180min), IF enough settle time remains after regrowth - the")
    print("'Settle min avail' column shows whether the fixed 6h budget still leaves room")
    print("for that long a read even at the worst-tested damage level. If it doesn't,")
    print("that is a genuinely new constraint: worse damage costs regrowth time, which")
    print("directly competes with the time needed for a reliable electrical read, inside")
    print("whatever real-world checking window an eventual protocol allows.")
    print("=" * 86)


if __name__ == '__main__':
    main()
