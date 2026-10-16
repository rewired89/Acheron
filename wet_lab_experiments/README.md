# Wet-Lab Experiments

Each file in this folder is a standalone, actionable protocol: strain,
construct, procedure, replicates, and fixed pass/fail criteria, enough to
hand to a lab and run. They are drawn from `experiments/BENCH_PROTOCOL_BSUBTILIS.md`,
which remains the fuller reference (citations, design rationale, strain
mismatch discussion, cost table) if a detail here needs more context.

**None of these have been run.** Every "predicted result" in an experiment
file is a simulation result from `docs/SCIENTIFIC_AUDIT_2026.md`, not a lab
measurement. That is the entire point of running them.

**Order matters.** Run in numeric order. Each one is a go/no-go gate, a
negative result stops spending rather than pushing forward into the next
experiment.

| # | Experiment | One-line goal |
|---|---|---|
| 1 | Toggle Confirmation (pilot P0, 1a gate, 1b long-run and controls) | Does the switch actually switch, cleanly, in real cells, and does it hold? |
| 2 | Persistence and Noise | Does it hold over time, and what's the real static level? |
| 3 | Damage and Regrowth | Does the stored bit survive the colony being hurt and growing back? |
| 4 | Repressor Copy Number | How many molecules per cell are actually doing the job? |
| 5 | Voltage Interface | Can the switch actually control a real electrical channel? |
| 6 | Oscillation and Readout | Does the bacteria's own background rhythm scramble the reading? |
| 7 | Reinforcement Circuit | Can a "heal harder" backup circuit fix the weakest link found so far? |

**Cost note:** only Experiment 1 has a planning estimate attached, $2,000 to
$5,000 and 6 to 10 weeks (`docs/pitch/Acheron_Validation_Proposal.docx`). That
figure predates the staged design (pilot P0, 1a gate, 1b long-run and controls), should be
read as a floor for both stages together, and has not been quoted by a lab. Experiments 2 through 7 have no
price attached anywhere in this project, don't invent one if asked, get a
quote from the collaborating lab instead.

**If a Stage's detail changes in `BENCH_PROTOCOL_BSUBTILIS.md`, update the
matching experiment file here too** — these are no longer thin pointers, so
they can drift out of sync with the source document if only one side is
edited.
