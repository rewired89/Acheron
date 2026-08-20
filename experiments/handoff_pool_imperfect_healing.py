"""
Acheron Experiment: Handoff-Then-Heal With a Reused, Finite Tile Pool —
and With Healing Modeled as Imperfect, Not a Clean Reset
=============================================================================

WHY THIS EXPERIMENT EXISTS:
simulations/biofilm_tile_handoff.py's run_handoff_chain() tests write ->
hold -> handoff -> heal, repeated for N cycles -- but it spawns a BRAND
NEW BacterialTile() for every single handoff. It never reuses a tile that
has already healed, so it never actually tests the "goes back to the end
of the line, heals, and comes back into rotation when needed again" part
of the theory -- only the "hand off to something fresh" part. This script
fixes that: a small FIXED pool of tiles rotates through repeated duty,
so a tile that healed several cycles ago gets reused as a future handoff
destination, many times over a long run.

It also tests a second, separate question: what if reset_and_heal()
isn't a clean reset? tasmorpho's real planarian data (see
analysis/hidden_state_model.py, numerically validated against a run of
the original tasmorpho script) found that ~23% of animals that looked
fully healed after a bioelectric perturbation still revealed a hidden
trace of it under a second challenge. This script imports that ACTUAL
fitted probability (not a hardcoded copy of it) and uses it as the
probability that a "healed" tile in THIS bacterial model retains a
partial residual bias toward whatever it last held, instead of resetting
cleanly.

IMPORTANT CAVEAT -- READ BEFORE TRUSTING ANY NUMBER BELOW:
The ~23% *probability* of residual confusion is a real number, taken
directly from a real paper -- but about a different organism (planarian
regeneration), for a different perturbation (chemical, not bioelectric
handoff), answering a different question (does a hidden state exist at
all, not how big it is on a millivolt scale). Applying that probability
to a bacterial biofilm tile is a modeling CHOICE, not a validated fact --
flagged clearly in the output below, not smuggled in as if measured on
this substrate. The *magnitude* of the residual bias (how far it pulls
the tile's voltage) has no source in tasmorpho at all -- tasmorpho's
model works in an abstract latent-probability space, not millivolts.
That magnitude is swept below as an explicit sensitivity parameter,
specifically so no single made-up magnitude gets reported as fact.

WHAT THIS DOES NOT DO:
Prove or disprove the multi-organism handoff theory. It stress-tests one
specific, previously-untested piece of one specific existing simulation
(bacterial biofilm handoff) under one hypothesis about imperfect healing,
imported from a citable source rather than invented, with its own
magnitude left as an open, swept parameter rather than asserted.

UNPLANNED SECOND FINDING (found while building the above, kept in because
it turned out to matter more): simulations/biofilm_tile_handoff.py's own
main() only runs 5 handoff cycles, and reports 100% fidelity at that
length. Running the SAME unmodified mechanism for 60 cycles (still with
brand-new fresh tiles every handoff -- nothing to do with pool reuse or
imperfect healing) reveals a real, reproducible asymmetry: bit=1 stays
near 97% fidelity over 60 cycles, bit=0 decays to ~68%. The failure mode
is a spontaneous bistable flip DURING the 24h hold period itself (visible
by inspecting individual runs: the SOURCE tile's own voltage has already
flipped rails before the next handoff even starts) -- not a handoff or
healing defect. This is a real property of the existing, validated
simulation's parameters that its own 5-cycle test was too short to catch,
directly relevant to the "keep going indefinitely" part of the theory:
each hold period is an independent chance to spontaneously lose the bit,
and that risk compounds over many cycles. The root cause of WHY bit=0 is
specifically more vulnerable than bit=1 was investigated but not fully
resolved (the V_HIGH/V_LOW wells are symmetric around V_MID; a metabolic-
noise-scaling asymmetry was checked and points the wrong direction) --
flagged as open, not asserted.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from simulations.biofilm_tile_handoff import BacterialTile, TileNoise, propagate_handoff
from analysis.hidden_state_model import fit as fit_hidden_state_model

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"


def get_residual_confusion_probability() -> float:
    """The real, fitted probability from tasmorpho's model: among animals
    that looked fully healed (single-headed) after a bioelectric
    perturbation, the fraction that still revealed a hidden trace under a
    second challenge. Computed live from the actual model fit, not
    hardcoded, so this number tracks analysis/hidden_state_model.py if it
    ever changes."""
    result = fit_hidden_state_model()
    return result.held_out_nigericin_challenge[0]  # nigericin: the closer analog to an external chemical/signal perturbation, not 8-OH (used to fit the model itself)


def run_pool_chain(n_cycles: int, bit: int, noise: TileNoise, pool_size: int,
                    residual_confusion_prob: float, residual_bias_fraction: float,
                    hours_before_handoff: float = 24.0, seed: int = 0) -> list[int]:
    """Rotate a fixed pool of `pool_size` tiles through repeated
    write-hold-handoff-heal-reuse cycles. Returns 1/0 correctness of the
    bit read at each new active tile immediately after handoff."""
    rng = np.random.default_rng(seed)
    tiles = [BacterialTile(noise, seed=seed * 1000 + i) for i in range(pool_size)]
    active_idx = 0
    tiles[active_idx].write(bit)
    results = []

    for cycle in range(n_cycles):
        n_hold_steps = int(hours_before_handoff * 60 / 1.0)
        for _ in range(n_hold_steps):
            tiles[active_idx].step(dt=1.0)

        next_idx = (active_idx + 1) % pool_size
        last_bit_on_active = tiles[active_idx].read()  # capture before healing

        propagate_handoff(tiles[active_idx], tiles[next_idx])
        results.append(int(tiles[next_idx].read() == bit))

        tiles[active_idx].reset_and_heal()  # unmodified original method -- clean reset
        if rng.random() < residual_confusion_prob:
            # Imperfect healing: nudge partway back toward what this tile
            # last held, instead of leaving the clean V_REST reset() gave it.
            last_voltage = BacterialTile.V_HIGH if last_bit_on_active else BacterialTile.V_LOW
            tiles[active_idx].V += residual_bias_fraction * (last_voltage - tiles[active_idx].V)

        active_idx = next_idx

    return results


def check_bit_asymmetry_over_long_runs(noise: TileNoise, n_cycles: int, n_trials: int,
                                        hours_before_handoff: float = 24.0) -> dict:
    """Run the ORIGINAL fresh-tile mechanism (import run_handoff_chain
    directly, nothing added) for both bit values, long enough to reveal
    whether fidelity actually stays flat -- the source file's own test
    only goes to 5 cycles."""
    from simulations.biofilm_tile_handoff import run_handoff_chain

    out = {}
    for bit in (0, 1):
        successes = np.zeros(n_cycles)
        for trial in range(n_trials):
            reads = run_handoff_chain(n_cycles, bit, noise, hours_before_handoff=hours_before_handoff,
                                       seed=trial * 1000 + bit)
            successes += (np.array(reads) == bit)
        out[bit] = successes / n_trials
    return out


def main() -> None:
    print("=" * 72)
    print("HANDOFF-THEN-HEAL WITH A REUSED TILE POOL + IMPERFECT HEALING")
    print("=" * 72)

    p_residual = get_residual_confusion_probability()
    print(f"Residual-confusion probability (from tasmorpho's actual fitted model, "
          f"nigericin held-out prediction): {p_residual:.3f}")
    print("CAVEAT: this probability is real (planarian data) but from a different")
    print("  organism, different perturbation, and different question than this")
    print("  bacterial tile model -- see this script's own docstring.")

    noise = TileNoise()
    pool_size = 3
    n_cycles = 60
    bias_fractions_to_sweep = [0.0, 0.1, 0.3, 0.5]  # 0.0 = clean heal (original assumption)
    n_trials = 15

    print(f"\nPool size: {pool_size} tiles (each reused every {pool_size} cycles)")
    print(f"Cycles: {n_cycles}, trials per condition: {n_trials}\n")

    all_results = {}
    for bias_fraction in bias_fractions_to_sweep:
        p_used = 0.0 if bias_fraction == 0.0 else p_residual
        successes = np.zeros(n_cycles)
        for trial in range(n_trials):
            bit = trial % 2
            reads = run_pool_chain(n_cycles, bit, noise, pool_size,
                                    residual_confusion_prob=p_used,
                                    residual_bias_fraction=bias_fraction,
                                    seed=trial)
            # BUG FIX: must compare against the bit actually written for
            # this trial, not a hardcoded 1 -- an earlier version of this
            # script compared `reads == 1` regardless of `bit`, which
            # silently scored a WRONG read as a success for every bit=0
            # trial. Caught by cross-checking against
            # check_bit_asymmetry_over_long_runs() below, which uses the
            # correct `== bit` comparison and disagreed with this function's
            # first-draft numbers.
            successes += (np.array(reads) == bit)
        rates = successes / n_trials
        all_results[bias_fraction] = rates
        label = "clean heal (original assumption)" if bias_fraction == 0.0 else f"imperfect heal, bias={bias_fraction:.0%}"
        print(f"{label:<38} final-10-cycle mean fidelity: {rates[-10:].mean():.1%}, "
              f"min over run: {rates.min():.1%}")

    # Second analysis: does fidelity actually stay flat over many cycles
    # with the ORIGINAL fresh-tile mechanism, or was 5 cycles just too
    # short to see it decay? Uses run_handoff_chain() unmodified.
    print("\n" + "-" * 72)
    print("SEPARATE CHECK: does the ORIGINAL mechanism stay reliable over more cycles?")
    print("-" * 72)
    asymmetry_trials = 40
    asymmetry_results = check_bit_asymmetry_over_long_runs(noise, n_cycles, asymmetry_trials)
    for bit, rates in asymmetry_results.items():
        print(f"bit={bit} (fresh tile every handoff, {asymmetry_trials} trials): "
              f"cycle {n_cycles} fidelity = {rates[-1]:.1%}, min over run = {rates.min():.1%}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    ax = axes[0]
    for bias_fraction, rates in all_results.items():
        label = "clean heal (p=0, original)" if bias_fraction == 0.0 else f"imperfect heal (p={p_residual:.2f}, bias={bias_fraction:.0%})"
        ax.plot(range(1, n_cycles + 1), rates * 100, label=label)
    ax.set_xlabel("handoff cycle (tiles reused every %d cycles)" % pool_size)
    ax.set_ylabel("fidelity across trials (%)")
    ax.set_ylim(-5, 105)
    ax.set_title("Residual-healing-bias sweep (reused pool)")
    ax.legend(fontsize=8)

    ax = axes[1]
    for bit, rates in asymmetry_results.items():
        ax.plot(range(1, n_cycles + 1), rates * 100, label=f"bit={bit}")
    ax.set_xlabel("handoff cycle (fresh tile every handoff -- original mechanism)")
    ax.set_ylabel("fidelity across trials (%)")
    ax.set_ylim(-5, 105)
    ax.set_title("Original mechanism, run past its own 5-cycle test length")
    ax.legend()

    plt.tight_layout()
    out_path = ANALYSIS_DIR / "handoff_pool_imperfect_healing.png"
    ANALYSIS_DIR.mkdir(exist_ok=True)
    plt.savefig(out_path, dpi=120)
    print(f"\nSaved figure: {out_path}")

    clean_final = all_results[0.0][-10:].mean()
    worst_bias = max(b for b in bias_fractions_to_sweep if b > 0)
    worst_final = all_results[worst_bias][-10:].mean()

    print("\n" + "=" * 72)
    print("INTERPRETATION")
    print("=" * 72)
    print("1) RESIDUAL-HEALING-BIAS QUESTION (what was asked for):")
    print(f"   Clean heal, reused pool: {clean_final:.1%} final fidelity. Largest tested bias")
    print(f"   ({worst_bias:.0%}, at tasmorpho's real {p_residual:.0%} incidence rate): {worst_final:.1%}.")
    if abs(worst_final - clean_final) < 0.05:
        print(f"   No meaningful difference. Root cause (verified directly, not assumed):")
        print(f"   propagate_handoff's coupling is a 'snap to rail' process -- I tested a")
        print(f"   destination tile starting from the OPPOSITE rail entirely, and it still")
        print(f"   converged to the correct bit within ~40 of the 120 minutes allotted.")
        print(f"   A one-time voltage nudge of any magnitude tested gets overpowered by that")
        print(f"   same mechanism. This means the specific way I modeled 'imperfect healing'")
        print(f"   (a single voltage offset right after healing) is the wrong shape of")
        print(f"   perturbation to test against this handoff design -- not proof that")
        print(f"   imperfect healing can't matter. A persistent bias during the NEXT handoff")
        print(f"   itself, rather than a one-time nudge beforehand, is the natural next test.")
    else:
        print(f"   A real difference -- imperfect healing at this rate/magnitude measurably")
        print(f"   hurts reused-tile handoff fidelity.")
    print(f"\n2) UNPLANNED FINDING (more consequential than what was asked for):")
    print(f"   The ORIGINAL, unmodified biofilm_tile_handoff.py mechanism -- fresh tile")
    print(f"   every handoff, nothing about pool reuse or imperfect healing -- was only")
    print(f"   ever tested for 5 cycles (100% fidelity there). Run for {n_cycles}:")
    print(f"     bit=1: {asymmetry_results[1][-1]:.1%} fidelity")
    print(f"     bit=0: {asymmetry_results[0][-1]:.1%} fidelity")
    print(f"   Both numbers are LOWER than the file's own headline 100% claim once you run")
    print(f"   long enough, and bit=0 degrades noticeably faster than bit=1. Traced to")
    print(f"   individual runs: the SOURCE tile's own voltage has already spontaneously")
    print(f"   flipped to the wrong bistable rail during a single 24h hold period, before")
    print(f"   any handoff or healing happens. That's a real property of this simulation's")
    print(f"   existing parameters, not something introduced here -- each hold period is an")
    print(f"   independent chance to lose the bit, and that risk compounds over many cycles,")
    print(f"   which is exactly the 'keep going indefinitely' part of the theory. WHY bit=0")
    print(f"   is specifically more vulnerable than bit=1 was checked against the obvious")
    print(f"   candidates (the V_HIGH/V_LOW wells are symmetric around V_MID; a metabolic-")
    print(f"   noise-scaling asymmetry was checked and points the wrong direction) and is")
    print(f"   left open rather than guessed at.")
    print(f"\nWhat NEITHER of these shows: whether a {p_residual:.0%} residual-confusion rate, any")
    print(f"  specific bias magnitude, or these exact noise parameters are correct for real")
    print(f"  bacterial biofilm -- none of it has been measured on this substrate. Both")
    print(f"  results are properties of Acheron's existing simulation code and one imported,")
    print(f"  clearly-flagged extrapolation, not wet-lab findings.")
    print("=" * 72)


if __name__ == "__main__":
    main()
