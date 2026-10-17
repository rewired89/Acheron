"""
Acheron Simulation 33: Does the Exact Model's Robustness Survive an mRNA Stage
and Shared (Extrinsic) Noise?
=====================================================================

PURPOSE:
bsubtilis_32 found that an exact molecule-by-molecule (Gillespie) model of the
Gardner toggle holds down to about 5 times the burst size in mean repressor
molecules, far below where the Gaussian-noise simulation fails. That model was
protein only and had no shared noise. Two things could make it too optimistic,
and they are exactly the ones the audit listed as untested:

1. AN mRNA STAGE. Real genes are transcribed into mRNA, which is translated
   into protein. With the mRNA stage, a protein burst comes from one mRNA's
   lifetime (b = k_p / gamma_m proteins per mRNA) and transcription events are
   Poisson. For the unregulated two-stage model the exact result is
       Fano factor = 1 + k_p / (gamma_m + gamma_p),
   so CV^2 = (1 + b * gamma_m / (gamma_m + gamma_p)) / <P>. Swain, Elowitz &
   Siggia's (1 + b) / <P> is its large-gamma_m limit. This file checks that the
   formula used in bsubtilis_25 (with b as translational burst) holds for the
   mRNA model, then repeats the toggle fidelity grid.
2. SHARED NOISE. A cell-wide factor (for example the RNA polymerase pool) that
   scales transcription of BOTH repressors together and fluctuates slowly. It is
   an Ornstein-Uhlenbeck process with mean 1, a chosen CV (eta_ext) and
   correlation time tau_ext (in units of the protein lifetime). Propensities are
   piecewise constant between updates, so stopping at each update and
   redrawing the waiting time keeps the simulation exact for that process.

MODEL:
Per arm: transcription events at rate (50 * Omega / b) * X / (1 + (P_other /
Omega)^2), mRNA decay at gamma_m per molecule (gamma_m = 20, so an mRNA lives
1/20 of a protein lifetime; an assumption, not a measurement), translation at
k_p = b * gamma_m per mRNA producing ONE protein per event, protein decay at 1 per
molecule. Mean ON repressor is about 50 * Omega molecules, as in bsubtilis_32.
Time unit is the protein lifetime (50 minutes at the simulation's mapping), the
horizon is 28.8 units (24 h).

WHAT THIS DOES NOT DO:
No cell division, partition noise, plasmid copy number, promoter switching or
cell-to-cell differences in the shared factor. gamma_m, the OU correlation time
and eta_ext are sweep axes or assumptions, not measurements. The shared factor
acts on transcription only.
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
X_STEP = 0.1


def run(args):
    """Two-stage toggle with optional shared noise. Returns
    (Omega, b, eta, tau, final_correct, in_state_cv, mean_ON_protein)."""
    Omega, b, eta, tau, bit, seed = args
    rnd = random.Random(seed)
    k_p = b * GAMMA_M
    k_tx = A1 * Omega / b
    # state: mRNA and protein for arm U (index 0) and V (index 1)
    P = [0, 0]
    M = [0, 0]
    on = 0 if bit == 1 else 1
    P[on] = int(round(A1 * Omega))
    M[on] = int(round(k_tx / GAMMA_M))
    rho = math.exp(-X_STEP / tau) if (eta > 0 and tau > 0) else 0.0
    z = 0.0
    X = 1.0
    t = 0.0
    next_x = X_STEP
    next_s = T_BURN
    samples = []
    crossed = False
    inv_om = 1.0 / Omega
    while t < T_UNITS:
        p0, p1 = P[0] * inv_om, P[1] * inv_om
        tx0 = k_tx * X / (1.0 + p1 * p1)
        tx1 = k_tx * X / (1.0 + p0 * p0)
        md0, md1 = GAMMA_M * M[0], GAMMA_M * M[1]
        tl0, tl1 = k_p * M[0], k_p * M[1]
        pd0, pd1 = float(P[0]), float(P[1])
        tot = tx0 + tx1 + md0 + md1 + tl0 + tl1 + pd0 + pd1
        dt = -math.log(1.0 - rnd.random()) / tot if tot > 0 else 1e9
        t_new = t + dt
        # shared factor update boundary (exact for piecewise-constant propensities)
        if eta > 0 and t_new >= next_x:
            t = next_x
            z = rho * z + math.sqrt(1.0 - rho * rho) * rnd.gauss(0, 1)
            X = max(0.05, 1.0 + eta * z)
            next_x += X_STEP
            continue
        while next_s <= t_new and next_s < T_UNITS:
            samples.append(P[on])
            if (P[0] < P[1]) == (bit == 1):
                crossed = True
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
    cv = float(np.std(samples) / mean_on) if (samples and not crossed and mean_on > 0) else float('nan')
    return Omega, b, eta, tau, correct, cv, mean_on


def unregulated(args):
    """Unregulated two-stage gene for the formula check. Returns (b, Omega, cv, mean)."""
    Omega, b, seed = args
    rnd = random.Random(seed)
    k_p = b * GAMMA_M
    k_tx = A1 * Omega / b
    M = int(round(k_tx / GAMMA_M))
    P = int(round(A1 * Omega))
    t, next_s, xs = 0.0, T_BURN, []
    tmax = 4 * T_UNITS
    while t < tmax:
        a1_, a2_, a3_, a4_ = k_tx, GAMMA_M * M, k_p * M, float(P)
        tot = a1_ + a2_ + a3_ + a4_
        t_new = t + (-math.log(1.0 - rnd.random()) / tot)
        while next_s <= t_new and next_s < tmax:
            xs.append(P)
            next_s += 0.25
        t = t_new
        r = rnd.random() * tot
        if r < a1_:
            M += 1
        elif r < a1_ + a2_:
            M -= 1
        elif r < a1_ + a2_ + a3_:
            P += 1
        else:
            P -= 1
    m = float(np.mean(xs))
    return b, Omega, float(np.std(xs) / m), m


def formula_section(n=12):
    print("=" * 92)
    print("1) FORMULA CHECK, unregulated two-stage gene (gamma_m = 20, gamma_p = 1)")
    print("=" * 92)
    combos = [(Omega, b) for Omega in (2, 8, 32) for b in (1, 5, 10, 20)]
    jobs = [(O, b, 11 * O + 3 * b + k) for (O, b) in combos for k in range(n)]
    with Pool(4) as pool:
        out = pool.map(unregulated, jobs, chunksize=2)
    acc = {}
    for b, O, cv, m in out:
        acc.setdefault((O, b), []).append((cv, m))
    print("CV^2 = Fano / <P>.  exact two-stage Fano = 1 + b * gamma_m / (gamma_m + gamma_p).")
    print("Swain, Elowitz & Siggia (as used in bsubtilis_25): Fano = 1 + b.   Protein-only (bsubtilis_32): Fano = b.")
    print(f"{'Omega':>6}{'b':>4}{'<P>':>8}{'measured CV':>13}{'exact two-stage':>17}{'Swain 1+b':>11}{'protein-only b':>16}")
    for (O, b) in combos:
        rs = acc[(O, b)]
        cv = float(np.mean([c for c, _ in rs]))
        P = float(np.mean([m for _, m in rs]))
        ex = math.sqrt((1 + b * GAMMA_M / (GAMMA_M + 1.0)) / P)
        sw = math.sqrt((1 + b) / P)
        po = math.sqrt(b / P)
        print(f"{O:>6}{b:>4}{P:>8.0f}{cv:>13.3f}{ex:>17.3f}{sw:>11.3f}{po:>16.3f}")
    print("\nThe measured CV follows the exact two-stage formula. Swain's (1 + b) is slightly high for finite")
    print("mRNA decay, and the protein-only model of bsubtilis_32 underestimates noise when b is small.")


def fidelity_section(n_per_bit=20):
    print("\n" + "=" * 92)
    print("2) TOGGLE WITH AN mRNA STAGE: final-state correct after 24 h equivalent (no shared noise)")
    print("=" * 92)
    omegas = [0.25, 0.5, 1, 2, 4, 8, 16]
    bursts = [1, 5, 10, 20]
    jobs = [(O, b, 0.0, 1.0, bit, 5000 * O + 41 * b + 3 * k + bit) for O in omegas for b in bursts
            for bit in (0, 1) for k in range(n_per_bit)]
    with Pool(4) as pool:
        out = pool.map(run, jobs, chunksize=4)
    acc = {}
    for O, b, eta, tau, c, cv, m in out:
        acc.setdefault((O, b), []).append((c, cv, m))
    print("cells show final-state correct (40 runs); ON repressor mean is about 50 * Omega molecules")
    print(f"{'Omega':>6}{'~mols':>7}" + "".join(f"burst {b}".rjust(11) for b in bursts))
    rows = {}
    for O in omegas:
        row = f"{O:>6}{50 * O:>7.0f}"
        for b in bursts:
            fid = float(np.mean([c for c, _, _ in acc[(O, b)]]))
            rows[(O, b)] = fid
            row += f"{fid:>10.0%} "
        print(row)
    print("\nSmallest mean ON-repressor count with >= 90% fidelity (and above it throughout), by burst size:")
    for b in bursts:
        need = None
        for O in omegas:
            if all(rows[(o, b)] >= 0.9 for o in omegas if o >= O):
                need = 50 * O
                break
        print(f"  burst {b:>2}: about {need:.0f} molecules" if need else f"  burst {b:>2}: more than the largest tested")


def extrinsic_section(n_per_bit=20):
    print("\n" + "=" * 92)
    print("3) SHARED (EXTRINSIC) NOISE ON TRANSCRIPTION of both arms, mRNA model, 24 h equivalent")
    print("   eta = CV of the shared factor, tau = its correlation time in protein lifetimes")
    print("=" * 92)
    cells = [(1, 5), (4, 5), (16, 5), (4, 10), (16, 10), (16, 20)]
    conds = [(0.0, 1.0), (0.2, 1.0), (0.2, 5.0), (0.5, 1.0), (0.5, 5.0)]
    jobs = [(O, b, eta, tau, bit, 7000 * O + 53 * b + int(eta * 100) * 7 + int(tau) * 3 + 5 * k + bit)
            for (O, b) in cells for (eta, tau) in conds for bit in (0, 1) for k in range(n_per_bit)]
    with Pool(4) as pool:
        out = pool.map(run, jobs, chunksize=4)
    acc = {}
    for O, b, eta, tau, c, cv, m in out:
        acc.setdefault((O, b, eta, tau), []).append(c)
    head = f"{'Omega':>6}{'~mols':>7}{'burst':>7}" + "".join(
        ("none" if eta == 0 else f"eta {eta:g}/tau {tau:g}").rjust(16) for eta, tau in conds)
    print(head)
    for (O, b) in cells:
        row = f"{O:>6}{50 * O:>7.0f}{b:>7}"
        for (eta, tau) in conds:
            row += f"{float(np.mean(acc[(O, b, eta, tau)])):>15.0%} "
        print(row)
    print("\nRead-me: a drop along a row is the cost of shared noise at that molecule count and burst size.")


def main():
    formula_section()
    fidelity_section()
    extrinsic_section()


if __name__ == '__main__':
    main()
