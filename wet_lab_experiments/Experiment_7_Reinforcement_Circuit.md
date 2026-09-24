# Experiment 7: Reinforcement Circuit

**Tests:** `docs/SCIENTIFIC_AUDIT_2026.md` Part 23 (`simulations/bsubtilis_16_damage_sensing_reinforcement.py`).
**Bench protocol this is drawn from:** `experiments/BENCH_PROTOCOL_BSUBTILIS.md`, Stage B6.
**Prerequisite: only run if Experiment 4 finds the real repressor copy number
low enough (around 1 molecule/cell) for partition noise to matter.**

## The goal, plainly

If Experiment 4 finds there really are very few switch-protein molecules per
cell, that's a real weak point during regrowth. This experiment tests a
proposed fix: an extra circuit that gives the stored bit a temporary boost
while the colony is healing, then backs off once healing is done.

## Build

- A stress-responsive promoter driving a transient boost of whichever toggle
  arm currently dominates. The simulation models this on the bacterial SOS
  response (RecA/LexA) but does **not** name a specific *B. subtilis*
  promoter — selecting that promoter is a design task this plan does not
  resolve, and must be done with the collaborating lab before building.
- Wire the boost to the cell's own stress response triggered by the same
  insults Experiment 3's arm 2b applies (heat or H2O2), not to an artificial
  signal, since that is what a real stress-responsive promoter actually
  senses. It should decay once the colony returns to steady growth.

## Test sequence

1. Repeat Experiment 3's arm 2a and 2b regrowth protocol with the
   reinforcement circuit added, at the lowest survival fraction (2%) where
   partition noise is expected to bite hardest.
2. Compare bit-survival fraction against Experiment 3's original results
   (same strain, same conditions, reinforcement circuit absent) to measure
   whether the boost actually helps.
3. **After reinforcement has fired and healing is complete**, apply a
   normal write pulse (same as Experiment 1's write procedure) and check
   whether the bit can still be flipped, or whether the circuit has been
   reinforced into being unwritable. This is a straightforward bench test
   and the simulation cannot answer it on its own.

## What "pass" looks like

The boost measurably improves bit-survival fraction through regrowth
compared to Experiment 3's baseline, **and** the switch can still be
rewritten normally afterward. Either half failing alone is a fail: a boost
that locks the switch permanently is not usable.

## Cost and time

Only relevant if Experiment 4 says it's needed. Not separately quoted.
