# Experiment 2: Persistence and Noise

**Tests:** the unmeasured noise parameters used throughout `simulations/bsubtilis_*`.
**Bench protocol this is drawn from:** `experiments/BENCH_PROTOCOL_BSUBTILIS.md`, Stage B1.
**Prerequisite:** run on the same cultures as Experiment 1, extended. Do not
run standalone.

## The goal, plainly

Watch Experiment 1's cultures for longer, 48 hours instead of 24, and while
watching, measure the real amount of natural static ("noise") in these actual
cells, instead of the guessed numbers every simulation so far has used.

## Procedure

1. **Extend timepoints to 48 hours**, with periodic dilution into fresh
   inducer-free medium to keep cells growing.
2. **Measure and record, at each timepoint:**
   - Fraction of cells in the correct state (real-world version of the
     simulations' `genetic_correct`).
   - Cell-to-cell variability in reporter level within each state population
     (real-world anchor for `transcriptional_noise_std`, currently a
     placeholder set to 3.0 in `bsubtilis_01_gardner_toggle_circuit.py` with
     no citation).
   - Spontaneous switching rate per generation (no simulation in the
     repository models this at all).
   - Reporter maturation half-life (`bsubtilis_10_reporter_readout.py`
     sweeps 5-60 minutes as an explicit placeholder).
3. **Run one addition in the same imaging session** (Elowitz, Levine, Siggia
   & Swain 2002, *Science* 297:1183-6, DOI 10.1126/science.1070919): a
   second construct with two differently-colored reporters under the SAME
   promoter in the SAME cell. Uncorrelated variation between the two colors
   is intrinsic noise (randomness in that gene's own expression); correlated
   variation (both colors moving together) is extrinsic noise (a shared,
   whole-cell fluctuation). This decides whether the shared-noise effect
   `simulations/bsubtilis_23_intrinsic_extrinsic_noise.py` found in a
   mismatched-promoter toggle (audit Part 27) applies to the real BBB
   promoters.

## What "pass" looks like

This is a measurement, not a yes/no test. The output is four real numbers
(state-holding fraction over time, reporter noise std, spontaneous switch
rate, maturation half-life) plus an intrinsic/extrinsic noise split, to
plug back into every simulation instead of a guess.

## What it unlocks

Once measured, the entire simulation suite can be rerun with real numbers
instead of assumptions, the single biggest category of "we assumed this"
caveat currently in the project.

## Cost and time

Not separately quoted, it's an extension of Experiment 1's cultures rather
than a new experiment, so its marginal cost is small.
