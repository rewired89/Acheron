# Experiments

**This folder holds bench protocols only: what you would physically do in a lab.**

It used to hold Python scripts. Those were simulations, not experiments, and they
now live in `simulations/`, with supporting demos and harnesses in `tools/`.
Nothing in this folder runs on a computer.

Nothing here has been run, and nothing here has been reviewed by a collaborating
lab yet. Treat both documents as drafts.

| File | Organism | What it would establish |
|---|---|---|
| `BENCH_PROTOCOL_BSUBTILIS.md` | *B. subtilis* | The primary track. Seven stages, cheapest first, from confirming the toggle switch is genuinely bistable through to the voltage interface and the readout-timing problem. Also lists the simulated results that no bench work can test. |
| `BENCH_PROTOCOL_HEK293.md` | HEK293 cells | The older mammalian-cell persistence experiment, matching Stage 1 of the staged funding plan. |

**Order of operations.** The *B. subtilis* protocol's Stage B0 is the cheapest
experiment in the project and the one that kills or confirms the whole circuit
track, so it goes first. `docs/pitch/Acheron_Validation_Proposal.docx` prices it
and sets the funding stages. `docs/REASONING_MAP.md` explains why the ordering
is what it is.

**Before running anything here,** read the strain section of the *B. subtilis*
protocol. The circuit parts and the electrical-signalling literature this project
depends on were characterised in two different bacterial strains that cannot both
be used at once, and that is a cost the simulations do not show.
