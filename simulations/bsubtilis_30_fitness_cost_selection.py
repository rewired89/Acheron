"""
Acheron Simulation 30: What If Cells That Lose the Circuit Grow Faster?
=====================================================================

PURPOSE:
Every simulation in this project assumes the circuit is free: expressing two
repressors and two reporters costs the cell nothing, and no cell ever loses
or silences it. Real constructs cost energy and resources. Over a long
culture, any cell that mutates a promoter, silences the reporters or loses
the integrant can outgrow the cells that carry the bit. That is selection,
not noise, and in a cytometry histogram it looks exactly like state loss, so
it can make a 72 hour pass/fail result ambiguous. An outside review raised
this (audit Part 30) and a search of the audit, bench protocol, experiments
and simulation map found no mention of fitness, burden or competition.

WHAT THIS DOES:
A population-level model with three kinds of cell:
  - circuit cells holding the WRITTEN state,
  - circuit cells that have FLIPPED to the other state (rate swept),
  - LOST cells that no longer express the circuit (reporter negative).
Each generation, lost cells grow (1 + s) times as fast as circuit cells, and
circuit cells turn into lost cells at rate mu per division. Serial dilution
back to a fixed size is implicit (the model tracks fractions). It reports
two readouts side by side:
  - UNGATED fraction holding the written state (every cell counted, which is
    what a naive cytometry read gives), and
  - GATED fraction (reporter-positive cells only, which separates "flipped"
    from "lost").
Sections: A) expected loss after 72 / 144 generations over a grid of s and
mu, B) generations until the ungated read drops below the 70 percent bar,
C) a stochastic version with a finite dilution bottleneck, to show the
spread, D) the same grid at only 7 generations, which is what a damage and
regrowth experiment (Experiment 3) involves, E) why gating matters, F)
SURVIVOR BIAS: if the cells that survive damage are not a random sample
(lost or downregulating cells survive more or less often than circuit cells),
the regrowth result is measuring the wrong subpopulation, and selection that
happened BEFORE the damage matters even though regrowth itself is short, G)
the same question in the cell-level regrowth engine of bsubtilis_27: the
headline claim is that a handful of survivors regrows to a correct colony, so
what if some survivors are already wrong-state or already lost the circuit?

WHAT THIS DOES NOT DO:
No value of s, mu or the flip rate is measured. All three are SWEEP AXES, so
the output is a map of how fast a bit disappears under each assumption, not
a prediction for B. subtilis. Mutation is treated as one lumped rate to the
lost state; real loss routes (point mutation, deletion, epigenetic-like
silencing, recombination between repeated parts) differ. Lost cells are
assumed to never revert. The competition assay and growth-rate comparison in
Experiment 1 exist to measure s directly.
"""

import os
import sys
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

PASS_BAR = 0.70
S_VALUES = [0.0, 0.01, 0.03, 0.10, 0.30]            # relative growth advantage of lost cells
MU_VALUES = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]          # loss events per circuit-cell division
GENERATIONS_72H = [36, 72, 144]                     # 72 h at 120, 60, 30 min doubling


def trajectory(s: float, mu: float, generations: int, flip: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
    """Expected fractions per generation. Returns (ungated, gated) arrays of
    length generations + 1. f = lost fraction, c = written-state share of the
    circuit cells."""
    f, c = 0.0, 1.0
    ungated = [1.0]
    gated = [1.0]
    for _ in range(generations):
        lost = (1.0 + s) * f + (1.0 - f) * mu
        circuit = (1.0 - f) * (1.0 - mu)
        f = lost / (lost + circuit)
        c = c * (1.0 - flip) + (1.0 - c) * flip
        ungated.append((1.0 - f) * c)
        gated.append(c)
    return np.array(ungated), np.array(gated)


def generations_to_bar(s: float, mu: float, flip: float = 0.0, cap: int = 2000) -> int:
    ungated, _ = trajectory(s, mu, cap, flip)
    below = np.where(ungated < PASS_BAR)[0]
    return int(below[0]) if below.size else -1


def stochastic_gens_to_bar(s: float, mu: float, bottleneck: int, reps: int = 30,
                           cap: int = 400, seed: int = 0) -> List[int]:
    """Wright-Fisher style: each generation the next population is a binomial
    sample of size `bottleneck` from the expected composition, so rare early
    losses can be lost or can jackpot."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(reps):
        n_lost, n_circ = 0, bottleneck
        hit = -1
        for g in range(1, cap + 1):
            lost_w = (1.0 + s) * n_lost + n_circ * mu
            circ_w = n_circ * (1.0 - mu)
            p_lost = lost_w / (lost_w + circ_w)
            n_lost = int(rng.binomial(bottleneck, p_lost))
            n_circ = bottleneck - n_lost
            if n_circ / bottleneck < PASS_BAR:
                hit = g
                break
        out.append(hit)
    return out


def survivor_bias_outcome(s: float, mu: float, pre_gens: int, bias: float,
                          regrowth_gens: int = 7) -> Tuple[float, float]:
    """Culture grows `pre_gens` generations before damage, then damage keeps a
    small survivor set in which lost cells are `bias` times as likely to
    survive as circuit cells (bias 1 = random survivors, >1 = lost cells
    over-represented, <1 = under-represented). Survivors then regrow for
    `regrowth_gens` generations. Returns (lost fraction among survivors,
    ungated written-state fraction after regrowth). The size of the survivor
    set is not modelled here; this tracks composition only."""
    f_pre = 1.0 - trajectory(s, mu, pre_gens)[0][-1]       # lost fraction before damage
    f = f_pre * bias / (f_pre * bias + (1.0 - f_pre))      # survivor composition
    start = f
    for _ in range(regrowth_gens):
        lost = (1.0 + s) * f + (1.0 - f) * mu
        circuit = (1.0 - f) * (1.0 - mu)
        f = lost / (lost + circuit)
    return start, 1.0 - f


def _survivor_job(args):
    from bsubtilis_27_noise_robustness_sweep import run_colony_trial_ex
    frac, bit, seed, wrong, lost = args
    return run_colony_trial_ex(frac, bit, seed, survivor_wrong_prob=wrong,
                               survivor_lost_prob=lost)['genetic']


def survivor_composition_sweep(fractions, probs, kind: str, n_trials: int = 30):
    """Cell-level regrowth where each survivor is independently WRONG-STATE
    (kind='wrong') or already LOST (kind='lost') with the given probability.
    Returns {(fraction, prob): (mean fidelity, share of trials >= 70%)}."""
    from multiprocessing import Pool
    jobs, keys = [], []
    for f in fractions:
        for q in probs:
            for b in (0, 1):
                for k in range(n_trials):
                    jobs.append((f, b, int(f * 10000) + k * 97 + b + int(q * 1000) * 13,
                                 q if kind == 'wrong' else 0.0,
                                 q if kind == 'lost' else 0.0))
                    keys.append((f, q))
    with Pool(4) as pool:
        out = pool.map(_survivor_job, jobs)
    acc = {}
    for key, r in zip(keys, out):
        acc.setdefault(key, []).append(r)
    return {k: (float(np.mean(v)), float(np.mean([x >= PASS_BAR for x in v])))
            for k, v in acc.items()}


def fmt_gen(g: int) -> str:
    return ">2000" if g < 0 else str(g)


def main():
    print("=" * 92)
    print("A) EXPECTED UNGATED FRACTION HOLDING THE WRITTEN STATE (no state flipping)")
    print("   rows: growth advantage s of circuit-lost cells | columns: loss rate mu per division")
    print("=" * 92)
    for gens in GENERATIONS_72H:
        print(f"\n--- after {gens} generations ---")
        print(f"{'s':<8}" + "".join(f"mu={m:.0e}".rjust(11) for m in MU_VALUES))
        for s in S_VALUES:
            row = [trajectory(s, m, gens)[0][-1] for m in MU_VALUES]
            print(f"{s:<8.2f}" + "".join(f"{x:>10.0%} " for x in row))

    print("\n" + "=" * 92)
    print("B) GENERATIONS UNTIL THE UNGATED READ FALLS BELOW THE 70% BAR")
    print("=" * 92)
    print(f"{'s':<8}" + "".join(f"mu={m:.0e}".rjust(11) for m in MU_VALUES))
    for s in S_VALUES:
        print(f"{s:<8.2f}" + "".join(f"{fmt_gen(generations_to_bar(s, m)):>10} " for m in MU_VALUES))

    print("\n" + "=" * 92)
    print("C) STOCHASTIC: generations to the bar with a finite dilution bottleneck")
    print("   median [5th-95th percentile] over 30 replicates; '-' = never within 400 generations")
    print("=" * 92)
    for bottleneck in (10_000, 1_000_000):
        print(f"\nbottleneck = {bottleneck:,} cells")
        for s, m in ((0.03, 1e-4), (0.10, 1e-5), (0.10, 1e-3), (0.30, 1e-6)):
            g = np.array([x for x in stochastic_gens_to_bar(s, m, bottleneck) if x > 0])
            hit = f"{len(g)}/30 reached"
            if len(g):
                print(f"  s={s:<5} mu={m:.0e}: median {np.median(g):.0f} "
                      f"[{np.percentile(g, 5):.0f}-{np.percentile(g, 95):.0f}]  ({hit})")
            else:
                print(f"  s={s:<5} mu={m:.0e}: -  ({hit})")

    print("\n" + "=" * 92)
    print("D) SAME GRID AFTER ONLY 7 GENERATIONS (what damage + regrowth involves)")
    print("=" * 92)
    print(f"{'s':<8}" + "".join(f"mu={m:.0e}".rjust(11) for m in MU_VALUES))
    for s in S_VALUES:
        print(f"{s:<8.2f}" + "".join(f"{trajectory(s, m, 7)[0][-1]:>10.0%} " for m in MU_VALUES))

    print("\n" + "=" * 92)
    print("E) WHY GATING MATTERS: 72 generations, s=0.10, mu=1e-3, flip rate swept")
    print("=" * 92)
    print(f"{'flip/gen':<10}{'ungated':>10}{'gated':>10}")
    for flip in (0.0, 1e-4, 1e-3, 1e-2):
        u, g = trajectory(0.10, 1e-3, 72, flip)
        print(f"{flip:<10.0e}{u[-1]:>10.0%}{g[-1]:>10.0%}")
    print("\n" + "=" * 92)
    print("F) SURVIVOR BIAS: culture grows 72 generations, damage keeps survivors in which")
    print("   lost cells are `bias` times as likely to survive as circuit cells, then 7")
    print("   generations of regrowth. Cells show lost share among survivors / ungated held.")
    print("=" * 92)
    biases = [0.5, 1.0, 2.0, 5.0, 10.0]
    print(f"{'s':<6}{'mu':<9}" + "".join(f"bias={b:g}".rjust(16) for b in biases))
    for s_, m_ in ((0.0, 1e-4), (0.03, 1e-4), (0.10, 1e-5), (0.10, 1e-4), (0.10, 1e-3)):
        cells = [survivor_bias_outcome(s_, m_, 72, b) for b in biases]
        print(f"{s_:<6.2f}{m_:<9.0e}" + "".join(f"{lo:>8.0%} /{hd:>5.0%}  " for lo, hd in cells))
    print("\nbias=1 is random survivors (what bsubtilis_07 assumes). The direction of real")
    print("bias is unknown and is NOT modelled; both directions are swept. Where the")
    print("pre-damage lost share is already large, any bias above 1 makes recovery look worse,")
    print("and any bias below 1 makes it look better than a random-survivor model says.")
    print("\n" + "=" * 92)
    print("G) SURVIVOR COMPOSITION IN THE CELL-LEVEL ENGINE: each survivor independently")
    print("   wrong-state (or already lost) with probability q. Cells show mean fidelity /")
    print("   share of colonies that still clear the 70% bar. 1, 3 and 13 survivors = 2%, 5%, 20%.")
    print("=" * 92)
    fractions, probs = [0.02, 0.05, 0.20], [0.0, 0.05, 0.10, 0.25, 0.50]
    for kind in ("wrong", "lost"):
        res = survivor_composition_sweep(fractions, probs, kind)
        print(f"\nsurvivors that are {kind.upper()}" + ("-STATE" if kind == "wrong" else " (circuit gone)"))
        print(f"{'survivors':<11}" + "".join(f"q={q:g}".rjust(14) for q in probs))
        for f in fractions:
            n = max(1, int(round(64 * f)))
            print(f"{n:<11}" + "".join(
                f"{res[(f, q)][0]:>7.0%} /{res[(f, q)][1]:>4.0%} " for q in probs))
    print("\nWrong-state and lost survivors give identical numbers on this ungated read, because")
    print("both simply fail to hold the written bit. They differ only on the gated read (the")
    print("mechanism number): lost cells leave it, wrong-state cells stay in it.")
    print("\nRecovery fidelity tracks survivor composition, because division copies whatever the")
    print("survivors hold. The claim that 2% survivors recover to 100% is therefore exactly as good")
    print("as the assumption that those survivors are all correct. With one survivor the outcome is")
    print("all or nothing; with more survivors the mean is the same but the spread narrows.")
    print("\nRead-me: ungated falls from BOTH loss and flipping, gated only from flipping.")
    print("A low ungated read with a high gated read means the circuit was lost, not the bit.")
    print("=" * 92)


if __name__ == '__main__':
    main()
