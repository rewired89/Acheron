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
4. **Response-time calibration (run first, it sets the hysteresis timing).**
   Hysteresis is only interpretable if each inducer level is held for much
   longer than the circuit takes to settle. Too short and a slow monostable
   circuit shows apparent hysteresis (a false positive); long enough and a
   monostable circuit relaxes to its single state and shows none (a correct
   negative), while a real toggle still shows two. The settling time cannot be
   assumed, and a washout alone cannot give it for a toggle, because a toggle
   never "forgets". So measure it with a step response: take M1 in the OFF
   history, step to a strong ON inducer level, and read the fraction ON by
   cytometry at short intervals until it plateaus; repeat in the other
   direction, and repeat with a step into the middle of the switching region,
   where settling is slowest. The slowest plateau time is the response time.
   Hold every hysteresis level for at least 3 times that, in culture that is
   kept growing by dilution, and still confirm with two successive reads.
5. **Hysteresis arm (primary bistability test, M1 and M2).** This is the
   decisive test, because a slow monostable circuit can fake a bimodal
   snapshot but cannot fake a history-dependent response (Gardner, Cantor &
   Collins 2000). Method:
   - Run a pilot dose-response first to find the inducer range that spans
     the switching region, then choose log-spaced inducer levels across it,
     with levels on both sides.
   - Pre-grow one population in the ON state and one in the OFF state
     (strong write, then washout), then expose each to every inducer level.
   - Hold each level for the equilibration time from step 4.
   - Read the fraction ON by **flow cytometry at single-cell resolution** at
     every level for both histories. A plate-reader mean gives a blurred loop
     that cannot be told apart from a slow transient.
6. **Culture method for the long timepoints (serial dilution, with sporulation
   managed, not just checked).** B. subtilis in batch culture reaches
   stationary phase and sporulates when nutrients run short. Spores do not
   divide, do not fluoresce, germinate on their own schedule (so manual
   passaging can carry them forward into later cultures with a different
   history from the vegetative cells) and are depleted from the population,
   so survivors stop being a representative sample.
   - **Regime:** manual serial dilution into fresh inducer-free medium at
     fixed intervals, chosen to keep cells exponential and well away from
     nutrient exhaustion, with OD before and after each dilution and the
     generations elapsed recorded. A microfluidic chemostat is cleaner but
     not needed for a first pass. Manual dilution adds handling variability
     and can select faster-growing variants, which is why the competition
     assay below is not optional.
   - **Measure spores at every passage:** split a sample, heat-shock one half
     (the standard step that kills vegetative cells and leaves spores, a
     typical protocol is 80 C for 10 minutes, confirm with the lab) and plate
     both. The CFU ratio is the spore fraction. Add phase-contrast
     microscopy at the start and end.
   - **Threshold, set in advance:** the maximum acceptable spore fraction is
     decided by the lab and the founders BEFORE the run and written here. It
     is left blank on purpose, because any number filled in without data
     would be invented. A sensible way to choose it is from the spore fraction
     measured for parental W168 in the same regime in a pilot.
   - **If it is exceeded:** treat that timepoint as compromised, not as a
     result, and change the design before repeating: a shorter run with
     justified timepoints, a medium that suppresses sporulation, tighter
     dilution intervals, or a continuous culture method.
7. **Timepoints:** 0, 2, 4, 6, 12, 24, 48, 72 hours after washout under the
   dilution regime above (growth and dilution are what a slow-relaxing
   monostable circuit cannot survive, so the dilution is part of the test).
8. **Washout-and-reread arm:** after the 24 hour read, wash a portion of
   each culture again into fresh inducer-free medium and re-read it at 48
   and 72 hours. A true toggle gives the same distribution. A slow
   monostable circuit keeps narrowing toward its single attractor.
9. **Fitness controls (needed to interpret the long timepoints).** Cells that
   lose or silence the circuit can outgrow cells that carry it, and in a
   histogram that looks exactly like state loss (see
   `simulations/bsubtilis_30_fitness_cost_selection.py`).
   - **Growth-rate comparison:** growth curves of each strain against
     parental W168 in the same medium, ON-state and OFF-state cultures
     separately. Record the doubling times.
   - **Competition assay, specified before it is run:**
     - *Reference strain:* a derivative of the same W168 stock the circuit
       strains were built from, carrying a constitutive fluorophore of a color
       distinct from both reporters at a neutral locus (not *amyE* or *lacA*)
       and a resistance marker different from the circuit strain's. The
       fluorophore and marker may themselves cost fitness, so:
     - *Neutrality control and label swap:* run reference-versus-reference
       with the two different labels (any drift in the ratio is the assay's
       noise floor), and run the circuit-versus-reference competition in both
       labelings.
     - *Isogenicity:* sequence both strains and confirm they differ only by
       the circuit, the label and its marker. A marker panel alone is not
       enough.
     - *No DNA exchange:* laboratory *B. subtilis* 168 lineages are naturally
       competent under competence-inducing conditions. Avoid those conditions,
       add DNase I to the cultures, and plate recovered clones on double
       selection to catch recombinants. A recombination event that moves the
       circuit or the label invalidates the result.
     - *Same regime as Experiment 1:* same medium, dilution schedule and
       temperature. A fitness cost measured in a chemostat is a different
       number and is not what the 72 hour run experiences.
     - Start at a known ratio and track it over the full 72 hours by cytometry
       or selective plating. The change in ratio per generation estimates the
       fitness cost, which is the input `bsubtilis_30` needs.
   - **Four-bin cytometry gate at every timepoint.** Classify every cell into:
     (A high, B low), (A low, B high), (both low), and (both high or
     intermediate). Set the thresholds in advance from parental W168
     (the low gate), fully induced single-state controls (the high gate) and
     single-color controls for spectral compensation. Exclude dead cells,
     debris and spores with a viability or nucleic-acid stain plus scatter,
     and report their share separately, otherwise they inflate the both-low
     bin and are misread as lost circuit. Report all four bins every time.
     The both-high bin is the most informative number in the experiment: a
     functional toggle should have almost none at steady state (brief
     both-high cells during switching are expected), and a persistent
     both-high population means mutual repression is failing and the circuit
     is a co-expresser, not a switch. A persistent intermediate population is
     the signature of a graded or slow circuit.
10. **Replicates:** 3 independent biological replicates, both write
    directions, all 3 variants. Minimum 10,000 events per cytometry sample.
11. **Optional, single-cell tracking:** image microcolonies on an agarose
    pad over time and confirm individual lineages hold their written state,
    not just that the population looks bimodal at a snapshot.

## Pass criteria (fixed in advance)

In order of importance:

- **Hysteresis (M1 and M2):** the ON-history and OFF-history response curves
  do not overlap across a range of inducer levels, by more than the
  replicate-to-replicate spread. A single overlapping curve means the circuit
  is graded or monostable, whatever the cytometry histograms looked like.
- M1 and M2 show a clearly bimodal GFP/mCherry distribution after washout,
  sitting in the state written.
- At least 70% of cells hold the written state at 24 hours, with at least
  3:1 separation between the two state populations, **and the bimodal
  distribution is stable across at least three consecutive timepoints
  spanning at least 48 hours** (for example 24, 48 and 72). A single
  snapshot at 24 hours is not enough, because a slow monostable circuit
  that relaxes over ~48 hours would also pass it.
- **Report two numbers at every timepoint, and read them together.**
  The *product number* is the fraction of ALL live cells in the written state
  and gates pass or fail (70%). The *mechanism number* is the fraction of
  circuit-positive cells in the written state and says whether the toggle
  itself works. The same fail can mean opposite things:
  - all cells below 70%, circuit-positive cells at or above 70%, large both-low
    bin: the toggle works but expression is lost or silenced. This is a
    fitness and stability problem. M1 still fails the product bar. The
    competition assay and sequencing of dark isolates decide the cause.
  - circuit-positive cells below 70%, small both-low bin: the toggle itself is
    broken. The both-high and intermediate bins and the flipped bin say how
    (co-expresser, graded or slow, or spontaneous switching).
  - a result met only after excluding both-low cells is reported as
    **uninterpretable at that timepoint**, not as a pass.
- The washout-and-reread arm reproduces the same distribution at 48 and 72
  hours.
- Both write directions work, on the same culture.
- M3 fails to show bimodality, or collapses to one state regardless of what
  was written, by the 72 hour timepoint at the latest, and shows a single
  hysteresis curve. A slow collapse that has not finished by 24 hours still
  counts as monostable.

## What fail means

M1 failing on the circuit-positive (mechanism) number means the BBB parts plus
the Gardner topology do not produce a toggle in this chassis. Stop and rethink
the chassis or repressor pair before spending anything further, including on
Experiments 2 through 7. M1 failing only on the all-cells (product) number,
with the circuit-positive number passing, means the toggle works and the
problem is expression loss or silencing: fix stability, not the topology.

## Cost and time

$2,000 to $5,000, 6 to 10 weeks (planning estimate, not yet quoted by a lab).
That estimate predates the hysteresis arm, the 72 hour dilution regime and the
fitness controls, the response-time calibration, the sporulation monitoring
and the strain sequencing, which add strains, cytometry runs, sequencing and
labor. Treat it as a
floor until a lab re-quotes the expanded design.
