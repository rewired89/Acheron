"""
Acheron Simulation 37: How Many Toggles Can One Cell Hold? Multi-Bit Words
Under a Shared Molecule Budget and Crosstalk
=====================================================================

PURPOSE:
Every result so far is for ONE toggle (one bit). The project's pitch is about
data, which means several bits in one cell or colony. This file gives a first,
rough idea of what the single-bit results imply for N bits, using the exact
molecular model of bsubtilis_33/34/35. It is a sensitivity map for the
assumptions a multi-bit design would rest on, not a design.

TWO QUESTIONS:
1. SHARED BUDGET. A cell has a limited capacity to make protein. With a fixed
   total of B mean ON repressor molecules shared by N toggles, each toggle gets
   B / N, so each toggle is noisier as N grows. How does the chance that the
   WHOLE word (all N bits) is still right after 24 hours and about 41 divisions
   fall with N and B? It is compared with the independent-bits prediction
   (single-bit fidelity ** N); a gap would mean the toggles interfere through
   something this model has (crosstalk) or the estimate is noisy.
2. CROSSTALK. Real repressors are never perfectly orthogonal. A foreign
   toggle's repressors count, with weight eps, as extra repressor at every
   other toggle's promoters: effective repressor = own opponent + eps * (all
   foreign repressor molecules). How much eps can an 8-bit word take?

MODEL:
N copies of the two-stage toggle (mRNA decay 20, protein loss by dilution only,
growth to volume 2 and binomial partitioning, bsubtilis_34's settings), one
cell lineage followed for 28.8 protein lifetimes (24 hours at the repo's
mapping). Burst size 5. Each word is a random bit pattern. Bits are scored
individually and as a word.

WHAT THIS DOES NOT DO:
Toggles are otherwise independent: no shared transcription or ribosome
competition beyond the molecule budget, no burden on growth, no plasmid or
gene copy number, no selection, no read-out error. Whether enough orthogonal,
well-behaved repressor pairs exist in B. subtilis to build N toggles is a
biology question this file cannot answer (the model's "pairs" are free). The
budget B, burst size and eps are sweep axes, not measurements. One bit per
toggle, so N toggles is N bits; no error-correcting code is modelled (that
would help; see the closing note).
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
V_STEP = 0.02
F_DIL = 1.0


def _binom(n, rnd):
    if n <= 0:
        return 0
    if n > 200:
        return min(n, max(0, int(round(rnd.gauss(n / 2.0, math.sqrt(n) / 2.0)))))
    return sum(1 for _ in range(n) if rnd.random() < 0.5)


def run_word(args):
    """Returns (list of per-bit correct flags). Omega is per toggle."""
    N, Omega, b, eps, seed = args
    rnd = random.Random(seed)
    bits = [rnd.randint(0, 1) for _ in range(N)]
    k_p = b * GAMMA_M
    k_tx = A1 * Omega / b
    P = [[0, 0] for _ in range(N)]
    M = [[0, 0] for _ in range(N)]
    for k in range(N):
        on = 0 if bits[k] == 1 else 1
        P[k][on] = int(round(A1 * Omega))
        M[k][on] = int(round(k_tx / GAMMA_M))
    V = 1.0
    t = 0.0
    next_v = V_STEP
    inv = 1.0 / Omega
    mu = F_DIL
    g_deg = 1.0 - F_DIL
    while t < T_UNITS:
        S = sum(P[k][0] + P[k][1] for k in range(N)) if eps > 0 else 0
        props = []
        tot = 0.0
        for k in range(N):
            p0, p1 = P[k][0] / (Omega * V), P[k][1] / (Omega * V)
            x = eps * (S - P[k][0] - P[k][1]) / (Omega * V) if eps > 0 else 0.0
            r1, r0 = p1 + x, p0 + x
            a = (k_tx * V / (1.0 + r1 * r1), k_tx * V / (1.0 + r0 * r0),
                 GAMMA_M * M[k][0], GAMMA_M * M[k][1],
                 k_p * M[k][0], k_p * M[k][1],
                 g_deg * P[k][0], g_deg * P[k][1])
            props.append(a)
            tot += sum(a)
        t_new = t + (-math.log(1.0 - rnd.random()) / tot if tot > 0 else 1e9)
        if t_new >= next_v:
            t = next_v
            V *= math.exp(mu * V_STEP)
            next_v += V_STEP
            if V >= 2.0:
                V /= 2.0
                for k in range(N):
                    for arr in (P[k], M[k]):
                        arr[0] = _binom(arr[0], rnd)
                        arr[1] = _binom(arr[1], rnd)
            continue
        t = t_new
        r = rnd.random() * tot
        done = False
        for k in range(N):
            a = props[k]
            s = sum(a)
            if r >= s:
                r -= s
                continue
            for j in range(8):
                if r < a[j]:
                    if j == 0: M[k][0] += 1
                    elif j == 1: M[k][1] += 1
                    elif j == 2: M[k][0] -= 1
                    elif j == 3: M[k][1] -= 1
                    elif j == 4: P[k][0] += 1
                    elif j == 5: P[k][1] += 1
                    elif j == 6: P[k][0] -= 1
                    else: P[k][1] -= 1
                    break
                r -= a[j]
            done = True
            break
        if not done:
            continue
    return [int((P[k][0] > P[k][1]) == (bits[k] == 1)) for k in range(N)]


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def run_grid(configs, n_runs, tag):
    jobs = [(N, Om, b, eps, 60000 + 997 * tag + 131 * i + 7 * k)
            for i, (N, Om, b, eps) in enumerate(configs) for k in range(n_runs)]
    with Pool(4) as pool:
        out = pool.map(run_word, jobs, chunksize=2)
    acc = {}
    for j, o in zip(jobs, out):
        acc.setdefault(j[:4], []).append(o)
    return acc


def budget_section(n_runs=30):
    print("=" * 92)
    print("1) FIXED TOTAL BUDGET B (mean ON repressor molecules shared by all toggles), burst 5, no crosstalk")
    print("   per-toggle molecules = B / N; 30 words per cell; 24 h equivalent with division")
    print("=" * 92)
    Ns = [1, 2, 4, 8]
    Bs = [200, 400, 800]
    configs = [(N, B / (50.0 * N), 5, 0.0) for B in Bs for N in Ns]
    acc = run_grid(configs, n_runs, 1)
    print(f"{'B':>6}{'N bits':>8}{'mols/toggle':>13}{'per-bit':>10}{'word (all N right)':>22}{'independent p^N':>18}")
    for B in Bs:
        for N in Ns:
            runs = acc[(N, B / (50.0 * N), 5, 0.0)]
            flat = [x for r in runs for x in r]
            pb = sum(flat) / len(flat)
            wk = sum(1 for r in runs if all(r))
            lo, hi = wilson(wk, len(runs))
            print(f"{B:>6}{N:>8}{B / N:>13.0f}{pb:>10.0%}{wk / len(runs):>10.0%} ({lo:.0%}-{hi:.0%})".ljust(58)
                  + f"{pb ** N:>12.0%}")
    print("\nA word needs EVERY bit right, so it falls roughly as per-bit fidelity ** N even before any crosstalk.")


def crosstalk_section(n_runs=30):
    print("\n" + "=" * 92)
    print("2) CROSSTALK at 8 bits, 100 molecules per toggle (B = 800), burst 5")
    print("   eps = weight of a foreign toggle's repressors at another toggle's promoters")
    print("=" * 92)
    epss = [0.0, 0.003, 0.01, 0.03, 0.1]
    configs = [(8, 2.0, 5, e) for e in epss]
    acc = run_grid(configs, n_runs, 2)
    print(f"{'eps':>8}{'per-bit':>10}{'word (all 8 right)':>24}")
    for e in epss:
        runs = acc[(8, 2.0, 5, e)]
        flat = [x for r in runs for x in r]
        pb = sum(flat) / len(flat)
        wk = sum(1 for r in runs if all(r))
        lo, hi = wilson(wk, len(runs))
        print(f"{e:>8g}{pb:>10.0%}{wk / len(runs):>10.0%} ({lo:.0%}-{hi:.0%})")
    print("\nWith 8 toggles there are 14 foreign repressor molecule pools; the effective crosstalk grows with N, so")
    print("an eps that is harmless for 2 bits can break 16.")


def main():
    budget_section()
    crosstalk_section()


if __name__ == '__main__':
    main()
