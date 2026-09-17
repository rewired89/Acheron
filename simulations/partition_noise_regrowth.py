"""
Acheron Simulation 22: Stochastic Partition Noise at Division - Does
Uneven Splitting Break the Damage/Regrowth Result?
================================================================================

PURPOSE:
Every damage/regrowth simulation in this project so far (Parts 8, 20, 21,
i.e. `bacterial_colony_regrowth.py` and everything built on top of it)
gives each daughter cell EXACTLY the mother's own repressor concentration
at division, deterministic inheritance. Every one of those files flags
this explicitly as a simplification: real division splits actual
molecule counts between two daughters, and that split is random, not
perfectly even. This file replaces the simplification with a real,
citable model of that randomness and re-tests whether the damage/regrowth
result (recovery from as little as 2% surviving cells) still holds.

THE REAL MATH THIS IS BUILT ON:
Huh & Paulsson (2011), "Non-genetic heterogeneity from stochastic
partitioning at cell division," Nature Genetics 43(2):95-100, DOI
10.1038/ng.729, PMID 21186354, PMC3208402. For a molecule segregating
BINOMIALLY at division (each individual copy has an independent 50%
chance of ending up in either daughter, the paper's own simplest and
most-ordered case), the paper derives the partitioning-error term
exactly (their Theory Box): kappa = 1/<X>, where <X> is the molecule's
average copy number. This means the relative noise added at each
division scales as 1/sqrt(copy number): a handful of copies splits very
unevenly by chance, thousands of copies split almost evenly. The paper
also states real segregation is often LESS ordered than pure binomial
(clustered or vesicle-bound molecules have kappa > 1/<X>), so binomial
partitioning, which is what this file implements, is a best-case
assumption, not a worst-case one.

THE UNMEASURED TRANSLATION THIS FILE HAS TO MAKE, STATED PLAINLY:
gardner_toggle_circuit.py's repressor concentrations (u, v) are
dimensionless, normalized units (alpha1/alpha2 ~ 50), not real molecule
counts. This project has no citation for how many actual repressor
protein molecules per cell that dimensionless scale corresponds to (real
bacterial transcription factors range from single digits, e.g. LacI, to
thousands, depending on the protein). Per docs/THIRD_PARTY_METHODS.md's
no-numeric-invention rule, this file sweeps an explicit
MOLECULES_PER_UNIT conversion (spanning very-low to high effective copy
number) instead of picking one value, so the result shows how the
finding depends on that assumption rather than asserting a single answer.

WHAT THIS TESTS, PRECISELY:
The same surviving-fraction sweep as `bacterial_colony_regrowth.py`, but
at every division event BOTH resulting daughters (not just the newly
created object, the "surviving" cell's own state is updated too) get a
freshly, independently binomially-partitioned share of the mother's u
and v, using the real kappa=1/<X> relationship above, instead of both
simply copying the mother's exact value.

WHAT THIS DOES NOT DO:
Does not model clustered/disordered partitioning (kappa > 1/<X>, which
Huh & Paulsson's own paper notes is common for eukaryotic and possibly
bacterial machinery), only the more-ordered binomial best case, so any
degradation found here is a floor, not a ceiling, on how much partition
noise could matter. Does not extend this to the fluorescent reporter or
voltage readouts (Parts 20-21), only the base genetic result Part 8
established. Both are natural follow-ups, not done here.
"""

import os
import sys
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from gardner_toggle_circuit import GardnerParams, GardnerToggleCell
from bacterial_colony_regrowth import DOUBLING_TIME_MIN, SETTLE_WINDOW_HOURS


def partition_value(value: float, molecules_per_unit: float,
                     rng: np.random.Generator) -> Tuple[float, float]:
    """Binomial partitioning at division (Huh & Paulsson 2011, kappa =
    1/<X>): each molecule independently has a 50% chance of going to
    either daughter. molecules_per_unit converts this model's
    dimensionless concentration units into an assumed molecule count."""
    if value <= 0 or molecules_per_unit <= 0:
        return value, value
    n_molecules = max(0, int(round(value * molecules_per_unit)))
    if n_molecules == 0:
        return 0.0, 0.0
    daughter_a_count = rng.binomial(n_molecules, 0.5)
    daughter_b_count = n_molecules - daughter_a_count
    return ((2.0 * daughter_a_count / n_molecules) * value,
            (2.0 * daughter_b_count / n_molecules) * value)


def run_colony_trial(surviving_fraction: float, target_bit: int, seed: int,
                      molecules_per_unit: float, n_cells: int = 64,
                      params: GardnerParams = None) -> float:
    params = params or GardnerParams()
    rng = np.random.default_rng(seed)

    n_survivors = max(1, int(round(n_cells * surviving_fraction))) if surviving_fraction > 0 else 0
    if n_survivors == 0:
        return 0.0

    cells = []
    for _ in range(n_survivors):
        c = GardnerToggleCell(params, seed=int(rng.integers(0, 2**31)),
                               transcriptional_noise_std=3.0)
        c.write(target_bit)
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
            u_a, u_b = partition_value(c.u, molecules_per_unit, rng)
            v_a, v_b = partition_value(c.v, molecules_per_unit, rng)
            c.u, c.v = u_a, v_a  # the surviving cell object becomes one daughter too
            daughter = GardnerToggleCell(params, seed=int(rng.integers(0, 2**31)),
                                          transcriptional_noise_std=3.0)
            daughter.u, daughter.v = u_b, v_b
            new_cells.append(daughter)
            if len(cells) + len(new_cells) >= n_cells:
                break
        cells.extend(new_cells)
        cells = cells[:n_cells]

    remaining_steps = int(max(0.0, total_minutes - elapsed))
    for _ in range(remaining_steps):
        for c in cells:
            c.step(dt=0.02)

    return sum(1 for c in cells if c.read_genetic() == target_bit) / len(cells)


def sweep(fractions: List[float], molecules_per_unit_values: List[float],
          n_trials: int = 10) -> Dict:
    results = {}
    for mpu in molecules_per_unit_values:
        for frac in fractions:
            scores = []
            for bit in [0, 1]:
                for trial in range(n_trials):
                    seed = int(frac * 10000) + int(mpu * 10) + trial * 97 + bit
                    scores.append(run_colony_trial(frac, bit, seed, mpu))
            results[(mpu, frac)] = float(np.mean(scores))
    return results


def main():
    print("=" * 86)
    print("STOCHASTIC PARTITION NOISE AT DIVISION - does uneven splitting break recovery?")
    print("=" * 86)

    fractions = [0.02, 0.05, 0.10, 0.20, 0.50, 1.0]
    # molecules_per_unit -> approx copy number at a typical value (~25, mid-range of alpha~50)
    molecules_per_unit_values = [0.04, 0.2, 1.0, 5.0, 20.0, 100.0]

    print("\nmolecules_per_unit is an unmeasured conversion (see module docstring) from this")
    print("model's dimensionless u/v units into an assumed real molecule count. Approx.")
    print("copy number shown is molecules_per_unit x 25 (a mid-range u/v value).\n")

    results = sweep(fractions, molecules_per_unit_values)

    header = f"{'Surviving':<12}" + "".join(f"{f'~{int(m*25)} molec':>14}" for m in molecules_per_unit_values)
    print(header)
    for frac in fractions:
        row = f"{frac:<12.0%}"
        for mpu in molecules_per_unit_values:
            row += f"{results[(mpu, frac)]:>14.0%}"
        print(row)

    print("\n" + "=" * 86)
    print("INTERPRETATION")
    print("=" * 86)
    print("bacterial_colony_regrowth.py found 100% recovery from 2% surviving cells with")
    print("NO partition noise (equivalent to the rightmost, highest-copy-number column")
    print("here approaching that same deterministic limit). Compare the leftmost columns")
    print("(low assumed copy number, where binomial partitioning noise is largest) to see")
    print("whether that result holds up once real, random division is modeled instead of")
    print("perfect inheritance, and at what copy number (if any) it starts to break down.")
    print("Since binomial partitioning is the BEST-CASE ordering (Huh & Paulsson found")
    print("real segregation is often less ordered than this), any degradation shown here")
    print("is a floor on the real effect, not a ceiling.")
    print("=" * 86)


if __name__ == '__main__':
    main()
