# Acheron Wet-Lab Bench Protocol: Testing the Simulations in *B. subtilis*

**Status:** Draft, September 2026. Not yet reviewed by a collaborating lab.
**Scope:** *B. subtilis* only. The planarian track is out of scope here and is
addressed in the "What this plan cannot test" section.
**Read first:** `docs/SCIENTIFIC_AUDIT_2026.md`. Every expected result below is
taken from a simulation logged there, with its audit Part number cited, so a
bench result can be compared against the exact prediction it is testing.

**What this document is:** a bench-level protocol, one level below
`docs/pitch/Acheron_Validation_Proposal.docx`. That document says which stages
to fund and roughly what each costs. This one says which strain, which parts,
which instrument, how many replicates, and what number counts as a pass or a
fail. It does not re-derive the proposal's cost or timeline figures.

**What already exists and is not duplicated here:**
`experiments/BENCH_PROTOCOL_HEK293.md` is the bench protocol for the HEK293
gap-junction persistence experiment (proposal Stage 1). There is no equivalent
bench-level protocol for the *B. subtilis* track, which is the track the
project's own cross-organism ranking (audit Part 13) puts first. That gap is
what this document fills.

---

## 0. The one-paragraph version

Build a Gardner-topology toggle switch from Bacillus BioBrick Box parts in
*B. subtilis* W168, read it with a two-color fluorescent reporter, and confirm
at single-cell resolution that it is genuinely bistable and not just graded.
Then damage the colony and regrow it and check the color still says the right
thing. Those two experiments cost the least and test the claims the project
actually depends on. Everything involving membrane voltage, the native
potassium wave, or electrical readout comes after, costs more, requires a
different strain background, and is where the real unknown lives.

---

## 1. Strain selection, and a mismatch the simulations do not show

This is the first thing a bench scientist will catch, so it is stated up front.

The project's two literature foundations were measured in **two different
strain backgrounds that cannot both be used at once**:

| Foundation | Strain it was measured in | Used by |
|---|---|---|
| Bacillus BioBrick Box promoter strengths and vectors | **W168** (domesticated lab strain) | `simulations/bsubtilis_01_gardner_toggle_circuit.py` and everything built on it |
| Biofilm potassium-wave signaling, yugO, the native oscillation | **NCIB 3610** (undomesticated ancestor) | `bsubtilis_08_native_oscillation_interference.py`, `bsubtilis_09_eis_readout_interference.py`, `bsubtilis_11_phase_locked_readout.py`, `bsubtilis_12_decoupled_channel_readout.py`, `bsubtilis_14_voltage_colony_regrowth.py` |

Strain 168 lost robust biofilm formation during domestication through four
chromosomal mutations (*sfp*, *epsC*, *swrA*, *degQ*) plus loss of a plasmid
carrying *rapP* (McLoon, Guttenplan, Kearns, Kolter & Losick 2011,
*J Bacteriol* 193(8):2027-2034, DOI 10.1128/JB.01542-10). Strain 3610 is poorly
transformable because of a plasmid-encoded competence inhibitor, ComI (Konkol,
Blair & Kearns 2013, *J Bacteriol* 195(18):4085-4093, DOI 10.1128/JB.00696-13,
PMID 23836866), so constructs generally go into it by SPP1 phage transduction
from a 168 donor, or into a competence-restored 3610 derivative. Confirm the
exact route with the collaborating lab before ordering anything.

**Three consequences the simulations do not currently reflect:**

1. **The reporter stages (B0 to B2) should run in W168**, where the BBB parts
   were characterized and transformation is routine. This is the cheap track.
2. **The interference stages (B4 to B5) require a 3610-derived background**,
   because W168 does not form the biofilm that produces the potassium wave in
   the first place. Moving the construct across is real extra work, not a
   formality.
3. **The interference problem only exists in the regime the project needs for
   biofilm-based storage.** A planktonic W168 culture has no potassium wave to
   interfere with. This does not make Parts 12, 13, 17, 18 and 21 wrong, it
   means those findings apply specifically to the biofilm configuration, and
   the plan should not pay for them until the reporter stages have earned it.

**Strains to order** (Bacillus Genetic Stock Center, bgsc.org):
*B. subtilis* W168 and NCIB 3610, plus the BBB 2.0 plasmid set, which Radeck et
al. 2017 state is distributed through BGSC.

---

## 2. The construct

### 2.1 Topology

Two arms, mutually repressing, matching
`simulations/bsubtilis_01_gardner_toggle_circuit.py`'s ODE exactly:

```
Arm A:  P_A  ->  repressor_B  +  reporter_A
Arm B:  P_B  ->  repressor_A  +  reporter_B
```

`GardnerParams` maps to the build as: `alpha1` = P_A strength, `alpha2` = P_B
strength, `strength_ratio` = P_B / P_A, `beta` and `gamma` = repressor
cooperativity (both fixed at 2 in simulation, Gardner's demonstrated bistable
regime).

### 2.2 Parts

- **Promoters:** from the BBB characterized set. The four constitutive parts
  span more than three orders of magnitude: J23101 (weakest, about 0.006 RPU),
  P*liaG* (the proposed 1 RPU reference), P*lepA* (intermediate), P*veg*
  (strongest, about 1000 RPU relative to P*liaG*). The inducible parts are
  P*liaI* (bacitracin, about 300-fold dynamic range) and P*xylA* with *xylR*
  (xylose, about 100-fold). All figures from Radeck et al. 2013,
  *J Biol Eng* 7:29, DOI 10.1186/1754-1611-7-29.
- **Repressor pair:** LacI and TetR is the default proposal, giving two
  orthogonal small-molecule write inputs (IPTG and anhydrotetracycline).
  Gardner's original pair was LacI plus a temperature-sensitive lambda cI in
  *E. coli*. **This substitution is a design proposal, not a measured choice**,
  and the *B. subtilis*-validated repressible promoter versions should be
  confirmed with the collaborating lab before synthesis.
- **Reporters:** sfGFP_Spn and mCherry_Bsu, both from the seven fluorescent
  proteins evaluated in BBB 2.0 (Radeck et al. 2017, *Sci Rep* 7:14134,
  DOI 10.1038/s41598-017-15107-z). One per arm.
- **Integration:** arm A at *amyE* (pBS1C or pBS1E), arm B at *lacA* (pBS2E).
  Different resistance markers so both integrate into one strain. Chromosomal
  integration, not a replicative plasmid, so copy number does not drift during
  the regrowth experiments in Stage B2. This is also the lower-noise choice,
  not just the copy-number-stable one, though not a noise-free one: Swain,
  Elowitz & Siggia (2002, *PNAS* 99:12795-800, DOI 10.1073/pnas.162041399)
  derive noise scaling as ~1/n with gene copy number n, and Dunlop, Cox,
  Levine, Murray & Elowitz (2008, *Nature Genetics* 40:1493-8, DOI
  10.1038/ng.281) show plasmid-borne genes carry measurably higher extrinsic
  noise than chromosomally integrated ones at comparable expression levels
  (their Fig. 3c/4d). Single-copy chromosomal integration is therefore a real
  noise cost traded for regrowth stability, not a free choice; see
  `simulations/bsubtilis_25_transcription_translation_noise_scaling.py` and
  audit Part 28.

### 2.3 The promoter-matching variants, which are the point of Stage B0

`bsubtilis_01_gardner_toggle_circuit.py` predicts that promoter matching is not a quality
knob but a precondition: at `strength_ratio` 0.1 the circuit stops being a
toggle at all and fidelity floors at 50 percent (audit Part 9). Build three
variants to test that directly:

| Variant | P_A / P_B | Simulated `strength_ratio` | Predicted outcome |
|---|---|---|---|
| **M1, matched** | same promoter part on both arms | 1.0 | Bistable, 100% fidelity at 24h |
| **M2, moderate mismatch** | P*liaG* / P*lepA* | within the 1.0 to 10.0 band | Bistable, 100% fidelity at 24h |
| **M3, severe mismatch** | P*liaG* / P*veg* (or the inverse) | approximately 0.1 or 10x in the collapsing direction | Monostable, fidelity floors near 50% |

M3 is the falsification arm. If M3 is bistable, the simulation's central design
constraint is wrong and that is a real, publishable correction. If M1 is not
bistable, the whole *B. subtilis* circuit track is in trouble and the project
finds that out for the price of the cheapest experiment on the list.

---

## 3. The stages, cheapest first

Each stage is a go/no-go gate. A negative result stops spend rather than
redirecting it into the next stage.

### Stage B0: does the toggle actually toggle?

**Tests audit Part 9 (`bsubtilis_01_gardner_toggle_circuit.py`) and Part 16
(`bsubtilis_10_reporter_readout.py`).**

- **Strain:** W168. Variant M1 is built for the pilot; M2 and M3 are built after the pilot passes.

This stage is specified in full, to the same wording, in
`wet_lab_experiments/Experiment_1_Toggle_Confirmation.md`, which is the standalone
version (there P0 is "Pilot P0", this stage's pilot is B0-P0). If one changes,
change the other.

## How this experiment is staged

Three steps, each a go/no-go gate for the next, so money is only spent on the
expensive parts after the cheap questions have a yes.

- **Pilot B0-P0, can this experiment be run at all?** Response-time calibration on
  its own cultures, the dose-response that locates the switching region, and the
  parental W168 spore baseline. If the circuit's settling time is longer than a
  vegetative culture can be sustained, the hysteresis test cannot run in batch
  culture and the design has to change before anything else is spent.
- **Stage B0a, does the switch switch?** Hysteresis (M1 against the M3 negative
  control) and a 24 hour read of all three variants. The go/no-go gate for B0b.
- **Stage B0b, does it hold, and can the result be trusted?** Runs only if B0a
  passes. Adds M2's hysteresis, the 72 hour run, the fitness and competition
  controls and the sporulation monitoring.

**Which strains are built when.** Build M1 first, for P0. Build M2 and M3 after P0
passes, because P0 can fail and constructs built before the gate would be wasted.
This default puts the gate ahead of batch savings. If the collaborating lab says a
batch build of all three is cheaper than building them separately, the lab's
answer overrides the default and should be recorded; the trade is paying for
constructs that a failed P0 would leave unused.

#### Shared methods (apply to P0, B0a and B0b)

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
     (Stage B0b) is destructive and off the cytometer, so it cannot be the gate; it
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
| Large [dark] together with a high spore or dead-cell share | **Culture problem**: handled in Stage B0b's sporulation rule, not a circuit result |
| The never-pulsed control is already bimodal, or already sits in one state | **Leak or default state**: the written-state results must be read against it, and it is the floor for any apparent bimodality |

A result met only after excluding [dark] cells is reported as **uninterpretable
at that timepoint**, not as a pass.

#### Pilot B0-P0: can this experiment be run at all? (M1 and parental W168 only)

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
     comparison against M3 happens in the hysteresis test in B0a). Hysteresis samples in B0a = 2 histories x inducer levels x
     strains (M1 and M3) x 2 successive reads x 3 replicates. These two are of the
     same order, so the calibration is a large part of the cost, not a footnote.
4. **Parental W168 spore baseline:** grow parental W168 under the planned dilution
   regime for at least 3 times the slowest response time, and later for the full
   72 hours, measuring the spore fraction at every passage (method in Stage B0b).
   This fixes the sporulation threshold.

##### Gate B0-P0

- **Go:** the slowest response time is short enough that 3 times that duration
  can be sustained under the dilution regime with the parental spore fraction at
  or below the threshold it defined.
- **No-go:** it is not. The hysteresis test cannot be run in batch culture. Stop,
  and take the design to the lab: options are a continuous or microfluidic culture
  method, a medium that suppresses sporulation (which means redoing the baseline),
  or redesigning the test. Do not proceed to B0a on a guess.

#### Stage B0a: does the switch switch? (M1, M2 and M3)

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

##### Pass criteria for B0a (fixed in advance)

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

##### What a fail means, and the go/no-go for B0b

- **M1 fails the mechanism number or the hysteresis test:** the BBB parts plus the
  Gardner topology do not produce a toggle in this chassis. Stop and rethink the
  chassis or repressor pair before spending anything further, including on B0b
  and Experiments 2 through 7.
- **M1 passes the mechanism number and hysteresis but fails the product number**
  (large [dark] population): the toggle works and the problem is expression loss
  or silencing. Proceed to B0b, whose controls exist to find the cause.
- **M3 turns out bistable:** the simulation's central design constraint is wrong,
  a real, publishable correction. Stop and re-examine before B0b.
- Pass on all of the above: proceed to B0b.

#### Stage B0b: does it hold, and can the result be trusted? (only if B0a passes)

1. **Run M2's hysteresis** with the same P0 calibration and the B0a method.
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
     medium and dilution regime during pilot B0-P0, run for at least as long as the
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
   | Same regime as the toggle run | Same medium, dilution schedule and temperature as Stage B0b. A cost measured in a chemostat is a different number |
   
   Start at a known ratio and track it over the full 72 hours by cytometry or
   selective plating. The change in ratio per generation estimates the fitness cost,
   the input `simulations/bsubtilis_30_fitness_cost_selection.py` needs.
7. **Optional, single-cell tracking:** image microcolonies on an agarose pad over
   time and confirm individual lineages hold their written state.
8. **Replicates:** 3 independent biological replicates, both write directions, all
   three variants. Minimum 10,000 events per cytometry sample.

##### Pass criteria for B0b (fixed in advance)

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

##### What a fail means

- Failing the mechanism number or the stability rule: the toggle does not hold.
- Failing only the product number with a passing mechanism number: the toggle
  holds in the cells that still carry it. Use the competition assay and sequencing
  of dark isolates to decide between fitness cost, mutation and silencing.


**Optional additional diagnostic, if time-lapse imaging is available
alongside end-point cytometry:** Dunlop, Cox, Levine, Murray & Elowitz
(2008, *Nature Genetics* 40:1493-8, DOI 10.1038/ng.281) show that the
time-lagged cross-correlation between two genes in the same cell, tracked
over time rather than at one timepoint, distinguishes an actively
repressing regulatory link (a delayed anticorrelation dip) from no link at
all, without perturbation. `simulations/bsubtilis_26_noise_crosscorrelation_diagnostic.py`
demonstrates the method on this project's own simulated construct and
found it confirms a functioning repression loop but does NOT by itself
distinguish M1/M2 from M3, since M3's failure is a loss of basin
separation, not a deactivated link; treat this as a complement to the
cytometry read above, not a substitute for it, and not required to pass
Stage B0.

### Stage B1: does it hold, and what is the real noise?

Runs on the Stage B0b cultures, extended. Low marginal cost, high value,
because it measures four parameters that every simulation in the repository
currently carries as an unmeasured placeholder.

- **Use B0b's timepoints (to 72 hours)** with periodic dilution into fresh
  inducer-free medium to keep cells growing.
- **Measure and record:**
  - Fraction of cells in the correct state at each timepoint, which is the
    real-world version of the simulations' `genetic_correct`.
  - Cell-to-cell variability in reporter level within each state population,
    which is the real-world anchor for `transcriptional_noise_std`, currently
    a placeholder set to 3.0 in `bsubtilis_01_gardner_toggle_circuit.py`.
    Swain, Elowitz & Siggia (2002, *PNAS* 99:12795-800, DOI
    10.1073/pnas.162041399) give the real formula this placeholder stands in
    for (noise as a function of burst size and mean expression level); their
    own cited E. coli range for burst size was read in Part 28 as implying this
    placeholder may be 3x to 17x too low. Audit Part 31 withdrew that headline
    (it compared unlike quantities) and showed that what matters is the noise as a
    fraction of the mean (CV), which depends on molecules per cell and burst size.
    An exact molecule-by-molecule model of the toggle holds at about 5 times the
    burst size in mean repressor molecules (`simulations/bsubtilis_32_analytic_and_gillespie_crosscheck.py`,
    unchanged by adding an mRNA stage and shared noise in `bsubtilis_33`),
    so this measurement, plus measured molecules per cell (Experiment 4), is exactly
    what is needed to say which side of that line the real circuit is on.
  - Spontaneous switching rate per generation, which no simulation in the
    repository models at all.
  - Reporter maturation half-life, which
    `bsubtilis_10_reporter_readout.py` sweeps across 5 to 60 minutes as an
    explicit placeholder.

**This stage's output is the main input to re-running the whole simulation
suite with measured rather than assumed noise.** That is worth saying to a
funder: the cheapest experiment on the list also retires the largest single
category of caveat in the audit.

**One addition worth costing in before this stage is finalized:** the
cell-to-cell variability bullet above measures total noise in one reporter
across a population, which conflates two mechanistically different sources.
Elowitz, Levine, Siggia & Swain (2002, *Science* 297:1183-6, DOI
10.1126/science.1070919) separated them with a specific design: two
differently-colored reporters under the SAME promoter, in the SAME cell.
Uncorrelated variation between the two colors is intrinsic noise (randomness
in that gene's own expression); correlated variation (both colors moving
together) is extrinsic noise (a shared, whole-cell fluctuation, e.g. total
RNA polymerase or ribosome availability at that moment). Running that
two-color-same-promoter control alongside the two-arm reporter this stage
already uses is a small addition to the same imaging session, not a separate
experiment, and its result decides something the current design cannot:
`simulations/bsubtilis_23_intrinsic_extrinsic_noise.py` (audit Part 27) found
that a shared, correlated noise source behaves differently in a mutual-
repression circuit than the independent-only noise this project has modeled
so far, at illustrative noise magnitudes a mismatched-but-passing promoter
ratio degraded while the matched ratio did not. Whether that matters for the
real BBB promoters is exactly what this control would answer.

### Stage B2: does the bit survive damage and regrowth?

**Tests audit Part 8 (`bsubtilis_07_colony_regrowth.py`), Part 20
(`bsubtilis_13_reporter_colony_regrowth.py`), Part 22 (`bsubtilis_15_partition_noise_regrowth.py`).**

Run two damage arms, because they separate a variable the simulations combine.

**Locus-stability check, run first on the same cultures.** After the final
regrowth, and again after a second full damage-and-regrowth round on the same
lineage, confirm by colony PCR (and sequencing of a subset) that both circuit
arms are intact at their intended loci (*amyE*, *lacA*). A duplicated, lost or
rearranged construct would look like a memory failure in the cytometry read
and no simulation models it. Interpret no arm 2a or 2b failure as a failure of
the mechanism until this passes. Use the B0 growth and competition results to
tell circuit loss or outgrowth by non-expressers from state loss, and use the
four-bin gate from B0.

**Survivor-bias control, run with both arms.** The cells that survive damage may
not be a random sample: stress responses and growth state can correlate with
circuit expression, so survivors could already be enriched for cells that were
downregulating the circuit before the insult, which would make a good recovery
look better than it is (or the reverse). Run damage on freshly written cultures
with as few generations as possible between write and insult, measure the
both-low and four-bin composition of the culture immediately before damage,
and measure the same composition among plated survivors (colony fluorescence).
The ratio of the lost share among survivors to the lost share before damage is a
direct estimate of the bias that `bsubtilis_30_fitness_cost_selection.py`
section F sweeps. At plausible fitness costs and loss rates, selection during the
roughly 7 division regrowth window does not dominate the result, but the
direction and size of survivor bias is not modelled and could make recovery look
better or worse.

- **Arm 2a, dilution only.** Write a bit, then dilute the culture to a defined
  low CFU count and let it regrow. This isolates exactly what the simulations
  model: fewer cells, more divisions to get back to full size, no other
  physiological change. Target surviving fractions across the simulated sweep:
  2, 10, 25, 50 and 100 percent, with CFU plating to confirm the actual number
  rather than the intended one.
- **Arm 2b, real insult.** Write a bit, then apply a calibrated sublethal
  insult (heat shock, or hydrogen peroxide, calibrated by CFU count to hit the
  same surviving fractions), then regrow. **The gap between 2a and 2b is the
  measurement that matters**, because every damage simulation in the repository
  models damage purely as removing cells, with no physiological effect at all
  on the survivors. Real damage stresses survivors, induces stress regulons,
  and changes growth rate. No simulation here represents that, and 2a minus 2b
  is the size of that blind spot.
- **Read:** flow cytometry at the end of regrowth plus settling, same
  thresholds as B0.
- **Also record:** actual doubling time under the recovery condition, and
  actual wall-clock time from insult to a readable colony. The simulations
  assume a 30-minute doubling time and a fixed 6-hour post-insult window
  (`DOUBLING_TIME_MIN`, `SETTLE_WINDOW_HOURS` in
  `bsubtilis_07_colony_regrowth.py`), and audit Part 21 found that budget has
  zero slack at worst-case damage. This is the measurement that says whether
  the budget is real.

**Predicted result:** recovery to near 100 percent fidelity from as little as 2
percent surviving cells, with no gap between genetic state and reporter
readout, per Parts 8 and 20.

**Pass criteria:** at least 70 percent correct bit at 2 percent survival in arm
2a. Report arm 2b separately rather than folding it in.

### Stage B3: repressor copy number

**Tests audit Part 22's one unmeasured conversion.**
`bsubtilis_15_partition_noise_regrowth.py` has to convert dimensionless repressor units into
real molecule counts and has no citation for the conversion, so it sweeps it.
The sweep found recovery is robust down to about 5 molecules per cell and only
degrades at about 1. Measuring the real number tells you which end of that
sweep applies.

- **Method:** quantitative single-cell counting via a calibrated fluorescent
  fusion, or targeted mass spectrometry, or quantitative western blot. In
  rising order of cost and precision.
- **Value:** if the real copy number is comfortably above 5 per cell, Part 22's
  weak point and Part 23's proposed reinforcement circuit are both moot and can
  be dropped from the roadmap. That is a cheap way to delete a whole branch of
  future work.

### Stage B4: the voltage interface, which is the actual unknown

**Tests the link audit Part 9 describes as having no prior art in any
organism.** Everything before this stage re-tests things that are strongly
precedented. This is the first experiment that tests something nobody has
built.

- **Strain:** 3610-derived background, per section 1.
- **Build:** couple one toggle arm's output to expression of a potassium
  channel. The named candidate is **yugO**, a TrkA-domain K+ efflux channel
  downstream of *mstX*, repressed by SinR (Lundberg, Becker & Choe 2013,
  *PLoS ONE* 8(5):e60993, DOI 10.1371/journal.pone.0060993, PMID 23737939).
- **Design warning carried from audit Part 14:** before committing to a BBB
  promoter for the toggle arms, check whether that promoter is itself
  SinR/Spo0A-regulated. Many biofilm-stage promoters are. If it is, the
  engineered circuit and the native signaling share an upstream transcriptional
  regulator, not just a membrane, and the two are not independent.
- **Read:** Thioflavin T fluorescence as a membrane-potential indicator, which
  is the reagent the biofilm electrical-signaling literature uses, plus
  two-electrode electrical impedance spectroscopy per Akabuogu, Zhang,
  Krašovec, Roberts & Waigh 2024, *Nano Letters* 24(7):2234-2241,
  DOI 10.1021/acs.nanolett.3c04446, PMID 38320294.
- **Three caveats to write into the protocol before running it:**
  1. **ThT is not calibrated to absolute millivolts.** The `V_HIGH = -10 mV`
     and `V_LOW = -80 mV` values in `bsubtilis_01_gardner_toggle_circuit.py` are inherited
     from the planarian model and have no *B. subtilis* measurement behind
     them. Report ThT readings in relative units and do not convert them to
     millivolts to compare against the simulation.
  2. **ThT perturbs the cells it measures.** Han & Payne 2022 report an effect
     of ThT on bacterial elongation rate (*Bioelectricity*,
     DOI 10.1089/bioe.2021.0027). Include a no-dye growth control.
  3. **ThT's potentiometric interpretation has been challenged**, in spores
     specifically rather than vegetative cells: Li, He, Aryal, Wicander, Korza
     & Setlow 2023, *mBio* 14(5):e02220-23, DOI 10.1128/mbio.02220-23, argue
     ThT fluorescence during germination reflects dye binding to hydrophobic
     coat proteins rather than electrochemical potential. That paper's scope is
     spores, not the vegetative biofilm cells this project cares about, so it
     is a reason to run an independent voltage control, not a reason to drop
     ThT.
- **Pass criteria:** a measurable, reproducible difference in membrane
  potential between the two written states, in the same direction each time,
  larger than the strain's own cell-to-cell variability.

**This stage is where the project should expect to fail first**, and it is
worth funding precisely because a clean negative here is the single most
valuable result available.

### Stage B5: the native oscillation and readout timing

**Tests audit Parts 12, 13, 17, 18 and 21.** Only run this if B4 produces a
measurable voltage bit.

- **First, measure the thing the simulations had to guess.** Every interference
  simulation sweeps oscillation amplitude from 10 to 70 mV because no source
  paper reports a millivolt figure. Measure the native oscillation's actual
  amplitude and period in your strain and your setup, in ThT units, in a strain
  carrying no engineered circuit at all. This one measurement determines
  whether the rest of the interference work matters, but the two easier fixes
  do not share one "low-end" band: **Part 17 found timing only rescues a fast
  read at the lowest tested amplitude (10 mV)**, where a perfectly-timed read
  hits 100% and tolerates real timing error well; by 20 mV a perfectly-timed
  read is already back to a coin flip (~50%), no better than a blind read.
  **Part 18 found partial decoupling works at a different point**: at a
  moderate amplitude (30 mV), cutting the native signal's coupling to just
  10% of today's assumed strength is enough to make even a fast, 1-minute
  read work well (94%). Neither fix, timing or partial decoupling, rescues a
  fast read at the documented worst case (70 mV); there, only the 180-minute
  average works, regardless of coupling level.
- **Then compare three readout strategies** on the same biofilm, per Part 13
  and Part 17: a single fast read, a read timed to the oscillation's predicted
  quiet phase, and a read averaged over about 180 minutes.
- **Then test decoupling**, per Part 18: build the same voltage-bit construct
  in a Δ*yugO* background, or route the engineered output through a different
  channel, and repeat. Budget for the biofilm-formation cost of losing yugO,
  which Lundberg et al. 2013 document.
- **Predicted result:** the single fast read collapses toward 50 percent at
  amplitudes above about 10 mV, the timed read does not rescue it, and the
  180-minute average recovers to near 100 percent.

**A bootstrapping problem to solve in the protocol, flagged in
`bsubtilis_11_phase_locked_readout.py`'s own docstring:** the timed-read arm needs to know
the oscillation's phase, and you cannot get phase from the readout you are
still trying to validate. Use ThT imaging of the biofilm's own wave, in the
circuit-free control strain, as the independent phase reference.

### Stage B6: the damage-sensing reinforcement circuit

**Tests audit Part 23 (`bsubtilis_16_damage_sensing_reinforcement.py`).** Run only if Stage
B3 finds repressor copy number low enough for partition noise to matter.

- **Build:** a stress-responsive promoter driving a transient boost of whichever
  toggle arm currently dominates. The simulation models this on the bacterial
  SOS response (RecA/LexA) but does not name a specific *B. subtilis* promoter.
  Selecting that promoter is a design task this plan does not resolve.
- **Test the question the simulation raised and did not answer:** after
  reinforcement has fired and healing is complete, can a normal write pulse
  still flip the bit, or has the circuit been reinforced into being
  unwritable? This is a straightforward bench test and the simulation cannot
  answer it.

---

## 4. The cheapest order, and why

| Order | Stage | Why here |
|---|---|---|
| 1 | B0 toggle confirmation | Cheapest. Kills or confirms the whole circuit track. Also tests M3, a falsifiable prediction the simulation made. |
| 2 | B1 persistence and noise | Almost free given B0's cultures. Retires the largest category of unmeasured parameters in the repository. |
| 3 | B2 damage and regrowth | Standard microbiology, no new instrument. Tests the project's headline self-healing claim in the organism it actually plans to use. |
| 4 | B3 copy number | Optional. Cheap enough to justify because it can delete Stage B6 entirely. |
| 5 | B4 voltage interface | First genuinely novel experiment. Needs the 3610 strain move, so it is a real step up in cost and time. |
| 6 | B5 oscillation and readout | Depends entirely on B4 succeeding. |
| 7 | B6 reinforcement circuit | Only if B3 says partition noise is real at the measured copy number. |

**The honest tension in this ordering, stated plainly:** Stages B0 through B2
largely re-test things that are well precedented. Toggle switches in bacteria
have worked since 2000, and division-based inheritance of protein state is what
cell division does. The genuinely unknown piece is Stage B4. A reviewer can
reasonably ask why the plan spends its first three stages on the precedented
part. The answer is that the specific combination is not precedented (Gardner
topology plus BBB parts plus this chassis, never built), that the
promoter-matching constraint in M3 is a real falsifiable prediction, and that
B1's measured noise parameters are what make every downstream simulation
trustworthy. That answer is defensible, but it should be given openly rather
than left for a reviewer to raise.

**Costs:** `docs/pitch/Acheron_Validation_Proposal.docx` prices its Stage 0
(equivalent to B0 here) at 2,000 to 5,000 dollars over 6 to 10 weeks, and notes
that figure is a planning estimate not yet quoted by a lab. Stages B1 through
B6 have not been quoted and no figure is invented for them here. Getting a real
quote from the collaborating lab is a prerequisite to any funding ask that
includes them.

---

## 5. Simulated results this plan cannot test

Listed because the task asked for them, and because leaving them unlisted would
misrepresent the plan's coverage.

**1. The 15x to 20x `bistable_k` benchmark (audit Part 8, Finding 2).**
`bistable_k` is a phenomenological modeling knob with no direct biological
referent, which the audit already states. There is no bench measurement that
returns a `bistable_k` value, so "feedback 15 to 20 times stronger than
naturally plausible" cannot be confirmed or refuted as stated. What Stage B0
tests instead is the thing that number was a proxy for: whether an engineered
circuit produces two genuinely separated stable states. Treat the multiplier as
retired by B0 rather than tested by it.

**2. The Bio-RAID multi-tile results (audit Part 8, Finding 3).** The finding
is that replication cannot rescue a per-tile signal already lost in noise.
Testing it requires a working voltage bit with a measurable per-tile error
rate, which does not exist until Stage B4 succeeds. Nothing in B0 through B3
touches it.

**3. Everything in the planarian track.**
`simulations/planarian_09_regrowth_state_inheritance.py` rests on a mean-field coupling
constant the audit itself ranks as the lowest-confidence assumption in the
project (Part 13), and audit Part 10 records that reliable arbitrary-sequence
genetic modification is not established in planarians. This plan is *B.
subtilis* only and does not advance the planarian results either way. The two
Levin-lab papers logged in audit Part 19 (Oviedo et al. 2008 DiBAC4(3) imaging
protocol, and Grodstein & Levin 2021) are the starting point if that track is
picked back up.

**4. The methylation mechanism (audit Part 11).** Both real fidelity anchors,
96 percent and 99.9 percent, are mammalian CpG measurements, and *B. subtilis*
does not natively carry the Dam/Dcm system they depend on. Testing this needs a
maintenance methyltransferase engineered in first, which is a separate build
with its own risk, not a stage of this plan.

**5. The exact worst-case time budget (audit Part 21).** The finding that
regrowth from a single surviving cell to 64 cells leaves exactly 180 minutes of
settling time falls out of the model's own `n_cells = 64` and
`SETTLE_WINDOW_HOURS = 6` choices. A real colony is not 64 cells and a single
surviving cell is not a condition you can set reproducibly. Stage B2 measures
the real inputs to that budget (actual doubling time under recovery, actual
time to a readable colony) so the budget can be recomputed, but the specific
"exactly zero slack" result is an artifact of the model's scale parameters and
is not directly testable.

**6. The dimensionless-to-molecule conversion (audit Part 22).** Stage B3
measures real repressor copy number, which is the useful half. There is no
measurement that returns the conversion factor between the simulation's
dimensionless u and v units and molecule counts, because those units are a
modeling normalization, not a physical quantity.

**7. The absolute voltage targets.** `V_HIGH = -10 mV` and `V_LOW = -80 mV`
came into the *B. subtilis* model from the planarian work. No stage here
validates those specific values, and Stage B4's ThT readout cannot, because ThT
is not calibrated to absolute millivolts. If absolute values are needed, that
requires a separate calibration method and should be scoped separately.

**8. Anything about damage's physiological effect on survivors.** Stage B2's
arm 2b measures the size of this gap but no simulation in the repository models
it, so there is no prediction for arm 2b to be compared against. The result
will be new information rather than a confirmation or a refutation.

---

## 6. References

Akabuogu, Zhang, Krašovec, Roberts & Waigh (2024). Electrical impedance
spectroscopy with bacterial biofilms: neuronal-like behavior. *Nano Letters*
24(7):2234-2241. DOI 10.1021/acs.nanolett.3c04446. PMID 38320294.

Gardner, Cantor & Collins (2000). Construction of a genetic toggle switch in
*Escherichia coli*. *Nature* 403:339-342. DOI 10.1038/35002131.

Han & Payne (2022). Effect of thioflavin T on the elongation rate of bacteria.
*Bioelectricity*. DOI 10.1089/bioe.2021.0027.

Huh & Paulsson (2011). Non-genetic heterogeneity from stochastic partitioning
at cell division. *Nature Genetics* 43(2):95-100. DOI 10.1038/ng.729.
PMID 21186354.

Konkol, Blair & Kearns (2013). Plasmid-encoded ComI inhibits competence in the
ancestral 3610 strain of *Bacillus subtilis*. *J Bacteriol* 195(18):4085-4093.
DOI 10.1128/JB.00696-13. PMID 23836866.

Li, He, Aryal, Wicander, Korza & Setlow (2023). Thioflavin-T does not report on
electrochemical potential and memory of dormant or germinating bacterial
spores. *mBio* 14(5):e02220-23. DOI 10.1128/mbio.02220-23.

Lundberg, Becker & Choe (2013). MstX and a putative potassium channel
facilitate biofilm formation in *Bacillus subtilis*. *PLoS ONE* 8(5):e60993.
DOI 10.1371/journal.pone.0060993. PMID 23737939.

McLoon, Guttenplan, Kearns, Kolter & Losick (2011). Tracing the domestication
of a biofilm-forming bacterium. *J Bacteriol* 193(8):2027-2034.
DOI 10.1128/JB.01542-10. PMID 21278284.

Prindle, Liu, Asally, Ly, Garcia-Ojalvo & Süel (2015). Ion channels enable
electrical communication in bacterial communities. *Nature* 527:59-63.
DOI 10.1038/nature15709. PMID 26503040.

Radeck et al. (2013). The Bacillus BioBrick Box: generation and evaluation of
essential genetic building blocks for standardized work with *Bacillus
subtilis*. *J Biol Eng* 7:29. DOI 10.1186/1754-1611-7-29. PMID 24295448.

Radeck et al. (2017). The Bacillus BioBrick Box 2.0: expanding the genetic
toolbox for the standardized work with *Bacillus subtilis*. *Sci Rep* 7:14134.
DOI 10.1038/s41598-017-15107-z.

Internal: `docs/SCIENTIFIC_AUDIT_2026.md` Parts 8 through 23;
`docs/pitch/Acheron_Validation_Proposal.docx`;
`experiments/BENCH_PROTOCOL_HEK293.md`; `docs/THIRD_PARTY_METHODS.md`.
