"""
Acheron Simulation 34: Does the Exact Model's Robustness Survive Cell Division
with Uneven (Partition) Splitting of Molecules?
=====================================================================

PURPOSE:
bsubtilis_32 and bsubtilis_33 showed that an exact molecule-by-molecule
(Gillespie) toggle holds at 90 percent or better down to a few times the burst
size in mean repressor molecules, even with an mRNA stage and shared noise. Both
left out the most obvious extra noise source in a growing culture: at each
division the mother's molecules are shared between daughters, and the share is
not exactly half. Each molecule goes to either daughter by a coin flip, so a
daughter gets Binomial(n, 1/2) of n molecules, an extra noise of its own.

MODEL:
Same two-stage toggle as bsubtilis_33 (mRNA decay gamma_m = 20, protein
degradation 1 - f, mean ON repressor about 50 * Omega * ... see below), with:
- cell volume V growing exponentially from 1 to 2 over a doubling time
  Td = ln(2) / f (protein-lifetime units), where f is the share of protein loss
  that is dilution by growth. f = 0 means no division (reduces to bsubtilis_33).
  f = 1 means loss is pure dilution; Td = 0.69 units, which is 35 minutes at the
  simulation's mapping of 1 unit = 50 minutes, near the 30 minute doubling used
  elsewhere in the repo. Protein degradation is 1 - f so the total loss rate is 1
  in every case and mean levels stay comparable.
- Transcription scales with V (gene dosage and machinery grow with the cell);
  repression uses concentration P / (Omega * V).
- At V = 2 the cell divides: mRNA and protein of each arm are partitioned and
  ONE daughter (random) is followed. 'binom' splits each molecule by a fair coin,
  'even' splits as evenly as possible (floor, with a random extra molecule) as a
  control that has the same dilution without partition noise.
- V is advanced in small fixed steps; propensities are piecewise constant
  between them, as in bsubtilis_33.

WHAT THIS DOES NOT DO:
It follows a single lineage, so there is no population selection (see
bsubtilis_30). Gene copy number is not modelled as discrete (a replicating
chromosome doubles the gene at a point in the cycle). There is no promoter
switching, no shared noise here (see bsubtilis_33), and the ON level is still
fixed at 50 times the repression threshold. f, gamma_m and Td are assumptions or
sweep axes, not measurements.
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
T_UNITS = 28.8
T_BURN = 5.0
SAMPLE_DT = 0.5
V_STEP = 0.02


def _split(n, mode, rnd):
    if n <= 0:
        return 0
    if mode == 'binom':
        # Binomial(n, 1/2) by direct draw (n can be large; use normal when n > 200)
        if n > 200:
            k = int(round(rnd.gauss(n / 2.0, math.sqrt(n) / 2.0)))
            return min(n, max(0, k))
        return sum(1 for _ in range(n) if rnd.random() < 0.5)
    k = n // 2
    if n % 2 and rnd.random() < 0.5:
        k += 1
    return k


def run(args):
    """Returns (Omega, b, f, mode, correct, n_div, mean_on_conc)."""
    Omega, b, f, mode, bit, seed = args
    rnd = random.Random(seed)
    k_p = b * GAMMA_M
    k_tx = A1 * Omega / b
    g_deg = 1.0 - f
    dividing = f > 0
    td = math.log(2.0) / f if dividing else 1e9
    mu = math.log(2.0) / td if dividing else 0.0
    P = [0, 0]
    M = [0, 0]
    on = 0 if bit == 1 else 1
    P[on] = int(round(A1 * Omega))
    M[on] = int(round(k_tx / GAMMA_M))
    V = 1.0
    t = 0.0
    next_v = V_STEP
    next_s = T_BURN
    samples = []
    n_div = 0
    while t < T_UNITS:
        p0, p1 = P[0] / (Omega * V), P[1] / (Omega * V)
        tx0 = k_tx * V / (1.0 + p1 * p1)
        tx1 = k_tx * V / (1.0 + p0 * p0)
        md0, md1 = GAMMA_M * M[0], GAMMA_M * M[1]
        tl0, tl1 = k_p * M[0], k_p * M[1]
        pd0, pd1 = g_deg * P[0], g_deg * P[1]
        tot = tx0 + tx1 + md0 + md1 + tl0 + tl1 + pd0 + pd1
        dt = -math.log(1.0 - rnd.random()) / tot if tot > 0 else 1e9
        t_new = t + dt
        if dividing and t_new >= next_v:
            t = next_v
            V *= math.exp(mu * V_STEP)
            next_v += V_STEP
            if V >= 2.0:
                V /= 2.0
                n_div += 1
                for i in (0, 1):
                    M[i] = _split(M[i], mode, rnd)
                    P[i] = _split(P[i], mode, rnd)
            continue
        while next_s <= t_new and next_s < T_UNITS:
            samples.append(P[on] / V)
            next_s += SAMPLE_DT
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
    correct = int((P[0] > P[1]) == (bit == 1))
    mean_on = float(np.mean(samples)) if samples else 0.0
    return Omega, b, f, mode, correct, n_div, mean_on


CONDS = [
    ('no division', 0.0, 'none'),
    ('even split, f=1', 1.0, 'even'),
    ('binomial split, f=0.5', 0.5, 'binom'),
    ('binomial split, f=1', 1.0, 'binom'),
]


def fidelity_section(n_per_bit=20):
    omegas = [0.25, 0.5, 1, 2, 4, 8]
    bursts = [1, 5, 10, 20]
    jobs = [(O, b, f, mode, bit, 9000 * O + 37 * b + 5 * k + bit + int(f * 10) * 101)
            for O in omegas for b in bursts for (_, f, mode) in CONDS
            for bit in (0, 1) for k in range(n_per_bit)]
    with Pool(4) as pool:
        out = pool.map(run, jobs, chunksize=4)
    acc = {}
    mons = {}
    divs = {}
    for O, b, f, mode, c, nd, mo in out:
        acc.setdefault((O, b, f, mode), []).append(c)
        mons.setdefault((O, b, f, mode), []).append(mo)
        divs.setdefault((f, mode), []).append(nd)
    print("=" * 92)
    print("24 h equivalent, final state correct, 40 runs per cell (one followed lineage)")
    print("=" * 92)
    for (name, f, mode) in CONDS:
        nd = np.mean(divs[(f, mode)])
        print(f"\n{name}   (divisions per run: {nd:.0f})")
        print(f"{'Omega':>6}{'~mols':>7}" + "".join(f"burst {b}".rjust(11) for b in bursts))
        for O in omegas:
            row = f"{O:>6}{50 * O:>7.0f}"
            for b in bursts:
                row += f"{float(np.mean(acc[(O, b, f, mode)])):>10.0%} "
            print(row)
    print("\nSmallest mean ON count (50 * Omega) with >= 90% fidelity and above it throughout:")
    for (name, f, mode) in CONDS:
        parts = []
        for b in bursts:
            need = None
            for O in omegas:
                if all(np.mean(acc[(o, b, f, mode)]) >= 0.9 for o in omegas if o >= O):
                    need = 50 * O
                    break
            parts.append(f"b={b}: {need:.0f}" if need else f"b={b}: >{50 * omegas[-1]:.0f}")
        print(f"  {name:<26}" + "   ".join(parts))
    print("\nMean ON-state concentration (molecules per unit volume), for scale:")
    for (name, f, mode) in CONDS:
        vals = [np.mean(mons[(4, b, f, mode)]) for b in bursts]
        print(f"  {name:<26}Omega=4: " + ", ".join(f"{v:.0f}" for v in vals) + "  (nominal 200)")


def main():
    fidelity_section()


if __name__ == '__main__':
    main()
