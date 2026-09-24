# Experiment 1: Toggle Confirmation

**Tests:** `docs/SCIENTIFIC_AUDIT_2026.md` Part 9 (`simulations/bsubtilis_01_gardner_toggle_circuit.py`) and Part 16 (`simulations/bsubtilis_10_reporter_readout.py`).
**Bench protocol this is drawn from:** `experiments/BENCH_PROTOCOL_BSUBTILIS.md`, Stage B0.

## The goal, plainly

Build the actual two-gene switch in real *B. subtilis* cells and check whether
it behaves like a genuine on/off switch, cleanly one state or the other, not a
dimmer that sits somewhere in between. This is the first real test of the
whole project's core idea.

## Strain and construct

- **Strain:** *B. subtilis* W168 (order from BGSC, bgsc.org, along with the
  BBB 2.0 plasmid set).
- **Topology:** two mutually-repressing arms.
  - Arm A: promoter P_A drives repressor_B + reporter_A.
  - Arm B: promoter P_B drives repressor_A + reporter_B.
- **Promoters (BBB characterized set):** J23101 (weakest), P*liaG*
  (reference), P*lepA* (intermediate), P*veg* (strongest, ~1000x P*liaG*).
- **Repressor pair:** LacI / TetR (proposal, not yet confirmed with the
  collaborating lab — confirm *B. subtilis*-validated repressible promoter
  versions before ordering).
- **Reporters:** sfGFP_Spn (arm A) and mCherry_Bsu (arm B).
- **Integration:** arm A at *amyE* (pBS1C/pBS1E), arm B at *lacA* (pBS2E),
  chromosomal (not plasmid), so copy number can't drift during Experiment 3's
  regrowth.

## Build three promoter-matching variants

| Variant | Promoters | Predicted outcome |
|---|---|---|
| M1, matched | same promoter both arms | Bistable, 100% fidelity at 24h |
| M2, moderate mismatch | P*liaG* / P*lepA* | Bistable, 100% fidelity at 24h |
| M3, severe mismatch | P*liaG* / P*veg* (or inverse) | Monostable, fidelity floors near 50% |

M3 is the falsification arm: if M3 turns out bistable, the simulation's
central design constraint is wrong, a real, publishable correction. If M1 is
not bistable, the whole *B. subtilis* circuit track is in trouble.

## Procedure

1. **Culture:** LB or a defined minimal medium, 37°C, shaking.
2. **Write:** transient inducer pulse, IPTG pulse sets one state, aTc pulse
   sets the other. Pulse, then wash by centrifugation and resuspension into
   inducer-free medium. Record pulse duration and concentration.
3. **Read:** flow cytometry at single-cell resolution. **Not optional** — a
   plate reader reports a population mean and cannot distinguish a bistable
   population (two separated peaks) from a monostable graded one (one broad
   peak). Population-average lux/lacZ is acceptable only as a cheap
   pre-screen before cytometry.
4. **Timepoints:** 0, 2, 4, 6, 12, 24 hours after washout.
5. **Replicates:** 3 independent biological replicates, both write
   directions, all 3 variants. Minimum 10,000 events per cytometry sample.

## Pass criteria (fixed in advance)

- M1 and M2 show a clearly bimodal GFP/mCherry distribution after washout,
  sitting in the state written.
- At least 70% of cells hold the written state at 24 hours, with at least
  3:1 separation between the two state populations.
- Both write directions work, on the same culture.
- M3 fails to show bimodality, or collapses to one state regardless of what
  was written.

## What fail means

M1 failing means the BBB parts plus the Gardner topology do not produce a
toggle in this chassis. Stop and rethink the chassis or repressor pair
before spending anything further, including on Experiments 2 through 7.

## Cost and time

$2,000 to $5,000, 6 to 10 weeks (planning estimate, not yet quoted by a lab).
