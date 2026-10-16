# Acheron

**Can arbitrary binary data be stored as a rewritable, self-healing state
inside a living cell, and still be there after the tissue is damaged and
grows back?**

That is the whole project. Acheron is a research effort, not a product.
There is no service, API, or device. What exists today is a suite of Python
simulations, a continuously updated self-audit of what those simulations do
and do not establish, filed patent documents, and funding materials for a
staged wet-lab validation.

**Read `docs/SCIENTIFIC_AUDIT_2026.md` before trusting any claim in this
repository, including the ones on this page.** It is the living record of
what has been validated, what is still assumed, and which of this project's
own earlier claims did not survive later testing. Several did not.

---

## Where the project actually stands

The current direction is **engineered *B. subtilis* first**, with planarian
flatworms as a less-grounded fallback. That is the reverse of how the project
started, and the reversal was forced by its own results.

**The original claim, now retired.** Phase 1 modeled planarian cells
passively holding a voltage-encoded bit for 24 hours and reported near-perfect
retention. Re-running that model with realistic biological noise (ion channel
shot noise, cell-to-cell variability, metabolic and thermal fluctuation)
collapsed integrity to roughly 50%, which is a coin flip. The original result
depended entirely on a zero-noise assumption. Passive persistence is not a
mechanism; it is a slow leak, and noise beats a slow leak.

**The pivot.** Holding a bit requires an actively engineered bistable circuit,
not a hopeful property of ordinary tissue. The project now models a
Gardner-style genetic toggle switch built from real *B. subtilis* BioBrick
parts. That model produced a concrete design constraint rather than a
reassurance: mismatched promoter strengths collapse the circuit into a
monostable dead switch, so promoter matching is the make-or-break variable
for the first experiment.

**Why bacteria over flatworms.** Ranking the candidate mechanisms by how much
untested wet-lab risk each one still hides gives: *B. subtilis* circuit,
then *B. subtilis* methylation, then planarian circuit, worst. The planarian
approach's cell-coupling strength has never been measured in real tissue, so
its numbers, even when they look good, rest on a borrowed assumption.

---

## What simulation has shown (and what that is worth)

Every item below is a simulation result, not a measurement. Nothing in this
project has been tested at a bench.

- **The genetic state survives damage and regrowth.** A colony knocked down
  to as little as 2% surviving cells regrows to full fidelity, because cell
  division copies the circuit's existing proteins into daughters. This is the
  project's actual differentiator.
- **Those recovery numbers depend on an unmeasured noise setting.** They were
  computed with a transcriptional-noise placeholder that a later check
  suggests is 3x to 17x too low. Re-running with the noise turned up shows
  recovery holds up to about 5 times the placeholder, drops at 10 times, and
  is near chance by 20 times, with mismatched promoters failing sooner. Whether
  the first experiment passes therefore depends on a number only the lab can
  supply. See audit Part 29.
- **Stochastic partition noise does not break it.** Modeling real, uneven
  splitting of molecules between daughter cells (binomial partitioning) leaves
  recovery at 99-100% down to about five molecules per cell. Only at an
  extreme and probably unrealistic single-molecule level does recovery degrade,
  and even then it does not fall to chance.
- **A fluorescent reporter readout tracks the genetic state exactly**, through
  damage and regrowth, with no added fragility of its own. This is why the
  first funded experiment uses a reporter assay and not an electrode.
- **Reading the bit as a voltage level is the hard part.** *B. subtilis*
  biofilms run their own native potassium-wave signaling, real and published
  and unrelated to anything this project builds. A single voltage snapshot
  taken during it collapses to about 50% accuracy even when the underlying
  genetic data is perfectly intact. Averaging a reading over roughly a full
  oscillation period (about three hours) restores accuracy, but that eats
  nearly the entire settling budget the regrowth model assumes, leaving no
  margin in the worst damage case.
- **An unresolved fork.** If the bit is encoded as a cell's *phase*
  relationship to that native oscillation rather than as a static voltage
  level, the oscillation becomes the carrier and the readout improves as the
  oscillation strengthens. The two schemes fail in opposite ways and want
  opposite chassis strains (level encoding wants the yugO channel weakened or
  deleted, phase encoding needs it intact), so this has to be decided before
  committing to a strain.
- **A proposed fix, not a built one.** A damage-sensing circuit modeled on the
  real bacterial SOS response rescues the single-molecule weak point
  completely in simulation. It is a design proposal. Nobody has built it, and
  it raises a question it does not answer: would a circuit reinforced that
  strongly resist a legitimate rewrite?

---

## What is still unproven

1. **Everything above is simulated.** No wet-lab result exists.
2. **The circuit-to-voltage link does not exist.** The connection from the
   toggle circuit's repressor output to a measurable membrane voltage is
   currently a hypothetical in the model, not a built construct.
3. **The core question is untested in any organism.** Does an engineered
   bistable circuit's state survive damage and regrowth, as opposed to
   ordinary cell division? Nobody has run this experiment anywhere.
4. **A real strain mismatch.** The BioBrick promoter parts were characterized
   in *B. subtilis* W168, while the biofilm potassium-wave literature that all
   the interference work rests on used NCIB 3610. Both cannot be used at once.

---

## Closest prior art, know this before claiming novelty

Yang, Bialecka-Fornal, Weatherwax, Larkin, Prindle, Liu, Garcia-Ojalvo & Süel
(2020), "Encoding membrane potential-based memory within a microbial
community," *Cell Systems* 10(5):417-423,
[DOI 10.1016/j.cels.2020.04.002](https://doi.org/10.1016/j.cels.2020.04.002).

They already wrote arbitrary spatial patterns into a living *B. subtilis*
biofilm's membrane potential with light, read them back non-destructively at
single-cell resolution for over three hours, and framed it as digital memory
for biological computing. Do not write "nobody has stored data as a
bioelectric state" anywhere.

The narrower claim that survives: their memory is a protein-level modification
that dilutes out as cells divide, and their own discussion notes their biofilm
cells are predominantly non-replicating. **Surviving division and regrowth is
this project's differentiator, and it is the one thing their mechanism cannot
do.**

---

## A second prior art, and what it does to the claim above

Bonnet, Subsoontorn & Endy (2012), "Rewritable digital data storage in live cells
via engineered control of recombination directionality," *PNAS* 109(23):8884-8889,
built an addressable, rewritable, digital memory in live bacterial cells, held by
the orientation of a stretch of DNA, heritable over more than a hundred cell
divisions, and read non-destructively by fluorescence.

That narrows the claim in the previous section. A DNA-orientation latch is
inherited at division for the same reason a protein toggle is, so "the state
survives division and regrowth" does not by itself separate this project from that
work. What has not been shown is a functional advantage over a DNA latch. What
might separate them is the damage-detecting, self-reinforcing part of the
hypothesis (a circuit that senses damage and strengthens the stored state during
regrowth), which is simulated and unbuilt. Whether the stored state should be
voltage at all is an open decision, laid out in `docs/VOLTAGE_DECISION_MEMO.md`.
Until that decision is recorded, the novelty claim is provisional and no material
should claim voltage novelty or an advantage over a DNA latch.

---

## The roadmap

Four independent, cheap gates rather than one combined bet. Full costs and
scoping live in `docs/INVESTOR_PITCH.md` and
`docs/pitch/Acheron_Validation_Proposal.docx`.

| Stage | Question | Cost |
|---|---|---|
| 0 | Does the matched-promoter toggle circuit hold two stable, switchable states in *B. subtilis*, read with a simple reporter assay? | $2K-$5K |
| 1 | Do voltage patterns persist 24h+ in a simple gap-junction-coupled HEK293 culture? | $2.4K-$10K |
| 2 | Do patterns persist in a regenerating organism, through damage and regrowth? | $10K-$30K |
| 3 | Can the circuit's output be coupled to a real membrane-voltage bit and read non-destructively? | To be scoped |

Stage 0 is the ask. It tests the single constraint the circuit simulation
flagged as make-or-break, uses parts that already exist and are free to
obtain, and sidesteps the readout problem entirely by using a reporter.

---

## Repository layout

`CODEMAP.md` is the structural map of the code and is the place to look for
where a given model lives. In brief:

| Area | Contents |
|---|---|
| `simulations/` | The models this page reports: toggle circuit, noise floor, colony regrowth, readout interference, partition noise, organism comparison |
| `experiments/` | Runnable demos and parameter studies, plus the HEK293 bench protocol |
| `analysis/`, `third_party/` | Methods adapted from published external work, attribution in `docs/THIRD_PARTY_METHODS.md` |
| `encoder/` | Binary to bioelectric pattern translation |
| `tests/` | pytest suite, covers `analysis/` |
| `docs/` | The audit, the bench protocol, pitch and patent material |
| `patents/` | Three documents, filed with the USPTO, pending examination |

See `QUICKSTART.md` to run the simulations.

---

## House rules for anyone writing here

- **No invented numbers.** Every figure must trace to a citation, to a labeled
  simulation result with its caveats attached, or be marked as an open
  question. The credibility strategy is rigor and visible self-correction, not
  polish.
- **Do not soften a caveat to make a claim sound stronger.** This project has
  already published corrections to its own headline results, and that is the
  point.

## License

Proprietary. Patents filed, pending examination.
