# Acheron: Self-Healing Bioelectric Memory
## Persistent, Regenerative Data Storage in Living Cells

**Pitch Narrative — Updated September 2026**

*This replaces the December 2025 version of this document. That version cited
"24hr pattern persistence" and "<1% bit error rate" as simulation proof
points. Acheron's own later noise-floor testing (see
`docs/SCIENTIFIC_AUDIT_2026.md`, Part 8) found those numbers only hold in a
zero-noise simulation; under realistic biological noise, integrity collapses
toward a coin flip. This document is written to be defensible under
technical due diligence — every claim below is either a cited fact, a
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
storage** — the kind needed on a spacecraft, a seafloor sensor, or any
system nobody can walk up to and repair.

## The Idea

Some organisms maintain voltage patterns across their tissue for long
periods without active energy input, and can **regrow the tissue itself**
after physical damage. Michael Levin's lab (Tufts) demonstrated this in
planarian flatworms: cut one in half, and the bioelectric pattern that
determines "this end grows a head" survives the cut and gets faithfully
rebuilt in both halves — sometimes even when researchers deliberately
altered it (his lab's two-headed-worm result). That's a real, published,
frequently-replicated finding.

**Acheron's question:** can that same kind of biological system — voltage
state plus a strong regenerative/inheritance mechanism — be used to store
*arbitrary* binary data, not just the organism's own natural body-plan
signal? If yes, that's a memory substrate that needs no power to hold its
state and can survive and repair physical damage that would destroy silicon
or kill a neuron culture outright.

## What We Actually Know So Far (and What We Don't)

This is the section most pitch decks skip. We think it's the reason to take
this one seriously.

**What's real, independent of us:**
- Bioelectric control of body-plan patterning in planaria is real,
  published, and reproduced across multiple labs (Levin et al., multiple
  papers 2006–2023).
- Engineered genetic bistability — a synthetic circuit that holds one of
  two states indefinitely once flipped — is a solved, 25-year-old result in
  a different organism: Gardner, Cantor & Collins built exactly this in
  *E. coli* in 2000 (*Nature*), explicitly describing it as an addressable
  cellular memory unit.
- Non-destructive electrical readout of living bacterial biofilm state is
  real and recent: Akabuogu et al. (2024, *Nano Letters*) showed a simple
  two-electrode impedance measurement distinguishes live from dead biofilm,
  tied to a specific ion channel's activity — a candidate low-cost readout
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
  Bacillus BioBrick Box), and it holds state reliably in simulation — with
  one concrete, previously-hidden design constraint surfaced: the two
  promoters driving the circuit must be closely matched in strength, or the
  circuit isn't bistable at all, just monostable and useless as a switch.
- We ran a **cross-organism comparison** most projects never bother to run
  honestly against their own preferred organism: at identical simulated
  damage/regrowth conditions, an engineered circuit in *B. subtilis*
  (bacteria) is currently the best-grounded path (its inheritance mechanism
  — cell division copying existing protein — is mechanistically forced, not
  a modeling assumption), a DNA-methylation-based mechanism in the same
  organism is medium-confidence (real fidelity numbers exist, but only from
  a different species), and the original planarian-circuit approach is
  currently the least-grounded of the three (the cell-coupling strength in
  our planarian model is a borrowed assumption, never measured in real
  planarian tissue). **We are reporting this even though it means our
  original organism choice is currently our weakest-evidence option** —
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
*non-natural* data pattern through damage and regrowth — not just through
normal cell division? Nobody has tested this in any organism. It is a
defined, falsifiable, relatively cheap experiment (see Roadmap), not an
open-ended unknown.

## Why This Matters Commercially

Extreme-environment computing — spacecraft, deep-sea systems, remote
infrastructure — has one hard, recurring requirement that silicon and
neuron-based biocomputing both fail differently: **nobody can service the
hardware in person.** Silicon degrades under radiation with no self-repair.
Neuron-based systems need continuous life support and a fixed replacement
cycle (Cortical Labs' own CL-1 pricing — $35K every 6 months — is a direct,
public illustration of that cost structure). A substrate that holds state
without power and can regrow after physical damage is a different category
of answer to the same problem, if it can be made to work reliably.

We are not going to put a specific TAM/revenue forecast in this document.
Every number we drafted for that in earlier versions of this pitch was
invented, not sourced, and we'd rather show up with a credible technical
story than a spreadsheet that doesn't survive a follow-up question.

## Roadmap: The One Experiment That Changes Everything

Per our own audit's conclusion, this is the actual next step, not a general
research program:

**Experiment:** Build the matched-promoter Gardner-style toggle circuit
(using the already-characterized Bacillus BioBrick Box parts our simulation
identified) in *B. subtilis*, write a bit, damage the colony, let it regrow
from survivors, and measure whether the bit reads back correctly —
non-destructively, using electrical impedance spectroscopy as the readout
method.

- **Cost:** ~$10K–$30K (reagents, plasmid synthesis/cloning, a lab
  partnership providing bench access and culturing expertise)
- **Timeline:** 6–12 months
- **Outcome:** Either validates the core mechanism (clear path to a
  multi-bit prototype) or falsifies it cleanly (redirect to the
  methylation-based mechanism, which is next in line by our own confidence
  ranking)

This is deliberately the cheapest, fastest experiment that produces a real
yes/no answer — not a moonshot ask.

## What We're Looking For From an Incubator Program

- **Lab access / partnership introductions** for basic molecular biology
  work (bacterial transformation, plasmid cloning) — this does not require
  planarian-specific expertise, which is a much rarer skill than standard
  synthetic biology in *B. subtilis*, a workhorse organism.
- **Technical mentorship** from people with real synthetic-biology/genetic
  circuit design experience, to pressure-test the toggle-circuit design
  before it's built.
- **Non-dilutive funding pathways** (grants, prizes) sized to the actual
  experiment above, not a large speculative raise.

## IP Status (Stated Plainly)

A patent strategy and draft applications exist internally (see
`docs/PATENT_STRATEGY.md`, `patents/`), covering the Bio-RAID
fault-tolerance architecture and self-healing recovery protocol. **As of
this writing, no provisional or utility patent application has been
confirmed filed with the USPTO** — the existing documents are drafted
strategy, not filing receipts. This section will be corrected the moment
that status changes; we're not going to claim "patent pending" in a formal
application until it's true.

## Team

**Founder:** [background: cybersecurity, UCF] — brings computational
modeling, error-correction/fault-tolerance system design, and the
discipline of red-teaming your own claims before someone else does. Not a
biologist by training, which is disclosed here as a fact, not hidden — the
technical partnerships this program would help unlock are exactly how that
gap gets closed.

---

**Contact:** sanchezleal1989@gmail.com
**Repository:** github.com/rewired89/Acheron (open — includes the full
simulation code, the audit that found our own result didn't hold up, and
the corrected path forward)

*This document intentionally leads with what we got wrong and how we found
out, because that process is the actual asset here — not a projection
nobody could verify.*
