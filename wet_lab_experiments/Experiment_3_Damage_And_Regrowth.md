# Experiment 3: Damage and Regrowth

**Full protocol:** `experiments/BENCH_PROTOCOL_BSUBTILIS.md`, Stage B2.

## The goal, plainly

This is the headline experiment, the one everything else has been leading
up to. Write a bit into the colony, hurt it on purpose, let it regrow, then
check whether the surviving colony still remembers what was written.

Run two versions side by side:
- **Gentle version:** just thin the colony out (fewer cells, nothing else
  wrong with them) and let it regrow. This matches exactly what every
  simulation so far has modeled.
- **Real version:** actually stress the survivors (heat or a mild chemical
  insult), not just remove cells. No simulation in this project accounts for
  real stress on survivors, so this is genuinely new information either way.

## What "pass" looks like

At least 70 percent of cells still hold the correct bit after regrowth, even
starting from as few as 2 percent of the original cells surviving. The
simulations predict close to 100 percent.

## What "fail" looks like

If the gentle version already fails, self-healing memory doesn't work the
way the whole project has assumed. If only the "real stress" version fails,
that's still useful, it means the idea works in principle but real-world
damage is harsher than any simulation modeled.

## Cost and time

Standard microbiology, no new equipment needed beyond what Experiments 1 and
2 already require. Not separately quoted.
