# Acheron Reasoning Map

The one page that explains how everything in this repository fits together, and
why it is arranged the way it is. Read this before anything else.

---

## What this project is

Acheron is a research project asking whether arbitrary binary data can be stored
as a rewritable, self-healing state inside living cells. Not data written into
DNA as a permanent archive, which already exists and is being commercialised.
Something closer to RAM: a state you can write, read without destroying it,
change your mind about, and which survives the cells being damaged and growing
back.

There is no product, no service and no running software. The output of this
project is three things: simulations that test whether the idea can work, an
honest running audit of what has been proven versus assumed, and materials
asking people to fund the first real experiments.

---

## Where everything lives

| Folder | What is in it | What it is not |
|---|---|---|
| `simulations/` | Every simulation of a scientific claim, named by organism. `SIMULATION_MAP.md` explains each one in plain English and in technical terms. | Not measurements. Nothing here has touched a living cell. |
| `experiments/` | Bench protocols. What you would actually do at a lab bench, with strains, parts, instruments, replicate counts and pass/fail thresholds. | Not run yet. Not reviewed by a lab yet. |
| `docs/` | The audit, this map, the whitepaper, pitch and strategy documents. | The older phase documents contain claims that did not survive later testing. Check the audit first. |
| `docs/pitch/` | Investor and incubator materials, including the deck generator. | |
| `tools/` | Demos, optimisers, sweeps and validation harnesses. Supporting machinery. | Not claims about biology. |
| `analysis/`, `encoder/`, `third_party/` | Reusable methods, the encode/decode layer, and vendored external code. | `third_party/` is other people's work, see `docs/THIRD_PARTY_METHODS.md`. |
| `patents/` | Three filed patent documents. | |
| `tests/` | Unit tests, covering `analysis/` only. | Not a test suite for the simulations. |
| `hardware/` | Empty. A placeholder. | There is no hardware. The cartridge-and-reader concept exists only as a pitch slide. |

**The single most important file is `docs/SCIENTIFIC_AUDIT_2026.md`.** It is
appended to over time, never rewritten, and it records what broke as carefully
as what worked. If it disagrees with any other document in this repository, it
wins.

---

## The chain of reasoning, in order

This is the actual history of the idea, including the parts where it was wrong.
Each step names the file that did the work.

**1. The original claim.** A bit written as a voltage into flatworm tissue would
hold for 24 hours on its own.
`simulations/planarian_01_bioelectric_persistence.py` said yes, 100%.

**2. The claim broke, under this project's own scrutiny.** Adding realistic
biological noise collapsed it to a coin flip.
`simulations/planarian_02_noise_floor.py`, audit Part 8. The original model had
no real attractor holding the bit in place, just a very slow leak, and noise
beats a slow leak.

**3. Redundancy could not save it.** Keeping three copies and voting does not
help when every copy is already no better than chance. This is Condorcet's jury
theorem, and it applies whether the copies are tiles
(`planarian_08_bio_raid_ecc.py`) or generations (`methylation_02`).

**4. The pivot.** Passive persistence is not enough. The bit needs an actively
engineered circuit holding it there.
`simulations/bsubtilis_01_gardner_toggle_circuit.py` builds one from a real
published topology and real, characterised, off-the-shelf bacterial parts, and
found a hard design rule in the process: mismatched promoter strengths do not
degrade the switch, they destroy it.

**5. The organism changed.** A side-by-side comparison
(`crossorganism_01_comparison_summary.py`, audit Part 13) ranked the three
candidate mechanisms not by their output numbers but by how much untested risk
each was hiding. Bacteria won, because their inheritance mechanism is not an
assumption: when a cell divides, the proteins holding the state physically go
into both daughters. The planarian approach, the original idea, came last.

**6. Storage through damage looked good.** Kill most of a colony, let it regrow,
and the bit survives from as few as 2% of cells
(`bsubtilis_07_colony_regrowth.py`), including when molecules split unevenly at
division (`bsubtilis_15`), and the colour readout survives it too
(`bsubtilis_13`).

**7. Reading it back became the hard part.** Bacteria run their own electrical
signalling, unrelated to anything this project builds, and it corrupts a voltage
reading even when the underlying data is perfectly intact
(`bsubtilis_08`, audit Part 12). Three attempted fixes were tested honestly and
two failed: a cheap electrode sweep is not immune (`bsubtilis_09`), and clever
timing does not dodge it (`bsubtilis_11`). Reading for a full three-hour cycle
works, and weakening the interference at its source helps at moderate levels
(`bsubtilis_12`).

**8. Then the framing was challenged.** A published paper the project had missed
(Yang et al. 2020) stores a bit in this exact organism as its *phase*
relationship to that same signalling, making the interference into the carrier
rather than the noise. `bsubtilis_18_phase_encoded_readout.py` tested that
framing and found a clean inversion: the old scheme fails as the signal grows,
the new one only works when the signal is there. Audit Part 25.

**9. Where that leaves the project.** Two prior-art corrections landed at the
same time (audit Parts 24 and 25), narrowing the novelty claim. What survives is
narrower and still real, and it is stated in the next section.

---

## What is proven, assumed, and disproven

**Proven, by other people, in the published literature:**
- Bistable genetic memory works in bacteria (Gardner et al. 2000).
- Bacterial biofilms carry long-range electrical signals through ion channels
  (Prindle et al. 2015).
- A membrane-potential state can be written into a living biofilm with light and
  read back non-destructively for hours (Yang et al. 2020).
- Rewritable digital data storage in live cells via recombinases, heritable over
  100+ divisions (Bonnet et al. 2012).

**Assumed, and unmeasured:**
- Every noise magnitude in every simulation here.
- The absolute voltage levels a bit would correspond to in bacteria.
- How strongly planarian cells pull each other's voltage around. This is the
  weakest assumption in the project.
- The real repressor copy number per cell.

**Disproven, by this project's own work:**
- That an arbitrary voltage pattern passively persists for 24 hours. It does
  not, under any realistic noise.
- That redundancy rescues a weak signal. It does not.
- That a single fast electrical sweep sees through the colony's own rhythm. It
  does not.
- That timing a quick read cleverly avoids that rhythm. It does not.

**Never built by anyone, in any organism:** the link from a genetic circuit's
state to a measurable membrane voltage. This is the real bet. Everything else
on the roadmap is comparatively well precedented.

---

## The honest novelty claim

Do not write "nobody has stored data as a bioelectric state" into any document.
It is no longer defensible and a reviewer will find the papers.

What survives is narrower and still worth funding: **every existing example of
data held in a living organism is either archival (written into DNA sequence, read
by destroying the sample), or a protein-level state that gets diluted away when
cells divide.** Surviving division and regrowth, while staying rewritable and
readable without destroying the sample, is what nobody has shown. That is the
property this project is actually built around, and it is the one thing the
bench protocol is designed to test first.

---

## Open questions, ranked by how much everything else depends on them

1. **Does the genetic circuit drive a measurable voltage?** Never built. This is
   Stage B4 in the bench protocol and the project's real risk.
2. **Level encoding or phase encoding?** They are mutually exclusive, they want
   opposite things from the same ion channel, and they point at different
   bacterial strains. This choice has to be made before ordering a strain.
3. **Do the real noise numbers land where the simulations assume?** Cheap to
   answer, Stage B1, and it retires the largest single category of caveat here.
4. **Does real damage behave like modelled damage?** Every simulation treats
   damage as removing cells with no effect on survivors. Stage B2 arm 2b
   measures the gap.

---

## Where to start reading, depending on who you are

- **Preparing for an interview or investor call:** `docs/ACHERON_INTERVIEW_GUIDE.md`,
  then `docs/ACHERON_101.md` for the concept chapters.
- **Coming back to this after a break:** this file, then the last two Parts of
  `docs/SCIENTIFIC_AUDIT_2026.md`.
- **A scientist assessing whether it is real:** `docs/SCIENTIFIC_AUDIT_2026.md`
  end to end, then `simulations/SIMULATION_MAP.md`, then
  `experiments/BENCH_PROTOCOL_BSUBTILIS.md`.
- **Deciding whether to fund it:** `docs/INVESTOR_PITCH.md` and
  `docs/pitch/Acheron_Validation_Proposal.docx`, then the audit's risk
  disclosures, which are deliberately blunt.
- **A lab being asked to run the experiment:**
  `experiments/BENCH_PROTOCOL_BSUBTILIS.md`, then audit Parts 8 through 25 for
  where each predicted number came from.
- **Writing code here:** `CLAUDE.md`, then `CODEMAP.md`, then the specific file.
  Source always wins over documentation if they disagree.
