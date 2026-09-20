# Readout Methods Checked Against Published Work (September 2026)

**Status:** literature check plus cost/difficulty triage. No new simulation
was run for this document. Every number below is either cited to a source
checked on 20 September 2026, or explicitly labeled as an unpriced estimate.
Per `docs/THIRD_PARTY_METHODS.md`'s no-numeric-invention rule, no cost was
invented to fill a gap, gaps are stated as gaps.

---

## 1. The problem this document is answering

Four of this project's own simulations, logged in
`docs/SCIENTIFIC_AUDIT_2026.md` Parts 12, 13, 17 and 18, converge on one
finding: reading the engineered bit as a **membrane-voltage value** does not
cleanly separate the stored state from *B. subtilis*'s own potassium-wave
oscillation (Ford et al. 2021; Mulder et al. 2025; channel named by
Lundberg, Becker & Choe 2013).

What has been ruled out or narrowed so far, by this project:

| Attempted fix | Simulation | Result |
|---|---|---|
| Single voltage snapshot | `native_oscillation_interference.py` | Fails. 50 to 59% accuracy at 10 to 20mV ambient oscillation |
| EIS-style time integration | `eis_readout_interference.py` | Only works at a ~180 minute window, one full oscillation period. A real EIS sweep is seconds to minutes, so a single sweep does not fix it |
| Timing the read to a quiet moment | `phase_locked_readout.py` | Fails above 10mV. Cumulative drift, not instantaneous waveform value, is the problem |
| Weakening the coupling (different channel, or yugO knockout) | `decoupled_channel_readout.py` | Works at 30mV with only a 90% coupling reduction. Does not work at the 70mV worst case without a complete knockout |
| Reading a fluorescent reporter instead of voltage | `gardner_toggle_reporter_readout.py` | Clean, but only because no cited mechanism couples the native oscillation to transcription, so no interference term was modeled |

So the honest internal position going into this check was: the only readout
that survives the full documented interference range is either a 3 hour
averaged electrical read, or an entirely non-electrical one.

---

## 2. What the published literature actually does

This is the blunt headline, and it is not flattering to the current design.

**No established engineered-cell-state readout uses membrane potential as
the state variable.** Every canonical bistable-memory paper reads protein
output, not voltage:

- **Gardner, Cantor & Collins (2000)**, "Construction of a genetic toggle
  switch in *Escherichia coli*," *Nature* 403:339-342, DOI
  [10.1038/35002131](https://doi.org/10.1038/35002131). The circuit this
  project's `gardner_toggle_circuit.py` is modeled on. Its state was read by
  **GFP fluorescence, by flow cytometry**, not by any electrical measurement.
- **Bonnet, Subsoontorn & Endy (2012)**, "Rewritable digital data storage in
  live cells via engineered control of recombination directionality," *PNAS*
  109(23):8884-8889, DOI
  [10.1073/pnas.1202344109](https://doi.org/10.1073/pnas.1202344109), PMID
  22615351. See section 5 below, this one matters for more than its readout.
  State read by **mutually exclusive GFP/RFP expression, via flow cytometry
  (30,000 cells per measurement) and microscopy**.
- **Huang, Yu, Lee et al. (2025)**, *Nature Communications* 16:9414, DOI
  [10.1038/s41467-025-64457-0](https://doi.org/10.1038/s41467-025-64457-0),
  already cited in `gardner_toggle_circuit.py` and
  `docs/THIRD_PARTY_METHODS.md`. Recombinase memory circuit, reporter readout.

**And the bacterial-bioelectricity field's own 2026 review says every
voltage readout carries confounds of exactly the kind this project hit.**
Cianflone, Keller, Subramaniam & Paternò (2026), "Bacterial bioelectricity,
the first 15 years: developments, tools, and remaining questions,"
*Frontiers in Photobiology* 4:1834373, DOI
[10.3389/fphbi.2026.1834373](https://doi.org/10.3389/fphbi.2026.1834373).
Its caveats, quoted:

- On the standard dyes (ThT, DiBAC, TMRM), the ones the Prindle-lab
  potassium-wave work uses: they "tend to measure the steady-state Vm rather
  than fast transients; furthermore, their signal might be altered by
  membrane permeability changes, the activity of the efflux pump or other
  variations in the membrane physiology independent from the Vm." The review
  also notes these dyes "may influence bacterial growth even at low
  concentrations."
- On genetically encoded voltage indicators (PROPS-like): they allow ~1 Hz
  optical recording but "require genomic modifications."
- On optical methods generally: "phototoxicity, heating, intrinsic
  non-photosynthetic light sensitivity and reactive oxygen species" are
  confounds that must be controlled.
- On the field as a whole: "Many studies excel at dynamics but remain
  limited in absolute Vm quantification, and cross-lab comparability is
  hindered by differences in probes, media, growth state, and illumination
  protocols."

That last point is the one to sit with. Absolute membrane-potential
quantification in bacteria is *itself* an open measurement problem in 2026,
independent of anything Acheron builds. A design whose read step depends on
resolving two voltage levels reliably is standing on the least settled part
of the measurement literature, not the most.

Independent corroboration of the dye problem specifically: Han & Payne
(2022), "Effect of Thioflavin T on the Elongation Rate of Bacteria,"
*Bioelectricity*, and Han & Payne (2023), "Gold Ions Hyperpolarize
Bacteria," same journal, both report the probe or its environment perturbing
the cells being measured.

---

## 3. What this repository already tests, versus what the literature uses

| Method | In this repo? | In the literature for engineered state? | Interference-immune? |
|---|---|---|---|
| Single-point membrane voltage | Yes, `native_oscillation_interference.py` | No precedent as a state readout | No |
| EIS / impedance | Yes, `eis_readout_interference.py` | Yes as a live/dead assay (Akabuogu et al. 2024), not as a bit readout | Only at a ~3h integration window |
| Phase-locked voltage sampling | Yes, `phase_locked_readout.py` | No precedent found | No |
| Reduced-coupling voltage read | Yes, `decoupled_channel_readout.py` | No precedent found | Partially, amplitude-dependent |
| Two-color fluorescent reporter | Yes, `gardner_toggle_reporter_readout.py` | **Yes, this is the standard** | No cited coupling mechanism, so yes by default |
| Bioluminescence (lux / luciferase) | Named in `encoder/bacterial_toggle_encoder.py` and the Stage 0 assay, never simulated | Yes, widely | Same reasoning as fluorescence |
| DNA-orientation state read by PCR | No | **Yes, Bonnet et al. 2012** | Yes, the state is not electrical at all |
| Nanopore methylation calling | Referenced in `methylation_bit_encoding.py` as the source paper's method | Yes | Yes, but destructive |

The gap is not that this project has not thought about reporters. Part 16
and the Stage 0 assay in `docs/pitch/Acheron_Validation_Proposal.docx`
already use one. The gap is that **the electrical readout is still on the
critical path in the pitch narrative**, while the literature has no
precedent for it and an active measurement-standardization problem around it.

---

## 4. The three most promising alternatives, with cost and difficulty

Ranked by how much of this project's actual open question each one answers
per dollar. Cost tiers are labeled, and only two hard figures below are
cited prices, the rest are explicitly unpriced.

### A. Two-color fluorescent reporter, read on a plate reader or microscope

**What it is:** GFP on one toggle arm, RFP on the other, read as a
population-level ratio or per-cell in images. Exactly Gardner 2000 and
Bonnet 2012.

**Why it is first:** it is the only option that is simultaneously the field
standard, already simulated here (Part 16), already the Stage 0 plan, and
immune to the identified interference mechanism by construction rather than
by hope.

**Cost:** reagents are cheap and already inside the existing Stage 0
planning range in `docs/pitch/EXPERIMENT_COM_CAMPAIGN.md` (a stated
$2,000 to $5,000 planning estimate, not a lab-confirmed quote, and not
re-derived here). **The instrument is the entire cost question**, and it
splits three ways:

- A filter-based microplate reader gives quantitative population averages.
  New instruments are five-figure purchases. Unpriced here, no quote obtained.
- An epifluorescence microscope gives the per-cell bimodality that actually
  proves bistability. Also five figures new. Unpriced here.
- A flow cytometer is what both canonical papers used. **Out of reach.** See
  section 6.

**Difficulty:** low on the biology, moderate on the instrument access.

**Blunt version for a home or low-budget setup:** a blue LED, an emission
filter and a phone camera can tell green from red in a dense culture. That
demonstrates *a* difference. It does not give you a **bimodal
single-cell distribution**, which is the actual evidence that a toggle is
bistable rather than just expressing two proteins at intermediate levels.
Without that, Stage 0 cannot return its intended answer. Do not budget this
as solved by a phone camera.

### B. Bioluminescence, read on an open-source $40 luminometer

**What it is:** put the luciferase output of one toggle arm on a
luminometer. Either a bacterial `lux` operon, which is substrate-autonomous
and needs no reagent addition, or a firefly/NanoLuc-class enzyme, which
needs substrate. The Stage 0 assay already names `lux` as an option.

**Why it is second:** bioluminescence needs **no excitation light source and
no optical filters**, which removes both the cost driver and the
phototoxicity confound the Cianflone 2026 review flags for every optical
method. And there is a validated, published, genuinely cheap instrument for
it.

**Cost, cited:** **LuminoCell**, Weissová, Fafílek, Radaszkiewicz et al.
(2022), *Life Science Alliance* 5(8):e202201421, DOI
[10.26508/lsa.202201421](https://doi.org/10.26508/lsa.202201421), PMID
35440493, costs **approximately $40 to assemble** and "requires less
than 1 h to assemble," from a TSL237S-LF light-to-frequency sensor, an
Arduino, and a 3D-printed housing holding six 40mm petri dishes. It reports
seven orders of magnitude of dynamic range against a commercial
instrument's eight. See
[life-science-alliance.org/content/5/8/e202201421](https://www.life-science-alliance.org/content/5/8/e202201421).

**Stated limitation, quoted from the same paper:** it "cannot compete with
commercial instruments in terms of detection limits," with "a detection
limit around 40 pW/s of light irradiance" versus attowatt-scale
photomultiplier instruments. The paper's own workaround is longer
integration time at the cost of temporal resolution.

**One caveat that has to be stated, not glossed:** LuminoCell was built and
validated for luciferase reporters in **mammalian cell culture in petri
dishes**, not for bacterial `lux` in *B. subtilis*. The photon-detection
physics carries over, the validation does not. Whether a *B. subtilis*
colony's `lux` output clears that 40 pW/s detection limit at realistic
culture density is an untested question for this project, and it is a cheap
one to answer with a single test construct before committing to the approach.

**Difficulty:** low on the electronics, low to moderate on the biology
(cloning a lux cassette into the toggle is ordinary work).

**Blunt version:** this is the **only** readout on this list that is
genuinely reachable on a home budget end to end. It is also
**population-level only**. One photon count per dish tells you the average,
not the distribution, so it has the same blind spot as option A's cheap
version: it cannot show bimodality. It is excellent for watching a
**switching event over time** in one culture, which is a real and useful
experiment, and it is not sufficient on its own to claim bistability.

### C. Move the state into DNA orientation and read it by PCR

**What it is:** stop storing the bit as a protein concentration or a voltage
and store it as the **orientation of a DNA segment**, flipped by a serine
integrase and flipped back by adding its excisionase. Read it by PCR with
orientation-specific primers, on a gel. Fluorescence becomes an optional
second channel rather than the only channel.

**Why it is on this list at all:** it is the one option whose persistence
through cell division has been **measured in a living organism**, not
simulated. Bonnet et al. 2012 report the state holding **over 100 cell
divisions with no input signal and no selection**, with set efficiency
">95% at the single-cell level" and reset "~85% to >90%." The construct is
publicly distributed (Addgene plasmid
[#38207](https://www.addgene.org/38207/)).

**Cost:** the readout itself is the cheapest quantitative option here. PCR
plus gel electrophoresis needs a thermocycler and a gel rig, both routinely
available secondhand, plus ordinary polymerase and primers. Unpriced here,
no quote obtained, but the instrument tier is well below a plate reader.

**Difficulty:** moderate to high, and the difficulty is **not** in the
readout. Bonnet et al. state they screened "~400 clones" to get reliable
combined set and reset behavior, and that state transitions took roughly 10
generations (900 minutes). Porting an integrase latch into *B. subtilis*
from an *E. coli* demonstration is real work.

**Blunt version, and this is the important one:** this is not a drop-in
replacement for the reader. It **changes what the stored state is**, and
therefore changes the project's central claim. It also reads destructively
in its simplest form, you sacrifice the sample to PCR it, which removes the
"repeatable read on the same living colony" property that made the
electrical route attractive in the first place.

### Honorable mention, for the methylation channel only

If the methylation encoding path in `methylation_bit_encoding.py` is ever
pursued, its readout is nanopore methylation calling, which is what that
file's source method (B2A, Nanopore plus Modkit) already uses. Current
**cited** list prices, checked on
[nanoporetech.com](https://nanoporetech.com/products/sequence/minion) on 20
September 2026: MinION Mk1D device **$3,150**, MinION Mk1D starter pack
**$5,150** including five R10.4.1 flow cells and sequencing kits. Per-flow-cell
pricing was not listed on that page, so it is not stated here. This is
destructive and per-read expensive, which makes it an archival verification
method, not a working memory readout.

---

## 5. One prior-art correction this check turned up

`docs/SCIENTIFIC_AUDIT_2026.md` Part 10 concludes: "every existing example
of 'data in a living organism' is either (a) an analog device with no
addressable write layer, or (b) DNA-sequence storage, which is
fundamentally archival, not a dynamic, rewritable state."

**Bonnet, Subsoontorn & Endy 2012 is a third category that sentence does not
cover**, and it was not in this repository anywhere before this document.
Its title is literally "Rewritable digital data storage in live cells." It
is addressable, it is digital, it is rewritable through multiple set and
reset duty cycles, it is heritable through 100+ divisions without selection,
and it is read non-destructively by fluorescence. It is not a bioelectric
state, and it is one bit per register rather than a scalable array, so the
distinctness of Acheron's approach is not erased. But "nothing found stores
arbitrary data as a dynamic, rewritable state" is too strong as written, and
a diligent investor or examiner will find this paper. Part 10 should be
amended rather than left standing.

---

## 6. Out of reach for a home or low-budget setup, stated plainly

No hedging on these. If a plan depends on one of them, the plan depends on a
partner lab.

- **Flow cytometry.** The readout both canonical toggle-switch papers
  actually used, and the only one that cleanly shows a bimodal single-cell
  distribution across tens of thousands of cells. Instrument and service
  contract are far outside a self-funded budget. Renting time at a core
  facility is the realistic route.
- **Fluorescence lifetime imaging (FLIM).** The current research direction
  for *absolute* membrane potential in *B. subtilis*. Requires time-resolved
  detection hardware on a confocal platform. Out of reach.
- **Confocal microscopy.** Same tier.
- **Patch clamp and single-cell electrophysiology.** Not applicable to
  bacteria at this scale anyway, and out of reach regardless.
- **Research-grade potentiostat EIS.** The Akabuogu et al. 2024 protocol
  assumes a real electrochemical workstation. There is one genuinely cheap
  exception worth naming honestly: AD5933-class impedance-converter modules
  are the basis of multiple published low-cost impedance systems (for
  example Kusche et al., four-electrode low-frequency impedance spectroscopy
  using the AD5933, PMID 23481406, and a portable AD5933 bioimpedance system
  in *Biomedical Engineering Advances*). Those are validated for
  bioimpedance, **not** for reproducing a biofilm negative-capacitance
  signature. Treating a $30 board as equivalent to the published protocol
  would be exactly the kind of unlabeled substitution this repo's rules
  forbid.
- **Microelectrode arrays (MEA).** Out of reach, and designed for
  electrogenic eukaryotic cells rather than this application.

---

## 7. Recommendation

1. **Take the electrical readout off the critical path for Stage 0.** The
   interference finding is not an argument for a cleverer voltmeter, it is an
   argument that the voltage interface is a later-stage research goal and not
   the thing that should gate the first experiment. Parts 12, 13, 17 and 18
   are a good-faith search for a fix, and the fix that survives is "do not
   read voltage yet."
2. **Run Stage 0 on the reporter, and add `lux` bioluminescence as the
   cheap continuous-monitoring channel alongside the fluorescence endpoint.**
   Fluorescence at a partner lab gives the bimodality evidence. A $40
   LuminoCell-class luminometer gives long-run switching kinetics on a home
   budget between lab visits. Neither substitutes for the other.
3. **Evaluate the integrase latch as a serious design alternative, not just
   as a citation.** It is the only mechanism on this list with measured
   multi-generation persistence in a real organism, which is precisely the
   open question this whole project rests on. It costs the project its
   "physiological state" framing. That trade should be made deliberately,
   with the founder deciding, not defaulted into either direction.
4. **Amend Part 10** with the Bonnet 2012 correction in section 5 above.

Items 1, 3 and 4 change project direction or published claims and are
therefore proposals, not actions taken. Nothing in the pitch materials,
`README.md`, or the audit's existing parts was edited to match this
document.

---

## Sources checked

- Gardner, Cantor & Collins (2000), *Nature* 403:339-342, DOI [10.1038/35002131](https://doi.org/10.1038/35002131)
- Bonnet, Subsoontorn & Endy (2012), *PNAS* 109(23):8884-8889, DOI [10.1073/pnas.1202344109](https://doi.org/10.1073/pnas.1202344109), PMID 22615351
- Cianflone, Keller, Subramaniam & Paternò (2026), *Frontiers in Photobiology* 4:1834373, DOI [10.3389/fphbi.2026.1834373](https://doi.org/10.3389/fphbi.2026.1834373)
- Weissová, Fafílek, Radaszkiewicz, Celiker, Macháčková, Čechová, Šebestíková, Hampl, Bryja, Krejčí & Bárta (2022), LuminoCell, *Life Science Alliance* 5(8):e202201421, DOI [10.26508/lsa.202201421](https://doi.org/10.26508/lsa.202201421), PMID 35440493
- Akabuogu, Zhang, Krašovec, Roberts & Waigh (2024), *Nano Letters* 24(7):2234-2241, DOI [10.1021/acs.nanolett.3c04446](https://doi.org/10.1021/acs.nanolett.3c04446), PMID 38320294 (already in this repo)
- Lundberg, Becker & Choe (2013), *PLoS ONE* 8(5):e60993, PMID 23737939 (already in this repo)
- Ford, Fisher, Prindle & Chopp (2021), *Bull Math Biol* 83(5):60, PMID 33856558 (already in this repo)
- Mulder et al. (2025), *PLOS Comput Biol* 21(12):e1013746, PMID 41343600 (already in this repo)
- Huang, Yu, Lee et al. (2025), *Nature Communications* 16:9414 (already in this repo)
- Han & Payne (2022, 2023), *Bioelectricity*, on probe-induced perturbation
- Kusche et al. (2013), AD5933 four-electrode impedance system, PMID 23481406
- Oxford Nanopore MinION product page, prices checked 20 September 2026
- Addgene plasmid [#38207](https://www.addgene.org/38207/) (RAD reset flipper)
