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
  collaborating lab, confirm *B. subtilis*-validated repressible promoter
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

**M3 is only a negative control if it lies outside the real bistable window, and
the window is a model result.** The model's window (strength ratio 0.247 to 16.25)
assumes Hill coefficient 2 on both arms and equal protein loss rates; at Hill 4, or
with the repressor of the weak arm lost four times faster, a ratio of 0.1 is
inside the window (`bsubtilis_35`). A ratio of 0.01 was outside it in every case
tested. So: (1) measure each arm's promoter strength with a single-promoter
reporter fusion before calling M3 severe, and treat the measured ratio, not the
nominal 0.1, as M3's value; (2) pick an M3 pair whose measured ratio is 0.01 or
lower if the parts allow; (3) if they do not, add a structural negative control
that does not depend on the window at all: one arm whose repressor-binding
operator is deleted, so it cannot be repressed and cannot be bistable at any Hill
coefficient or ratio. A "M3 bistable" result only counts against the simulation
if M3's measured ratio is at or below 0.01 or it is the operator-deleted control.

## How this experiment is staged

Three steps, each a go/no-go gate for the next, so money is only spent on the
expensive parts after the cheap questions have a yes.

- **Pilot P0, can this experiment be run at all?** Response-time calibration on
  its own cultures, the dose-response that locates the switching region, and the
  parental W168 spore baseline. If the circuit's settling time is longer than a
  vegetative culture can be sustained, the hysteresis test cannot run in batch
  culture and the design has to change before anything else is spent.
- **Stage 1a, does the switch switch?** Hysteresis (M1 against the M3 negative
  control) and a 24 hour read of all three variants. The go/no-go gate for 1b.
- **Stage 1b, does it hold, and can the result be trusted?** Runs only if 1a
  passes. Adds M2's hysteresis, the 72 hour run, the fitness and competition
  controls and the sporulation monitoring.

**Which strains are built when.** Build M1 first, for P0. Build M2 and M3 after P0
passes, because P0 can fail and constructs built before the gate would be wasted.
This default puts the gate ahead of batch savings. If the collaborating lab says a
batch build of all three is cheaper than building them separately, the lab's
answer overrides the default and should be recorded; the trade is paying for
constructs that a failed P0 would leave unused.

## Shared methods (apply to P0, 1a and 1b)

1. **Culture:** LB or a defined minimal medium, 37°C, shaking.
2. **Write:** transient inducer pulse, IPTG pulse sets one state, aTc pulse
   sets the other. Pulse, then wash by centrifugation and resuspension into
   inducer-free medium. Record pulse duration and concentration.
3. **Read:** flow cytometry at single-cell resolution. **Not optional.** A
   plate reader reports a population mean and cannot distinguish a bistable
   population (two separated peaks) from a monostable graded one (one broad
   peak). Population-average lux or lacZ is acceptable only as a cheap
   pre-screen before cytometry.
4. **Gating hierarchy (fixed before any data, identical for every sample).**
   Compensation is NOT a gate; it is a correction applied to the data (step 0).
   - **Step 0, compensation (applied to the data, not a selection):** build the
     compensation matrix from single-color controls (GFP only, mCherry only) and
     an unstained parental W168 sample, and apply it to the fluorescence channels
     of every event before any fluorescence gate.
   - **Gate 1, events:** the instrument trigger. Bacteria sit near the detection
     limit of many cytometers, so the trigger channel and threshold are set by the
     lab and checked with size beads and a parental W168 sample. They are written
     down and not changed.
   - **Gate 2, singlets:** forward-scatter area against height (and side-scatter
     area against height if the instrument reports it), to remove doublets.
   - **Gate 3, live cells:** a viability or nucleic-acid stain. A scatter-only
     live gate is not reliable, so a dye is required.
   - **Gate 4, spore and debris exclusion:** a scatter gate drawn using a purified
     spore preparation run as a control (heat-shocked and washed) and a
     medium-only sample for debris, **paired with a third fluorescence channel**
     that does not overlap sfGFP or mCherry: a spore- or viability-specific stain,
     or a spore reporter in a third color (the lab chooses). Scatter alone is
     weak, because spores and stationary-phase vegetative cells overlap in
     scatter and a gate that removes spores will also remove some vegetative
     cells. A spore reporter built on GFP would collide with the toggle's own
     sfGFP reporter, so it must be a different color. Heat-shock plating
     (Stage 1b) is destructive and off the cytometer, so it cannot be the gate; it
     is the **validation** of the gate. At each passage the spore fraction the
     cytometry gate reports must agree with the plated spore fraction. If it does
     not, the gate is wrong. Spores are reported as their own share and never
     counted as cells, otherwise they inflate the both-low bin.
   - **Gate 5, fluorescence bins,** applied to the compensated data. Thresholds
     come from controls: parental W168 sets the low gate (autofluorescence) and
     fully induced single-state controls set the high gate.
   Record the exact gates and do not change them between timepoints or strains.
5. **Four bins, reported at every timepoint:** [A+B-] (A high, B low),
   [A-B+] (A low, B high), [dark] (both low), and [both] (both high, or
   intermediate).
6. **Two numbers, reported together at every timepoint.** The *product number*
   is the fraction of ALL live cells in the written state and gates pass or
   fail (70%). The *mechanism number* is the fraction of circuit-positive cells
   (everything outside [dark]) in the written state and says whether the toggle
   itself works.
7. **Pre-registered interpretation table.** Fixed before data are seen. Changing
   it afterwards invalidates the pass.

| Pattern at steady state (after the equilibration time) | Conclusion |
|---|---|
| Write A gives mostly [A+B-], write B gives mostly [A-B+]; [dark] and [both] small; hysteresis loop open | **Working toggle** |
| Write A gives [A+B-] but write B also gives mostly [A+B-] (or the reverse) | **Asymmetric circuit**: one state is unstable. Name the failing direction. Suspect promoter matching |
| Both write directions end in the same single bin whatever was written | **Monostable** (the expected result for M3) |
| Persistent [both] population in both directions | **Mutual repression failed**: a co-expresser, not a switch. Brief [both] cells during switching are expected and do not count |
| Broad or intermediate single-reporter populations that move with inducer; one hysteresis curve | **Graded circuit** |
| Written state present but decaying over timepoints, with cells appearing in the opposite bin | **Spontaneous switching or slow relaxation**: check 48 and 72 hours against the washout-and-reread arm |
| Large [dark] population, remaining cells in the correct bins (mechanism number passes, product number fails) | **Expression lost or silenced**: a stability and fitness problem, not a topology problem. The competition assay and sequencing of dark isolates decide the cause |
| Large [dark] at time zero, before any long culture | **Construct or induction failure**, not state loss |
| Large [dark] together with a high spore or dead-cell share | **Culture problem**: handled in Stage 1b's sporulation rule, not a circuit result |
| The never-pulsed control is already bimodal, or already sits in one state | **Leak or default state**: the written-state results must be read against it, and it is the floor for any apparent bimodality |

A result met only after excluding [dark] cells is reported as **uninterpretable
at that timepoint**, not as a pass.

## Pilot P0: can this experiment be run at all? (M1 and parental W168 only)

1. **Dose-response pilot:** M1 across a wide log-spaced inducer range, one
   replicate, to locate the switching region. Hysteresis needs this anyway.
2. **No-pulse control:** a never-pulsed M1 culture grown alongside everything
   else and read at the same times. It shows how the circuit leaks and which
   state it defaults to when nothing has been written, which is the floor for
   any apparent bimodality. The false-positive rate for the [both] bin when there
   is no circuit at all comes from parental W168 and the single-color controls
   already required for the gates.
3. **Response-time calibration (its own cultures, run and finished first).**
   Hysteresis is only interpretable if each inducer level is held much longer than
   the circuit takes to settle. Too short and a slow monostable circuit shows
   apparent hysteresis (a false positive); long enough and a monostable circuit
   relaxes to its single state and shows none (a correct negative), while a real
   toggle still shows two. The settling time cannot be assumed, and a washout
   alone cannot give it for a toggle, because a toggle never "forgets". So measure
   it with a step response: take M1 in the OFF history, step to a strong ON
   inducer level, and read the fraction ON by cytometry at short intervals until
   it plateaus; repeat in the other direction, and repeat with a step into the
   middle of the switching region, where settling is slowest. The slowest plateau
   time is the response time.
   - **Independence:** the calibration uses its own cultures, set up and finished
     before any hysteresis culture is started. The equilibration time is fixed
     from it in advance and is not adjusted after the hysteresis curves are seen.
     The only allowed change is the pre-specified rule below.
   - **Rule:** every hysteresis level is held for at least 3 times the slowest
     plateau time, in culture kept growing by dilution, and confirmed by two
     successive reads. If the two reads at a level still differ, lengthen that
     level and repeat it.
   - **Sample count (a count, not a price, because no lab has quoted):**
     calibration cytometry samples = 3 step types x read times until plateau (set
     by a coarse first pass) x 3 replicates, on M1 only (M3 is not yet built; the
     comparison against M3 happens in the hysteresis test in 1a). Hysteresis samples in 1a = 2 histories x inducer levels x
     strains (M1 and M3) x 2 successive reads x 3 replicates. These two are of the
     same order, so the calibration is a large part of the cost, not a footnote.
4. **Parental W168 spore baseline:** grow parental W168 under the planned dilution
   regime for at least 3 times the slowest response time, and later for the full
   72 hours, measuring the spore fraction at every passage (method in Stage 1b).
   This fixes the sporulation threshold.

### Gate P0

- **Go:** the slowest response time is short enough that 3 times that duration
  can be sustained under the dilution regime with the parental spore fraction at
  or below the threshold it defined.
- **No-go:** it is not. The hysteresis test cannot be run in batch culture. Stop,
  and take the design to the lab: options are a continuous or microfluidic culture
  method, a medium that suppresses sporulation (which means redoing the baseline),
  or redesigning the test. Do not proceed to 1a on a guess.

## Stage 1a: does the switch switch? (M1, M2 and M3)

1. **Build and sequence-verify M2 and M3** (M1 was built for P0), with
   single-color and parental W168 controls for the gates. Run a never-pulsed
   control for every strain alongside, read at the same timepoints.
2. **Hysteresis (primary bistability test) on M1 and M3.** This is the decisive
   test, because a slow monostable circuit can fake a bimodal snapshot but cannot
   fake a history-dependent response (Gardner, Cantor & Collins 2000). M3 is not
   optional here: it is the negative control without which a loop on M1 alone
   cannot be shown to mean anything, because the assay has not been shown to give
   a single curve for a circuit known to be monostable.
   - Choose log-spaced inducer levels across the switching region from P0, with
     levels on both sides.
   - Pre-grow one population in the ON state and one in the OFF state (strong
     write, then washout), then expose each to every inducer level.
   - Hold each level for the equilibration time fixed by P0.
   - Read the fraction ON by **flow cytometry at single-cell resolution** at every
     level for both histories. A plate-reader mean gives a blurred loop that
     cannot be told apart from a slow transient.
3. **24 hour read on M1, M2 and M3:** write each strain in both directions, wash,
   keep growing by dilution, and read at 0, 2, 4, 6, 12 and 24 hours with the
   gating hierarchy and four bins. Report the product and mechanism numbers and
   the four bins at every timepoint. M2 tells you how much promoter mismatch the
   circuit tolerates, which is the design-relevant question. Check a sample by
   phase-contrast microscopy at the end for spores.
4. **Replicates:** 3 independent biological replicates, both write directions, all
   three strains. Minimum 10,000 events per cytometry sample.

### Pass criteria for 1a (fixed in advance)

- **Hysteresis:** the M1 ON-history and OFF-history curves do not overlap across
  a range of inducer levels by more than the replicate-to-replicate spread, and
  M3 shows a single curve.
- M1 matches the **Working toggle** row of the interpretation table in both
  write directions, with at least 3:1 separation between the two state
  populations.
- M1's product number is at least 70% at 24 hours, and its mechanism number is at
  least 70%.
- M3 matches the **Monostable** row.
- **M2 is reported, not required to proceed.** Its row of the table and its two
  numbers are recorded as the measured tolerance to promoter mismatch. The
  simulations predict M2 behaves like M1; if it does not, that is a design result,
  not a failure of the gate.

### What a fail means, and the go/no-go for 1b

- **M1 fails the mechanism number or the hysteresis test:** the BBB parts plus the
  Gardner topology do not produce a toggle in this chassis. Stop and rethink the
  chassis or repressor pair before spending anything further, including on 1b
  and Experiments 2 through 7.
- **M1 passes the mechanism number and hysteresis but fails the product number**
  (large [dark] population): the toggle works and the problem is expression loss
  or silencing. Proceed to 1b, whose controls exist to find the cause.
- **M3 turns out bistable:** the simulation's central design constraint is wrong,
  a real, publishable correction. Stop and re-examine before 1b.
- Pass on all of the above: proceed to 1b.

## Stage 1b: does it hold, and can the result be trusted? (only if 1a passes)

1. **Run M2's hysteresis** with the same P0 calibration and the 1a method.
2. **Long timepoints, 0, 2, 4, 6, 12, 24, 48 and 72 hours after washout,** for M1,
   M2 and M3, under the dilution regime below (growth and dilution are what a
   slow-relaxing monostable circuit cannot survive, so the dilution is part of
   the test).
3. **Sporulation, managed with a rule.** B. subtilis in batch culture reaches
   stationary phase and sporulates when nutrients run short. Spores do not divide,
   do not fluoresce, germinate on their own schedule (so manual passaging can carry
   them into later cultures with a different history from the vegetative cells) and
   deplete the population, so survivors stop being a representative sample.
   - **Regime:** manual serial dilution into fresh inducer-free medium at fixed
     intervals chosen to keep cells exponential and well away from nutrient
     exhaustion, with OD before and after each dilution and generations elapsed
     recorded. A microfluidic chemostat is cleaner but not needed for a first pass.
   - **Measure at every passage:** split a sample, heat-shock one half (the standard
     step that kills vegetative cells and leaves spores; a typical protocol is 80 C
     for 10 minutes, confirm with the lab) and plate both. The CFU ratio is the
     spore fraction. Add phase-contrast microscopy at the start and end.
   - **Threshold rule (no invented number):** the maximum acceptable spore fraction
     is the upper end of the replicate range measured for parental W168 in the same
     medium and dilution regime during pilot P0, run for at least as long as the
     experiment it supports. The lab and the founders write that number into the
     protocol before the first timepoint.
   - **If the threshold is exceeded at any passage:** mark that passage and every
     later timepoint as compromised (not a result), stop the culture, and apply the
     first workable fallback in this order:
     1. Tighten the dilution schedule (no change to the design, re-check the spore
        fraction on the next run, no extra cost beyond the repeat).
     2. Shorten the run and report the longest duration that stayed under the
        threshold as the limit of the claim.
     3. Change the medium to one that suppresses sporulation. This changes the
        experiment: the P0 baseline, the response-time calibration and M3 must be
        redone in the new medium before any result can be compared.
     4. Move to continuous culture (a chemostat or microfluidic device). This needs
        equipment the collaborating lab must have and adds cost; the lab decides.
4. **Washout-and-reread arm:** after the 24 hour read, wash a portion of each
   culture again into fresh inducer-free medium and re-read it at 48 and 72
   hours. A true toggle gives the same distribution. A slow monostable circuit
   keeps narrowing toward its single attractor.
5. **Growth-rate comparison:** growth curves of each strain against parental W168
   in the same medium, ON-state and OFF-state cultures separately. Record the
   doubling times.
6. **Competition assay.** Before it is run, every row below must be answered "yes"
   and written down. If any is "no", the assay is not run, because the result would
   not mean anything.
   
   | Required | Specification |
   |---|---|
   | Reference strain is named | A derivative of the same W168 stock the circuit strains were built from ("REF"), with a constitutive fluorophore of a color distinct from both reporters at a standard integration site other than *amyE* and *lacA*, and a resistance marker different from the circuit strain's. The exact fluorophore and site are chosen with the lab |
   | REF is isogenic outside the label | Both REF and the circuit strain are sequenced, and the only differences from the parental stock are the circuit, the label and its marker. A marker panel alone is not enough |
   | The label's own cost is measured | Growth curves of REF against unlabelled parental W168, and a REF-versus-parental competition (told apart by plating or by fluorescence). REF counts as neutral only if it shows no measurable cost |
   | Label swap and noise floor | REF-versus-REF with two different labels (any drift is the assay's noise floor), and circuit-versus-REF run in both labelings |
   | No DNA exchange | Laboratory *B. subtilis* 168 lineages are naturally competent under competence-inducing conditions. Avoid them, add DNase I to the cultures, and plate recovered clones on double selection to catch recombinants. A recombination event that moves the circuit or the label invalidates the result |
   | Same regime as the toggle run | Same medium, dilution schedule and temperature as Stage 1b. A cost measured in a chemostat is a different number |
   
   Start at a known ratio and track it over the full 72 hours by cytometry or
   selective plating. The change in ratio per generation estimates the fitness cost,
   the input `simulations/bsubtilis_30_fitness_cost_selection.py` needs.
7. **Optional, single-cell tracking:** image microcolonies on an agarose pad over
   time and confirm individual lineages hold their written state.
8. **Replicates:** 3 independent biological replicates, both write directions, all
   three variants. Minimum 10,000 events per cytometry sample.

### Pass criteria for 1b (fixed in advance)

- M1 keeps matching the **Working toggle** row at 24, 48 and 72 hours, with the
  bimodal distribution stable across at least three consecutive timepoints
  spanning at least 48 hours. A 24 hour snapshot alone could be passed by a slow
  monostable circuit relaxing over about 48 hours. M2's result over the same
  timepoints is reported against the same row.
- The product number stays at least 70% and the mechanism number stays at least
  70% across those timepoints for M1. If the product number passes only after
  excluding [dark] cells, the timepoint is uninterpretable, and the competition
  assay says whether fitness cost explains it.
- The washout-and-reread arm reproduces the same distribution at 48 and 72 hours.
- Every timepoint is under the sporulation threshold; timepoints over it are
  compromised and do not count toward the three consecutive.
- The competition assay passed its pre-run checklist and its result (fitness cost
  per generation, with the noise floor) is reported.
- M3 matches the **Monostable** row by the 72 hour timepoint at the latest. A
  slow collapse that has not finished by 24 hours still counts as monostable.

### What a fail means

- Failing the mechanism number or the stability rule: the toggle does not hold.
- Failing only the product number with a passing mechanism number: the toggle
  holds in the cells that still carry it. Use the competition assay and sequencing
  of dark isolates to decide between fitness cost, mutation and silencing.

## Cost and time

No lab has quoted any step. The earlier planning figure of $2,000 to $5,000 and 6
to 10 weeks predates this design and should be read as a floor for P0, 1a and 1b
together. P0 is not a small add-on: its calibration is of the same order as the
hysteresis test it sets up, which is why it is run first as a gate. Stage 1b adds
strains, cytometry runs, sequencing and labor, and its cost depends on the
sporulation fallback the lab ends up using. Sample-count formulas are in P0 and 1a.
