# Building a Stable On/Off Switch Inside Living Bacteria

**Draft campaign copy for Experiment.com. Written to that platform's standard section
structure so it can be pasted into a new project with minimal editing. Confirm current
Experiment.com funding-model mechanics (all-or-nothing vs. flexible funding, fee
structure, minimum campaign length) against the platform's live terms before publishing,
since those have changed over time and are not something to assume from this draft.**

---

## One-line summary

Testing whether a real, freely available synthetic-biology circuit design creates two
stable, switchable genetic states in living *Bacillus subtilis*, the first wet-lab test
from a computational research project into engineered biological memory.

## Funding goal

- **Base goal: $5,000** — funds Stage 0 below in full.
- **Stretch goal: $15,000** — funds Stage 0 and begins Stage 1, a second, independent
  test of a related open question in a faster-growing mammalian cell line.

Both figures are drawn directly from the cost ranges in our internal validation
proposal (below), not invented for this campaign. A lab partner will provide an
itemized quote before any funds are drawn down.

---

## Overview

Acheron is a research project asking whether binary data can be stored as a
rewritable, self-healing voltage state in living cells, engineered rather than
natural. Existing biocomputing efforts (Cortical Labs, Koniku, FinalSpark) use
cultured neurons: volatile, short-lived, and unable to repair themselves. We are
testing a different substrate: a genetic circuit that holds a stable, switchable
"bit" through engineered bistability rather than continuous power.

We are not asking you to fund a finished product. We are asking you to fund the
specific, cheap, fast experiment that tells us honestly whether the core mechanism
exists in living cells at all. If it doesn't, we want to find that out for $5,000,
not after years of downstream work.

## Why this project, and why now

Months of computational work (real published citations plus original simulation,
listed in full below) found that the project's original claim, that a voltage
pattern would simply persist passively in a cell for 24 hours, only holds in a
zero-noise simulation. Once realistic biological noise is added, integrity collapses
to roughly a coin flip. The concept only survives if backed by a deliberately
engineered, strongly bistable genetic circuit, not passive cell biology.

We then designed that circuit from two free, real sources: the Gardner, Cantor and
Collins (2000) genetic toggle switch, the original synthetic bistable circuit
built in a living cell, combined with promoters from the Bacillus BioBrick Box, a
free, open, BioBrick-compatible parts library characterized directly in
*B. subtilis*. Simulating the combined design surfaced a specific, checkable design
rule: two promoters of similar strength produce a fully robust switch, while a
severe strength mismatch collapses bistability entirely, so that whichever bit is
written, the circuit always relaxes to the same state.

That is a testable, falsifiable prediction. Nobody has tested it. This project
funds that test.

## What are the goals of the study?

**Stage 0 (base goal): confirm real bistability in living cells.**
Build a matched-strength promoter pair from the existing, free Bacillus BioBrick
Box library into the Gardner toggle-switch topology, transform it into
*B. subtilis*, and read it out with a standard reporter assay (lacZ or lux). We are
looking for a clearly bimodal reporter signal across a colony population, with
reliable switching between the two states following a transient induction pulse in
either direction.

This has never been tested. Gardner's own toggle switch was built and measured in
*E. coli*, not *B. subtilis*, and nobody has combined it with these particular,
chassis-matched parts before.

**Stage 1 (stretch goal): test whether an arbitrary voltage pattern persists at all,
in a simple, fast system.**
In parallel with the genetic question, we still need to know whether an arbitrary
(non-natural) voltage pattern, once written, persists the way naturally evolved
patterns do, or decays back to a cell's resting state. Stage 1 tests this in a
gap-junction-coupled mammalian cell line (HEK293), chosen because it is fast,
reproducible, and easy to transfect, as a quick, independent read on that question
before committing to a slower, harder-to-culture organism.

## Budget

| Item category | Notes |
|---|---|
| BioBrick part acquisition | Bacillus BioBrick Box parts are free to academic/research requesters; this covers shipping/handling and any distribution fees |
| Plasmid construction and cloning reagents | Gibson assembly or equivalent, competent cell transformation reagents |
| Growth media and reporter assay reagents | Standard *B. subtilis* culture media, lacZ or lux substrate reagents |
| Plate reader / imaging time | Reading bimodal reporter output across a population |
| Sequencing confirmation | Verifying constructed plasmids match the intended design before running the assay |
| General consumables | Tips, plates, tubes, standard lab supplies |

We have not yet received a formal quote from a lab partner for these line items; the
$2,000 to $5,000 range above is a planning estimate based on typical costs for
bacterial reporter-assay work of this scope, not a lab-confirmed figure. We will
publish the actual itemized quote as a lab-notes update once a partner lab is
confirmed. Funds are earmarked for reagents, part acquisition, and contracted bench
time at a partner lab, not for founder compensation or overhead.

## Endgame

**If the result is positive** (clearly bimodal, switchable reporter signal): this
resolves the single design constraint (promoter matching) our simulation flagged as
make-or-break, and directly justifies funding the next, more expensive stage, the
voltage-interface build, where the circuit's genetic output is coupled to an actual
ion channel so the "bit" becomes a real, measurable membrane-voltage state. Nobody
has built or measured that link, in any organism.

**If the result is negative** (no reliable bistability, even with matched
promoters): that is still a real, useful answer. It tells us the Gardner topology
does not transfer cleanly to this chassis and parts combination, and redirects
effort toward a different circuit design rather than continuing to fund an
unproven assumption. We will report a negative result exactly as prominently as a
positive one.

Either way, results (raw reporter data, plasmid maps, and our interpretation) will
be posted as lab notes on this project page as they come in, and written up as a
preprint. This project has consistently kept commercially sensitive implementation
details as trade secrets while publishing the underlying science openly, and this
experiment's results fall on the open side of that line.

## Risks and challenges

We are stating plainly what this experiment can and cannot tell you, because a
funding request that only lists what could go right is a weaker basis for trust
than one that shows we have already tried to break our own idea.

- We have demonstrated in simulation, not in living cells, that a matched-promoter
  Gardner-style circuit should be bistable in *B. subtilis*. This experiment is the
  first real test of that prediction.
- Even a successful Stage 0 result does not establish that the circuit's output can
  be coupled to membrane voltage. That link (Claim B, in our fuller validation
  proposal) has no prior art at all and is a separate, larger piece of work.
- Bacterial reporter assays are generally reliable, low-risk science, but strain
  handling, transformation efficiency, or reporter choice can introduce delays that
  push past our estimated 6 to 10 week timeline.
- We are a small, founder-led team without an in-house wet lab. This experiment
  depends on securing a contracted lab or academic partner to actually run the
  bench work; campaign funds cover that partner's costs, and timeline estimates
  assume a partner is engaged promptly after funding closes.

## Bibliography

1. Gardner, T.S., Cantor, C.R. and Collins, J.J. (2000). Construction of a genetic
   toggle switch in *Escherichia coli*. *Nature*, 403, 339-342.
   https://doi.org/10.1038/35002131
2. Radeck, J. et al. (2013). The Bacillus BioBrick Box: generation and evaluation of
   essential genetic building blocks for standardized work with *Bacillus
   subtilis*. *Journal of Biological Engineering*, 7, 29.
   https://doi.org/10.1186/1754-1611-7-29
3. Radeck, J. et al. (2017). The Bacillus BioBrick Box 2.0: expanding the genetic
   toolbox for the standardized work with *Bacillus subtilis*. *Scientific
   Reports*, 7, 15058. https://doi.org/10.1038/s41598-017-15107-z
4. Manicka, S. and Levin, M. (2019). Modeling somatic computation with non-neural
   bioelectric networks. *Scientific Reports*, 9, 18612.
   https://doi.org/10.1038/s41598-019-54859-8
5. Mathews, J. and Levin, M. (2016). Gap junctional signaling in pattern
   regulation: Physiological network connectivity instructs growth and form.
   *Developmental Neurobiology*, 77, 643-673. https://doi.org/10.1002/dneu.22405
6. Prindle, A. et al. (2015). Ion channels enable electrical communication in
   bacterial communities. *Nature*, 527, 59-63.
   https://doi.org/10.1038/nature15709
7. Lundberg, M.E., Becker, E.C. and Choe, S. (2013). MstX and a putative potassium
   channel facilitate biofilm formation in *Bacillus subtilis*. *PLoS ONE*, 8(5),
   e60993. https://doi.org/10.1371/journal.pone.0060993

Simulation results referenced above are original computational work performed for
this project. Source code is available on request.

## Team

**Dayana Sanchez, Founder and Lead Researcher.** Originated the Acheron concept and
has led the project's simulation, literature review, and circuit design work to
date.

**Jacqueline Solano, Co-Founder.** Leads business operations for the project.

## Reward tiers (non-financial; no equity or profit share is offered at any tier)

- **$10 — Thank you.** Your name listed on the project's supporter page.
- **$25 — Lab notes access.** Early access to raw lab-notes updates as results
  come in, before the public write-up.
- **$50 — Behind the design.** A short video walkthrough of the toggle-switch
  circuit design and why the promoter-matching constraint matters.
- **$100 — Ask us anything.** A recorded Q&A response addressing backer questions
  about the experiment and results.
- **$250 — Acknowledged contributor.** Named acknowledgment in the resulting
  bioRxiv preprint, in addition to all of the above.
