# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Acheron is a research project (not a deployed application) investigating whether
arbitrary binary data can be stored as a rewritable, self-healing bioelectric or
epigenetic state in living tissue, primarily *B. subtilis* bacteria and, less
confidently, planarian flatworms. There is no running service, API, or UI. The
deliverables are: Python simulations, a growing self-audit of what's actually
been proven vs. assumed, patent drafts, and investor/incubator pitch materials.

**Read `docs/SCIENTIFIC_AUDIT_2026.md` before writing anything that makes a
scientific or investor-facing claim.** It is the living, continuously-appended
source of truth for what's validated, what's assumed, and what's been found
wrong since the original pitch. Do not trust claims in the older docs
(`docs/INVESTOR_PITCH_PHASE2_UPDATE.md`, the `PHASE2`/`PHASE3`/`PHASE4` docs,
`docs/WHITEPAPER_Somatic_Morphogenetic_Memory.md`) without cross-checking them
against the audit first, several of the project's own early claims did not
survive later testing. `README.md` and `QUICKSTART.md` were rewritten from the
audit in September 2026 and are current; keep them that way when the audit
gains a part that changes the headline picture.

## Commands

```bash
python -m pytest tests/                              # unit tests (covers analysis/ only)
python -m pytest tests/test_hidden_state_model.py -q  # single test file
python simulations/bsubtilis_19_reservoir_benchmark.py     # runnable demo/experiment (no test framework; most of experiments/ works this way)
python simulations/bsubtilis_05_asymmetry_structural_search.py
```

There is no build/lint step. Dependencies are in `requirements.txt`, but a
fresh sandbox may not have them installed (`numpy`, `scipy`, `pytest` have all
been missing at session start before), install with `pip3 install <pkg>`
rather than assuming they're present.

## The core throughline (why the project looks the way it does)

**What Acheron is, in the founder's own words (confirmed 21 September 2026).**
Acheron is one hypothesis, not one organism: write bits into a living thing,
damage it, the organism detects that damage by itself, transfers the data into
its own regrowth, and the information is kept. The organism is interchangeable,
*B. subtilis*, planaria, or others later; *B. subtilis* is being tested first
because it is cheap and fast, not because planaria were abandoned. Self-detection
of damage is one of the four steps, not an optional extra. Sessions have drifted
into describing this as a *B. subtilis* voltage project with planaria dropped,
do not.


1. **Phase 1 claim:** planarian cells could passively hold an arbitrary
   voltage-encoded bit for 24+ hours (`simulations/planarian_01_bioelectric_persistence.py`).
2. **That claim broke under its own later scrutiny:** `simulations/
   planarian_02_noise_floor.py` showed the result only holds with zero
   noise; realistic biological noise collapses integrity to ~50% (a coin
   flip). This is documented, not hidden, in `docs/SCIENTIFIC_AUDIT_2026.md`
   Part 8.
3. **The pivot:** passive persistence isn't enough; an *actively engineered
   bistable circuit* is needed. `simulations/bsubtilis_01_gardner_toggle_circuit.py` models
   a Gardner-style genetic toggle switch (real topology, real *B. subtilis*
   BioBrick parts), and found a real design constraint: mismatched promoter
   strengths collapse the circuit to a monostable dead switch.
4. **Cross-organism honesty check:** `simulations/crossorganism_01_comparison_summary.py`
   ranks three candidate mechanisms by how much wet-lab risk each still
   hides. Result: the *B. subtilis* engineered circuit is currently the
   best-grounded option; the original planarian approach is the
   *weakest*-evidence option (its cell-coupling assumption has never been
   measured). This project has since been *B. subtilis*-first, with planaria
   as a less-grounded fallback, not the other way around.
5. **Readout is its own open problem:** `simulations/
   bsubtilis_08_native_oscillation_interference.py` and `bsubtilis_09_eis_readout_interference.py`
   found that *B. subtilis*'s own native potassium-wave signaling (real,
   published, unrelated to anything this project builds) can corrupt a
   voltage reading even when the underlying circuit data is intact.
   **But that framing is now contested by the project's own work:** audit
   Part 25 and `simulations/bsubtilis_18_phase_encoded_readout.py` (September 2026)
   found that if the bit is encoded as the cell's phase relationship to
   that oscillation rather than as a static voltage level, the oscillation
   becomes the carrier and the readout gets *better* as it gets stronger.
   The two encoding schemes have opposite failure modes and want opposite
   chassis strains (level encoding wants yugO weakened or deleted, phase
   encoding needs yugO intact), so this is a fork the project has to
   choose before committing to a strain, not a detail.
   **Weakened again by audit Part 26** (also September 2026): Part 25's
   phase result used an *imposed* sinusoid with the in-phase/anti-phase
   behaviour assumed. `simulations/bsubtilis_21_optical_write_replication.py`
   tried to derive that anti-phase from the potassium mechanism Yang et al.
   describe and could not, in a 12-point parameter sweep, for a structural
   reason. Phase encoding therefore rests on their published experiment plus
   an assumed coupling, with no working mechanistic model in this repo behind
   it. Reporter-first (Part 24) remains the recommendation.
6. **The one open question everything currently depends on:** does an
   engineered bistable circuit's state survive damage-and-regrowth
   (not just ordinary cell division)? Nobody has tested this in any
   organism. It's a defined, ~$10K-$30K, 6-12 month wet-lab experiment, not
   an open-ended unknown, see `docs/INVESTOR_PITCH.md`'s Roadmap section.

## Repo conventions specific to this project

- **No-numeric-invention rule** (`docs/THIRD_PARTY_METHODS.md`): any number
  used must trace to either a real citation, a labeled simulation result with
  its caveats stated, or be flagged as an open question. This project's
  credibility strategy is leading with rigor and self-correction, not hype,
  do not soften or round claims to sound more impressive.
- **`analysis/` and `third_party/`** contain methods adapted from published
  external work (tasmorpho, NeuromorphicMyceliumChip, ElectricMorphogenesis),
  cross-validated against the original implementations where possible, see
  `docs/THIRD_PARTY_METHODS.md` for exactly what's vendored vs. reimplemented
  and why.
- **`patents/`**. Three provisional applications were filed with the USPTO in
  2025 (Bio-RAID core system, self-healing recovery, environment-adaptive
  longevity). Per the founder (confirmed September 2026) they are filed and
  pending examination, so state IP status as "filed, pending examination," not
  "in progress." **Those three documents were removed from the working tree on
  21 September 2026 at the founder's explicit instruction, repeated after the
  record-keeping risk was raised.** Their text is still in git history; the
  applications themselves are unaffected by the deletion and remain pending. Do
  not restore the files without being asked, and do not describe the filings as
  withdrawn, because they are not.
  `patents/PATENT_GAP_ANALYSIS_2026.md` is still the document to bring to the
  patent attorney: a fabricated prior-art citation sat in filed Patent 1's
  Background, Bonnet 2012 and Süel 2020 are disclosed nowhere in the filings,
  and every independent claim recites planarian tissue and absolute-voltage
  encoding, all of which the project retired.
  `patents/drafts_2026/` holds the replacement drafts, written 21 September
  2026 and **not filed, not attorney-reviewed, no application numbers**: draft A
  (genetic bistable state surviving damage and regrowth through division-based
  inheritance, the strongest), draft B (damage-responsive reinforcement during
  regrowth), draft C (phase-referenced encoding, narrow, closest prior art).
  `patents/drafts_2026/PATENTABILITY_ASSESSMENT_2026.md` says what cannot be
  filed and why: absolute-voltage encoding in *B. subtilis* is anticipated by
  Yang et al. 2020, DNA-sequence storage by Yachie & Tomita 2007, DNA-orientation
  latches by Bonnet et al. 2012, and the environment-adaptive longevity subject
  has nothing measured behind it and should not be refiled. No claim in any
  draft recites a number, per the no-numeric-invention rule.
  **Open question nobody has answered:** whether `docs/BIORXIV_MANUSCRIPT.md`
  was ever posted to bioRxiv. The GitHub repo is private, so it is not a public
  disclosure, but a posted preprint is, and it would set a one year US filing
  deadline and very likely bar European novelty. Ask the founder before filing.
- **`experiments/BENCH_PROTOCOL_BSUBTILIS.md`** (added September 2026) is the
  bench-level *B. subtilis* protocol derived from the simulations and the
  audit: strain choice, BBB parts, stages B0-B6 in cheapest-first order,
  pass/fail thresholds, and an explicit list of simulated results the plan
  cannot test. It sits one level below
  `docs/pitch/Acheron_Validation_Proposal.docx` (which sets stages and costs)
  and is the *B. subtilis* counterpart to `experiments/BENCH_PROTOCOL_HEK293.md`
  (HEK293). Not yet reviewed by a collaborating lab; treat as a draft. It
  flags a real strain mismatch the simulations do not show: BBB promoter
  parts were characterized in W168, while the biofilm potassium-wave
  literature everything in the interference simulations rests on is NCIB
  3610, and those cannot both be used at once.
- **`docs/pitch/`** holds investor/incubator materials.
  `Acheron_Pitch_Deck.pptx` is the current deck (21 slides); its generator
  script is `docs/pitch/build_deck.js` (Node + pptxgenjs), edit that and
  rerun it, don't hand-edit the compiled `.pptx`. See the pptx skill's
  validate/QA workflow before shipping any rebuild.
  `Acheron_Hardware_Concept.pptx` (added September 2026) is a standalone
  6-slide deck of the sealed-cartridge-and-reader product concept, built
  from `docs/pitch/build_hardware_deck.js`. It exists because the founder
  wanted the hardware design on its own to show a partner and to have an
  answer ready if an investor asks what the product would be. Treat the
  cartridge and reader as a legitimate concept sketch to keep and show,
  not something to downplay, its slide 6 already states plainly that no
  prototype exists and that every result behind it is simulated. Same
  no-invented-numbers rule applies: the array size, dimensions and timings
  on it are labeled illustrative, the 2 percent survival figure is labeled
  a simulation result, and the spaceflight claim carries its citation.
  `Acheron_Plain_Explainer.pptx` (added 21 September 2026) is an 11-slide
  plain-language explainer of the whole project for a reader with no science
  background, built for co-founder Jacqueline Solano and meant to be printed,
  from `docs/pitch/build_explainer_deck.js`. It is not investor material and
  deliberately does not share the investor deck's palette or fonts. It carries
  the nine-sentence summary the founder signed off on, the "this was a
  simulation, not a laboratory" framing, the correction that 2 percent is the
  lowest survival level tested rather than a measured limit, and real funding
  comparables (NSF SBIR up to $305K Phase I, BioCompute's ~$37.7K total per
  Inc42, Catalog's $35M 2021 round) instead of an invented market size. Keep it
  that way if asked to update it.
  `Acheron_Validation_Proposal.docx` is the existing staged wet-lab funding
  ask (Stages 0-3, cost/time ranges, honest risk disclosure) that the
  crowdfunding drafts below are built from, don't re-derive its numbers.
  `EXPERIMENT_COM_CAMPAIGN.md` and `WEFUNDER_REPUBLIC_REG_CF_CAMPAIGN.md`
  (added September 2026) are draft campaign copy for rewards-based
  science crowdfunding and Reg CF equity crowdfunding respectively, not
  yet reviewed by the founder or (for the Reg CF one) a securities
  attorney; treat both as drafts pending that review, not as ready to
  publish.
- **Closest prior art, know this before making a novelty claim:** Yang,
  Bialecka-Fornal, Weatherwax, Larkin, Prindle, Liu, Garcia-Ojalvo & Süel
  (2020), *Cell Systems* 10(5):417-423, DOI 10.1016/j.cels.2020.04.002,
  already wrote arbitrary spatial patterns into a living *B. subtilis*
  biofilm's membrane potential with light, read them back non-destructively
  at single-cell resolution for over 3 hours, and framed it as digital
  memory for biological computing. Audit Part 25 covers what this does and
  does not take away. Do NOT write "nobody has stored data as a bioelectric
  state" into any investor-facing document. The claim that survives is
  narrower: their memory is a protein-level modification that would not
  survive cell division, and surviving division is this project's actual
  differentiator.
- **Never invent or carry forward unverified personal/biographical facts about
  the founders** (name, school, background) into any document without an
  explicit confirmation in the current conversation. This has happened once
  already: an older file, `partnerships/ORLANDO_LAB_PARTNERSHIPS.md`, frames
  the founder as "a UCF cybersecurity student" in its section headers and
  draft outreach emails, a claim never confirmed and since removed from the
  pitch deck and `docs/INVESTOR_PITCH.md`. That file itself has NOT been
  fixed yet, ask the founder whether to correct it before sending any of its
  draft emails or reusing its framing.
- **Writing style for anything produced for the founder** (docs, decks,
  emails): no em dashes, ever, use a comma or period instead. This has been
  requested repeatedly and firmly. Also avoid meta-commentary in
  investor-facing material, i.e. don't narrate the document's own edit
  history or reasoning to the reader (no "(original pitch)" labels, no
  "why this document leads with X" sections); write only what the external
  audience needs, keep process/reasoning notes in chat or in this file.
- **Founders:** Dayana Sanchez (Founder & Lead Researcher, originated the
  concept, does the technical work) and Jacqueline Solano (Co-Founder,
  business operations, satisfies a US-citizen-founder requirement for some
  accelerator programs).
- **Sandbox quirk:** LibreOffice's `soffice --convert-to pdf` has been
  observed failing on *any* input file in this environment (not specific to
  a given `.pptx`), so visual/pixel QA of decks isn't reliably available.
  Rely on `scripts/office/validate.py` (schema/structure) and a full
  `markitdown` text-dump read-through instead, and say so explicitly rather
  than claiming a visual check that didn't happen.
- **Git workflow, permanent rule (confirmed September 2026, do not ask
  again):** commit and push everything directly to `main`. Do not create
  feature/side branches. If a session is forced onto a branch other than
  `main` by the harness/environment it's running in, merge that branch
  into `main` and push `main` before finishing, that override doesn't
  change this rule.
- **Scope discipline:** when a task says "read X" or "understand this
  feedback," that means read and report back, not implement changes off
  your own read of what the feedback implies. Don't take action beyond
  what was actually asked, confirming a follow-up question mid-task isn't
  the same as being asked for that follow-up in the first place. If the
  next step seems obvious, say what you'd do and let the founder say go.

## Repository layout (reorganised September 2026)

Read `docs/REASONING_MAP.md` first in any new session. It is the one page that
explains how the project connects, what is proven versus assumed versus
disproven, and where to start reading.

- **`simulations/`** holds every simulation of a scientific claim, named
  `<organism>_<number>_<topic>.py`, in four tracks: `planarian_`, `bsubtilis_`,
  `methylation_`, `crossorganism_`. The number is reading order within that
  track, roughly chronological, so the folder reads as a story. **Do not rename
  or renumber these without updating every reference**, they are cited by name
  throughout `docs/SCIENTIFIC_AUDIT_2026.md`, `CODEMAP.md` and the bench
  protocols. Append new work at the end of its track rather than renumbering.
- **`simulations/SIMULATION_MAP.md`** explains every simulation twice, once in
  plain English and once technically, with its audit Part number. Add an entry
  when adding a simulation.
- **`experiments/`** holds bench protocols ONLY, no Python. Currently
  `BENCH_PROTOCOL_BSUBTILIS.md` (primary, stages B0-B6) and
  `BENCH_PROTOCOL_HEK293.md`. Neither has been reviewed by a lab.
- **`tools/`** holds demos, optimisers, parameter sweeps and validation
  harnesses, i.e. supporting machinery that is not a claim about biology.
- **`hardware/`** is empty and is a placeholder. There is no hardware. The
  cartridge-and-reader concept exists only as a pitch-deck slide, so do not
  describe it as built.

## CodeMap Protocol

`CODEMAP.md` (project root) is a structural reference for `analysis/`,
`encoder/`, `simulations/`, `experiments/`, `tests/`,
`third_party/electric_morphogenesis/`, `docs/pitch/build_deck.js`,
`docs/pitch/build_hardware_deck.js`, and
`NEXT_STEPS.py`, not a replacement for reading the source.

- At the start of a task, read only the `CODEMAP.md` section(s) relevant to
  it, not the whole file.
- Before modifying a symbol documented there, verify its current
  implementation in the source file, the source is always authoritative if
  the two disagree.
- After adding, deleting, or materially changing an architecturally
  meaningful symbol (a class, or a function that's either an entry point or
  imported by another module), update its `CODEMAP.md` entry. Trivial
  local-variable-level changes don't need an update.
- `CODEMAP.md` must be committed together with the structural code change
  that prompted the update, not separately.
- If the repository grows past 150 source files or gains a genuinely
  separate service/app, re-map incrementally per unit (see `CODEMAP.md`'s
  own header for why it was mapped in one pass at 44 files) rather than
  regenerating the whole file at once.

## Next steps (as of September 2026, so a new session doesn't have to re-derive this)

1. **Decide on `partnerships/ORLANDO_LAB_PARTNERSHIPS.md`**: still contains
   the unconfirmed "UCF cybersecurity student" framing throughout, including
   in ready-to-send draft outreach emails to UCF faculty. Ask the founder
   whether to strip/rewrite it before it's used.
2. **The wet-lab experiment is the actual next milestone** for the science
   (see throughline item 6 above), everything else is downstream of it.
3. **Pitch deck is current and was heavily iterated** across several
   sessions (founder info, patent status, competitor framing, tone,
   external reviewer feedback) and again in September 2026 to fold in a
   batch of new simulation results: it now has 21 slides. Added since the
   19-slide version: a "Cleaner Readout" slide on the fluorescent
   GFP/RFP reporter finding (tracks the genetic state exactly, including
   through simulated damage/regrowth, and sidesteps the voltage-readout
   interference problem by mechanism, not luck), and a "What This
   Becomes" hardware-concept slide (the sealed cartridge + reader
   device, cites real B. subtilis spaceflight survival precedent,
   Deshevaya et al. 2024, Wassmann et al. 2012). The Roadmap slide was
   corrected from the old single combined $10K-$30K experiment to the
   already-established four-stage plan (Stage 0 first, ~$2K-$5K,
   matching `docs/INVESTOR_PITCH.md` and `docs/pitch/
   Acheron_Validation_Proposal.docx`), which the deck had drifted out of
   sync with; the Ask slide and the "simulated vs. measured" slide's
   dollar figure were updated to match. Jacqueline Solano's team-slide
   bio is still a single line by the founder's explicit choice (asked and
   declined to expand it beyond already-confirmed facts as of September
   2026), not an oversight. If asked to update the deck again, start from
   `docs/pitch/build_deck.js`, not from scratch, and rerun the pptx skill's
   validate + markitdown text-dump QA before sending, the founder has
   flagged small wording/tone issues multiple times and wants a careful
   read-through, not a fast turnaround.
4. **`CODEMAP.md` now exists** (created September 2026, single-pass, 44
   source files). Keep it updated per the CodeMap Protocol above rather than
   letting it drift, and re-map incrementally if the repo passes 150 files.
