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
(`README.md`, `docs/INVESTOR_PITCH_PHASE2_UPDATE.md`, the `PHASE2`/`PHASE3`/
`PHASE4` docs) without cross-checking them against the audit first, several
of the project's own early claims did not survive later testing.

## Commands

```bash
python -m pytest tests/                              # unit tests (covers analysis/ only)
python -m pytest tests/test_hidden_state_model.py -q  # single test file
python experiments/reservoir_benchmark_gardner.py     # runnable demo/experiment (no test framework; most of experiments/ works this way)
python experiments/asymmetry_structural_search.py
```

There is no build/lint step. Dependencies are in `requirements.txt`, but a
fresh sandbox may not have them installed (`numpy`, `scipy`, `pytest` have all
been missing at session start before), install with `pip3 install <pkg>`
rather than assuming they're present.

## The core throughline (why the project looks the way it does)

1. **Phase 1 claim:** planarian cells could passively hold an arbitrary
   voltage-encoded bit for 24+ hours (`simulations/bioelectric_persistence.py`).
2. **That claim broke under its own later scrutiny:** `simulations/
   noise_floor_characterizer.py` showed the result only holds with zero
   noise; realistic biological noise collapses integrity to ~50% (a coin
   flip). This is documented, not hidden, in `docs/SCIENTIFIC_AUDIT_2026.md`
   Part 8.
3. **The pivot:** passive persistence isn't enough; an *actively engineered
   bistable circuit* is needed. `simulations/gardner_toggle_circuit.py` models
   a Gardner-style genetic toggle switch (real topology, real *B. subtilis*
   BioBrick parts), and found a real design constraint: mismatched promoter
   strengths collapse the circuit to a monostable dead switch.
4. **Cross-organism honesty check:** `simulations/organism_comparison_summary.py`
   ranks three candidate mechanisms by how much wet-lab risk each still
   hides. Result: the *B. subtilis* engineered circuit is currently the
   best-grounded option; the original planarian approach is the
   *weakest*-evidence option (its cell-coupling assumption has never been
   measured). This project has since been *B. subtilis*-first, with planaria
   as a less-grounded fallback, not the other way around.
5. **Readout is its own open problem:** `simulations/
   native_oscillation_interference.py` and `eis_readout_interference.py`
   found that *B. subtilis*'s own native potassium-wave signaling (real,
   published, unrelated to anything this project builds) can corrupt a
   voltage reading even when the underlying circuit data is intact.
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
- **`patents/`** holds the three filed patent documents (Bio-RAID core
  system, self-healing recovery, environment-adaptive longevity). Per the
  founder (confirmed September 2026), these have been filed with the USPTO,
  state IP status as "filed, pending examination," not "in progress."
- **`docs/pitch/`** holds investor/incubator materials.
  `Acheron_Pitch_Deck.pptx` is the current deck (19 slides); its generator
  script is `docs/pitch/build_deck.js` (Node + pptxgenjs), edit that and
  rerun it, don't hand-edit the compiled `.pptx`. See the pptx skill's
  validate/QA workflow before shipping any rebuild.
  `Acheron_Validation_Proposal.docx` is the existing staged wet-lab funding
  ask (Stages 0-3, cost/time ranges, honest risk disclosure) that the
  crowdfunding drafts below are built from, don't re-derive its numbers.
  `EXPERIMENT_COM_CAMPAIGN.md` and `WEFUNDER_REPUBLIC_REG_CF_CAMPAIGN.md`
  (added September 2026) are draft campaign copy for rewards-based
  science crowdfunding and Reg CF equity crowdfunding respectively, not
  yet reviewed by the founder or (for the Reg CF one) a securities
  attorney; treat both as drafts pending that review, not as ready to
  publish.
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

## CodeMap Protocol

`CODEMAP.md` (project root) is a structural reference for `analysis/`,
`encoder/`, `simulations/`, `experiments/`, `tests/`,
`third_party/electric_morphogenesis/`, `docs/pitch/build_deck.js`, and
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
3. **Pitch deck is current and was heavily iterated** this session (founder
   info, patent status, competitor framing, tone) and again in a later
   session (September 2026) to act on external reviewer feedback: it now
   has 19 slides, adding an unmissable "simulated vs. measured" disclosure
   slide near the front, a B. subtilis-vs-E. coli chassis-justification
   slide, a biosafety/containment slide, a qualitative (not numeric) risk
   confidence visual on the risk-ranking slide replacing a bar chart that
   showed three identical bars, and a market slide reframed to explicitly
   disclaim being a market-size estimate. Jacqueline Solano's team-slide
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
