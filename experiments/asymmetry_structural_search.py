"""
Acheron Experiment: Automated Structural Search for the Residual Bit=0/Bit=1
Escape Asymmetry
=============================================================================

BACKGROUND:
bit_asymmetry_root_cause.py found, by hand-picked one-at-a-time ablation,
that metabolic noise's coupling to V_REST is the primary driver of the
bit=0/bit=1 escape-rate gap in BacterialTile.step() (biofilm_tile_handoff.py).
It also tested ONE candidate fix (recentering V_REST to V_MID) without
applying it, found it closes ~60% of the gap, and speculated -- without
testing -- that the asymmetric clip bounds (-120, 60; midpoint -30, not
V_MID=-45) are the likely remaining cause. THIS SCRIPT TESTS THAT SPECULATION,
instead of leaving it as an untested guess.

WHY THIS IS THE RIGHT SHAPE OF EXPERIMENT (and its real limits):
This is modeled on the METHODOLOGICAL PATTERN of Lobo, Morokuma & Levin
(2016), "Computational discovery and in vivo validation of hnf4 as a
regulatory gene in planarian regeneration": don't hand-pick one hypothesis
and check it, search the whole small space of candidate structural fixes,
and treat CONVERGENCE ACROSS MANY INDEPENDENT RANDOM-SEED RUNS -- not a
single lucky run -- as the evidence standard. That paper searched a
combinatorial gene-regulatory-network topology space against real published
phenotype data and then validated the winning prediction with an actual
RNAi knockdown experiment in living planaria.

THIS SCRIPT DOES NOT DO THAT. It searches a 3-factor structural space
against Acheron's own existing simulation code, using noise parameters that
biofilm_tile_handoff.py and noise_floor_characterizer.py already flag as
unmeasured placeholders (no patch-clamp data exists yet for an engineered
B. subtilis line). Any "discovery" here is a finding about this simulation's
own equations, not a validated fact about real bacterial biofilm -- exactly
the same caveat bit_asymmetry_root_cause.py already applies to itself. There
is no wet-lab validation step here, unlike Lobo et al. That is the honest
scope of a computational-only discovery loop: it produces a specific,
falsifiable prediction, not proof.

SEARCH SPACE (3 independent binary structural factors, 8 combinations):
  - v_rest_fix:          off (V_REST=-50, original) / on (V_REST=V_MID=-45)
  - symmetric_clip:      off (-120, 60, original)   / on (V_MID-90, V_MID+90)
  - decoupled_metabolic: off (noise scales with |V_REST - V|, original)
                         on  (noise scales with |V_MID - V|, symmetric by
                              construction around the bistable center)

For each of the 8 combinations, the escape-rate gap (bit=0 escape rate minus
bit=1 escape rate) is measured across N_BATCHES independent random-seed
batches, not one run. A combination only counts as "closing the gap" if the
mean gap across batches is small AND consistent (low batch-to-batch spread)
-- the same convergence-over-independent-runs standard the background
section above describes.
"""

from __future__ import annotations

import numpy as np
from itertools import product

V_HIGH, V_LOW, V_MID = -10.0, -80.0, -45.0
V_REST_ORIGINAL = -50.0
TAU, C_MEM = 60.0, 5.0
BISTABLE_K = 0.20
CHANNEL_NOISE_STD, THERMAL_NOISE_STD, METABOLIC_NOISE_FRACTION = 5.0, 0.4, 0.10
CLIP_ORIGINAL = (-120.0, 60.0)
CLIP_SYMMETRIC = (V_MID - 90.0, V_MID + 90.0)  # same 180mV width, centered on V_MID

N_STEPS = 1440       # 24h at dt=1min, matches bit_asymmetry_root_cause.py
N_TRIALS_PER_BATCH = 2000
N_BATCHES = 20


def simulate_escape_rate(v_rest: float, clip_bounds: tuple[float, float],
                          decoupled_metabolic: bool, start_v: float, bit_is_high: bool,
                          n_trials: int, n_steps: int, rng: np.random.Generator) -> float:
    """Vectorized reimplementation of BacterialTile.step()'s escape test,
    run across n_trials independent trajectories at once. Matches the
    original formula exactly when v_rest=V_REST_ORIGINAL,
    clip_bounds=CLIP_ORIGINAL, decoupled_metabolic=False."""
    V = np.full(n_trials, start_v, dtype=float)
    lo, hi = clip_bounds
    for _ in range(n_steps):
        I_leak = (v_rest - V) / (200.0 * TAU)
        I_bistable = BISTABLE_K * (V - V_MID)
        if decoupled_metabolic:
            # Symmetric by construction: same |distance from V_MID| means
            # same noise magnitude for V_HIGH and V_LOW, unlike the original
            # formula which references V_REST (off-center vs. V_MID).
            noise_std = (np.abs(V_MID - V) / (200.0 * TAU)) * METABOLIC_NOISE_FRACTION
        else:
            noise_std = np.abs(I_leak) * METABOLIC_NOISE_FRACTION
        I_metabolic = rng.normal(0.0, noise_std)
        dV = (I_leak + I_bistable + I_metabolic) / C_MEM
        dV += rng.normal(0.0, CHANNEL_NOISE_STD, size=n_trials)
        dV += rng.normal(0.0, THERMAL_NOISE_STD, size=n_trials)
        V = np.clip(V + dV, lo, hi)
    escaped = (V > V_MID) != bit_is_high
    return float(escaped.mean())


def measure_gap(v_rest: float, clip_bounds: tuple[float, float], decoupled_metabolic: bool,
                 combo_index: int) -> tuple[float, float]:
    """Returns (mean gap, std of gap) across N_BATCHES independent random-seed batches."""
    gaps = []
    for batch in range(N_BATCHES):
        rng_high = np.random.default_rng(combo_index * 100_000 + batch * 2)
        rng_low = np.random.default_rng(combo_index * 100_000 + batch * 2 + 1)
        esc_high = simulate_escape_rate(v_rest, clip_bounds, decoupled_metabolic,
                                         V_HIGH, True, N_TRIALS_PER_BATCH, N_STEPS, rng_high)
        esc_low = simulate_escape_rate(v_rest, clip_bounds, decoupled_metabolic,
                                        V_LOW, False, N_TRIALS_PER_BATCH, N_STEPS, rng_low)
        gaps.append(esc_low - esc_high)
    return float(np.mean(gaps)), float(np.std(gaps))


def main() -> None:
    print("=" * 78)
    print("STRUCTURAL SEARCH: WHAT CLOSES THE RESIDUAL BIT=0/BIT=1 ESCAPE GAP?")
    print("=" * 78)
    print(f"Baseline (all factors off) reproduces bit_asymmetry_root_cause.py's")
    print(f"baseline config: V_REST={V_REST_ORIGINAL}, clip={CLIP_ORIGINAL}, "
          f"metabolic noise referenced to V_REST.")
    print(f"{N_BATCHES} independent random-seed batches x {N_TRIALS_PER_BATCH} trials "
          f"each, per combination.\n")

    factor_names = ("v_rest_fix", "symmetric_clip", "decoupled_metabolic")
    results = []
    for combo_index, (vr_fix, clip_fix, decouple_fix) in enumerate(product([False, True], repeat=3)):
        v_rest = V_MID if vr_fix else V_REST_ORIGINAL
        clip_bounds = CLIP_SYMMETRIC if clip_fix else CLIP_ORIGINAL
        mean_gap, std_gap = measure_gap(v_rest, clip_bounds, decouple_fix, combo_index)
        results.append({
            "v_rest_fix": vr_fix, "symmetric_clip": clip_fix,
            "decoupled_metabolic": decouple_fix,
            "mean_gap": mean_gap, "std_gap": std_gap,
        })

    header = f"{'v_rest_fix':<12}{'sym_clip':<11}{'decoupled':<12}{'mean_gap':>10}{'std_gap':>10}{'|gap|/std':>12}"
    print(header)
    print("-" * len(header))
    for r in sorted(results, key=lambda r: abs(r["mean_gap"])):
        ratio = abs(r["mean_gap"]) / r["std_gap"] if r["std_gap"] > 1e-9 else float("inf")
        print(f"{str(r['v_rest_fix']):<12}{str(r['symmetric_clip']):<11}"
              f"{str(r['decoupled_metabolic']):<12}{r['mean_gap']:>+9.1%} "
              f"{r['std_gap']:>9.1%} {ratio:>11.2f}")

    baseline = next(r for r in results if not r["v_rest_fix"]
                     and not r["symmetric_clip"] and not r["decoupled_metabolic"])
    best = min(results, key=lambda r: abs(r["mean_gap"]))

    print("\n" + "=" * 78)
    print("INTERPRETATION")
    print("=" * 78)
    print(f"Baseline gap (matches bit_asymmetry_root_cause.py): "
          f"{baseline['mean_gap']:+.1%} +/- {baseline['std_gap']:.1%}")
    print(f"Best combination found by search: v_rest_fix={best['v_rest_fix']}, "
          f"symmetric_clip={best['symmetric_clip']}, "
          f"decoupled_metabolic={best['decoupled_metabolic']}")
    print(f"  -> gap {best['mean_gap']:+.1%} +/- {best['std_gap']:.1%} "
          f"(|gap|/std = {abs(best['mean_gap']) / best['std_gap'] if best['std_gap'] > 1e-9 else float('inf'):.2f})")
    print()
    print("A ratio well below ~1 means the residual gap is statistically")
    print("indistinguishable from batch-to-batch noise at this sample size --")
    print("i.e. the search converged on a combination that closes the gap, not")
    print("just one that happened to look good in a single run.")
    print()
    print("WHAT THIS DOES NOT DO: confirm any of this matters for a real")
    print("bacterial biofilm -- these are still Acheron's own placeholder noise")
    print("parameters (see biofilm_tile_handoff.py's own caveat), unmeasured on")
    print("any real engineered B. subtilis line. This closes a specific,")
    print("previously-untested question about the EXISTING SIMULATION CODE:")
    print("whether the clip-bound asymmetry speculated about in")
    print("bit_asymmetry_root_cause.py actually contributes, and whether")
    print("decoupling metabolic noise from V_REST (rather than just recentering")
    print("V_REST) is a cleaner or more complete fix. Those are testable,")
    print("falsifiable claims about code, reproducible by rerunning this script.")
    print("=" * 78)


if __name__ == "__main__":
    main()
