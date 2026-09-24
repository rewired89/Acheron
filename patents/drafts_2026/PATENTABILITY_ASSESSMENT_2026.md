# What Acheron can and cannot patent, September 2026

Not legal advice. Written by reading this project's own code, its audit, and the
prior art the audit cites. A registered patent attorney has to sign off before
anything here is filed.

The short answer to "can we patent anything": **yes, but less than the three
filed applications claim, and not the part the pitch deck leads with as
electrical.** Three subjects survive the prior art and are drafted in this
folder. Four subjects do not survive and should not be filed.

---

## Can be filed

### 1. Genetic bistable state that survives damage and regrowth
`DRAFT_A_DIVISION_INHERITED_MEMORY.md`

This is the strongest of the three, and it is the one thing the closest prior
art structurally cannot do. Yang et al. 2020 (the Süel lab, *Cell Systems*
10(5):417-423) already published arbitrary spatial patterns written into a
living *B. subtilis* biofilm's membrane potential, read back non-destructively
at single-cell resolution, framed by its own authors as digital memory. But
their memory is a persistent protein-level modification of existing yugO
channels, and their own discussion says biofilm cells there are "predominantly
non-replicating." A protein modification dilutes out when cells divide. A
genetic toggle state does not, because division copies the circuit into both
daughters. That distinction is the whole invention.

Bonnet, Subsoontorn & Endy 2012 (*PNAS* 109(23):8884-8889) is closer on
rewritability, being heritable over 100+ divisions, but it is a DNA-orientation
latch propagated through ordinary growth. It does not address recovery of a
population's stored state after most of the population is destroyed.

### 2. Damage-sensing reinforcement during the regrowth window
`DRAFT_B_DAMAGE_SENSING_REINFORCEMENT.md`

A stress-responsive element that transiently boosts whichever toggle arm
currently dominates, active only while the colony is regrowing, then relaxing.
No prior art found for coupling a damage-response promoter to a memory
circuit's own current state for the purpose of preserving stored data. It is
also the fix for the one real fragility this project's own noise testing found
(partition noise at roughly one effective repressor molecule per cell).

### 3. Phase-referenced encoding against an endogenous oscillation
`DRAFT_C_PHASE_REFERENCED_ENCODING.md`

Encoding the bit as a phase relationship to the colony's own potassium
oscillation rather than as an absolute voltage level. This one is the most
speculative and has the closest prior art: Yang et al. 2020 already produced
anti-phase behaviour between exposed and unexposed cells and explicitly framed
it as "either 'on' or 'off,' as in traditional digital memory." So the generic
idea of phase-as-a-bit in this organism is anticipated. What is not anticipated
is a **genetically encoded, rewritable, division-heritable** determinant of
which phase a cell adopts. File it narrow, tied to the genetic circuit, or not
at all.

---

## Should not be filed

**Absolute-voltage-level encoding in a *B. subtilis* biofilm.** Anticipated by
Yang et al. 2020 in the same organism, same strain, same channel. This project's
own simulations also found it collapses to roughly 50% accuracy under the
colony's native oscillation, so it fails enablement as well as novelty.

**Data stored as DNA sequence.** Yachie & Tomita 2007 did it in *B. subtilis*.
BioCompute Inc. is commercialising it.

**A rewritable DNA-orientation latch.** Bonnet et al. 2012.

**Environment-adaptive longevity prediction (the subject of filed Patent 3).**
Its numbers are tuning parameters in a degradation model, and its claim 5
recites accuracy "within 3% of actual results" where "actual results" means the
same simulation's output. There is nothing to enable and nothing measured. Do
not refile this subject.

---

## Three problems that apply to all three drafts

**1. Nothing has been built.** Every result behind these drafts is simulation.
Under 35 USC 112 a specification must enable a person skilled in the art to
make and use the invention. A provisional application is the right instrument
here precisely because it buys a 12 month priority date while the wet lab work
that would support a non-provisional gets done. Filing a non-provisional on
simulated results invites a rejection the project cannot currently answer.

**2. The duty to disclose.** 37 CFR 1.56 requires disclosing known material
prior art. Yang et al. 2020 and Bonnet et al. 2012 are now known. They are not
cited anywhere in the three filed applications, and one of those applications
carries a fabricated prior-art citation ("U.S. Patent 10,123,456 -
hypothetical", which is a real granted number pointing at some unrelated
invention). Both issues go to the attorney immediately, ahead of any new filing.

**3. Public disclosure, which needs checking rather than assuming.** The GitHub
repository is **private** (verified 21 September 2026), so it is not a public
disclosure and starts no clock. `docs/BIORXIV_MANUSCRIPT.md` is the open
question: if that manuscript was actually posted to bioRxiv, it is a public
disclosure, which leaves a one year grace period for a US filing under 35 USC
102(b)(1) and very likely bars novelty in Europe and most other absolute-novelty
jurisdictions. **Someone has to confirm whether it was posted, and when.** The
answer changes the filing deadline and the achievable geographic scope. Nothing
in this repository records it either way.

---

## No numeric limitations in the claims

Per `docs/THIRD_PARTY_METHODS.md`'s no-invented-numbers rule, none of the three
drafts recites a number in a claim. The filed applications recite roughly a
dozen (0.6% per day, 80% integrity, 2% in 3 days, and so on), every one of them
a tuning parameter from a simulation. A numeric limitation narrows a claim
permanently and is trivial to design around by using a slightly different
number. Simulation results appear in the drafts' descriptions, labeled as
simulation, where they support enablement without narrowing scope.
