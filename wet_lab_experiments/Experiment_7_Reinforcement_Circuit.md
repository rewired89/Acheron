# Experiment 7: Reinforcement Circuit

**Full protocol:** `experiments/BENCH_PROTOCOL_BSUBTILIS.md`, Stage B6.
**Only run this if Experiment 4 finds the real molecule count low enough
for it to matter.**

## The goal, plainly

If Experiment 4 finds there really are very few switch-protein molecules per
cell, that's a real weak point during regrowth. This experiment tests a
proposed fix: an extra circuit, modeled on a real bacterial stress-response
system, that gives the stored bit a temporary boost while the colony is
healing, then backs off once healing is done.

It also answers a question the simulations raised but couldn't answer on
their own: once that boost circuit has fired, can the bit still be
deliberately rewritten afterward, or does the reinforcement lock it in place
permanently by accident?

## What "pass" looks like

The boost measurably improves how well the bit survives regrowth, and the
switch can still be rewritten normally afterward.

## Cost and time

Only relevant if Experiment 4 says it's needed. Not separately quoted.
