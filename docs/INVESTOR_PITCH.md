# Acheron: Self-Healing Bioelectric Memory
## Persistent, Regenerative Data Storage in Living Cells

**Pitch Narrative, Updated September 2026**

*This replaces the December 2025 version of this document. That version cited
"24hr pattern persistence" and "<1% bit error rate" as simulation proof
points. Acheron's own later noise-floor testing (see
`docs/SCIENTIFIC_AUDIT_2026.md`, Part 8) found those numbers only hold in a
zero-noise simulation; under realistic biological noise, integrity collapses
toward a coin flip. This document is written to be defensible under
technical due diligence, every claim below is either a cited fact, a
clearly-labeled simulation result with its caveats, or a clearly-labeled
open question. Nothing here should be softened to sound more impressive;
that already backfired once in this project's history.*

---

## The Problem

Every commercial biocomputing product today uses **neurons** as the
computing substrate:

| Company | Substrate | Lifespan | Price |
|---|---|---|---|
| Cortical Labs | Human neurons on silicon (CL-1) | 6 months | $35,000/unit |
| Koniku | Neuron-silicon sensing chips | ~2 years | Not public |
| FinalSpark | Brain organoids | Not public | Cloud access only |

Neurons are excitable cells: they need continuous energy to hold a signal,
they degrade on a fixed clock, and none of them regenerate. That's fine for
fast computation. It's a bad fit for **long-duration, low-maintenance
storage**, the kind needed on a spacecraft, a seafloor sensor, or any
system nobody can walk up to and repair.

## The Idea

Some organisms maintain voltage patterns across their tissue for long
periods without active energy input, and can **regrow the tissue itself**
after physical damage. Michael Levin's lab (Tufts) demonstrated this in
planarian flatworms: cut one in half, and the bioelectric pattern that
determines "this end grows a head" survives the cut and gets faithfully
rebuilt in both halves, sometimes even when researchers deliberately
altered it (his lab's two-headed-worm result). That's a real, published,
frequently-replicated finding.

**Acheron's question:** can that same kind of biological system, voltage
state plus a strong regenerative/inheritance mechanism, be used to store
*arbitrary* binary data, not just the organism's own natural body-plan
signal? If yes, that's a memory substrate that needs no power to hold its
state and can survive and repair physical damage that would destroy silicon
or kill a neuron culture outright.

## The Full Goal (Storage Is Step One, Not the Finish Line)

Being clear about scope: writing a bit into a cell's voltage state is only
the first of three things this has to do to be useful as real memory:

1. **Write** a bit into the cell's engineered voltage state.
2. **Transfer on split.** When the organism naturally regenerates or
   divides, the written data travels with it into the new organism, not
   just its genetic material, the state itself.
3. **Self-heal for reuse.** The original cell/colony recovers to a clean
   baseline afterward, so it can be written to again rather than being a
   one-time-use component.

**In plain English:** a living cell is a reusable notebook. Writing a bit
is a pencil note in it. The organism splitting or regrowing is like
photocopying the notebook, so the new notebook already has the note copied
in. Self-healing is the original notebook erasing its own note so it's
ready to write a new one.

This full cycle is genuinely hard to test computationally, which is exactly
why it's framed here as the goal the roadmap experiment works toward, not a
claim being made today. The closest thing to a working model of it already
exists in this project's own simulations: `simulations/biofilm_tile_handoff.py`
implements a write, then `propagate_handoff()` (transfer to a new tile),
then `reset_and_heal()` (the original tile clears back to baseline and
becomes reusable) cycle, and `experiments/handoff_pool_imperfect_healing.py`
stress-tests it across many reuse cycles. What it does not yet test is the
harder version: whether an *engineered bistable circuit's* state (the fix
described below) survives that same handoff-and-heal cycle, as opposed to
the simpler passive-voltage tile model it currently uses.

## What We Actually Know So Far (and What We Don't)

This is the section most pitch decks skip. We think it's the reason to take
this one seriously.

**What's real, independent of us:**
- Bioelectric control of body-plan patterning in planaria is real,
  published, and reproduced across multiple labs (Levin et al., multiple
  papers 2006–2023).
- Engineered genetic bistability, a synthetic circuit that holds one of
  two states indefinitely once flipped, is a solved, 25-year-old result in
  a different organism: Gardner, Cantor & Collins built exactly this in
  *E. coli* in 2000 (*Nature*), explicitly describing it as an addressable
  cellular memory unit.
- Non-destructive electrical readout of living bacterial biofilm state is
  real and recent: Akabuogu et al. (2024, *Nano Letters*) showed a simple
  two-electrode impedance measurement distinguishes live from dead biofilm,
  tied to a specific ion channel's activity, a candidate low-cost readout
  mechanism.

**What we found by actually testing our own assumptions, not just citing
others' (full detail in `docs/SCIENTIFIC_AUDIT_2026.md`):**
- Our first-pass simulation's headline result (patterns hold for 24+ hours
  with near-zero error) only holds with zero noise. Add realistic
  biological noise sources (channel noise, metabolic fluctuation,
  cell-to-cell variability) and it decays toward chance within hours. This
  was our own finding, from our own code, and we're leading with it rather
  than burying it.
- The fix is identifiable and specific: passive bioelectric persistence
  isn't enough; the system needs an **actively engineered bistable
  circuit** (Gardner-style), not just "cells doing what cells naturally
  do." We modeled this circuit (`simulations/gardner_toggle_circuit.py`)
  using real, chassis-matched, already-characterized genetic parts (the
  Bacillus BioBrick Box), and it holds state reliably in simulation, with
  one concrete, previously-hidden design constraint surfaced: the two
  promoters driving the circuit must be closely matched in strength, or the
  circuit isn't bistable at all, just monostable and useless as a switch.
- We ran a **cross-organism comparison** most projects never bother to run
  honestly against their own preferred organism: at identical simulated
  damage/regrowth conditions, an engineered circuit in *B. subtilis*
  (bacteria) is currently the best-grounded path (its inheritance mechanism
 , cell division copying existing protein, is mechanistically forced, not
  a modeling assumption), a DNA-methylation-based mechanism in the same
  organism is medium-confidence (real fidelity numbers exist, but only from
  a different species), and the original planarian-circuit approach is
  currently the least-grounded of the three (the cell-coupling strength in
  our planarian model is a borrowed assumption, never measured in real
  planarian tissue). **We are reporting this even though it means our
  original organism choice is currently our weakest-evidence option**,
  because knowing that now, before spending wet-lab money, is the entire
  point of doing the simulation work first.
- We also found and are reporting a specific new risk before anyone asked
  about it: *B. subtilis* biofilms have their own natural electrical
  signaling (a potassium-wave mechanism, published by the Prindle lab,
  2015) that runs continuously regardless of anything we build, and our
  simulation shows it can corrupt an instantaneous voltage reading even
  when the underlying engineered circuit's data is completely intact. This
  is a solvable engineering problem (timing the read around the natural
  oscillation, or using the impedance-based readout instead of raw
  voltage), not a fatal one, but it's the kind of thing that only surfaces
  from actually building and stress-testing the model.

**The one open question everything else depends on:**
Does an engineered bistable circuit, once built in a living cell that also
has strong regenerative/inheritance properties, actually hold a
*non-natural* data pattern through damage and regrowth, not just through
normal cell division? Nobody has tested this in any organism. It is a
defined, falsifiable, relatively cheap experiment (see Roadmap), not an
open-ended unknown.

## Why This Matters Commercially

Extreme-environment computing, spacecraft, deep-sea systems, remote
infrastructure, has one hard, recurring requirement that silicon and
neuron-based biocomputing both fail differently: **nobody can service the
hardware in person.** Silicon degrades under radiation with no self-repair.
Neuron-based systems need continuous life support and a fixed replacement
cycle. A substrate that holds state without power and can regrow after
physical damage is a different category of answer to the same problem, if
it can be made to work reliably.

**We are deliberately not inventing an Acheron-specific TAM or revenue
forecast**, every number in earlier versions of this pitch was invented,
not sourced, and we'd rather show up with two real, externally-verifiable
numbers than a spreadsheet that doesn't survive a follow-up question:

- **What customers already pay for the closest existing alternative:**
  Cortical Labs' CL-1 (neuron-based) sells for $35,000/unit and needs
  replacing every 6 months, roughly $350K over 5 years per unit, with zero
  self-repair. That's a live, public data point for what this market
  already tolerates paying to avoid downtime, even from a substrate that
  can't heal itself.
- **The adjacent, independently-tracked market:** radiation-hardened space
  electronics is sized at roughly $1.2B-$2.0B in 2026 across analyst
  estimates (Grand View Research, Fortune Business Insights, Research and
  Markets), growing at ~4-5.6% CAGR into the early 2030s, driven largely by
  LEO satellite constellations (Starlink, Kuiper, OneWeb) needing more
  radiation-tolerant memory and processors. We are not claiming Acheron
  captures any specific share of that market, we're citing it as evidence
  the underlying need (radiation-tolerant, low-maintenance memory) is real,
  tracked by independent analysts, and growing, not a market we made up to
  justify the pitch.

**The honest framing: this upside is entirely conditional on the roadmap
experiments below succeeding.** We're not asking anyone to price that risk
in advance, we're asking for the ~$2K-$5K it costs to fund Stage 0 and find
out whether the core circuit even works.

## Why This Is Different From Every Real Competitor We Found

Only two real, closer competitors exist for what Acheron actually is, a
dynamic, rewritable, self-healing bioelectric memory (see
`docs/COMPETITIVE_ANALYSIS.md` update, August 2026). A third group, neuron-
based wetware companies, gets mentioned constantly in this space but isn't
actually competing for the same thing, and it's worth being precise about
why:

- **Adjacent research, not a competitor: Cortical Labs (CL-1), Koniku.**
  Both build neuron-based wetware for cognition and sensing tasks (playing
  games, detecting explosives, training AI), a different product category
  from memory storage, so not a rival product. Their hardware is still
  worth studying: CL-1 uses high-density electrode arrays (HD-MEAs) to
  write and read electrical signals into living tissue bidirectionally, a
  mature solution to a problem Acheron also has. Koniku holds a real patent
  (JP6858769) for an electrode design that improves signal-to-noise ratio
  when recording from neurons, directly relevant to the native-oscillation
  readout problem this project's own audit found. (One thing not to
  overclaim: Koniku's marketing describes "high redundancy, stable power
  consumption, operation in noisy environments," but that specific claim
  wasn't independently verifiable against a technical source, treat it as
  a company claim, not a confirmed result, if it comes up.) FinalSpark is
  the same category (neuron organoids for AI), with no comparably specific
  technical lead found.
- **Mycelium memristor (LaRocco et al. 2025):** the closest published
  *self-healing* bioelectric device, real, and genuinely impressive
  (90±1% accuracy, survives dehydration/rehydration). But it's an **analog**
  device: one continuous resistance value, with no addressable write
  layer, you can't target "bit #47" the way a real memory needs. And 90%
  accuracy is a disqualifying error rate for binary storage (a memory wrong
  1 time in 10 is not usable as memory). Acheron is targeting an
  addressable, individually-writable/readable bit architecture, not a
  continuous analog signal.
- **DNA-sequence storage (BioCompute Inc. and Biomemory, building on
  Yachie & Tomita 2007):** real, funded, and gaining ground fast, Biomemory
  acquired Catalog Technologies in 2026 and is targeting a commercial,
  end-to-end DNA data storage launch by the end of the year. Both already
  store arbitrary data in a living organism's genome. But it's **archival**:
  written once, read only by destructive sequencing, closer to etching a
  record you can only read by destroying the copy than to a working memory
  you check and update in place. Acheron is solving a different
  engineering problem on purpose: a **dynamic, rewritable,
  non-destructively-readable** physiological state, not a write-once
  archive. If the bioelectric approach doesn't pan out, this category is
  worth revisiting as a fallback, but it trades this project's current
  open question (does a bioelectric state hold under noise) for a
  different one specific to genome editing in the target organism, not a
  shortcut past having an open question at all.

## Roadmap: Four Staged Experiments, Not One Combined Bet

Earlier versions of this roadmap asked for one combined experiment, build
the circuit, damage the colony, regrow it, and read the result back with
electrical impedance spectroscopy, all in a single $10K-$30K ask. That
bundled three separate open questions (does the circuit hold two states at
all, does the state survive damage and regrowth, and does the electrical
readout work) into one pass/fail result. Per our own audit
(`docs/SCIENTIFIC_AUDIT_2026.md`, Parts 13 and 15) and the full staged plan
in `docs/pitch/Acheron_Validation_Proposal.docx`, we've split it into four
independent, cheaper stages, each a clean go/no-go gate:

| Stage | Question answered | Est. cost | Est. time |
|---|---|---|---|
| 0 — *B. subtilis* toggle confirmation | Does the matched-promoter Gardner-style toggle circuit (Bacillus BioBrick Box parts) actually show two stable, switchable states, read with a simple reporter assay (lacZ/lux), no electrical readout involved yet? | $2K–$5K | 6–10 weeks |
| 1 — HEK293 gap-junction persistence | Do arbitrary voltage patterns persist 24h+ in a fast, simple gap-junction-coupled culture? | $2.4K–$10K | 3–6 months |
| 2 — Planarian minimal viable experiment | Do arbitrary patterns persist in the target regenerative organism, including damage and regrowth? | $10K–$30K | 6–12 months |
| 3 — Voltage-interface build | Can the toggle circuit's repressor output be coupled to a real, measurable membrane-voltage bit, and read back non-destructively? | To be scoped with a synthetic-biology partner | TBD |

We recommend funding Stage 0 first: it's the fastest, cheapest way to test
the single design constraint (promoter matching) our own circuit simulation
flagged as make-or-break, using parts that already exist and are free to
obtain, and it deliberately avoids the electrical-readout problem entirely
by using a reporter assay instead. Stage 3 is scoped last and separately on
purpose: our own follow-up simulation (Part 13) found that a single
electrical-impedance reading of the circuit's voltage state does not
survive the biofilm's own native potassium-wave signaling unless the
reading is integrated over close to a full oscillation cycle (roughly
three hours), a real design constraint for that stage specifically, not a
reason to avoid it, but a reason not to fund it before Stage 0 confirms the
underlying circuit even works.

A negative result at any stage is a fast, cheap answer that redirects
effort, not a wasted spend, see the full success criteria and honest risk
disclosure in `docs/pitch/Acheron_Validation_Proposal.docx`.

## What We're Looking For, Deliberately Small, Not a Seed Round

We are not raising a general-purpose seed round right now. What this stage
actually needs is narrower and cheaper than that:

1. **Funding for Stage 0** described above (~$2K-$5K: reagents, plasmid
   synthesis/cloning, a lab partnership providing bench access), the
   fastest, cheapest gate on the whole roadmap, with the later stages
   funded separately once each prior gate passes.
2. **Budget to hire a paid synthetic-biology / genetic-circuit design
   consultant**, someone with real hands-on expertise to review and help
   execute the toggle-circuit build, not just informal mentoring hours. We
   would rather pay for a few weeks of a real expert's time than move
   forward on a design nobody with domain experience has pressure-tested.
3. **Lab access / partnership introductions** for standard bacterial
   transformation and plasmid cloning, this does not require
   planarian-specific expertise, which is a much rarer skill than standard
   synthetic biology in *B. subtilis*, a workhorse organism.

Non-dilutive funding pathways (grants, prizes) sized to items 1-2 above are
a good fit for where this project actually is, not a large speculative
raise priced against an unvalidated mechanism.

## IP Status

Patent applications have been filed with the USPTO covering the Bio-RAID
fault-tolerance architecture, the self-healing recovery protocol, and the
environment-adaptive longevity system (see `patents/` for the three
underlying documents). Status: filed / pending examination.

## Team

**Dayana Sanchez, Founder & Lead Researcher.** Originated the core
concept and has led all technical work to date: the simulation
architecture, the encoder software, and the audit process that found and
corrected this project's own central assumption before anyone outside the
project did.

**Jacqueline Solano, Co-Founder.** Leads business operations, and
satisfies the program's requirement that at least one founder be a U.S.
citizen.

---

**Contact:** Dayana Sanchez, sanchezleal1989@gmail.com | Jacqueline Solano,
jackiea.solano@gmail.com
**Repository:** github.com/rewired89/Acheron (open, includes the full
simulation code, the audit that found our own result didn't hold up, and
the corrected path forward)

*This document intentionally leads with what we got wrong and how we found
out, because that process is the actual asset here, not a projection
nobody could verify.*
