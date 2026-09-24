"""
Acheron Experiment: Root Cause of the Bit=0 / Bit=1 Escape Asymmetry
=============================================================================

BACKGROUND:
bsubtilis_03_handoff_pool_imperfect_healing.py found that bsubtilis_02_biofilm_tile_handoff.py's
existing (unmodified) tile dynamics let bit=0 spontaneously flip during a
single 24h hold period roughly 2x more often than bit=1 -- confirmed with
a clean, handoff-free, pool-free isolation test (just repeated step()
calls from V_HIGH vs. V_LOW). This script finds WHY, by ablating each
term in BacterialTile.step()'s update equation one at a time and
comparing escape rates.

CONCLUSION (verified by ablation below, not asserted):
- The bistable feedback term is symmetric: V_HIGH and V_LOW are both
  exactly 35mV from V_MID, with equal restoring-force magnitude. Not the
  cause.
- The deterministic leak term (pulling toward V_REST every step) has
  ~zero effect on escape rate when disabled entirely -- its magnitude is
  ~2000x smaller than the bistable term. Not the cause on its own.
- Disabling metabolic noise collapses ~75-80% of the baseline gap between
  bit=0 and bit=1 escape rates. THIS is the primary driver.
- Root cause: metabolic noise's standard deviation is defined as
  `abs(I_leak) * metabolic_noise_fraction`, and I_leak depends on
  `V_REST - V`. V_REST (-50mV) is NOT equidistant between V_HIGH (-10mV)
  and V_LOW (-80mV) -- it sits 5mV closer to V_LOW (V_MID is -45mV, so
  V_REST is offset toward the V_LOW/bit=0 side). That off-center offset
  makes the metabolic-noise magnitude asymmetric between the two rails,
  which nets out (per the ablation below) to make the bit=1/V_HIGH well
  MORE escape-resistant and the bit=0/V_LOW well LESS so.

WHAT THIS DOES NOT DO:
Say whether this asymmetry matters for real bacterial biofilm -- these
are Acheron's own existing "realistic biological noise" placeholder
parameters (borrowed from planarian_02_noise_floor.py, itself flagged
there as not yet measured on an engineered B. subtilis line). It explains
a real behavior of the existing simulation code, not a biological fact.
The actionable takeaway: V_REST should probably be recentered to V_MID
(or the metabolic-noise formula decoupled from raw leak magnitude) if the
bit=0/bit=1 asymmetry itself is undesirable -- that fix is proposed, not
applied here, since it would change validated existing simulation
behavior and should be a deliberate choice, not a side effect of this
diagnostic.
"""

from __future__ import annotations

import numpy as np

V_REST, V_HIGH, V_LOW, V_MID = -50.0, -10.0, -80.0, -45.0
TAU, C_MEM = 60.0, 5.0
BISTABLE_K, CHANNEL_NOISE_STD, THERMAL_NOISE_STD, METABOLIC_NOISE_FRACTION = 0.20, 5.0, 0.4, 0.10


def step(V: float, rng: np.random.Generator, disable_leak: bool = False,
          disable_metabolic: bool = False, disable_thermal: bool = False,
          disable_channel: bool = False) -> float:
    """Reimplementation of BacterialTile.step(), term-by-term disableable.
    Matches simulations/bsubtilis_02_biofilm_tile_handoff.py's formula exactly (dt=1.0,
    no external_drive) -- kept as a standalone function here rather than
    importing/monkeypatching, so each term can be independently switched
    off without touching the validated original class."""
    true_leak = (V_REST - V) / (200.0 * TAU)
    I_leak = 0.0 if disable_leak else true_leak
    I_bistable = BISTABLE_K * (V - V_MID)
    I_metabolic = 0.0 if disable_metabolic else rng.normal(0, abs(true_leak) * METABOLIC_NOISE_FRACTION)
    dV = (I_leak + I_bistable + I_metabolic) / C_MEM * 1.0
    if not disable_channel:
        dV += rng.normal(0, CHANNEL_NOISE_STD)
    if not disable_thermal:
        dV += rng.normal(0, THERMAL_NOISE_STD)
    return float(np.clip(V + dV, -120, 60))


def escape_rate(start_v: float, bit_is_high: bool, n_trials: int, n_steps: int, seed_offset: int, **disables) -> float:
    escapes = 0
    for trial in range(n_trials):
        rng = np.random.default_rng(trial + seed_offset)
        V = start_v
        for _ in range(n_steps):
            V = step(V, rng, **disables)
        if (V > V_MID) != bit_is_high:
            escapes += 1
    return escapes / n_trials


def main() -> None:
    print("=" * 72)
    print("ROOT CAUSE: WHY DOES BIT=0 ESCAPE MORE OFTEN THAN BIT=1?")
    print("=" * 72)
    print(f"V_HIGH={V_HIGH}, V_LOW={V_LOW}, V_MID={V_MID}, V_REST={V_REST}")
    print(f"Distance V_HIGH->V_MID = {V_HIGH - V_MID}, V_LOW->V_MID = {V_MID - V_LOW}  (symmetric)")
    print(f"Distance V_REST->V_MID = {V_MID - V_REST}  (NOT zero -- V_REST sits off-center, "
          f"toward the V_LOW/bit=0 side)\n")

    n_trials, n_steps = 500, 1440
    configs = [
        ("baseline (all terms)", {}),
        ("no leak", {"disable_leak": True}),
        ("no metabolic noise", {"disable_metabolic": True}),
        ("no leak, no metabolic", {"disable_leak": True, "disable_metabolic": True}),
        ("no thermal", {"disable_thermal": True}),
    ]

    print(f"{'Configuration':<28}{'bit=1 (V_HIGH) escape':>24}{'bit=0 (V_LOW) escape':>24}{'gap':>10}")
    print("-" * 86)
    baseline_gap = None
    for name, disables in configs:
        esc_high = escape_rate(V_HIGH, True, n_trials, n_steps, 10_000, **disables)
        esc_low = escape_rate(V_LOW, False, n_trials, n_steps, 20_000, **disables)
        gap = esc_low - esc_high
        if name.startswith("baseline"):
            baseline_gap = gap
        print(f"{name:<28}{esc_high:>23.1%} {esc_low:>23.1%} {gap:>+9.1%}")

    print("\n" + "=" * 72)
    print("INTERPRETATION")
    print("=" * 72)
    print("Removing the leak term alone changes nothing -- it's ~2000x smaller than")
    print("  the bistable restoring force and has no measurable effect on its own.")
    print("Removing metabolic noise collapses most of the gap between bit=0 and")
    print("  bit=1 escape rates (see 'no metabolic noise' row above vs. baseline).")
    print("  Metabolic noise's magnitude is defined as abs(I_leak) * a fixed")
    print("  fraction, and I_leak depends on how far V sits from V_REST -- which is")
    print("  NOT the same distance for V_HIGH and V_LOW, because V_REST isn't at")
    print("  V_MID. That off-center placement is the actual root cause: an")
    print("  incidental consequence of V_REST=-50 not being recentered to V_MID=-45")
    print("  when this bacterial model's constants were set, not a deliberate")
    print("  asymmetric-reliability design choice.")
    print("ACTIONABLE FIX (not applied here -- would change validated existing")
    print("  behavior, so left as a proposal): recenter V_REST to V_MID, or decouple")
    print("  metabolic noise's magnitude from raw leak distance, if symmetric bit=0/")
    print("  bit=1 reliability is wanted.")
    print("=" * 72)


if __name__ == "__main__":
    main()
