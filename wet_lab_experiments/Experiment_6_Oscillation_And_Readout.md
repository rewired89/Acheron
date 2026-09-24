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
   measurement decides whether the rest of this stage matters, but the two
   easier fixes below do not share one "low-end" band: **timing (Part 17)
   only rescues a fast read at the lowest tested amplitude, 10 mV** (a
   perfectly-timed read hits 100% there; by 20 mV a perfectly-timed read is
   already back to a coin flip). **Partial decoupling (Part 18) works at a
   different point**, a moderate 30 mV, where cutting the native signal's
   coupling to just 10% of today's assumed strength makes even a fast,
   1-minute read work well (94%). Neither fix rescues a fast read at the
   documented worst case, 70 mV — there only the 180-minute average works,
   regardless of coupling level.
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

Confirms which reading method actually works despite the rhythm, and at
which amplitude each fix stops working. Predicted: a fast, untimed read is
fine at very low amplitude but degrades as amplitude rises; a perfectly
timed read only rescues it at the lowest amplitude tested (10 mV) and is
back to a coin flip by 20 mV; a Δ*yugO*/decoupled read rescues a fast read
at a moderate amplitude (30 mV) that timing alone cannot; and at the
documented worst case (70 mV), only the 180-minute average recovers to near
100%, regardless of timing or decoupling.

## Why it matters

If the slow average is really the only reliable method, that sets a hard
floor on how quickly this system can ever be read, which matters for any
real-world use case.

## Cost and time

Depends entirely on Experiment 5 succeeding first. Not separately quoted.
