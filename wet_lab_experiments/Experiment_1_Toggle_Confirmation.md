# Experiment 1: Toggle Confirmation

**Tests:** `docs/SCIENTIFIC_AUDIT_2026.md` Part 9 (`simulations/bsubtilis_01_gardner_toggle_circuit.py`) and Part 16 (`simulations/bsubtilis_10_reporter_readout.py`).
**Bench protocol this is drawn from:** `experiments/BENCH_PROTOCOL_BSUBTILIS.md`, Stage B0.

## The goal, plainly

Build the actual two-gene switch in real *B. subtilis* cells and check whether
it behaves like a genuine on/off switch, cleanly one state or the other, not a
dimmer that sits somewhere in between. This is the first real test of the
whole project's core idea.

## Strain and construct

- **Strain:** *B. subtilis* W168 (order from BGSC, bgsc.org, along with the
  BBB 2.0 plasmid set).
- **Topology:** two mutually-repressing arms.
  - Arm A: promoter P_A drives repressor_B + reporter_A.
  - Arm B: promoter P_B drives repressor_A + reporter_B.
- **Promoters (BBB characterized set):** J23101 (weakest), P*liaG*
  (reference), P*lepA* (intermediate), P*veg* (strongest, ~1000x P*liaG*).
- **Repressor pair:** LacI / TetR (proposal, not yet confirmed with the
  collaborating lab — confirm *B. subtilis*-validated repressible promoter
  versions before ordering).
- **Reporters:** sfGFP_Spn (arm A) and mCherry_Bsu (arm B).
- **Integration:** arm A at *amyE* (pBS1C/pBS1E), arm B at *lacA* (pBS2E),
  chromosomal (not plasmid), so copy number can't drift during Experiment 3's
  regrowth.

## Build three promoter-matching variants

| Variant | Promoters | Predicted outcome |
|---|---|---|
| M1, matched | same promoter both arms | Bistable, 100% fidelity at 24h |
| M2, moderate mismatch | P*liaG* / P*lepA* | Bistable, 100% fidelity at 24h |
| M3, severe mismatch | P*liaG* / P*veg* (or inverse) | Monostable, fidelity floors near 50% |

M3 is the falsification arm: if M3 turns out bistable, the simulation's
central design constraint is wrong, a real, publishable correction. If M1 is
not bistable, the whole *B. subtilis* circuit track is in trouble.

## Procedure

1. **Culture:** LB or a defined minimal medium, 37°C, shaking.
2. **Write:** transient inducer pulse, IPTG pulse sets one state, aTc pulse
   sets the other. Pulse, then wash by centrifugation and resuspension into
   inducer-free medium. Record pulse duration and concentration.
3. **Read:** flow cytometry at single-cell resolution. **Not optional** — a
   plate reader reports a population mean and cannot distinguish a bistable
   population (two separated peaks) from a monostable graded one (one broad
   peak). Population-average lux/lacZ is acceptable only as a cheap
   pre-screen before cytometry.
4. **Hysteresis arm (primary bistability test, M1 and M2).** This is the
   decisive test, because a slow monostable circuit can fake a bimodal
   snapshot but cannot fake a history-dependent response (Gardner, Cantor &
   Collins 2000). Method:
   - Run a pilot dose-response first to find the inducer range that spans
     the switching region, then choose log-spaced inducer levels across it,
     with levels on both sides.
   - Pre-grow one population in the ON state and one in the OFF state
     (strong write, then washout), then expose each to every inducer level.
   - Hold each level for enough generations that reporter maturation and
     dilution have equilibrated (the maturation half-life comes from
     Experiment 2; use the same generation count at every level). Confirm by
     reading each level at two successive times and requiring no change. A
     read taken too soon measures a transient, not hysteresis.
   - Read the fraction ON by flow cytometry at every level for both
     histories.
5. **Culture method for the long timepoints (serial dilution, stated up
   front).** B. subtilis in batch culture reaches stationary phase and can
   sporulate, so a 72 hour run needs a defined regime. Use manual serial
   dilution into fresh inducer-free medium at fixed intervals chosen to keep
   cells in exponential growth, recording the OD before and after each
   dilution and the number of generations elapsed. A microfluidic chemostat
   is cleaner but is not needed for a first pass. Manual dilution adds
   handling variability and can select for faster-growing variants, which is
   why the competition assay below is part of this experiment, not optional.
   Check a sample by phase-contrast microscopy at the end for spores.
6. **Timepoints:** 0, 2, 4, 6, 12, 24, 48, 72 hours after washout under the
   dilution regime above (growth and dilution are what a slow-relaxing
   monostable circuit cannot survive, so the dilution is part of the test).
7. **Washout-and-reread arm:** after the 24 hour read, wash a portion of
   each culture again into fresh inducer-free medium and re-read it at 48
   and 72 hours. A true toggle gives the same distribution. A slow
   monostable circuit keeps narrowing toward its single attractor.
8. **Fitness controls (needed to interpret the long timepoints).** Cells that
   lose or silence the circuit can outgrow cells that carry it, and in a
   histogram that looks exactly like state loss (see
   `simulations/bsubtilis_30_fitness_cost_selection.py`).
   - **Growth-rate comparison:** growth curves of each strain against
     parental W168 in the same medium, ON-state and OFF-state cultures
     separately. Record the doubling times.
   - **Competition assay:** mix the circuit strain with an otherwise
     isogenic reference strain carrying a distinguishable marker (a third
     fluorescent protein, or a distinct selectable marker) at a known ratio,
     carry the mixture through the same 72 hour dilution regime, and track
     the ratio over time by cytometry or selective plating. The change in
     ratio per generation estimates the fitness cost, which is the number the
     fitness simulation needs.
   - **Loss-of-circuit gate:** in every cytometry analysis, count cells
     negative for BOTH reporters separately from cells that have flipped to
     the opposite state. Report three fractions: holding the written state,
     flipped, and lost.
9. **Replicates:** 3 independent biological replicates, both write
   directions, all 3 variants. Minimum 10,000 events per cytometry sample.
10. **Optional, single-cell tracking:** image microcolonies on an agarose
    pad over time and confirm individual lineages hold their written state,
    not just that the population looks bimodal at a snapshot.

## Pass criteria (fixed in advance)

In order of importance:

- **Hysteresis (M1 and M2):** the ON-history and OFF-history response curves
  do not overlap across a range of inducer levels, by more than the
  replicate-to-replicate spread. A single overlapping curve means the circuit
  is graded or monostable, whatever the cytometry histograms looked like.
- M1 and M2 show a clearly bimodal GFP/mCherry distribution after washout,
  sitting in the state written.
- At least 70% of cells hold the written state at 24 hours, with at least
  3:1 separation between the two state populations, **and the bimodal
  distribution is stable across at least three consecutive timepoints
  spanning at least 48 hours** (for example 24, 48 and 72). A single
  snapshot at 24 hours is not enough, because a slow monostable circuit
  that relaxes over ~48 hours would also pass it.
- The 70% figure is met on the reporter-positive cells AND on all cells. If
  it is met only after excluding cells that have lost both reporters, the
  result is reported as **uninterpretable at that timepoint** (selection or
  circuit loss), not as a pass. The competition assay then says whether
  fitness cost explains it.
- The washout-and-reread arm reproduces the same distribution at 48 and 72
  hours.
- Both write directions work, on the same culture.
- M3 fails to show bimodality, or collapses to one state regardless of what
  was written, by the 72 hour timepoint at the latest, and shows a single
  hysteresis curve. A slow collapse that has not finished by 24 hours still
  counts as monostable.

## What fail means

M1 failing means the BBB parts plus the Gardner topology do not produce a
toggle in this chassis. Stop and rethink the chassis or repressor pair
before spending anything further, including on Experiments 2 through 7.

## Cost and time

$2,000 to $5,000, 6 to 10 weeks (planning estimate, not yet quoted by a lab).
That estimate predates the hysteresis arm, the 72 hour dilution regime and the
fitness controls, which add strains, cytometry runs and labor. Treat it as a
floor until a lab re-quotes the expanded design.
