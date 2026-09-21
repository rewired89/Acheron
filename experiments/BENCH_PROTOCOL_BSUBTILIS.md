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
  the regrowth experiments in Stage B2.

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

- **Strain:** W168, variants M1, M2, M3.
- **Culture:** LB or a defined minimal medium, 37 C, shaking. Standard,
  nothing special required.
- **Write:** transient inducer pulse. IPTG pulse sets one state, aTc pulse sets
  the other. Pulse, then wash by centrifugation and resuspension into
  inducer-free medium. Record pulse duration and concentration, because the
  simulation's `write()` is an instantaneous idealization with no equivalent.
- **Read:** **flow cytometry, at single-cell resolution.** This is not
  optional. A plate reader reports a population mean, and a population mean
  cannot tell a bistable population (two separated peaks) from a monostable
  graded one (one broad peak at the same mean). Population-average lux or
  lacZ is acceptable only as a first cheap screen before cytometry.
- **Timepoints:** 0, 2, 4, 6, 12, 24 hours after washout.
- **Replicates:** three independent biological replicates, both write
  directions, all three variants. Minimum 10,000 events per cytometry sample.

**Pass criteria, fixed in advance:**
- M1 and M2 show a clearly bimodal GFP/mCherry distribution after washout, with
  the population sitting in the state it was written to.
- At least 70 percent of cells hold the written state at 24 hours, with at
  least 3:1 separation between the two state populations. These are the
  project's own thresholds used throughout the computational work, so the
  numbers are directly comparable.
- Both write directions work, in both directions, on the same culture.
- M3 fails to show bimodality, or collapses to one state regardless of what was
  written.

**What a fail means:** M1 failing means the BBB parts plus the Gardner topology
do not produce a toggle in this chassis. Stop and rethink the chassis or the
repressor pair before spending anything further.

### Stage B1: does it hold, and what is the real noise?

Runs on the same cultures as B0, extended. Low marginal cost, high value,
because it measures four parameters that every simulation in the repository
currently carries as an unmeasured placeholder.

- **Extend timepoints to 48 hours** with periodic dilution into fresh
  inducer-free medium to keep cells growing.
- **Measure and record:**
  - Fraction of cells in the correct state at each timepoint, which is the
    real-world version of the simulations' `genetic_correct`.
  - Cell-to-cell variability in reporter level within each state population,
    which is the real-world anchor for `transcriptional_noise_std`, currently
    a placeholder set to 3.0 in `bsubtilis_01_gardner_toggle_circuit.py` with no citation.
  - Spontaneous switching rate per generation, which no simulation in the
    repository models at all.
  - Reporter maturation half-life, which
    `bsubtilis_10_reporter_readout.py` sweeps across 5 to 60 minutes as an
    explicit placeholder.

**This stage's output is the main input to re-running the whole simulation
suite with measured rather than assumed noise.** That is worth saying to a
funder: the cheapest experiment on the list also retires the largest single
category of caveat in the audit.

### Stage B2: does the bit survive damage and regrowth?

**Tests audit Part 8 (`bsubtilis_07_colony_regrowth.py`), Part 20
(`bsubtilis_13_reporter_colony_regrowth.py`), Part 22 (`bsubtilis_15_partition_noise_regrowth.py`).**

Run two damage arms, because they separate a variable the simulations combine.

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
  whether the rest of the interference work matters. Parts 17 and 18 both found
  the answer flips between the low end (10 to 30 mV, where timing and partial
  decoupling both help) and the high end (70 mV, where only long averaging
  works).
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
