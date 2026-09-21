"""
Acheron Simulation 23: A Damage-Sensing Reinforcement Circuit - Does
Actively Protecting the Bit During Regrowth Help?
================================================================================

PURPOSE:
Every damage/regrowth file so far (Parts 8, 20, 21, 22) treats recovery
as purely passive: cells divide, the circuit's own baseline dynamics
either hold the bit or don't, nothing in the design actively responds to
the fact that damage just happened. Part 22 found one real, if extreme,
weak point: at a very low assumed repressor copy number (~1 molecule),
partition noise degrades recovery to 66-87%. Founder's own idea (raised
earlier this session): what if cells could detect "I'm damaged" and DO
something about it, not just rely on ordinary division? This file builds
and tests the simplest version of that idea, using a real, well-known
bacterial mechanism as the template, and sees whether it rescues Part
22's specific weak point.

THE REAL BIOLOGY THIS IS MODELED ON:
Bacteria already have a real, extensively characterized damage-sensing
system: the SOS response. DNA damage activates RecA, which triggers
cleavage of the LexA repressor, de-repressing a whole regulon of
damage-response genes, a coordinated, transient, damage-triggered
transcriptional program. See Maslowska, Makiela-Dzbenska & Fijalkowska
(2019), "The SOS system: A complex and tightly regulated response to DNA
damage," Environmental and Molecular Mutagenesis 60(4):368-384, DOI
10.1002/em.22267, PMID 30447030; and Kaushik, Tiwari & Tiwari (2022),
"Interaction of RecA mediated SOS response with bacterial persistence,
biofilm formation, and host response," Int J Biol Macromol 217:931-943,
DOI 10.1016/j.ijbiomac.2022.07.176, PMID 35905765. Both establish the
mechanism (a real damage sensor exists and drives a real transcriptional
response) as fact, real, in B. subtilis's relatives and in general
bacterial biology.

WHAT THIS FILE PROPOSES, AND IS CLEAR IS A PROPOSAL, NOT A CITED RESULT:
Wiring a damage/stress-responsive promoter (SOS-like, or B. subtilis's
own analogous stress regulons) to TRANSIENTLY boost whichever arm of the
toggle switch is currently dominant, reinforcing the stored bit
specifically during the vulnerable regrowth window, then relaxing back
to baseline once regrowth completes. Nobody has built or measured this.
It is a design proposal using real, existing biological machinery (a
damage sensor and an inducible promoter both exist in real bacteria) to
solve a problem this project's own simulations found (Part 22), the same
category of grounded-but-unbuilt proposal as bsubtilis_01_gardner_toggle_circuit.py's
original repressor-to-ion-channel link.

WHAT THIS TESTS, PRECISELY:
Part 22's worst-case scenario (~1 molecule effective copy number, where
recovery degraded to 66-87%), rerun with the toggle's dominant arm
boosted by a swept multiplier (1x = no reinforcement, matching Part 22's
result exactly, up to 20x) during the regrowth phase only, reinforcement
switched off during settling (mimicking the SOS response's own resolve-
after-damage-clears pattern), tying the reinforcement's timing to
regrowth completion specifically. That timing match is this file's own
simplifying assumption, not a cited fact.

WHAT THIS DOES NOT DO:
Does not model the SOS response's own real activation/decay kinetics
(this file uses a simple on-during-regrowth/off-during-settling switch,
not a decaying signal), does not identify which specific B. subtilis
stress promoter would drive this in practice, and does not check whether
reinforcing the dominant arm this way has side effects on writability
(would a strongly reinforced circuit resist a NEW write attempt after
healing, when you want to change the bit? Not tested here, a real
follow-up question this design raises).
"""

import os
import sys
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from bsubtilis_01_gardner_toggle_circuit import GardnerParams, GardnerToggleCell
from bsubtilis_07_colony_regrowth import DOUBLING_TIME_MIN, SETTLE_WINDOW_HOURS
from bsubtilis_15_partition_noise_regrowth import partition_value

WORST_CASE_MOLECULES_PER_UNIT = 0.04  # Part 22's ~1-molecule extreme, where recovery degraded


class ReinforcedGardnerCell(GardnerToggleCell):
    """GardnerToggleCell with an added, proposed damage-triggered
    reinforcement: while `reinforcement_active`, whichever arm currently
    dominates gets its own promoter strength multiplied by
    `boost_multiplier`. Not existing biology, see module docstring."""

    def __init__(self, params: GardnerParams, seed: int = None,
                 transcriptional_noise_std: float = 0.0,
                 boost_multiplier: float = 1.0):
        super().__init__(params, seed=seed, transcriptional_noise_std=transcriptional_noise_std)
        self.boost_multiplier = boost_multiplier
        self.reinforcement_active = False

    def step(self, dt: float = 0.02):
        boost = self.boost_multiplier if self.reinforcement_active else 1.0
        alpha1_eff = self.p.alpha1 * (boost if self.u >= self.v else 1.0)
        alpha2_eff = (self.p.alpha2 * self.p.strength_ratio) * (boost if self.v > self.u else 1.0)

        du = alpha1_eff / (1 + self.v ** self.p.beta) - self.u
        dv = alpha2_eff / (1 + self.u ** self.p.gamma) - self.v
        if self.tx_noise > 0:
            du += self.rng.normal(0, self.tx_noise)
            dv += self.rng.normal(0, self.tx_noise)
        self.u = max(0.0, self.u + du * dt)
        self.v = max(0.0, self.v + dv * dt)

        target_V = self.V_HIGH if self.u > self.v else self.V_LOW
        dV = (target_V - self.V) * 0.05 * dt * 100
        dV += self.rng.normal(0, self.channel_noise * np.sqrt(dt))
        dV += self.rng.normal(0, self.thermal_noise * np.sqrt(dt))
        self.V = np.clip(self.V + dV, -120, 60)


def run_colony_trial(surviving_fraction: float, target_bit: int, seed: int,
                      boost_multiplier: float, n_cells: int = 64,
                      params: GardnerParams = None) -> float:
    params = params or GardnerParams()
    rng = np.random.default_rng(seed)

    n_survivors = max(1, int(round(n_cells * surviving_fraction))) if surviving_fraction > 0 else 0
    if n_survivors == 0:
        return 0.0

    cells = []
    for _ in range(n_survivors):
        c = ReinforcedGardnerCell(params, seed=int(rng.integers(0, 2**31)),
                                   transcriptional_noise_std=3.0,
                                   boost_multiplier=boost_multiplier)
        c.write(target_bit)
        c.reinforcement_active = True  # damage just happened, sensor triggers
        cells.append(c)

    total_minutes = SETTLE_WINDOW_HOURS * 60.0
    elapsed = 0.0

    while len(cells) < n_cells and elapsed < total_minutes:
        for _ in range(int(DOUBLING_TIME_MIN / 1.0)):
            for c in cells:
                c.step(dt=0.02)
        elapsed += DOUBLING_TIME_MIN
        new_cells = []
        for c in cells:
            u_a, u_b = partition_value(c.u, WORST_CASE_MOLECULES_PER_UNIT, rng)
            v_a, v_b = partition_value(c.v, WORST_CASE_MOLECULES_PER_UNIT, rng)
            c.u, c.v = u_a, v_a
            daughter = ReinforcedGardnerCell(params, seed=int(rng.integers(0, 2**31)),
                                              transcriptional_noise_std=3.0,
                                              boost_multiplier=boost_multiplier)
            daughter.u, daughter.v = u_b, v_b
            daughter.reinforcement_active = True
            new_cells.append(daughter)
            if len(cells) + len(new_cells) >= n_cells:
                break
        cells.extend(new_cells)
        cells = cells[:n_cells]

    # Regrowth complete (or time ran out): sensor resolves, matching the SOS
    # response's own damage-clears-so-response-resolves pattern (a modeling
    # choice, not a cited kinetic fact, see module docstring).
    for c in cells:
        c.reinforcement_active = False

    remaining_steps = int(max(0.0, total_minutes - elapsed))
    for _ in range(remaining_steps):
        for c in cells:
            c.step(dt=0.02)

    return sum(1 for c in cells if c.read_genetic() == target_bit) / len(cells)


def sweep(fractions: List[float], boost_multipliers: List[float],
          n_trials: int = 10) -> Dict:
    results = {}
    for boost in boost_multipliers:
        for frac in fractions:
            scores = []
            for bit in [0, 1]:
                for trial in range(n_trials):
                    seed = int(frac * 10000) + int(boost * 10) + trial * 97 + bit
                    scores.append(run_colony_trial(frac, bit, seed, boost))
            results[(boost, frac)] = float(np.mean(scores))
    return results


def main():
    print("=" * 86)
    print("DAMAGE-SENSING REINFORCEMENT - does actively protecting the bit help?")
    print("=" * 86)
    print(f"\nRe-testing Part 22's worst-case scenario (~1 effective molecule per cell,")
    print("molecules_per_unit={:.2f}), where recovery degraded to 66-87% with NO".format(
        WORST_CASE_MOLECULES_PER_UNIT))
    print("reinforcement (boost_multiplier=1.0 below should reproduce that result).\n")

    fractions = [0.02, 0.05, 0.10, 0.20, 0.50, 1.0]
    boost_multipliers = [1.0, 2.0, 5.0, 10.0, 20.0]

    results = sweep(fractions, boost_multipliers)

    header = f"{'Surviving':<12}" + "".join(f"{f'{b:.0f}x boost':>12}" for b in boost_multipliers)
    print(header)
    for frac in fractions:
        row = f"{frac:<12.0%}"
        for boost in boost_multipliers:
            row += f"{results[(boost, frac)]:>12.0%}"
        print(row)

    print("\n" + "=" * 86)
    print("INTERPRETATION")
    print("=" * 86)
    print("The 1x column should reproduce Part 22's ~1-molecule result (66-87%, worse at")
    print("higher damage). If higher boost multipliers recover accuracy back toward 100%,")
    print("that is the computational case for the founder's damage-sensing idea: a real,")
    print("buildable circuit addition (an SOS-like damage sensor wired to the toggle's")
    print("own dominant promoter) that specifically shores up the one weak point this")
    print("project's own noise testing found, rather than a general, unfocused fix.")
    print("If it doesn't help, or needs an unrealistically large boost, that's equally")
    print("worth knowing before proposing it as a real design addition.")
    print("=" * 86)


if __name__ == '__main__':
    main()
