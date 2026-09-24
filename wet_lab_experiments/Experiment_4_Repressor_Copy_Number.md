# Experiment 4: Repressor Copy Number

**Tests:** `docs/SCIENTIFIC_AUDIT_2026.md` Part 22's one unmeasured conversion (`simulations/bsubtilis_15_partition_noise_regrowth.py`).
**Bench protocol this is drawn from:** `experiments/BENCH_PROTOCOL_BSUBTILIS.md`, Stage B3.
**Prerequisite:** none beyond Experiment 1's strain (optional, can run any
time after Experiment 1).

## The goal, plainly

Count how many actual molecules of each switch-gene's repressor protein
exist inside one cell. `bsubtilis_15_partition_noise_regrowth.py` had to
convert dimensionless repressor units into real molecule counts with no
citation for the conversion, so it swept a range instead. The sweep found
recovery after regrowth is robust down to about 5 molecules per cell and
only degrades at about 1. This experiment measures which end of that sweep
actually applies.

## Procedure

Use one of the following, in rising order of cost and precision:

1. **Quantitative single-cell counting via a calibrated fluorescent fusion**
   (cheapest) — fuse the repressor to a well-characterized fluorescent tag,
   calibrate copy number against a known-count standard, count per cell by
   microscopy or cytometry.
2. **Targeted mass spectrometry** (mid-cost) — quantify repressor peptide
   abundance directly via selected/multiple-reaction monitoring against a
   labeled standard.
3. **Quantitative western blot** (highest precision, more overhead) —
   compare band intensity against a purified-protein standard curve.

Run on the M1 (matched) strain from Experiment 1, both written states,
during steady-state (not immediately after a write pulse).

## What "pass" looks like

Not a pass/fail line, a measurement. Report the real molecule count per
cell for each repressor.

## What it unlocks

If the real count comes back comfortably above 5 per cell, Experiment 7
(the reinforcement circuit) can be dropped from the plan entirely, saving
time and money later. If it comes back near 1, Experiment 7 becomes
necessary.

## Cost and time

Optional. Cheap enough to justify on its own because a good result deletes
a later, more expensive experiment. Not separately quoted.
