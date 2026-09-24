# Experiment 1: Toggle Confirmation

**Full protocol:** `experiments/BENCH_PROTOCOL_BSUBTILIS.md`, Stage B0.

## The goal, plainly

Build the actual two-gene switch in real *B. subtilis* cells and check
whether it behaves like a genuine on/off switch, cleanly one state or the
other, not a dimmer that sits somewhere in between. This is the first real
test of the whole project's core idea.

Also tests something specific: the simulations predict that if the two
genes are badly mismatched in strength, the switch breaks and gets stuck in
one state permanently. This experiment builds one matched version and one
badly-mismatched version on purpose, to see if that prediction is right.

## What "pass" looks like

At least 70 percent of cells still hold whatever state they were written to,
24 hours later, in the matched version. The mismatched version is expected
to fail on purpose, that's the prediction being tested, not a bug.

## What "fail" looks like

If the matched version doesn't hold a clean state either, the core circuit
design doesn't work in this organism as built, and that needs rethinking
before anything else in this folder is worth funding.

## Cost and time

$2,000 to $5,000, 6 to 10 weeks (planning estimate, not yet quoted by a lab).
