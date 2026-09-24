# Wet-Lab Experiments, Plain-English Index

This folder answers one question per file: **what do we need to physically do
in a lab, and why.** Each experiment here is a plain-English front door to a
Stage already fully specified in `experiments/BENCH_PROTOCOL_BSUBTILIS.md`,
strain, parts, instrument, replicate count, and the exact pass/fail numbers
live there, not here. This folder does not duplicate those numbers, it points
to them, so there is one source of truth, not two.

**None of these have been run.** Every "predicted result" listed in an
experiment file is a simulation result from `docs/SCIENTIFIC_AUDIT_2026.md`,
not a lab measurement. That is the entire point of running them.

**Order matters.** Run in numeric order. Each one is a go/no-go gate, a
negative result stops spending rather than pushing forward into the next
experiment.

| # | Experiment | One-line goal | Full protocol |
|---|---|---|---|
| 1 | Toggle Confirmation | Does the switch actually switch, cleanly, in real cells? | Stage B0 |
| 2 | Persistence and Noise | Does it hold over time, and what's the real static level? | Stage B1 |
| 3 | Damage and Regrowth | Does the stored bit survive the colony being hurt and growing back? | Stage B2 |
| 4 | Repressor Copy Number | How many molecules per cell are actually doing the job? | Stage B3 |
| 5 | Voltage Interface | Can the switch actually control a real electrical channel? | Stage B4 |
| 6 | Oscillation and Readout | Does the bacteria's own background rhythm scramble the reading? | Stage B5 |
| 7 | Reinforcement Circuit | Can a "heal harder" backup circuit fix the weakest link found so far? | Stage B6 |

**Cost note:** only Experiment 1 has a real planning estimate attached,
$2,000 to $5,000, 6 to 10 weeks (`docs/pitch/Acheron_Validation_Proposal.docx`),
and even that is not yet quoted by a lab. Experiments 2 through 7 have no
price attached anywhere in this project, don't invent one if asked, get a
quote from the collaborating lab instead.
