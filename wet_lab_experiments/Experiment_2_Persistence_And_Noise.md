# Experiment 2: Persistence and Noise

**Full protocol:** `experiments/BENCH_PROTOCOL_BSUBTILIS.md`, Stage B1.

## The goal, plainly

Runs on the same cells as Experiment 1, just watched for longer, 48 hours
instead of 24. While watching, measure the real amount of natural static
("noise") in these actual cells, instead of the guessed number every
simulation so far has been using.

This is the cheapest experiment in the whole plan, it reuses cultures
already growing for Experiment 1, and it answers the single biggest
"we don't actually know this" question in the project.

Small addition worth doing at the same time: a second color-based test that
separates two different kinds of static, one that's specific to each gene
individually, and one that comes from the whole cell wobbling at once. That
distinction came out of a research article the founder brought in, see
`docs/SCIENTIFIC_AUDIT_2026.md` Part 27.

## What "pass" looks like

There isn't a pass/fail line here the way other experiments have one, this
is a measurement, not a yes/no test. The output is a real number to plug
back into every simulation instead of a guess.

## What it unlocks

Once this is measured, the entire simulation suite can be rerun with real
numbers instead of assumptions, which is the single biggest category of
"we assumed this" caveat currently in the project.

## Cost and time

Not separately quoted, it's an extension of Experiment 1's cultures rather
than a new experiment, so its marginal cost is small. No number invented
beyond that.
