"""
Acheron Simulation 31: Noise That Does Not Depend on the Step Size, and a
Rerun of the Noise-Sensitive Results
=====================================================================

PURPOSE:
Audit Part 31 found that GardnerToggleCell.step in bsubtilis_01 adds its random
kick to the derivative and then multiplies by dt, so the noise intensity per
unit time changes with the step size (measured: halving dt cut the repressor
level's standard deviation by roughly half). A correctly discretized noisy
equation scales the kick by the square root of dt, so the noise intensity per
unit time does not change when the step does. This file:

1. Defines GardnerToggleCellSDE, a subclass (the original is imported, never
   modified) whose noise is dt independent. Its noise parameter keeps the OLD
   meaning at the reference step: `transcriptional_noise_std = tx` gives the
   same noise as the old class with that tx at dt = 0.02, because
   sigma = tx * sqrt(0.02) and a step of 0.02 then adds sigma * sqrt(0.02) * Z =
   tx * 0.02 * Z, exactly the old increment. At substeps = 1 the two classes
   therefore produce identical numbers (checked below). With substeps > 1 the
   SAME stochastic equation is integrated more finely.
2. Shows the dt dependence of the old class and the dt independence of the new
   one.
3. Reruns the single-cell noise sweep, the colony recovery sweep, and headline
   cells of the timing (bsubtilis_28) and stress (bsubtilis_29) sweeps with finer
   integration, and compares them with the original results.

WHAT THIS DOES NOT DO:
It does not give the noise a physical scale. tx is still a sweep axis, not a
measured quantity. Relating it to molecules per cell and burst size is the job
of bsubtilis_32_analytic_and_gillespie_crosscheck.py. Rerun results are the same
model integrated more accurately, not a different model.
"""

import os
import sys
from multiprocessing import Pool
from typing import List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from bsubtilis_01_gardner_toggle_circuit import GardnerParams, GardnerToggleCell

DT_REF = 0.02


class GardnerToggleCellSDE(GardnerToggleCell):
    """Gardner toggle with dt-independent noise (square-root-of-dt scaling).

    `transcriptional_noise_std` is the old per-step kick size defined at the
    reference step DT_REF, so existing tx values keep their meaning."""

    def __init__(self, params, seed=None, transcriptional_noise_std=0.0,
                 channel_noise_std=5.0, thermal_noise_std=0.4, substeps=1):
        super().__init__(params, seed=seed,
                         transcriptional_noise_std=transcriptional_noise_std,
                         channel_noise_std=channel_noise_std,
                         thermal_noise_std=thermal_noise_std)
        self.substeps = int(substeps)
        self.sigma = transcriptional_noise_std * np.sqrt(DT_REF)

    def step(self, dt: float = 0.02):
        h = dt / self.substeps
        p = self.p
        a2 = p.alpha2 * p.strength_ratio
        for _ in range(self.substeps):
            du = p.alpha1 / (1 + self.v ** p.beta) - self.u
            dv = a2 / (1 + self.u ** p.gamma) - self.v
            nu = nv = 0.0
            if self.sigma > 0:
                nu = self.sigma * np.sqrt(h) * self.rng.normal(0, 1)
                nv = self.sigma * np.sqrt(h) * self.rng.normal(0, 1)
            self.u = max(0.0, self.u + du * h + nu)
            self.v = max(0.0, self.v + dv * h + nv)
        target_V = self.V_HIGH if self.u > self.v else self.V_LOW
        dV = (target_V - self.V) * 0.05 * dt * 100
        dV += self.rng.normal(0, self.channel_noise * np.sqrt(dt))
        dV += self.rng.normal(0, self.thermal_noise * np.sqrt(dt))
        self.V = np.clip(self.V + dV, -120, 60)


def _sde_factory(substeps: int):
    def make(params, seed=None, transcriptional_noise_std=0.0, **kw):
        return GardnerToggleCellSDE(params, seed=seed,
                                    transcriptional_noise_std=transcriptional_noise_std,
                                    substeps=substeps)
    return make


# ----------------------------------------------------------------- section 1
def level_std(cls_factory, tx: float, dt: float, n_seeds: int = 6, minutes: int = 1440):
    """Std of the repressor level in the written state, same total simulated
    time at any dt. cls_factory(params, seed, tx) -> cell; step(dt) is called."""
    stds = []
    n_steps = int(round(minutes * DT_REF / dt))
    for k in range(n_seeds):
        c = cls_factory(GardnerParams(), k, tx)
        c.write(1)
        us = []
        for i in range(n_steps):
            c.step(dt=dt)
            if i > n_steps // 5 and c.u > c.v:
                us.append(c.u)
        stds.append(np.std(us))
    return float(np.mean(stds))


def _old(params, seed, tx):
    return GardnerToggleCell(params, seed=seed, transcriptional_noise_std=tx)


def _new(params, seed, tx):
    return GardnerToggleCellSDE(params, seed=seed, transcriptional_noise_std=tx, substeps=1)


def _s1_job(args):
    kind, tx, dt = args
    f = _old if kind == 'old' else _new
    return (kind, tx, dt, level_std(f, tx, dt))


# ----------------------------------------------------------------- section 2
def _fid_job(args):
    ratio, tx, substeps, k, bit = args
    c = GardnerToggleCellSDE(GardnerParams(strength_ratio=ratio), seed=k * 100 + bit,
                             transcriptional_noise_std=tx, substeps=substeps)
    c.write(bit)
    for _ in range(1440):
        c.step(dt=DT_REF)
    return int(c.read_genetic() == bit)


def fidelity_table(ratios, multipliers, substeps, n_trials=20):
    jobs = [(r, 3.0 * m, substeps, k, b) for r in ratios for m in multipliers
            for b in (0, 1) for k in range(n_trials)]
    with Pool(4) as pool:
        out = pool.map(_fid_job, jobs, chunksize=40)
    acc = {}
    for (r, tx, s, k, b), v in zip(jobs, out):
        acc.setdefault((r, tx), []).append(v)
    return {key: float(np.mean(v)) for key, v in acc.items()}


# ----------------------------------------------------------------- section 3
def colony_with(substeps, fractions, multipliers, n_trials=6):
    import bsubtilis_27_noise_robustness_sweep as m27
    original = m27.GardnerToggleCell
    m27.GardnerToggleCell = _sde_factory(substeps)
    try:
        out = {}
        for m in multipliers:
            out[m] = m27.colony_recovery(fractions, 3.0 * m, n_trials=n_trials)
        return out
    finally:
        m27.GardnerToggleCell = original


def _s4_job(args):
    import bsubtilis_27_noise_robustness_sweep as m27
    kind, kw, frac, bit, seed = args
    m27.GardnerToggleCell = _sde_factory(4)
    r = m27.run_colony_trial_ex(frac, bit, seed, **kw)
    return kind, r['genetic'], r['voltage_window']


def section4(n_trials=6):
    print("\n" + "=" * 92)
    print("4) HEADLINE CELLS OF THE TIMING AND STRESS SWEEPS, 4x finer integration")
    print("   cells show genetic / long-window voltage read")
    print("=" * 92)
    cells = []
    for dbl in (30.0, 60.0):
        for delay in (0.0, 60.0):
            for frac in (0.02, 0.20):
                cells.append((f"timing: doubling {dbl:.0f} min, delay {delay:.0f} min, {frac:.0%} survivors",
                              dict(doubling_min=dbl, equil_delay_min=delay, amplitude_mv=30.0), frac))
    for shift in (-40.0, 0.0, 40.0):
        cells.append((f"stress: sustained shift {shift:+.0f} mV for the whole window, 2% survivors",
                      dict(stress_minutes=360.0, stress_shift_mv=shift), 0.02))
    cells.append(("stress: 10x noise for 180 min, 2x slower, 2% survivors",
                  dict(stress_minutes=180.0, stress_doubling_multiplier=2.0,
                       stress_noise_multiplier=10.0), 0.02))
    jobs = [(label, kw, frac, b, int(frac * 10000) + k * 97 + b)
            for (label, kw, frac) in cells for b in (0, 1) for k in range(n_trials)]
    with Pool(4) as pool:
        out = pool.map(_s4_job, jobs)
    acc = {}
    for label, g, v in out:
        acc.setdefault(label, []).append((g, v))
    for (label, kw, frac) in cells:
        rs = acc[label]
        print(f"{label:<78}{np.mean([a for a, _ in rs]):>5.0%} /{np.mean([b for _, b in rs]):>5.0%}")
    print("\nOriginal results: timing cells at 30 min doubling and 0 delay gave 100% / 100%; with a")
    print("60 min delay at 2% survivors, or 60 min doubling at 2% survivors, the voltage read fell to")
    print("50% while genetic stayed 100%. Sustained shifts of +/-40 mV gave 100% genetic / 50% voltage,")
    print("0 mV gave 100% / 100%. 10x noise for 180 min gave about 96% / 96%.")


def main():
    print("=" * 92)
    print("1) DOES THE NOISE DEPEND ON THE STEP SIZE?  (std of repressor level in written state,")
    print("   same total simulated time, 6 seeds)")
    print("=" * 92)
    dts = [0.02, 0.01, 0.005, 0.0025]
    jobs = [(k, tx, dt) for k in ('old', 'new') for tx in (3.0, 15.0) for dt in dts]
    with Pool(4) as pool:
        res = {(k, tx, dt): v for (k, tx, dt, v) in pool.map(_s1_job, jobs)}
    print(f"{'class':<14}{'tx':>6}" + "".join(f"dt={d:g}".rjust(11) for d in dts))
    for k in ('old', 'new'):
        for tx in (3.0, 15.0):
            label = 'original' if k == 'old' else 'dt-independent'
            print(f"{label:<14}{tx:>6.0f}" + "".join(f"{res[(k, tx, d)]:>11.2f}" for d in dts))
    print("\nThe original class changes with dt. The dt-independent class stays level.")

    ratios = [1.0, 2.0, 5.0, 10.0, 0.1]
    mults = [1, 2, 3, 5, 10, 20]
    print("\n" + "=" * 92)
    print("2) SINGLE-CELL 24 h FIDELITY, matched to bsubtilis_27, integrated with finer steps")
    print("   rows = promoter ratio, columns = noise multiple of tx=3.0")
    print("=" * 92)
    tables = {s: fidelity_table(ratios, mults, s) for s in (1, 4)}
    for s in (1, 4):
        label = "reference step (substeps=1, identical to the original class)" if s == 1 \
            else "4x finer integration of the same equation (substeps=4)"
        print(f"\n{label}")
        print(f"{'ratio':<8}" + "".join(f"{m}x".rjust(9) for m in mults))
        for r in ratios:
            print(f"{r:<8}" + "".join(f"{tables[s][(r, 3.0 * m)]:>8.0%} " for m in mults))
    print("\nOriginal bsubtilis_27 table, for comparison (30 trials per bit):")
    print("1.0      100%     100%     100%     100%      60%      53%")
    print("2.0      100%     100%     100%      87%      53%      52%")
    print("5.0      100%     100%      83%      70%      50%      55%")
    print("10.0     100%      77%      65%      52%      50%      52%")
    print("0.1       50%      50%      50%      50%      47%      47%")

    print("\n" + "=" * 92)
    print("3) COLONY RECOVERY (matched promoters), reference step vs 4x finer integration")
    print("=" * 92)
    fr = [0.02, 0.05, 0.20]
    mm = [1, 3, 5, 10, 20]
    for s in (1, 4):
        r = colony_with(s, fr, mm)
        print(f"\nsubsteps={s}   (survivors x noise multiple)")
        print(f"{'survivors':<10}" + "".join(f"{m}x".rjust(8) for m in mm))
        for f in fr:
            print(f"{f:<10.0%}" + "".join(f"{r[m][f]:>7.0%} " for m in mm))
    print("\nOriginal bsubtilis_27: 2%, 5%, 20% survivors all 100% to 5x, 84 to 85% at 10x, 55 to 57% at 20x.")
    print("=" * 92)
    section4()


if __name__ == '__main__':
    main()
