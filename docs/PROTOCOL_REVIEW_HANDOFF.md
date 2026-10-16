# Protocol Review Handoff: Acheron Experiment 1

**For:** a microbiologist or synthetic biologist who has run a genetic toggle
experiment in *Bacillus subtilis* and used flow cytometry on bacteria.
**Ask:** read the protocol below as a practitioner and tell us what is wrong with
the craft. We are not asking for a scientific endorsement of the project.

## The project in three lines

Acheron asks whether a bit written into a living cell as a genetic state is still
there after the cells are damaged and regrow. Everything so far is simulation; no
bench result exists. The first experiment checks that the engineered switch
behaves like a real two-state switch at all.

## What this packet contains, and where each piece lives

All of the following are inside `wet_lab_experiments/Experiment_1_Toggle_Confirmation.md`
(and, with the same wording, in Stage B0 of `experiments/BENCH_PROTOCOL_BSUBTILIS.md`).
A review of the protocol without these would not be a review of the same
experiment, so please read them as one document:

| Piece | Section of Experiment 1 |
|---|---|
| Gating hierarchy, with compensation as a correction and not a gate | Shared methods, item 4 |
| Four-bin classification and the two reported numbers | Shared methods, items 5 and 6 |
| Pre-registered table mapping each bin pattern to a conclusion | Shared methods, item 7 |
| Pilot design and its go/no-go gate | Pilot P0 and Gate P0 |
| Pass and fail criteria for each stage | Pass criteria for 1a and 1b, and the "What a fail means" sections |
| Sporulation rule and competition checklist | Stage 1b |
| Values only a lab can set | The table in this note, below |

## What to read, in this order

1. `wet_lab_experiments/Experiment_1_Toggle_Confirmation.md`, the standalone
   protocol (about ten minutes).
2. `experiments/BENCH_PROTOCOL_BSUBTILIS.md`, Stage B0 (same text, with the
   citations and design rationale around it).
3. Only if useful: `docs/SCIENTIFIC_AUDIT_2026.md`, Parts 29 and 30, which record
   how the protocol came to look the way it does.

## What the protocol is

A pilot gate (P0), then Stage 1a, then Stage 1b. P0 builds only the matched
toggle (M1), measures its settling time, a never-pulsed control and the baseline
spore fraction, and decides whether hysteresis can be run in batch culture at all. Stage 1a runs hysteresis on the matched-promoter toggle (M1)
against a severely mismatched negative control (M3) and a 24 hour read of all
three variants including a moderately mismatched one (M2). Stage 1b, only if 1a
passes, adds the 72 hour run, a competition assay and sporulation monitoring.

## What we have decided in advance

- Pass and fail criteria, including a two-number reporting rule (all live cells,
  and circuit-positive cells) and a table that maps each pattern in a four-bin
  cytometry gate to a conclusion. The table is fixed before data.
- Hysteresis is the primary test of bistability; a snapshot of bimodality is not.
- A step-response calibration, on its own cultures, sets how long each inducer
  level is held (at least three times the slowest settling time).
- Sporulation is measured at every passage and has a pre-set threshold rule.

## Values only a lab can set (please fill in or tell us how to choose)

These are left open on purpose. Any number we wrote without data would be
invented.

| Open value | Where | What we need from you |
|---|---|---|
| Maximum acceptable spore fraction | Stage 1b sporulation rule | Is "upper end of the parental W168 spore fraction in a pilot" a sound basis? What would you use? |
| Neutral integration site and reference fluorophore | Competition assay | A site other than amyE and lacA that is neutral in 168 lineages, and a fluorophore that does not overlap sfGFP and mCherry |
| Cytometer trigger channel and threshold for bacteria | Gating step 1 | What works on your instrument for small cells |
| Spore exclusion method | Gating step 4 | We pair a scatter gate with a third-channel spore or viability stain (or a reporter in a third color, not GFP) and validate it by heat-shock plating. Is that the right design, and which stain or reporter would you use? |
| Build M1 only for P0, or all three strains at once | Staging | We default to M1 only so a failed pilot wastes nothing. If a batch build of all three is cheaper in your hands, say so and by how much |
| Inducer range, number of levels, read times in the calibration | P0 and 1a | How many, and how coarse a first pass |
| Dilution interval and medium for a 72 hour run | Stage 1b | What keeps 168 vegetative for three days |
| Repressor pair | Construct | We propose LacI and TetR and have not confirmed *B. subtilis*-validated versions |
| Heat-shock step for spore counting | Sporulation rule | We cite a typical 80 C for 10 minutes. Confirm |

## Specific questions

1. Is the gating order correct and complete for a two-color bacterial toggle? We
   treat compensation as a correction applied to the data before the fluorescence
   gates, not a gate.
2. Is a step response the right way to get the settling time of a bistable
   circuit? Is "three times the slowest plateau time" a reasonable hold?
3. Can hysteresis be run in batch culture with dilution, or will it need a
   chemostat or microfluidic device?
4. Is M3 useful as the negative control for the hysteresis assay, and is the
   chosen M1 and M3 pairing the right one?
5. Is the competition-assay checklist enough to trust a fitness estimate?
6. What is missing that a practitioner would never forget and we have forgotten?

## What this review is not

- Not a review of the voltage question (whether the final stored state should be a
  membrane voltage). That is a separate decision, recorded in
  `docs/VOLTAGE_DECISION_MEMO.md`, and does not change Experiment 1.
- Not a request to endorse any claim in the project's pitch material.

## Related simulation results a reviewer may want

The survivor-composition simulation is done, not pending: recovery after damage
just tracks what the surviving cells hold, so the project's headline number (a
small fraction of survivors recovering fully) is only as good as the assumption
that those survivors are correct. See `docs/SCIENTIFIC_AUDIT_2026.md` Part 30 and
`simulations/bsubtilis_30_fitness_cost_selection.py`, section G.

## Honest status

- Every result behind this design is a simulation. No lab has reviewed the
  protocol before you. No lab has quoted its cost.
- The earlier planning figure of $2,000 to $5,000 predates this design and is a
  floor, not an estimate.
- The protocol has grown across several rounds of outside review. We suspect it is
  now bigger than the first experiment needs to be. If you think it is, say what
  you would cut.
