# Experiment 6: Oscillation and Readout

**Full protocol:** `experiments/BENCH_PROTOCOL_BSUBTILIS.md`, Stage B5.
**Only run this if Experiment 5 succeeds.**

## The goal, plainly

*B. subtilis* colonies naturally run their own background electrical rhythm,
for their own reasons, nothing to do with this project. The simulations
found that rhythm can make a perfectly intact stored bit look scrambled if
you take a quick reading at the wrong moment.

This experiment measures that real rhythm for the first time (every
simulation so far had to guess its strength), then compares three ways of
reading the bit: a fast snapshot, a snapshot timed to a quiet moment in the
rhythm, and a slow reading averaged over about 3 hours.

## What "pass" looks like

Confirms which reading method actually works despite the rhythm. The
simulations predict the fast snapshot fails, timing it carefully doesn't
fully fix it, and the slow 3-hour average works reliably.

## Why it matters

If the slow average is really the only reliable method, that sets a hard
floor on how quickly this system can ever be read, which matters for any
real-world use case.

## Cost and time

Depends entirely on Experiment 5 succeeding first. Not separately quoted.
