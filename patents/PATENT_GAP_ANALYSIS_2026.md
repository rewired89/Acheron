# Patent Gap Analysis, September 2026

## What this document is

The three patent applications in this folder were drafted before the project's
own simulations retired several of the claims they rest on. This is the list of
every place the filed text and the current science disagree, ranked by how much
damage each one can do.

It is an analysis, not a rewrite. The three patent files have deliberately not
been edited. See "Why the filed text was not edited" at the end.

Source of truth for everything below is `docs/SCIENTIFIC_AUDIT_2026.md`. Audit
Part numbers are cited inline.

---

## Severity 1: fix before an examiner or an investor's counsel reads these

### 1.1 There is a fabricated prior-art citation in Patent 1

`PATENT_01_BIO_RAID_CORE_SYSTEM.md`, Background Art section:

> Prior art in biological computing (U.S. Patent 10,123,456 - hypothetical)
> describes bioelectric signal storage but lacks: [...]

That number is written into the Background as prior art and labeled
"hypothetical" in the same breath. US Patent 10,123,456 is a real granted
number in a range that issued in late 2018, so it points at some unrelated
invention. A Background section is read as the applicant's own characterisation
of the field. This needs to come out and be replaced with real citations.

### 1.2 Two directly relevant pieces of prior art are cited nowhere

Neither paper appears in any of the three documents. Both are closer to the
claimed subject matter than anything the Background does cite.

**Bonnet, Subsoontorn & Endy (2012)**, "Rewritable digital data storage in live
cells via engineered control of recombination directionality," *PNAS*
109(23):8884-8889, DOI 10.1073/pnas.1202344109. Addressable, digital,
rewritable data storage in living cells, heritable over 100+ cell divisions
with no input and no selection, read non-destructively by fluorescence. Audit
Part 24.

**Yang, Bialecka-Fornal, Weatherwax, Larkin, Prindle, Liu, Garcia-Ojalvo &
Süel (2020)**, "Encoding membrane potential-based memory within a microbial
community," *Cell Systems* 10(5):417-423, DOI 10.1016/j.cels.2020.04.002.
Arbitrary spatial patterns written into a living *B. subtilis* biofilm's
membrane potential, read back non-destructively at single-cell resolution for
over three hours, framed by its authors as digital memory for biological
computing. Audit Part 25.

For a US application there is a duty to disclose known material prior art
(37 CFR 1.56). These are known now. This is the single highest-exposure item
in this document and it is a question for the patent attorney, not for this
repository.

### 1.3 Unfilled placeholders remain in all three documents

All three carry `[PROVISIONAL APPLICATION NUMBER IF FILED], filed [DATE]`, and
Patent 2 additionally carries `[PATENT #1 APPLICATION NUMBER]`. If the
documents in this folder are the text that was filed, these need reconciling
against what was actually submitted. If they are drafts that differ from the
filed text, this folder needs to say so.

---

## Severity 2: the claims are locked to science the project has since retired

### 2.1 Every independent claim recites planarian tissue as the substrate

Patent 1 claims 1(a) and 13(a), Patent 2 throughout, Patent 3 by reference.

`simulations/crossorganism_01_comparison_summary.py` ranks the three candidate
mechanisms by how much untested wet-lab risk each hides and puts the planarian
approach last, because its cell-coupling assumption has never been measured in
real tissue. Audit Part 4. The project has been *B. subtilis*-first since, with
planaria as the weaker fallback.

The claims are therefore narrowest exactly where the evidence is weakest, and
say nothing about the organism the project actually intends to build in.

### 2.2 The encoding scheme in the claims is the one that failed

Patent 1 claim 1(b) and claims 7 and 18 recite converting bits into cellular
voltage gradients, with the specification fixing bit 0 at -40mV and bit 1 at
+40mV. That is absolute-level voltage encoding.

`simulations/planarian_02_noise_floor.py` re-ran that scheme with realistic
biological noise and integrity fell to roughly 50%, a coin flip. Audit Part 8.
`simulations/bsubtilis_08_native_oscillation_interference.py` found the same
collapse from the organism's own potassium-wave signaling even with the
underlying data intact. Audit Part 12. Audit Part 24 recommends taking
electrical readout off the critical path entirely in favour of a reporter.

### 2.3 Patent 1 claim 12 is contradicted by the project's own noise result

Claim 12 recites that pattern_fidelity can remain 100% while bio_health is 70%,
and the specification presents three-way majority voting as the mechanism that
makes this true.

Majority voting only improves on a single read when each individual read is
already better than chance. At roughly 50% per-read accuracy, adding replicas
does not converge on the right answer. So the noise floor result and claim 12
cannot both be right, and the noise floor result is the one with a simulation
behind it. The encoder code already carries this warning in
`encoder/bacterial_toggle_encoder.py`; the patent does not.

### 2.4 Numeric limitations in the claims came from simulation knobs

Hard numbers recited in the claims, with no measured biological equivalent
behind any of them:

| Number | Where it is claimed | What it actually is |
|---|---|---|
| 0.6% per day stabilization boost | P1 claims 1(h), 3, 13(g); P2 claims 1(d), 3, 11(d) | a tuning parameter in the degradation model |
| 0.4 / 0.2 / 0.1% per day recovery bands | P1 claim 19 | same |
| 0.03 / 0.05 / 0.08% per day baseline degradation | P3 claims 2, 3 | same |
| 2.0% per day chronic degradation probability | P3 claim 3 | same |
| 80% integrity threshold, 5 days, 2% in 3 days | P1 claims 2, 4; P2 claims 1(a), 2 | same |

This is the no-invented-numbers rule applied to the patents. A numeric
limitation narrows a claim permanently and is trivial for a competitor to
design around by using 0.55% per day. Recited without measurement behind them,
these numbers cost scope and buy nothing.

### 2.5 Patent 3 claim 5 claims accuracy against reality that was never measured

> **Claim 5**: The method of claim 4, wherein longevity prediction achieves
> accuracy within 3% of actual results for all environment profiles.

"Actual results" here means the output of the same simulation the prediction
came from. That is self-consistency, not accuracy. Nothing in this project has
been measured at a bench.

---

## Severity 3: everything the project can currently defend is unclaimed

A grep across all three documents returns zero hits for *B. subtilis*, toggle
switch, Gardner, reporter, GFP, fluorescence, spore, phase encoding, potassium,
yugO, BioBrick, or cell division.

So none of the following is covered by any claim, and all of it is 2026 work:

- The Gardner-topology genetic toggle switch in *B. subtilis* built from
  Bacillus BioBrick Box parts, and the promoter-matching constraint that
  simulation found (`bsubtilis_01`, audit Part 9).
- Stored state surviving damage and regrowth because cell division copies the
  circuit into daughter cells, recovering to full fidelity from as few as 2% of
  cells surviving (`bsubtilis_07`, `bsubtilis_13`, audit Part 20). **This is the
  differentiator `README.md` leads with and the one thing the closest prior art
  cannot do, and it appears in no claim.**
- The two-colour fluorescent reporter readout that tracks the genetic state
  exactly through damage and regrowth (`bsubtilis_13`, audit Parts 16 and 20).
- The damage-sensing reinforcement circuit modeled on the bacterial SOS
  response (`bsubtilis_16`, audit Part 23).
- Phase-relationship encoding against the native oscillation, where the
  oscillation becomes the carrier rather than the interference
  (`bsubtilis_18`, audit Part 25).
- Spore dormancy as the shelf state of the medium.

The redundancy and healing machinery in Patents 1 and 2 is storage-system
engineering that would read on any substrate. The biology that makes it novel
is the part that is missing.

---

## Severity 4: marketing copy inside the specifications

Patent 1 and Patent 2 both contain blocks headed **Investor Pitch:** with
quoted promotional sentences, and Patent 1's summary states "0% logical bit
errors (PERFECT correctness)" and "Zero data loss guarantee." Patent 3's
abstract projects "78.5% healthy-3-live after 10 years."

All of these describe simulation output and none of them is labeled as such in
the patent text. A durability guarantee stated without a measurement behind it
is the kind of sentence an opposing counsel reads aloud.

---

## Why the filed text was not edited

A patent application cannot be amended by editing a file. Once filed, changes
reach the record only through a preliminary amendment, a continuation-in-part,
or a fresh application, and all three are the attorney's call, not a decision
that should be made here.

More practically: these markdown files are currently the only record of what
was submitted and when. Rewriting them in place would destroy the ability to
answer "what did we actually file," which is a question that will be asked.

What this analysis is for is the conversation with the patent attorney. The
short version to bring to that conversation:

1. Disclose Bonnet 2012 and Süel 2020, and remove the fabricated citation.
2. The filed claims protect a planarian voltage-encoding architecture the
   project no longer pursues. Ask what, if anything, is worth keeping alive.
3. The genuinely novel and currently defensible result, an engineered bistable
   circuit whose state survives damage and regrowth through cell division, is
   unclaimed and undisclosed. Ask whether it is still filable and on what
   timeline, given that it is now described in a public repository.

Item 3 is the one with a clock on it.
