"""
Acheron Simulation 35: Falsification Controls, Model-Dependence of the Bistable
Window, Confidence Intervals and a Flip-Rate Estimate
=====================================================================

PURPOSE:
bsubtilis_32 to 34 showed that the analytic fixed-point analysis, the Gaussian
simulation and the exact molecular (Gillespie) model agree on the toggle. An
outside review made four fair objections, and this file answers them:

A) HOW MUCH DOES THE BISTABLE WINDOW DEPEND ON THE MODEL? The window of
   promoter strength ratios (0.247 to 16.25 in bsubtilis_32) holds for Hill
   coefficient 2 on both arms and equal protein loss rates. This part recomputes
   it exactly for other Hill coefficients and for unequal loss rates, and says
   where the severe-mismatch control of Experiment 1 (M3, ratio 0.1) sits in each.
B) DO THE TWO MODELS DISAGREE WHEN THEY SHOULD? Agreement between two models
   that share assumptions proves little unless they also fail together where the
   theory says the toggle must fail. The molecular model is run with Hill
   coefficient 1 (theory: monostable at every ratio), at ratios outside the
   window, and with Hill coefficient 3 at a ratio the analytic part says moves
   inside the window.
C) HOW PRECISE ARE THE FIDELITY NUMBERS? The bsubtilis_34 grid is rerun with more
   runs and Wilson 95 percent intervals, so thresholds read as ranges.
D) WHAT IS THE FLIP RATE? Fidelity at 24 hours is a proxy. Long runs record the
   time of the first committed flip (the other repressor above half the ON level
   while the written one is below it), giving a rate per hour with an exact
   Poisson interval, and the 24 hour retention that rate implies, to compare with
   the fidelity actually measured.

WHAT THIS DOES NOT DO:
A model result, not a measurement. A flip-rate closed form (Kramers type) is
not derived here; the rate is estimated from simulation, and a run with zero flips
gives only an upper bound. Molecules per cell, burst size, Hill coefficient and
loss rates of the real repressors are unmeasured. 1 time unit is 50 minutes at the
repo's mapping.
"""

import math
import os
import random
import sys
from multiprocessing import Pool

import numpy as np
from scipy.optimize import brentq
from scipy.stats import chi2

sys.path.insert(0, os.path.dirname(__file__))

A1 = 50.0
GAMMA_M = 20.0
T_UNITS = 28.8
T_BURN = 5.0
V_STEP = 0.02
UNIT_HOURS = 50.0 / 60.0


# ------------------------------------------------------------------ A: analytic
def stable_count(a1, a2, beta, gamma, delta_u=1.0, n=6000):
    """Number of stable fixed points of du = a1/(1+v^beta) - delta_u*u,
    dv = a2/(1+u^gamma) - v. Stable iff f'(v) * g'(u) < delta_u * 1."""
    F = lambda u: u - a1 / (delta_u * (1 + (a2 / (1 + u ** gamma)) ** beta))
    # upper limit a little above a1/delta: at high Hill the ON root sits within 1e-19 of
    # a1/delta and F there rounds to exactly 0, hiding the sign change
    us = np.linspace(1e-9, 1.02 * a1 / delta_u, n)
    fs = F(us)
    cnt = 0
    for i in range(n - 1):
        if fs[i] * fs[i + 1] < 0:
            u = brentq(F, us[i], us[i + 1], xtol=1e-12)
            v = a2 / (1 + u ** gamma)
            fp = a1 * beta * v ** (beta - 1) / (1 + v ** beta) ** 2
            gp = a2 * gamma * u ** (gamma - 1) / (1 + u ** gamma) ** 2
            if fp * gp < delta_u:
                cnt += 1
    return cnt


def bistable(r, beta, gamma, delta_u):
    return stable_count(A1, A1 * r, beta, gamma, delta_u) == 2


def window(beta, gamma, delta_u):
    """Return (low edge, high edge) of the bistable ratio window, or None."""
    grid = np.logspace(-3, 3, 61)
    flags = [bistable(r, beta, gamma, delta_u) for r in grid]
    if not any(flags):
        return None
    i0 = flags.index(True)
    i1 = len(flags) - 1 - flags[::-1].index(True)

    def edge(a, b, inside_is_b):
        for _ in range(40):
            m = math.sqrt(a * b)
            if bistable(m, beta, gamma, delta_u) == inside_is_b:
                b = m
            else:
                a = m
        return math.sqrt(a * b)

    lo = grid[0] if i0 == 0 else edge(grid[i0 - 1], grid[i0], True)
    hi = grid[-1] if i1 == len(grid) - 1 else edge(grid[i1], grid[i1 + 1], False)
    return lo, hi


def analytic_section():
    print("=" * 92)
    print("A) HOW THE BISTABLE WINDOW (ratio of promoter strengths) MOVES WITH THE MODEL")
    print("=" * 92)
    print(f"{'Hill (both arms)':<18}{'loss of u / loss of v':<24}{'window':<22}{'0.1 inside?':<13}{'0.01 inside?':<13}")
    conds = [(1, 1, 1.0), (1.5, 1.5, 1.0), (2, 2, 1.0), (3, 3, 1.0), (4, 4, 1.0),
             (2, 2, 0.25), (2, 2, 0.5), (2, 2, 2.0), (2, 2, 4.0),
             (3, 3, 0.25), (3, 3, 4.0), (2, 3, 1.0), (3, 2, 1.0)]
    for beta, gamma, du in conds:
        w = window(beta, gamma, du)
        label = f"{beta:g} / {gamma:g}"
        loss = f"{du:g} / 1"
        if w is None:
            print(f"{label:<18}{loss:<24}{'no bistable ratio':<22}{'no':<13}{'no':<13}")
        else:
            ins1 = 'yes' if bistable(0.1, beta, gamma, du) else 'no'
            ins2 = 'yes' if bistable(0.01, beta, gamma, du) else 'no'
            print(f"{label:<18}{loss:<24}{w[0]:.3g} to {w[1]:.3g}".ljust(64) + f"{ins1:<13}{ins2:<13}")
    print("\nHill 1 (no cooperativity) is never bistable. Higher cooperativity or unequal loss rates")
    print("widen or shift the window, so the severe-mismatch control at ratio 0.1 is only 'severe' if the")
    print("real window is close to the Hill-2, equal-loss one. Ratio 0.01 stays outside in these cases.")


# --------------------------------------------------------- shared molecular sim
def sim(args):
    """Two-stage toggle, optional growth and division, optional first-passage stop.
    arm V's transcription is scaled by `ratio`; repression Hill exponent is `beta`.
    Returns (final_correct, flip_time_or_None, elapsed)."""
    Omega, b, beta, ratio, f, mode, bit, seed, T, track = args
    rnd = random.Random(seed)
    k_p = b * GAMMA_M
    k_tx = A1 * Omega / b
    g_deg = 1.0 - f
    dividing = f > 0
    mu = f if dividing else 0.0           # ln2/td with td = ln2/f
    on = 0 if bit == 1 else 1
    sc = [1.0, ratio]
    P = [0, 0]
    M = [0, 0]
    P[on] = int(round(A1 * Omega * sc[on]))
    M[on] = int(round(k_tx * sc[on] / GAMMA_M))
    V = 1.0
    t = 0.0
    next_v = V_STEP
    flip = None
    half = 0.5 * A1 * Omega * sc[on]
    other = 1 - on
    half_o = 0.5 * A1 * Omega * sc[other]
    while t < T:
        p0, p1 = P[0] / (Omega * V), P[1] / (Omega * V)
        tx0 = k_tx * V / (1.0 + p1 ** beta)
        tx1 = ratio * k_tx * V / (1.0 + p0 ** beta)
        md0, md1 = GAMMA_M * M[0], GAMMA_M * M[1]
        tl0, tl1 = k_p * M[0], k_p * M[1]
        pd0, pd1 = g_deg * P[0], g_deg * P[1]
        tot = tx0 + tx1 + md0 + md1 + tl0 + tl1 + pd0 + pd1
        t_new = t + (-math.log(1.0 - rnd.random()) / tot if tot > 0 else 1e9)
        if dividing and t_new >= next_v:
            t = next_v
            V *= math.exp(mu * V_STEP)
            next_v += V_STEP
            if V >= 2.0:
                V /= 2.0
                for i in (0, 1):
                    for arr in (M, P):
                        n = arr[i]
                        if mode == 'binom':
                            arr[i] = (sum(1 for _ in range(n) if rnd.random() < 0.5) if n <= 200
                                      else min(n, max(0, int(round(rnd.gauss(n / 2.0, math.sqrt(n) / 2.0))))))
                        else:
                            arr[i] = n // 2 + (1 if (n % 2 and rnd.random() < 0.5) else 0)
            continue
        t = t_new
        r = rnd.random() * tot
        if r < tx0:
            M[0] += 1
        elif r < tx0 + tx1:
            M[1] += 1
        elif r < tx0 + tx1 + md0:
            M[0] -= 1
        elif r < tx0 + tx1 + md0 + md1:
            M[1] -= 1
        elif r < tx0 + tx1 + md0 + md1 + tl0:
            P[0] += 1
        elif r < tx0 + tx1 + md0 + md1 + tl0 + tl1:
            P[1] += 1
        elif r < tx0 + tx1 + md0 + md1 + tl0 + tl1 + pd0:
            P[0] -= 1
        else:
            P[1] -= 1
        if track and P[on] / V < half and P[other] / V > half_o:
            flip = t
            break
    correct = int((P[0] > P[1]) == (bit == 1))
    return correct, flip, t


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


# ------------------------------------------------------------------ B: falsification
def falsification_section(n_per_bit=20):
    print("\n" + "=" * 92)
    print("B) DO THE ANALYTIC AND MOLECULAR MODELS FAIL TOGETHER WHERE THEY SHOULD?")
    print("   molecular model, 24 h equivalent, mean ON about 200 molecules (Omega 4), burst 5,")
    print("   40 runs per cell, 'correct' averaged over both written states (about 50% = monostable)")
    print("=" * 92)
    cases = [(2, 1.0, 1), (1, 1.0, 1), (1, 1.0, 4), (1, 2.0, 1), (2, 0.01, 1), (2, 0.1, 1), (2, 0.2, 1),
             (2, 0.3, 1), (2, 0.5, 1), (2, 30.0, 1), (3, 0.01, 1), (3, 0.05, 1), (3, 0.15, 1), (3, 0.2, 1),
             (3, 0.5, 1)]
    jobs = [(4, 5, beta, r, 0.0, 'none', bit, 17000 + 31 * i + 5 * k + bit, T_UNITS * hz, False)
            for i, (beta, r, hz) in enumerate(cases) for bit in (0, 1) for k in range(n_per_bit)]
    with Pool(4) as pool:
        out = pool.map(sim, jobs, chunksize=4)
    acc = {}
    for j, o in zip(jobs, out):
        acc.setdefault((j[2], j[3], round(j[8] / T_UNITS)), []).append(o[0])
    print(f"{'Hill':>5}{'ratio':>8}{'horizon':>9}{'molecular fidelity':>20}{'  95% CI':>16}{'analytic: bistable?':>24}")
    for beta, r, hz in cases:
        v = acc[(beta, r, hz)]
        k = sum(v)
        lo, hi = wilson(k, len(v))
        a = bistable(r, beta, beta, 1.0)
        print(f"{beta:>5}{r:>8g}{f'{hz}x 24 h':>9}{k / len(v):>19.0%} {lo:>8.0%}-{hi:.0%}{'yes' if a else 'no':>20}")
    print("\nA well-behaved pair of models gives high fidelity where the analytic part says bistable and about")
    print("50% where it says monostable (Hill 1, or a ratio outside the window). Hill 1 at ratio 1 is slow to")
    print("forget (its relaxation rate is about 0.14 per protein lifetime), so a 24 h read still carries")
    print("memory; the 4x horizon row shows it decaying toward 50%.")


# ------------------------------------------------------------------ C: intervals
def intervals_section(n_per_bit=50):
    print("\n" + "=" * 92)
    print("C) bsubtilis_34 GRID (binomial split, f = 1) WITH 100 RUNS PER CELL AND 95% WILSON INTERVALS")
    print("=" * 92)
    omegas = [0.25, 0.5, 1, 2, 4]
    bursts = [1, 5, 10, 20]
    jobs = [(O, b, 2, 1.0, 1.0, 'binom', bit, 23000 + 97 * int(O * 4) + 13 * b + 3 * k + bit, T_UNITS, False)
            for O in omegas for b in bursts for bit in (0, 1) for k in range(n_per_bit)]
    with Pool(4) as pool:
        out = pool.map(sim, jobs, chunksize=4)
    acc = {}
    for j, o in zip(jobs, out):
        acc.setdefault((j[0], j[1]), []).append(o[0])
    print(f"{'Omega':>6}{'~mols':>7}" + "".join(f"burst {b}".rjust(16) for b in bursts))
    for O in omegas:
        row = f"{O:>6}{50 * O:>7.0f}"
        for b in bursts:
            v = acc[(O, b)]
            k = sum(v)
            lo, hi = wilson(k, len(v))
            row += f"{k / len(v):>7.0%} ({lo:.0%}-{hi:.0%})".rjust(16)
        print(row)
    print("\nRead a threshold as the first row whose whole interval sits at or above 90%, not as a point value.")


# ------------------------------------------------------------------ D: flip rate
def flip_section(n_runs=40):
    print("\n" + "=" * 92)
    print("D) FLIP RATE FROM LONG RUNS (binomial split, f = 1), first committed flip, horizon 300 units")
    print("   (about 250 h); rate per hour with an exact Poisson 95% interval; implied 24 h retention")
    print("=" * 92)
    T = 300.0
    cells = [(0.25, 5), (0.5, 5), (1, 5), (2, 5), (0.5, 20), (1, 20), (2, 20), (4, 20)]
    jobs = [(O, b, 2, 1.0, 1.0, 'binom', k % 2, 31000 + 61 * int(O * 4) + 7 * b + k, T, True)
            for (O, b) in cells for k in range(n_runs)]
    with Pool(4) as pool:
        out = pool.map(sim, jobs, chunksize=2)
    acc = {}
    for j, o in zip(jobs, out):
        acc.setdefault((j[0], j[1]), []).append(o)
    print(f"{'Omega':>6}{'~mols':>7}{'burst':>7}{'flips':>7}{'exposure h':>12}{'rate per h':>12}{'95% interval':>22}{'24 h retention':>16}")
    for (O, b) in cells:
        rs = acc[(O, b)]
        flips = sum(1 for r in rs if r[1] is not None)
        expo = sum(r[2] for r in rs) * UNIT_HOURS
        rate = flips / expo
        lo = chi2.ppf(0.025, 2 * flips) / 2 / expo if flips > 0 else 0.0
        hi = chi2.ppf(0.975, 2 * (flips + 1)) / 2 / expo
        ret = math.exp(-rate * 24.0)
        rng = f"{lo:.4f} to {hi:.4f}"
        print(f"{O:>6}{50 * O:>7.0f}{b:>7}{flips:>7}{expo:>12.0f}{rate:>12.4f}{rng:>22}{ret:>15.0%} ")
    print("\nA cell with zero flips gives an upper bound only. First committed flip is a first-passage time;")
    print("a flip back is not counted. Retention = exp(-rate * 24 h) assumes a constant rate.")


def main():
    analytic_section()
    falsification_section()
    intervals_section()
    flip_section()


if __name__ == '__main__':
    main()
