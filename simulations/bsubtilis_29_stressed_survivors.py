"""
Acheron Simulation 29: What If the Survivors of Damage Are Not Healthy?
=====================================================================

PURPOSE:
Every damage and regrowth result in this project (bsubtilis_07, 13, 14, 15)
treats damage as removing cells and nothing else: the survivors then behave
exactly like undamaged cells. The simulation README lists this as a known gap
(No. 4), and Stage B2 arm 2b of the bench protocol is designed to measure it.
Real damage also stresses survivors. Three consequences are plausible and
have never been tried here: survivors divide more slowly, their gene
expression gets noisier, and their membrane voltage shifts.

WHAT THIS DOES:
Using the parameterised engine in bsubtilis_27_noise_robustness_sweep.py
(which at defaults reproduces bsubtilis_07 and bsubtilis_14), applies a
STRESS WINDOW after damage in which survivors get any combination of:
  - a slower doubling time (multiplier on the 30 minute baseline),
  - higher transcriptional noise (multiplier on the placeholder),
  - a steady voltage shift (mV, either sign), which is added to the voltage
    only and never to the genetic state.
After the stress window the survivors return to normal. Three sweeps:
A) growth penalty x voltage shift (stress ends before the read, and stress lasting the whole window), B) growth penalty x noise rise,
C) stress-window length at a harsh combination.
Reports genetic fidelity (what a fluorescent reporter would see) next to
the long-window voltage read, so the two readouts can be compared directly.

WHAT THIS DOES NOT DO:
No stress magnitude here is measured. Each is a sweep axis, so the output is
a map of how much stress the result tolerates, not a prediction of how much
there will be. Stress is applied uniformly to all survivors, with no
cell-to-cell variation in how stressed each one is, and the voltage shift is
a steady offset, not a modelled physiological response (for example loss of
the proton gradient). Whether a damaged cell's voltage moves up or down is
not known to this project, so both signs are swept.
"""

import os
import sys
from multiprocessing import Pool
from typing import Dict, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from bsubtilis_27_noise_robustness_sweep import run_colony_trial_ex

FRACTIONS = [0.02, 0.20]
N_TRIALS = 6
GROWTH = [1.0, 1.5, 2.0, 3.0]
SHIFTS = [-40.0, -20.0, 0.0, 20.0, 40.0]
NOISE = [1.0, 3.0, 10.0]
STRESS_MIN = 180.0


def _job(args: Tuple) -> Dict:
    frac, bit, seed, kw = args
    return run_colony_trial_ex(frac, bit, seed, **kw)


def _run(grid):
    """grid: list of (key, kwargs). Returns {key: {frac: (genetic, window)}}."""
    jobs, keys = [], []
    for key, kw in grid:
        for f in FRACTIONS:
            for b in (0, 1):
                for k in range(N_TRIALS):
                    jobs.append((f, b, int(f * 10000) + k * 97 + b, kw))
                    keys.append((key, f))
    with Pool(4) as pool:
        out = pool.map(_job, jobs)
    acc: Dict = {}
    for (key, f), r in zip(keys, out):
        acc.setdefault(key, {}).setdefault(f, []).append(r)
    return {key: {f: (float(np.mean([x['genetic'] for x in v])),
                      float(np.mean([x['voltage_window'] for x in v])))
                  for f, v in d.items()} for key, d in acc.items()}


def main():
    for dur in (STRESS_MIN, 360.0):
        print("=" * 92)
        print(f"A) GROWTH PENALTY x VOLTAGE SHIFT (stress window {dur:.0f} min, no extra noise)")
        print("   cells show  genetic / V-window, at 2% then 20% survivors")
        print("=" * 92)
        grid = [((g, s), dict(stress_minutes=dur, stress_doubling_multiplier=g,
                              stress_shift_mv=s)) for g in GROWTH for s in SHIFTS]
        res = _run(grid)
        print(f"{'slower x':<9}{'shift mV':>9}   {'2% surv':>14}   {'20% surv':>14}")
        for g in GROWTH:
            for s in SHIFTS:
                r = res[(g, s)]
                print(f"{g:<9.1f}{s:>+9.0f}   "
                      f"{r[0.02][0]:>6.0%} /{r[0.02][1]:>5.0%}   {r[0.20][0]:>6.0%} /{r[0.20][1]:>5.0%}")
        print()

    print("=" * 92)
    print("B) GROWTH PENALTY x NOISE RISE DURING STRESS (no voltage shift)")
    print("=" * 92)
    grid = [((g, n), dict(stress_minutes=STRESS_MIN, stress_doubling_multiplier=g,
                          stress_noise_multiplier=n)) for g in (1.0, 2.0) for n in NOISE]
    res = _run(grid)
    print(f"{'slower x':<9}{'noise x':>9}   {'2% surv':>14}   {'20% surv':>14}")
    for (g, n), r in sorted(res.items()):
        print(f"{g:<9.1f}{n:>9.0f}   "
              f"{r[0.02][0]:>6.0%} /{r[0.02][1]:>5.0%}   {r[0.20][0]:>6.0%} /{r[0.20][1]:>5.0%}")

    print("\n" + "=" * 92)
    print("C) STRESS-WINDOW LENGTH at 2x slower, 10x noise, +40 mV shift")
    print("=" * 92)
    grid = [(m, dict(stress_minutes=m, stress_doubling_multiplier=2.0,
                     stress_noise_multiplier=10.0, stress_shift_mv=40.0))
            for m in (60.0, 180.0, 360.0)]
    res = _run(grid)
    print(f"{'stress min':<11}   {'2% surv':>14}   {'20% surv':>14}")
    for m, r in sorted(res.items()):
        print(f"{m:<11.0f}   "
              f"{r[0.02][0]:>6.0%} /{r[0.02][1]:>5.0%}   {r[0.20][0]:>6.0%} /{r[0.20][1]:>5.0%}")

    print("\nRead-me: first number = genetic fidelity (reporter readout), second =")
    print("long-window voltage read (the unbuilt electrical readout). A voltage shift")
    print("only ever moves the second number. Growth penalty and noise rise are what")
    print("can move the first.")
    print("=" * 92)


if __name__ == '__main__':
    main()
