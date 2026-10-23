"""
Acheron Simulation 32: Two Independent Cross-Checks of the Toggle Model
=====================================================================

PURPOSE:
Every noise-sensitive result in this project comes from one model: the
dimensionless Gardner toggle with additive Gaussian noise (bsubtilis_01). If
that model has a modelling-choice problem, every file built on it inherits it.
This file checks it two independent ways, using different mathematics:

A) ANALYTIC, no randomness. The toggle's fixed points satisfy
       u = a1 / (1 + v^beta),   v = a2 / (1 + u^gamma).
   Substituting v gives one equation in u, whose roots are found with a bracketed
   root finder. Stability follows from the Jacobian, whose eigenvalues are
   -1 +/- sqrt(d_u * d_v) with d_u = a1*beta*v^(beta-1)/(1+v^beta)^2 and
   d_v = a2*gamma*u^(gamma-1)/(1+u^gamma)^2 (stable iff d_u * d_v < 1). Exactly
   two stable points and one saddle means bistable. This gives the exact window
   of promoter strength ratios in which the toggle can hold two states, and a
   noise-free margin (distance from each stable point to the saddle). It is
   compared with where the simulation actually collapses and with the order in
   which mismatched variants fail under noise.

B) EXACT STOCHASTIC SIMULATION (Gillespie), in molecule counts. The same toggle
   as discrete molecules: production events (in bursts of mean size b, so the
   mean production flux is unchanged), one-molecule degradation, and the same
   Hill repression with half-maximum at Omega molecules per unit of u. The mean
   level of the ON repressor is about 50 * Omega molecules. It has no Gaussian
   approximation and no time step. It is compared with the simulation's
   noise-versus-fidelity curve through a scale-free quantity, the coefficient of
   variation (CV, standard deviation divided by mean) of the ON repressor, so the
   unit mismatch found in audit Part 31 cannot enter. It also checks the model's
   CV against the exact protein-only burst result CV^2 = b / <P> (Fano factor b)
   and shows how that relates to Swain, Elowitz & Siggia's CV^2 = (1 + b) / <P>,
   whose extra "1" comes from a Poisson mRNA stage that this model does not have.

C) CHEMICAL LANGEVIN (state-dependent noise). The same molecular model with the
   Gaussian approximation kept but the noise made proportional to the reaction
   fluxes, du = (f - u) dt + sqrt((f * (2b - 1) + u) / Omega) dW. It sits between
   the simulation's additive noise (the same size whatever the level) and the
   exact Gillespie model (noise that shrinks as the level shrinks), so it shows
   which feature of the noise decides the failure point.

WHAT THIS DOES NOT DO:
Agreement between these methods shows that the model's math and code are
consistent and that its conclusions do not hinge on one noise formulation. It
does NOT show the biology is right. The Gillespie model still has no mRNA stage,
no extrinsic noise and no cell division. Burst size b and molecule scale Omega are
sweep axes, not measurements.
"""

import math
import os
import random
import sys
from multiprocessing import Pool

import numpy as np
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(__file__))
from bsubtilis_01_gardner_toggle_circuit import GardnerParams, GardnerToggleCell
from bsubtilis_31_dt_independent_noise_rerun import GardnerToggleCellSDE

A1 = 50.0
T_UNITS = 28.8          # 24 h at one step of 0.02 dimensionless units per minute
T_BURN = 5.0
SAMPLE_DT = 0.5


# ---------------------------------------------------------------- analytic
def fixed_points(a1, a2, beta=2.0, gamma=2.0, n=20001):
    F = lambda u: u - a1 / (1 + (a2 / (1 + u ** gamma)) ** beta)
    us = np.linspace(1e-9, a1, n)
    fs = F(us)
    roots = []
    for i in range(n - 1):
        if fs[i] == 0:
            roots.append(us[i])
        elif fs[i] * fs[i + 1] < 0:
            roots.append(brentq(F, us[i], us[i + 1], xtol=1e-12))
    pts = []
    for u in roots:
        v = a2 / (1 + u ** gamma)
        du = a1 * beta * v ** (beta - 1) / (1 + v ** beta) ** 2
        dv = a2 * gamma * u ** (gamma - 1) / (1 + u ** gamma) ** 2
        lam = math.sqrt(du * dv)
        pts.append((u, v, 'stable' if lam < 1 else 'saddle'))
    return pts


def is_bistable(r):
    pts = fixed_points(A1, A1 * r)
    return sum(1 for p in pts if p[2] == 'stable') == 2


def window_edge(lo, hi):
    """Bisect the ratio at which bistability switches, between lo (one side) and hi."""
    s_lo = is_bistable(lo)
    for _ in range(40):
        mid = math.sqrt(lo * hi)
        if is_bistable(mid) == s_lo:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


def margin(r):
    """Smallest distance from a stable point to the saddle (noise-free basin margin)."""
    pts = fixed_points(A1, A1 * r)
    st = [(u, v) for u, v, k in pts if k == 'stable']
    sd = [(u, v) for u, v, k in pts if k == 'saddle']
    if len(st) < 2 or not sd:
        return 0.0
    return min(math.hypot(u - sd[0][0], v - sd[0][1]) for u, v in st)


def _sim_fid(args):
    r, tx, bit, k = args
    c = GardnerToggleCell(GardnerParams(strength_ratio=r), seed=k * 100 + bit,
                          transcriptional_noise_std=tx)
    c.write(bit)
    for _ in range(1440):
        c.step(dt=0.02)
    return int(c.read_genetic() == bit)


def analytic_section():
    print("=" * 92)
    print("A) ANALYTIC: where can the toggle hold two states? (a1 = 50, beta = gamma = 2)")
    print("=" * 92)
    lo_edge = window_edge(0.2, 0.5)
    hi_edge = window_edge(10.0, 20.0)
    print(f"Exact bistable window in the strength ratio a2/a1: {lo_edge:.3f} to {hi_edge:.2f}")
    print("Outside it there is one fixed point and the toggle cannot hold two states.\n")

    ratios = [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 1.0, 2.0, 5.0, 10.0, 12.0, 15.0, 18.0, 20.0, 30.0]
    jobs = [(r, 0.0, b, k) for r in ratios for b in (0, 1) for k in range(3)]
    with Pool(4) as pool:
        out = pool.map(_sim_fid, jobs)
    acc = {}
    for (r, tx, b, k), v in zip(jobs, out):
        acc.setdefault(r, []).append(v)
    print("Noise-free simulation (tx = 0): fidelity is 100% if two states exist, 50% if one.")
    print(f"{'ratio':>7}{'stable pts':>12}{'bistable (analytic)':>22}{'simulated fidelity':>22}")
    agree = 0
    for r in ratios:
        pts = fixed_points(A1, A1 * r)
        ns = sum(1 for p in pts if p[2] == 'stable')
        bist = ns == 2
        fid = float(np.mean(acc[r]))
        ok = (bist and fid > 0.95) or ((not bist) and fid < 0.55)
        agree += ok
        print(f"{r:>7.2f}{ns:>12}{str(bist):>22}{fid:>21.0%}  {'agree' if ok else 'DISAGREE'}")
    print(f"\nAgreement between analytic window and noise-free simulation: {agree} of {len(ratios)} ratios.")

    print("\nNoise-free basin margin (distance from the nearer stable point to the saddle) and the order")
    print("in which promoter-ratio variants lose fidelity under noise in the simulation (bsubtilis_27):")
    sim_first_below_90 = {1.0: 10, 2.0: 5, 5.0: 3, 10.0: 2}
    print(f"{'ratio':>7}{'margin':>10}{'noise multiple at which fidelity first drops below 90%':>62}")
    rs = [1.0, 2.0, 5.0, 10.0]
    ms = [margin(r) for r in rs]
    for r, m in zip(rs, ms):
        print(f"{r:>7.1f}{m:>10.1f}{sim_first_below_90[r]:>62}x")
    order_margin = sorted(rs, key=lambda r: -margin(r))
    order_sim = sorted(rs, key=lambda r: -sim_first_below_90[r])
    print(f"\nRanking by analytic margin (largest first): {order_margin}")
    print(f"Ranking by simulated noise tolerance:       {order_sim}")
    print("Same order means the simulation fails mismatched variants in the order the geometry predicts.")
    print("(Simulated thresholds come from the bsubtilis_27 table, 30 trials per bit, so +/- sampling noise.)")


# ---------------------------------------------------------------- Gillespie
def gillespie_run(args):
    Omega, b, bit, seed = args
    rnd = random.Random(seed)
    a1 = a2 = A1
    U = int(round(a1 * Omega)) if bit == 1 else 0
    V = 0 if bit == 1 else int(round(a2 * Omega))
    inv_b = 1.0 / b
    log1mp = math.log(1.0 - inv_b) if b > 1 else 0.0
    t = 0.0
    next_s = T_BURN
    on = []
    crossed = False
    while t < T_UNITS:
        u = U / Omega
        v = V / Omega
        pU = Omega * a1 / (1.0 + v * v) * inv_b
        pV = Omega * a2 / (1.0 + u * u) * inv_b
        tot = pU + pV + U + V
        if tot <= 0:
            break
        t += -math.log(1.0 - rnd.random()) / tot
        while next_s <= t and next_s < T_UNITS:
            on.append(U if bit == 1 else V)
            if (U < V) == (bit == 1):
                crossed = True
            next_s += SAMPLE_DT
        r = rnd.random() * tot
        if r < pU:
            U += 1 if b == 1 else 1 + int(math.log(1.0 - rnd.random()) / log1mp)
        elif r < pU + pV:
            V += 1 if b == 1 else 1 + int(math.log(1.0 - rnd.random()) / log1mp)
        elif r < pU + pV + U:
            U -= 1
        else:
            V -= 1
    correct = int((U > V) == (bit == 1))
    cv = float(np.std(on) / np.mean(on)) if (on and not crossed and np.mean(on) > 0) else float('nan')
    return Omega, b, correct, cv, (float(np.mean(on)) if on else 0.0)


def sde_run(args):
    tx, bit, k = args
    c = GardnerToggleCellSDE(GardnerParams(), seed=k * 100 + bit,
                             transcriptional_noise_std=tx, substeps=1)
    c.write(bit)
    on, crossed = [], False
    for i in range(1440):
        c.step(dt=0.02)
        if i >= 250 and (i - 250) % 25 == 0:
            on.append(c.u if bit == 1 else c.v)
            if (c.u < c.v) == (bit == 1):
                crossed = True
    correct = int(c.read_genetic() == bit)
    cv = float(np.std(on) / np.mean(on)) if (not crossed and np.mean(on) > 0) else float('nan')
    return tx, correct, cv


def gillespie_section(n_per_bit=20):
    print("\n" + "=" * 92)
    print("B) EXACT STOCHASTIC (GILLESPIE) vs THE SIMULATION, compared through the scale-free CV")
    print("=" * 92)
    omegas = [0.25, 0.5, 1, 2, 4, 8, 16, 32, 64]
    bursts = [1, 5, 10, 20]
    jobs = [(O, b, bit, 1000 * O + 17 * b + 3 * k + bit) for O in omegas for b in bursts
            for bit in (0, 1) for k in range(n_per_bit)]
    with Pool(4) as pool:
        out = pool.map(gillespie_run, jobs, chunksize=4)
    acc = {}
    for O, b, correct, cv, mean_on in out:
        acc.setdefault((O, b), []).append((correct, cv, mean_on))
    print("Gillespie, 24 h equivalent, matched promoters, 40 runs per row.")
    print("exact protein-only burst result: CV^2 = b / <P>.  Swain, Elowitz & Siggia: CV^2 = (1 + b) / <P>")
    print("(their extra '1' is a Poisson mRNA stage, absent here, so the two agree only for large b).")
    print(f"{'Omega':>6}{'burst b':>9}{'mean ON mols':>14}{'measured CV':>13}{'sqrt(b/P)':>11}{'Swain':>8}{'final-state correct':>21}")
    g_rows = []
    for b in bursts:
        for O in omegas:
            rs = acc[(O, b)]
            fid = float(np.mean([c for c, _, _ in rs]))
            cvs = [cv for _, cv, _ in rs if not math.isnan(cv)]
            cv = float(np.mean(cvs)) if cvs else float('nan')
            P = float(np.mean([m for _, _, m in rs]))
            f_cv = math.sqrt(b / P) if P > 0 else float('nan')
            sw_cv = math.sqrt((1 + b) / P) if P > 0 else float('nan')
            g_rows.append((b, O, P, cv, f_cv, fid))
            print(f"{O:>6}{b:>9}{P:>14.0f}{cv:>13.3f}{f_cv:>11.3f}{sw_cv:>8.3f}{fid:>20.0%}")

    print("\nSimulation (additive-noise SDE of bsubtilis_01, 24 h equivalent, 60 runs per row):")
    txs = [3, 6, 9, 12, 15, 21, 30, 45, 60]
    jobs = [(tx, bit, k) for tx in txs for bit in (0, 1) for k in range(30)]
    with Pool(4) as pool:
        out = pool.map(sde_run, jobs, chunksize=20)
    sacc = {}
    for tx, correct, cv in out:
        sacc.setdefault(tx, []).append((correct, cv))
    print(f"{'tx':>6}{'measured CV':>13}{'final-state correct':>21}")
    s_rows = []
    for tx in txs:
        rs = sacc[tx]
        fid = float(np.mean([c for c, _ in rs]))
        cvs = [cv for _, cv in rs if not math.isnan(cv)]
        cv = float(np.mean(cvs)) if cvs else float('nan')
        s_rows.append((tx, cv, fid))
        print(f"{tx:>6}{cv:>13.3f}{fid:>20.0%}")

    print("\nCV at which final-state fidelity first falls below 90% (same yardstick for every model):")
    def first_below(rows, cv_idx, fid_idx):
        cand = [(r[cv_idx], r[fid_idx]) for r in rows if not math.isnan(r[cv_idx])]
        cand.sort()
        for cv, fid in cand:
            if fid < 0.90:
                return cv
        return None
    s_cv = first_below(s_rows, 1, 2)
    print(f"  additive-noise simulation: CV about {s_cv:.3f}" if s_cv else "  additive-noise simulation: not reached")
    for b in bursts:
        rows = [r for r in g_rows if r[0] == b]
        g_cv = first_below(rows, 3, 5)
        top = max((r[3] for r in rows if not math.isnan(r[3])), default=float('nan'))
        print(f"  Gillespie, burst {b:>2}:        CV about {g_cv:.3f}" if g_cv else
              f"  Gillespie, burst {b:>2}:        no failure in this grid (largest CV reached {top:.2f})")

    print("\nSmallest mean ON-repressor count that still gives >= 90% final-state fidelity, by burst size:")
    for b in bursts:
        rows = sorted([r for r in g_rows if r[0] == b], key=lambda r: r[2])
        need = next((r[2] for r in rows if r[5] >= 0.90 and all(x[5] >= 0.90 for x in rows if x[2] >= r[2])), None)
        print(f"  burst {b:>2}: about {need:.0f} molecules" if need else f"  burst {b:>2}: more than the largest tested")
    print("\nRead-me: the additive-noise simulation and the exact molecular model do NOT agree on where the")
    print("toggle fails (see sections C and D for why). The molecule counts above are what Experiment 4")
    print("(molecules per cell) and Experiment 2 (burst size) need to be compared with.")


def cle_run(args):
    Omega, b, bit, seed, substeps = args
    rnd = random.Random(seed)
    a1 = a2 = A1
    u = a1 if bit == 1 else 0.0
    v = 0.0 if bit == 1 else a2
    h = 0.02 / substeps
    sq = math.sqrt(h)
    on, crossed = [], False
    for i in range(1440):
        for _ in range(substeps):
            fu = a1 / (1.0 + v * v)
            fv = a2 / (1.0 + u * u)
            nu = math.sqrt(max(fu * (2 * b - 1) + u, 0.0) / Omega) * sq * rnd.gauss(0, 1)
            nv = math.sqrt(max(fv * (2 * b - 1) + v, 0.0) / Omega) * sq * rnd.gauss(0, 1)
            u = max(0.0, u + (fu - u) * h + nu)
            v = max(0.0, v + (fv - v) * h + nv)
        if i >= 250 and (i - 250) % 25 == 0:
            on.append(u if bit == 1 else v)
            if (u < v) == (bit == 1):
                crossed = True
    correct = int((u > v) == (bit == 1))
    cv = float(np.std(on) / np.mean(on)) if (not crossed and np.mean(on) > 0) else float('nan')
    return Omega, b, correct, cv


def cle_section(n_per_bit=20):
    print("\n" + "=" * 92)
    print("C) CHEMICAL LANGEVIN (state-dependent noise) vs GILLESPIE, final-state correct after 24 h equivalent")
    print("=" * 92)
    omegas = [0.25, 0.5, 1, 2, 4, 8]
    bursts = [1, 5, 10, 20]
    jobs = [(O, b, bit, 7000 * O + 31 * b + 5 * k + bit, 4) for O in omegas for b in bursts
            for bit in (0, 1) for k in range(n_per_bit)]
    with Pool(4) as pool:
        out = pool.map(cle_run, jobs, chunksize=8)
    cacc = {}
    for O, b, c, cv in out:
        cacc.setdefault((O, b), []).append((c, cv))
    gjobs = [(O, b, bit, 9000 * O + 29 * b + 7 * k + bit) for O in omegas for b in bursts
             for bit in (0, 1) for k in range(n_per_bit)]
    with Pool(4) as pool:
        gout = pool.map(gillespie_run, gjobs, chunksize=8)
    gacc = {}
    for O, b, c, cv, m in gout:
        gacc.setdefault((O, b), []).append(c)
    print("cells show  Langevin / Gillespie  (40 runs each); ON repressor mean is about 50 * Omega molecules")
    print(f"{'Omega':>6}{'~mols':>7}" + "".join(f"burst {b}".rjust(16) for b in bursts))
    for O in omegas:
        row = f"{O:>6}{50 * O:>7.0f}"
        for b in bursts:
            lg = float(np.mean([c for c, _ in cacc[(O, b)]]))
            gi = float(np.mean(gacc[(O, b)]))
            row += f"{lg:>8.0%} /{gi:>5.0%}  "
        print(row)
    print("\nIf the molecular models hold where the additive-noise simulation fails, the simulation's")
    print("failure point comes from its noise being the same size in the repressed arm as in the active arm.")


def _off_arm_gillespie(args):
    Omega, b, seed = args
    rnd = random.Random(seed)
    a1 = a2 = A1
    U, V = int(round(a1 * Omega)), 0
    inv_b = 1.0 / b
    log1mp = math.log(1.0 - inv_b) if b > 1 else 0.0
    t, next_s, vs = 0.0, T_BURN, []
    while t < T_UNITS:
        u, v = U / Omega, V / Omega
        pU = Omega * a1 / (1.0 + v * v) * inv_b
        pV = Omega * a2 / (1.0 + u * u) * inv_b
        tot = pU + pV + U + V
        t += -math.log(1.0 - rnd.random()) / tot
        while next_s <= t and next_s < T_UNITS:
            vs.append(V / Omega)
            next_s += SAMPLE_DT
        r = rnd.random() * tot
        if r < pU:
            U += 1 if b == 1 else 1 + int(math.log(1.0 - rnd.random()) / log1mp)
        elif r < pU + pV:
            V += 1 if b == 1 else 1 + int(math.log(1.0 - rnd.random()) / log1mp)
        elif r < pU + pV + U:
            U -= 1
        else:
            V -= 1
    return float(np.mean(vs))


def _off_arm_sde(args):
    tx, seed = args
    c = GardnerToggleCellSDE(GardnerParams(), seed=seed, transcriptional_noise_std=tx, substeps=1)
    c.write(1)
    vs = []
    for i in range(1440):
        c.step(dt=0.02)
        if i >= 250 and (i - 250) % 25 == 0 and c.u > c.v:
            vs.append(c.v)
    return float(np.mean(vs)) if vs else float('nan')


def _off_arm_cle(args):
    Omega, b, seed = args
    rnd = random.Random(seed)
    u, v = A1, 0.0
    h = 0.02 / 4
    sq = math.sqrt(h)
    vs = []
    for i in range(1440):
        for _ in range(4):
            fu = A1 / (1.0 + v * v)
            fv = A1 / (1.0 + u * u)
            nu = math.sqrt(max(fu * (2 * b - 1) + u, 0.0) / Omega) * sq * rnd.gauss(0, 1)
            nv = math.sqrt(max(fv * (2 * b - 1) + v, 0.0) / Omega) * sq * rnd.gauss(0, 1)
            u = max(0.0, u + (fu - u) * h + nu)
            v = max(0.0, v + (fv - v) * h + nv)
        if i >= 250 and (i - 250) % 25 == 0 and u > v:
            vs.append(v)
    return float(np.mean(vs)) if vs else float('nan')


def off_arm_section(n=20):
    print("\n" + "=" * 92)
    print("D) WHY THE GAUSSIAN MODELS DISAGREE WITH THE EXACT ONE: the repressed arm sits near zero molecules")
    print("=" * 92)
    O, b = 1, 5
    det = A1 / (1.0 + A1 ** 2)
    with Pool(4) as pool:
        g = pool.map(_off_arm_gillespie, [(O, b, 100 + k) for k in range(n)])
        c = pool.map(_off_arm_cle, [(O, b, 200 + k) for k in range(n)])
        sd9 = pool.map(_off_arm_sde, [(9.0, 300 + k) for k in range(n)])
        sd21 = pool.map(_off_arm_sde, [(21.0, 400 + k) for k in range(n)])
    print(f"Mean level of the REPRESSED repressor (in units of u), written state, Omega={O}, burst {b}:")
    print(f"  noise-free value:                             {det:.3f}")
    print(f"  exact Gillespie (discrete molecules):         {np.nanmean(g):.3f}")
    print(f"  chemical Langevin (Gaussian, clipped at 0):   {np.nanmean(c):.3f}")
    print(f"  additive-noise simulation, tx = 9:            {np.nanmean(sd9):.3f}")
    print(f"  additive-noise simulation, tx = 21:           {np.nanmean(sd21):.3f}")
    print("\nA Gaussian kick with a floor at zero pushes the repressed arm up from its true near-zero level.")
    print("The raised repressor then suppresses the active arm and makes a flip far likelier than in the")
    print("exact model. That is the likely reason the Gaussian models fail where the discrete one holds.")


def main():
    analytic_section()
    gillespie_section()
    cle_section()
    off_arm_section()


if __name__ == '__main__':
    main()
