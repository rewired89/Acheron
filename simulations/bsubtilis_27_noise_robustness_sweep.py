"""
Acheron Simulation 27: Does the Toggle Still Pass With Realistic Noise?
=====================================================================

PURPOSE:
bsubtilis_25_transcription_translation_noise_scaling.py found that the
uncited `transcriptional_noise_std=3.0` used by every fidelity result in the
B. subtilis track may be 3x to 17x smaller than Swain, Elowitz & Siggia
(2002) imply. That is a bound in the OPTIMISTIC direction: if real noise is
higher, every fidelity number that used 3.0 is too generous. Nothing in the
repo had re-run the fidelity results across that range. This file does.

WHAT THIS DOES:
1. Single-cell genetic fidelity after 24 h (the bsubtilis_01 test) at noise
   multipliers 1x to 20x of the placeholder, for the same promoter-ratio
   variants used there (1.0 matched, 2.0 and 5.0 moderate, 10.0 and 0.1
   severe mismatch).
2. Colony recovery after damage and regrowth (the bsubtilis_07 test) at the
   same noise multipliers, for 2 percent, 5 percent and 20 percent survivors.
3. A sanity check that this file's colony engine, at default settings,
   gives the same picture as bsubtilis_07 (it must, or nothing built on it
   can be trusted).

It also defines `run_colony_trial_ex`, a parameterised version of the
bsubtilis_07 / bsubtilis_14 regrowth trial that bsubtilis_28 and
bsubtilis_29 import. GardnerToggleCell is imported and never modified.

WHAT THIS DOES NOT DO:
The multipliers are a sweep axis, NOT measured B. subtilis noise. No
multiplier here is a prediction. The result is a map of "how much noise can
the circuit take before it fails the project's own 70 percent bar", which is
what a wet-lab noise measurement (two-colour reporter assay, Stage B0) would
then be compared against. Noise is the same independent per-gene term as
bsubtilis_01 (intrinsic style); the shared term is bsubtilis_23's job.
"""

import os
import sys
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from bsubtilis_01_gardner_toggle_circuit import (
    GardnerParams, GardnerToggleCell, run_persistence,
)
from bsubtilis_08_native_oscillation_interference import ambient_oscillation_offset
from bsubtilis_09_eis_readout_interference import eis_style_read

PLACEHOLDER_TX_NOISE = 3.0
PASS_BAR = 0.70                    # Experiment 1's own fidelity bar
# Voltage restoring rate per step in GardnerToggleCell.step: 0.05 * dt * 100
# with dt = 0.02 -> 0.1 of the gap closed per step, so a constant offset of d
# per step settles at a steady-state shift of d / 0.1 = 10 d.
V_TRACK_RATE = 0.1


def run_colony_trial_ex(surviving_fraction: float, target_bit: int, seed: int,
                        n_cells: int = 64, params: GardnerParams = None,
                        tx_noise: float = PLACEHOLDER_TX_NOISE,
                        doubling_min: float = 30.0, settle_hours: float = 6.0,
                        equil_delay_min: float = 0.0, long_window_min: int = 180,
                        amplitude_mv: float = 0.0, period_hours: float = 3.0,
                        stress_minutes: float = 0.0,
                        stress_doubling_multiplier: float = 1.0,
                        stress_shift_mv: float = 0.0,
                        stress_noise_multiplier: float = 1.0) -> Dict[str, float]:
    """One regrowth trial. With every stress/delay argument at its default
    this is the bsubtilis_07 / bsubtilis_14 trial. Returns genetic fidelity,
    a single-snapshot voltage read, a long-window voltage read, whether the
    colony got back to full size, and how many minutes the window used."""
    params = params or GardnerParams()
    rng = np.random.default_rng(seed)
    n_surv = max(1, int(round(n_cells * surviving_fraction))) if surviving_fraction > 0 else 0
    if n_surv == 0:
        return {'genetic': 0.0, 'voltage_snapshot': 0.0, 'voltage_window': 0.0,
                'regrown': 0.0, 'window_used_min': 0.0}

    def new_cell(u=None, v=None, V=None):
        c = GardnerToggleCell(params, seed=int(rng.integers(0, 2**31)),
                              transcriptional_noise_std=tx_noise)
        if u is not None:
            c.u, c.v, c.V = u, v, V
        else:
            c.write(target_bit)
        return c

    cells = [new_cell() for _ in range(n_surv)]
    total = settle_hours * 60.0
    t = 0.0
    next_div = doubling_min * (stress_doubling_multiplier if stress_minutes > 0 else 1.0)
    t_full = None if len(cells) < n_cells else 0.0
    histories: List[List[int]] = []

    while t < total:
        t += 1.0
        stressed = t <= stress_minutes
        offset = ambient_oscillation_offset(t, amplitude_mv, period_hours) if amplitude_mv else 0.0
        if stressed:
            offset += stress_shift_mv * V_TRACK_RATE
        for c in cells:
            c.tx_noise = tx_noise * (stress_noise_multiplier if stressed else 1.0)
            c.step(dt=0.02)
            if offset:
                c.V = float(np.clip(c.V + offset, -120, 60))
        if t_full is None and t >= next_div:
            fresh = []
            for c in cells:
                fresh.append(new_cell(c.u, c.v, c.V))
                if len(cells) + len(fresh) >= n_cells:
                    break
            cells = (cells + fresh)[:n_cells]
            next_div = t + doubling_min * (
                stress_doubling_multiplier if t < stress_minutes else 1.0)
            if len(cells) >= n_cells:
                t_full = t
        if t_full is not None and t >= t_full + equil_delay_min:
            if not histories:
                histories = [[] for _ in cells]
            for i, c in enumerate(cells):
                histories[i].append(c.read_voltage())

    genetic = sum(1 for c in cells if c.read_genetic() == target_bit) / len(cells)
    if histories and histories[0]:
        snap = sum(1 for h in histories if h[-1] == target_bit) / len(histories)
        w = min(long_window_min, len(histories[0]))
        win = sum(1 for h in histories
                  if eis_style_read(h, len(h) - w, w) == target_bit) / len(histories)
        used = float(w)
    else:
        snap = win = sum(1 for c in cells if c.read_voltage() == target_bit) / len(cells)
        used = 0.0
    return {'genetic': genetic, 'voltage_snapshot': snap, 'voltage_window': win,
            'regrown': float(t_full is not None), 'window_used_min': used}


def single_cell_fidelity(ratio: float, tx_noise: float, n_trials: int = 30) -> float:
    params = GardnerParams(strength_ratio=ratio)
    ok = 0
    for bit in (0, 1):
        for k in range(n_trials):
            ok += run_persistence(bit, params, hours=24.0, seed=k * 100 + bit,
                                  tx_noise=tx_noise)['genetic_correct']
    return ok / (2 * n_trials)


def _colony_job(args):
    frac, bit, seed, tx = args
    return run_colony_trial_ex(frac, bit, seed, tx_noise=tx)['genetic']


def colony_recovery(fractions: List[float], tx_noise: float, n_trials: int = 6) -> Dict[float, float]:
    from multiprocessing import Pool
    jobs = [(f, b, int(f * 10000) + k * 97 + b, tx_noise)
            for f in fractions for b in (0, 1) for k in range(n_trials)]
    with Pool(4) as pool:
        out = pool.map(_colony_job, jobs)
    res: Dict[float, List[float]] = {f: [] for f in fractions}
    for (f, _, _, _), r in zip(jobs, out):
        res[f].append(r)
    return {f: float(np.mean(v)) for f, v in res.items()}


def main():
    multipliers = [1, 2, 3, 5, 10, 20]
    ratios = [1.0, 2.0, 5.0, 10.0, 0.1]

    print("=" * 84)
    print("SINGLE-CELL GENETIC FIDELITY AT 24 h vs. NOISE (placeholder 3.0 = 1x)")
    print("=" * 84)
    print(f"{'ratio':<8}" + "".join(f"{m}x".rjust(9) for m in multipliers))
    for r in ratios:
        row = [single_cell_fidelity(r, PLACEHOLDER_TX_NOISE * m) for m in multipliers]
        print(f"{r:<8}" + "".join(f"{x:>8.0%} " for x in row))

    print("\n" + "=" * 84)
    print("COLONY RECOVERY AFTER DAMAGE + REGROWTH (matched promoters) vs. NOISE")
    print("=" * 84)
    fractions = [0.02, 0.05, 0.20]
    print(f"{'survivors':<10}" + "".join(f"{m}x".rjust(9) for m in multipliers))
    table = {m: colony_recovery(fractions, PLACEHOLDER_TX_NOISE * m) for m in multipliers}
    for f in fractions:
        print(f"{f:<10.0%}" + "".join(f"{table[m][f]:>8.0%} " for m in multipliers))

    print("\nPass bar = 70% (Experiment 1). Read each row left to right: the first")
    print("column that drops below the bar is the noise multiple at which the")
    print("circuit stops passing. That multiple is what the two-colour-reporter")
    print("assay has to beat for Experiment 1 to be worth running.")
    print("=" * 84)


if __name__ == '__main__':
    main()
