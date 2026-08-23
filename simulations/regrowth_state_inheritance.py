"""
Acheron Simulation 8: Regrowth State Inheritance
====================================================

PURPOSE:
Every prior simulation tested either (a) a pattern sitting still with no
injury at all, or (b) a DELIBERATE handoff to a separate, externally-
controlled fresh tile. Neither tests the actual question this project's
original scientific audit flagged as its most important open item: if the
organism is damaged and heals ITSELF, in place, with no external
controller rewriting anything, does the surviving tissue's engineered
state successfully propagate into the newly regenerated tissue, or does
new tissue come back in a naive/default state with no memory of what was
there before?

This also covers a related, biologically real scenario: planarians don't
just heal small wounds, they reproduce asexually via FISSION, splitting
into fragments that each regenerate into a complete new organism
(Sakurai et al. 2012, DOI 10.1387/ijdb.113439ts). Whatever fraction of a
fragment's cells survived the split already hold the correct engineered
state; the rest of the new organism is built by neoblasts, planaria's
distributed pluripotent stem cells (Sal√≥ 2006, DOI 10.1002/bies.20416).
This simulation asks: for a given surviving fraction, does the final
regenerated organism end up holding the correct data?

MODEL:
Deliberately reuses the SAME validated bistable + noise physics from
gardner_toggle_circuit.py and the SAME coupling mechanism from
biofilm_tile_handoff.py, rather than inventing new, unvalidated physics.
A fragment is modeled as a population of units: a surviving fraction that
already holds the correct state, and a "naive" fraction (representing
neoblast-derived new tissue) that starts unwritten and is exposed to
mean-field coupling from the surviving population throughout the
regeneration window.

HONEST LIMITS OF THIS MODEL (read before citing a result from this file):
- The coupling mechanism (local propagation of a bistable attractor state)
  is validated for the bacterial biofilm case, NOT for planarian tissue.
  Applying it here is a principled first estimate, not a claim about real
  planarian neoblast biology.
- Real neoblast differentiation, migration timing, and whether/how they
  actually sense surrounding bioelectric state are empirical unknowns.
  This model's timing is drawn from regeneration_data_loss_window.py's
  literature-derived estimates (~24-36h total), not new data.
- This is exactly the kind of result that answers "is this worth wet-lab
  testing" - it is NOT a substitute for the wet-lab test itself.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from gardner_toggle_circuit import GardnerParams, GardnerToggleCell


@dataclass
class RegrowthConfig:
    surviving_fraction: float       # fraction of fragment already holding correct state at t=0
    n_units: int = 60               # total units modeled in the regenerated organism
    coupling_k: float = 0.05        # naive-unit <- survivor-population coupling strength
    regen_hours: float = 30.0       # total regrowth window (~24-36h, per regeneration_data_loss_window.py)


def run_regrowth_trial(config: RegrowthConfig, target_bit: int, seed: int,
                        params: GardnerParams = None) -> float:
    """
    Simulate one fragment regenerating. Returns the fraction of the FINAL
    organism (survivors + newly-formed units) that reads out as the
    correct bit after the regeneration window.
    """
    params = params or GardnerParams()
    rng = np.random.default_rng(seed)
    n_survivors = int(round(config.n_units * config.surviving_fraction))
    n_naive = config.n_units - n_survivors

    cells = []
    # Survivors: already committed, written before the injury/fission event.
    for i in range(n_survivors):
        c = GardnerToggleCell(params, seed=int(rng.integers(0, 2**31)),
                               transcriptional_noise_std=3.0)
        c.write(target_bit)
        cells.append(c)
    # Naive units: neoblast-derived, start unwritten (symmetric, uncommitted state).
    for i in range(n_naive):
        c = GardnerToggleCell(params, seed=int(rng.integers(0, 2**31)),
                               transcriptional_noise_std=3.0)
        cells.append(c)

    n_steps = int(config.regen_hours * 60 / 1.0)
    for _ in range(n_steps):
        # Mean-field coupling: survivor population's average state pulls on
        # every naive unit, same coupling form as propagate_handoff() in
        # biofilm_tile_handoff.py, applied continuously through the window
        # rather than a fixed pulse.
        if n_survivors > 0:
            survivor_u = np.mean([c.u for c in cells[:n_survivors]])
            survivor_v = np.mean([c.v for c in cells[:n_survivors]])
        else:
            survivor_u = survivor_v = 0.0

        for i, c in enumerate(cells):
            if i < n_survivors:
                c.step(dt=0.02)
            else:
                # Naive unit: own dynamics plus a pull toward the survivor
                # population's average commitment.
                du = params.alpha1 / (1 + c.v ** params.beta) - c.u
                dv = (params.alpha2 * params.strength_ratio) / (1 + c.u ** params.gamma) - c.v
                du += rng.normal(0, 3.0) + config.coupling_k * (survivor_u - c.u)
                dv += rng.normal(0, 3.0) + config.coupling_k * (survivor_v - c.v)
                c.u = max(0.0, c.u + du * 0.02)
                c.v = max(0.0, c.v + dv * 0.02)

    correct = sum(1 for c in cells if c.read_genetic() == target_bit)
    return correct / config.n_units


def sweep_surviving_fraction(fractions: List[float], n_trials: int = 12) -> Dict[float, float]:
    """For each surviving fraction, average final-organism correctness over n_trials."""
    results = {}
    for frac in fractions:
        config = RegrowthConfig(surviving_fraction=frac)
        scores = []
        for bit in [0, 1]:
            for trial in range(n_trials):
                seed = int(frac * 10000) + trial * 97 + bit
                scores.append(run_regrowth_trial(config, bit, seed))
        results[frac] = float(np.mean(scores))
    return results


def main():
    print("=" * 72)
    print("REGROWTH STATE INHERITANCE — does the regenerated organism keep the data?")
    print("=" * 72)

    fractions = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90, 1.0]
    print("\nScenario A: fission-style split, whole-organism regrowth from a fragment")
    print(f"{'Surviving fraction':<22}{'Final organism correctness':>28}")
    results = sweep_surviving_fraction(fractions)
    threshold_found = None
    for frac, score in results.items():
        status = "PASS" if score >= 0.70 else "FAIL"
        if status == "PASS" and threshold_found is None and frac > 0:
            threshold_found = frac
        print(f"{frac:<22.0%}{score:>27.1%}   {status}")

    print("\n" + "=" * 72)
    print("INTERPRETATION")
    print("=" * 72)
    if threshold_found:
        print(f"Under this coupling model, ~{threshold_found:.0%} surviving correctly-stated")
        print("tissue is where the regenerated organism starts reliably keeping its data.")
        print("Below that, coupling from survivors isn't strong enough to pull enough")
        print("naive neoblast-derived tissue into the correct state.")
    else:
        print("No surviving-fraction level in this sweep reliably preserved the data -")
        print("at this coupling strength, even mostly-intact fragments lose the signal.")
    print("\nThis quantifies your own intuition ('there's a limit') instead of leaving")
    print("it qualitative - but remember the honest limits noted at the top of this")
    print("file: the coupling strength itself is borrowed from the bacterial model,")
    print("not measured in real planarian tissue. This tells you the shape of the")
    print("answer and what to go measure, not the final answer.")
    print("=" * 72)


if __name__ == '__main__':
    main()
