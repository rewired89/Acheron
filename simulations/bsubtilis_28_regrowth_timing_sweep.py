"""
Acheron Simulation 28: How Much Slack Does the Regrowth Budget Really Have?
=====================================================================

PURPOSE:
bsubtilis_14_voltage_colony_regrowth.py found that at its worst damage level
(one surviving cell), regrowing to 64 cells takes 6 doubling rounds at 30
minutes each, leaving exactly 180 minutes of a 6 hour window, which is
exactly one 180 minute averaged electrical read and not a minute more. The
audit calls this zero margin. Two inputs behind it are assumptions, not
measurements: the 30 minute doubling time (survivors of damage are unlikely
to grow at the undisturbed rate) and the implicit assumption that the
colony is ready to be read the instant it is back at full size.

WHAT THIS DOES:
Re-runs the regrowth trial (the engine defined in
bsubtilis_27_noise_robustness_sweep.py, which at defaults reproduces
bsubtilis_07 and bsubtilis_14) across doubling times of 30, 45 and 60
minutes and a settling delay of 0, 30 and 60 minutes between "colony back to
full size" and "read can start", at 2, 5 and 20 percent survivors, with the
native potassium oscillation on at 30 and 70 mV. Reports, per cell of the
grid: genetic fidelity (what a fluorescent reporter would see), the
single-snapshot voltage read, the long-window voltage read, whether the
colony regrew in time, and how many minutes of window the read actually got.

WHAT THIS DOES NOT DO:
The doubling times and delays are a sweep axis, not measured values. The
settling delay is a placeholder for "whatever time a real sample needs
before the electrical read is valid", which nobody has measured. Everything
carried over from bsubtilis_14 (sinusoidal oscillation shape, majority vote
as a stand-in for a frequency sweep, deterministic partitioning) is
unchanged.
"""

import os
import sys
from multiprocessing import Pool
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from bsubtilis_27_noise_robustness_sweep import run_colony_trial_ex

DOUBLING_TIMES = [30.0, 45.0, 60.0]
DELAYS = [0.0, 30.0, 60.0]
FRACTIONS = [0.02, 0.05, 0.20]
AMPLITUDES = [30.0, 70.0]
N_TRIALS = 5


def _job(args: Tuple) -> Dict:
    frac, bit, seed, dbl, delay, amp = args
    return run_colony_trial_ex(frac, bit, seed, doubling_min=dbl,
                               equil_delay_min=delay, amplitude_mv=amp)


def main():
    jobs = [(f, b, int(f * 10000) + k * 97 + b, d, e, a)
            for a in AMPLITUDES for d in DOUBLING_TIMES for e in DELAYS
            for f in FRACTIONS for b in (0, 1) for k in range(N_TRIALS)]
    with Pool(4) as pool:
        out = pool.map(_job, jobs)

    cells: Dict[Tuple, List[Dict]] = {}
    for (f, b, s, d, e, a), r in zip(jobs, out):
        cells.setdefault((a, d, e, f), []).append(r)

    print("=" * 96)
    print("REGROWTH BUDGET: doubling time x settling delay (6 h window, 64-cell colony)")
    print("=" * 96)
    for a in AMPLITUDES:
        print(f"\n--- native oscillation {a:.0f} mV, 3 h period ---")
        print(f"{'doubl':>6}{'delay':>7}{'surv':>6}{'regrown':>9}{'genetic':>9}"
              f"{'V-snap':>8}{'V-window':>10}{'window min':>12}")
        for d in DOUBLING_TIMES:
            for e in DELAYS:
                for f in FRACTIONS:
                    rs = cells[(a, d, e, f)]
                    m = lambda k: float(np.mean([x[k] for x in rs]))
                    print(f"{d:>6.0f}{e:>7.0f}{f:>6.0%}{m('regrown'):>9.0%}"
                          f"{m('genetic'):>9.0%}{m('voltage_snapshot'):>8.0%}"
                          f"{m('voltage_window'):>10.0%}{m('window_used_min'):>12.0f}")

    print("\n" + "=" * 96)
    print("READ-ME: 'regrown' is the share of trials where the colony got back to 64 cells")
    print("inside 6 h. 'window min' is how much of the 180 min averaged read the budget")
    print("allowed. A V-window figure with a short window is a weaker read than the")
    print("bsubtilis_09 fix assumed; compare it against V-snap, which is the no-fix case.")
    print("Genetic fidelity is the reporter-readout case and does not use the window.")
    print("=" * 96)


if __name__ == '__main__':
    main()
