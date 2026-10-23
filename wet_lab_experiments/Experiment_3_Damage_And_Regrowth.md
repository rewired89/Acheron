# Experiment 3: Damage and Regrowth

**Tests:** `docs/SCIENTIFIC_AUDIT_2026.md` Part 8 (`simulations/bsubtilis_07_colony_regrowth.py`), Part 20 (`bsubtilis_13_reporter_colony_regrowth.py`), Part 22 (`bsubtilis_15_partition_noise_regrowth.py`).
**Bench protocol this is drawn from:** `experiments/BENCH_PROTOCOL_BSUBTILIS.md`, Stage B2.
**Prerequisite:** Experiment 1a passes (M1 confirmed bistable by hysteresis and the
mechanism number). Experiment 1b's growth-rate and competition results are needed
to interpret any shortfall here.

## The goal, plainly

This is the headline experiment, the one everything else has been leading up
to. Write a bit into the colony, hurt it on purpose, let it regrow, then
check whether the surviving colony still remembers what was written.

## Procedure: run two damage arms side by side

**Arm 2a, dilution only.** Write a bit (same write procedure as Experiment
1), then dilute the culture to a defined low CFU count and let it regrow.
This isolates exactly what the simulations model: fewer cells, more
divisions to reach full size, no other physiological change. Target
surviving fractions: 2%, 10%, 25%, 50%, 100%, with CFU plating to confirm
the actual survival number rather than the intended one.

**Arm 2b, real insult.** Write a bit, then apply a calibrated sublethal
insult (heat shock, or hydrogen peroxide, calibrated by CFU count to hit the
same survival fractions as 2a), then regrow. **The gap between 2a and 2b is
the measurement that matters** — every damage simulation in the repository
models damage purely as removing cells, with no physiological effect on the
survivors. Real damage stresses survivors, induces stress regulons, changes
growth rate. No simulation represents that; 2a minus 2b is the size of that
blind spot.

**Locus-stability check (cheap, run on the same cultures).** After the
final regrowth, and again after a second full round of damage and regrowth
on the same lineage, confirm by colony PCR (and sequencing of a subset) that
both circuit arms are still at their intended loci (*amyE*, *lacA*) and
intact. A circuit that is duplicated, lost or rearranged during regrowth
loses the bit for a reason no simulation here models, and it would look like
a memory failure in the cytometry read. Run this before interpreting any
arm 2a / 2b failure as a failure of the mechanism.

**Fitness, loss and survivor-bias controls.** Use the growth-rate and
competition results from Experiment 1 to interpret any shortfall. A
damage-and-regrowth run is only about 7 divisions, so at plausible fitness
costs and loss rates selection during regrowth does not dominate the result
(see `simulations/bsubtilis_30_fitness_cost_selection.py`, section D). That is
NOT the same as saying selection cannot matter: the survivors of damage may not
be a random sample, and survivors already enriched for cells that were
downregulating the circuit would make recovery look better than it is. Section
F of that file sweeps the effect, and shows that how many generations the
culture ran between write and insult matters a great deal. So:
- run damage on freshly written cultures with as few generations as possible
  between write and insult;
- measure the four-bin composition (A high B low, A low B high, both low, both
  high or intermediate; thresholds and exclusions as in Experiment 1) of the
  culture immediately before damage;
- plate survivors and measure the same composition among them by colony
  fluorescence. The lost share among survivors divided by the lost share before
  damage is a direct estimate of the bias;
- report holding, flipped, lost and ambiguous fractions for each arm, and the
  product and mechanism numbers as defined in Experiment 1.

**Read:** flow cytometry at the end of regrowth plus settling, same 70%
correct / 3:1 separation thresholds as Experiment 1.

**Also record:** actual doubling time under the recovery condition, and
actual wall-clock time from insult to a readable colony. The simulations
assume a 30-minute doubling time and a fixed 6-hour post-insult settling
window, and audit Part 21 found that budget has zero slack at worst-case
damage — this measurement says whether that budget is real.

## Pass criteria

At least 70% of cells still hold the correct bit after regrowth in arm 2a,
even starting from as few as 2% surviving cells. Report arm 2b separately
rather than folding it into the same number.

## What fail means

If arm 2a already fails, self-healing memory doesn't work the way the whole
project has assumed, stop and rethink before Experiments 4-7. If only arm 2b
fails, that's still useful: it means the idea works in principle but
real-world damage is harsher than any simulation modeled.

## Cost and time

Standard microbiology, no new equipment needed beyond what Experiments 1 and
2 already require. Not separately quoted.
