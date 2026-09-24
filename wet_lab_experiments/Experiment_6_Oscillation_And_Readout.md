# Experiment 6: Oscillation and Readout

**Tests:** `docs/SCIENTIFIC_AUDIT_2026.md` Parts 12, 13, 17, 18, 21.
**Bench protocol this is drawn from:** `experiments/BENCH_PROTOCOL_BSUBTILIS.md`, Stage B5.
**Prerequisite: only run if Experiment 5 produces a measurable voltage bit.**

## The goal, plainly

*B. subtilis* colonies naturally run their own background electrical rhythm,
for their own reasons unrelated to this project. The simulations found that
rhythm can make a perfectly intact stored bit look scrambled if you take a
quick reading at the wrong moment.

## Procedure

1. **First, measure the thing the simulations had to guess.** Every
   interference simulation sweeps oscillation amplitude from 10 to 70 mV
   because no source paper reports a millivolt figure. Measure the native
   oscillation's actual amplitude and period, in ThT units, in a strain
   carrying no engineered circuit at all (circuit-free control). This one
   measurement decides whether the rest of this stage matters: Parts 17-18
   found the answer flips between the low end (10-30 mV, where timing and
   partial decoupling help) and the high end (70 mV, where only long
   averaging works).
2. **Then compare three readout strategies on the same biofilm:**
   - A single fast read.
   - A read timed to the oscillation's predicted quiet phase.
   - A read averaged over about 180 minutes.
3. **Then test decoupling:** build the same voltage-bit construct in a
   Δ*yugO* background, or route the engineered output through a different
   channel, and repeat the three-way readout comparison. Budget for the
   biofilm-formation cost of losing yugO (Lundberg et al. 2013).

**Bootstrapping problem to solve before running this:** the timed-read arm
needs to know the oscillation's phase, but you can't get phase from the
readout you're still validating. Use ThT imaging of the biofilm's own wave,
in the circuit-free control strain, as the independent phase reference.

## What "pass" looks like

Confirms which reading method actually works despite the rhythm. Predicted:
the fast snapshot collapses toward 50% above ~10 mV amplitude, timing it
doesn't fully rescue it, and the 180-minute average recovers to near 100%.

## Why it matters

If the slow average is really the only reliable method, that sets a hard
floor on how quickly this system can ever be read, which matters for any
real-world use case.

## Cost and time

Depends entirely on Experiment 5 succeeding first. Not separately quoted.
