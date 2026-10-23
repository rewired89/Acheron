"""
Acheron Simulation 36: Colony Regrowth and the Damage-Sensing Boost in the
Molecular (Gillespie) Model
=====================================================================

PURPOSE:
The headline "a few percent of survivors regrow into a colony that all holds the
bit" (bsubtilis_07, 14, 27) and the damage-sensing rescue (bsubtilis_16) were
built on models that bsubtilis_31 to 35 showed to be pessimistic near zero
copies (Gaussian noise) or to have no bursts and no mRNA stage (the colony
model of bsubtilis_15). Nothing re-ran them in the exact molecule-by-molecule
model. This file does, additively: no earlier file is changed.

MODEL:
The two-stage molecular toggle of bsubtilis_33/34/35 (mRNA decay 20, protein
degradation 1 - f with f = 1 so loss is pure dilution, doubling time ln 2 in
protein-lifetime units = 35 minutes at the repo's mapping), with growth,
division and binomial partitioning. A trial starts from n_surv survivors, all
written to the target bit (survivor composition is bsubtilis_30 section G's
job). Each survivor founds a lineage that divides, keeping BOTH daughters, until
the colony reaches about 64 cells (g = ceil(log2(64 / n_surv)) doublings),
after which it keeps following one random daughter per division until the end of
the window. Every lineage is simulated for the same total time: 4.2 units of
regrowth plus 7.2 units (6 hours) of settling. Recovery is the fraction of final
cells whose written arm is the higher one. A 100 percent survivor row (g = 0) is
the baseline with no regrowth. Cells are independent (no crowding or
competition).

DAMAGE-SENSING BOOST (bsubtilis_16's idea, here a proposal and not a result):
while a lineage still has doublings to do (the regrowth phase), the transcription
rate of whichever arm currently has more protein is multiplied by m; it is off
afterwards. m = 1 is no boost.

WHAT THIS DOES NOT DO:
No selection (bsubtilis_30), no discrete gene copy number, no promoter switching,
no shared noise, no crowding. Survivors are assumed correct. Molecule count, burst
size, f and the boost are sweep axes or proposals, not measurements. A boost that
raises recovery here says nothing about whether a real SOS-type promoter can be
wired to a toggle arm.
"""

import math
import os
import random
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

A1 = 50.0
GAMMA_M = 20.0
V_STEP = 0.02
T_REGROW = 4.2
T_SETTLE = 7.2
T_TOTAL = T_REGROW + T_SETTLE
N_FULL = 64
F_DIL = 1.0


def _binom(n, rnd):
    if n <= 0:
        return 0
    if n > 200:
        return min(n, max(0, int(round(rnd.gauss(n / 2.0, math.sqrt(n) / 2.0)))))
    return sum(1 for _ in range(n) if rnd.random() < 0.5)


def evolve(Omega, b, P, M, V, t, t_end, boost, rnd):
    """Run one cell until it divides (V reaches 2) or t_end.
    boost is the multiplier on the currently dominant arm's transcription (1 = none).
    Returns ('div'|'end', t, P, M, V)."""
    k_p = b * GAMMA_M
    k_tx = A1 * Omega / b
    g_deg = 1.0 - F_DIL
    mu = F_DIL
    next_v = t + V_STEP
    P = list(P)
    M = list(M)
    while t < t_end:
        p0, p1 = P[0] / (Omega * V), P[1] / (Omega * V)
        s0 = boost if (boost != 1.0 and P[0] >= P[1]) else 1.0
        s1 = boost if (boost != 1.0 and P[1] > P[0]) else 1.0
        tx0 = s0 * k_tx * V / (1.0 + p1 * p1)
        tx1 = s1 * k_tx * V / (1.0 + p0 * p0)
        md0, md1 = GAMMA_M * M[0], GAMMA_M * M[1]
        tl0, tl1 = k_p * M[0], k_p * M[1]
        pd0, pd1 = g_deg * P[0], g_deg * P[1]
        tot = tx0 + tx1 + md0 + md1 + tl0 + tl1 + pd0 + pd1
        t_new = t + (-math.log(1.0 - rnd.random()) / tot if tot > 0 else 1e9)
        if t_new >= next_v:
            t = next_v
            if t >= t_end:
                break
            V *= math.exp(mu * V_STEP)
            next_v += V_STEP
            if V >= 2.0:
                return 'div', t, P, M, V / 2.0
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
    return 'end', t_end, P, M, V


def trial(args):
    """One colony. Returns (fraction of final cells correct, final cell count)."""
    Omega, b, surv_frac, boost, bit, seed = args
    rnd = random.Random(seed)
    n_surv = max(1, int(round(N_FULL * surv_frac)))
    g_budget = max(0, math.ceil(math.log2(N_FULL / n_surv)))
    on = 0 if bit == 1 else 1
    k_tx = A1 * Omega / b
    stack = []
    for _ in range(n_surv):
        P = [0, 0]
        M = [0, 0]
        P[on] = int(round(A1 * Omega))
        M[on] = int(round(k_tx / GAMMA_M))
        stack.append((P, M, 1.0 + rnd.random(), 0.0, g_budget))
    # starting volume is random in [1, 2) so survivors are not synchronized
    finals = []
    while stack:
        P, M, V, t, g = stack.pop()
        status, t, P, M, V = evolve(Omega, b, P, M, V, t, T_TOTAL,
                                    boost if g > 0 else 1.0, rnd)
        if status == 'end':
            finals.append((P[0], P[1]))
            continue
        Pa = [_binom(P[0], rnd), _binom(P[1], rnd)]
        Ma = [_binom(M[0], rnd), _binom(M[1], rnd)]
        Pb = [P[0] - Pa[0], P[1] - Pa[1]]
        Mb = [M[0] - Ma[0], M[1] - Ma[1]]
        if g > 0:
            stack.append((Pa, Ma, V, t, g - 1))
            stack.append((Pb, Mb, V, t, g - 1))
        else:
            if rnd.random() < 0.5:
                stack.append((Pa, Ma, V, t, 0))
            else:
                stack.append((Pb, Mb, V, t, 0))
    correct = sum(1 for p0, p1 in finals if (p0 > p1) == (bit == 1))
    return correct / len(finals), len(finals)


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def sweep(cells, fracs, boosts, n_trials):
    jobs = [(O, b, fr, m, bit, 1000 * i + 131 * j + 17 * k + bit)
            for i, (O, b) in enumerate(cells) for j, (fr, m) in enumerate(
                [(fr, m) for fr in fracs for m in boosts])
            for bit in (0, 1) for k in range(n_trials)]
    with Pool(4) as pool:
        out = pool.map(trial, jobs, chunksize=2)
    acc = {}
    for j, o in zip(jobs, out):
        acc.setdefault((j[0], j[1], j[2], j[3]), []).append(o)
    return acc


def main():
    cells = [(0.5, 5), (1, 5), (1, 20), (2, 20), (4, 20)]
    fracs = [1.0, 0.20, 0.05, 0.02]
    print("=" * 92)
    print("1) COLONY RECOVERY IN THE MOLECULAR MODEL, no boost (m = 1)")
    print("   mean fraction of final cells holding the written bit; 12 colonies per cell (6 per bit)")
    print("   100% = no damage baseline (a single lineage-following colony of 64 over the same time)")
    print("=" * 92)
    acc = sweep(cells, fracs, [1.0], 6)
    print(f"{'Omega':>6}{'~mols':>7}{'burst':>7}" + "".join(f"{f'{fr:.0%} surv':>14}" for fr in fracs))
    for (O, b) in cells:
        row = f"{O:>6}{50 * O:>7.0f}{b:>7}"
        for fr in fracs:
            v = [x[0] for x in acc[(O, b, fr, 1.0)]]
            row += f"{np.mean(v):>8.0%} ({min(v):.0%}+)"
        print(row)
    print("   (the figure in brackets is the worst colony)")

    print("\n" + "=" * 92)
    print("2) DAMAGE-SENSING BOOST (proposal): dominant arm's transcription x m during regrowth only")
    print("   2% survivors, 20 colonies per cell (10 per bit)")
    print("=" * 92)
    bcells = [(0.5, 5), (1, 20), (0.5, 20)]
    boosts = [1.0, 2.0, 5.0, 10.0]
    acc2 = sweep(bcells, [0.02], boosts, 10)
    print(f"{'Omega':>6}{'~mols':>7}{'burst':>7}" + "".join(f"m = {m:g}".rjust(14) for m in boosts))
    for (O, b) in bcells:
        row = f"{O:>6}{50 * O:>7.0f}{b:>7}"
        for m in boosts:
            v = [x[0] for x in acc2[(O, b, 0.02, m)]]
            row += f"{np.mean(v):>8.0%} ({min(v):.0%}+)"
        print(row)
    print("\nReading: with every cell founded by a correct survivor, recovery is the single-lineage hold over the")
    print("regrowth plus settling time, exactly as bsubtilis_30 section G says. A boost matters only where a lineage")
    print("would otherwise lose the bit; it also pushes any wrong-state cell harder toward the wrong state.")


if __name__ == '__main__':
    main()
