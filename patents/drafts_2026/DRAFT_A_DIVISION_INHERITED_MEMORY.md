# DRAFT, NOT FILED

**Provisional patent application, draft A**
Prepared 21 September 2026. Not reviewed by a patent attorney. Not filed.
Application number: none.
See `patents/drafts_2026/PATENTABILITY_ASSESSMENT_2026.md` for what this draft
does and does not survive on, and `patents/PATENT_GAP_ANALYSIS_2026.md` for why
the 2025 filings are superseded.

---

## Title

Damage-Tolerant Data Storage in Living Cells Using a Genetically Encoded
Bistable State Inherited Through Cell Division

## Inventors

Dayana Sanchez, Jacqueline Solano

## Field

Data storage in engineered living cells. More specifically, storing arbitrary
binary data as the state of a genetic regulatory circuit in a bacterial
population, such that the stored data survives destruction of most of the
population and is restored by ordinary cell division during regrowth.

## Background

Existing approaches to storing data in living cells fall into three groups, and
each has a limitation this application addresses.

**Membrane-potential storage.** Yang, Bialecka-Fornal, Weatherwax, Larkin,
Prindle, Liu, Garcia-Ojalvo and Süel, "Encoding membrane potential-based memory
within a microbial community," *Cell Systems* 10(5):417-423 (2020), DOI
10.1016/j.cels.2020.04.002, write arbitrary spatial patterns into a living
*Bacillus subtilis* biofilm by brief blue light exposure and read them back
non-destructively at single-cell resolution for over three hours. The stored
state is a persistent modification of existing yugO potassium channel protein,
which the authors describe as arising from "enduring modifications at the
protein level" rather than from positive feedback. A protein-level modification
is diluted among daughter cells at division and is not replicated, so the
approach depends on the cells being predominantly non-replicating, which the
authors note is the case in the biofilms studied. Such a store does not survive
an event that destroys most of the population and requires regrowth.

**DNA-sequence storage.** Yachie and Tomita, "Alignment-Based Approach for
Durable Data Storage into Living Organisms," *Biotechnology Progress* (2007),
encode data as genomic sequence in *B. subtilis*, read by sequencing. Sequence
storage is inherently archival and write-once at a given locus, and reading it
destroys the sample.

**DNA-orientation latches.** Bonnet, Subsoontorn and Endy, "Rewritable digital
data storage in live cells via engineered control of recombination
directionality," *PNAS* 109(23):8884-8889 (2012), DOI 10.1073/pnas.1202344109,
store one bit as the orientation of a DNA segment, set by an integrase and reset
by an integrase plus excisionase, stable over 100 cell divisions without
selection, read by fluorescence. This is rewritable and heritable through
ordinary growth. It does not address recovery of a population's stored state
after most of the population has been destroyed, and each rewrite requires
enzymatic inversion of the register rather than a change of regulatory state.

**Transcriptional bistable switches.** Gardner, Cantor and Collins,
"Construction of a genetic toggle switch in *Escherichia coli*," *Nature*
403:339-342 (2000), DOI 10.1038/35002131, established a two-repressor mutually
inhibitory topology with two stable states, switched by transient induction and
read by fluorescence. Huang, Yu, Lee et al., *Nature Communications* 16:9414
(2025), DOI 10.1038/s41467-025-64457-0, build and quantitatively validate
recombinase-based genetic memory circuits. Neither addresses data storage
surviving destruction and regrowth of the host population, nor recovery of
stored data from a small surviving fraction.

**The unmet need.** No known system stores arbitrary binary data in a living
substrate such that the data survives physical destruction of the great majority
of the substrate and is autonomously restored to full fidelity as the substrate
regrows. That is the subject of this application.

## Summary

Arbitrary binary data is stored in a population of engineered bacterial cells,
one bit per addressable region, as the state of a mutually inhibitory
two-repressor transcriptional circuit resident in each cell of that region. The
circuit has two stable states. Each state is written by a transient induction
pulse applied to one arm of the circuit, after which the state persists with no
further input.

Because the stored state is the concentration ratio of two repressor proteins
maintained by an ongoing genetic feedback loop, and not a modification of a
fixed number of protein molecules, cell division reproduces the state rather
than diluting it: each daughter cell inherits both the circuit and its current
operating point, and the feedback loop re-establishes the same stable state in
the daughter. Consequently, destroying an arbitrary fraction of the region and
allowing the survivors to regrow restores the stored bit across the regrown
population, provided at least one cell holding the correct state survives and
divides.

In simulation of this mechanism (`simulations/bsubtilis_07_colony_regrowth.py`
and `simulations/bsubtilis_13_reporter_colony_regrowth.py` in the inventors'
codebase), a region recovered to full fidelity of the stored bit from as little
as two percent of its cells surviving, and a two-colour transcriptional reporter
readout tracked the underlying genetic state with no measured gap at every
surviving fraction tested. These are simulation results and are stated as such;
no wet-lab measurement of this mechanism exists as of the filing date of this
application.

The state is read non-destructively through a transcriptional reporter, with one
detectable output gene placed under the control of each arm of the circuit, so
that the two stable states produce mutually exclusive outputs. Readout does not
require measuring membrane potential and is therefore not subject to
interference from the host organism's own endogenous electrical signalling.

## Detailed description

### Storage element

Each addressable region contains a population of cells carrying a first
repressor gene under the control of a first promoter and a second repressor gene
under the control of a second promoter, wherein the first repressor represses
the second promoter and the second repressor represses the first promoter. Each
promoter is additionally responsive to an inducer that relieves repression of
the opposing arm, providing the write input.

In one embodiment the host is *Bacillus subtilis* and the promoters and
ribosome binding sites are drawn from a characterised chassis-matched part
library (the Bacillus BioBrick Box). Simulation of this topology
(`simulations/bsubtilis_01_gardner_toggle_circuit.py`) identified a design
constraint that is part of this disclosure: if the strengths of the two
promoters are substantially mismatched, the circuit becomes monostable and
cannot hold both states. Matched or near-matched promoter strength is therefore
a requirement of the storage element, not merely a preference.

### Write

A bit is written to a region by transiently applying the inducer corresponding
to the desired state. The pulse need not be maintained. Once the circuit has
settled into the addressed state, the input is removed and the state persists
through the feedback loop alone, consuming no addressed input.

Write addressing may be spatial, for example by applying an optical or chemical
induction stimulus to a defined region of a surface-grown population, giving one
bit per region and an array of regions per substrate.

### Read

Each arm of the circuit additionally drives a detectable reporter, the two
reporters being distinguishable from one another. In one embodiment these are
two spectrally separated fluorescent proteins. In another they are a
bioluminescent enzyme on one arm and none on the other, so that the bit is read
as presence or absence of light emission without an excitation source. Reading
does not consume or destroy the population, so the same region may be read
repeatedly.

Reading at single-cell resolution across a region additionally distinguishes a
genuinely bistable population, which shows two separated modes, from a
population at an intermediate expression level, which shows one. This
distinction is the evidence that the stored state is bistable rather than
graded.

### Recovery after damage

Damage is any event that destroys a fraction of the cells in a region:
mechanical disruption, desiccation, radiation, chemical insult, or thermal
insult. Following such an event, the surviving cells are allowed to regrow under
permissive conditions.

Each surviving cell carries the circuit and its current state. At division, both
daughters receive the circuit and a share of the existing repressor pool, and
the feedback loop drives each daughter to the same stable state as the mother.
Regrowth therefore repopulates the region with cells in the stored state rather
than in a random or reset state. No external rewrite, no reference copy, and no
error-correcting computation outside the cells is required.

A settle interval follows regrowth, during which the regrown population's
reporter output converges before the region is read. In simulation, recovery to
full fidelity occurred at every surviving fraction tested down to two percent.

### Reinforcement during regrowth, optional

Where the number of repressor molecules per cell is small, unequal partition of
the existing repressor pool between daughters at division introduces a risk of
a daughter settling into the wrong state. Simulation
(`simulations/bsubtilis_15_partition_noise_regrowth.py`) found recovery degraded
at approximately one effective repressor molecule per cell. An optional
reinforcement element, in which a damage-responsive or stress-responsive
promoter transiently increases expression of whichever arm currently dominates
and relaxes once regrowth completes, restored full recovery in simulation
(`simulations/bsubtilis_16_damage_sensing_reinforcement.py`). That element is
the subject of a separate application, draft B in this folder, and is recited
here as an optional dependent feature.

### Dormant storage state, optional

Where the host is a spore-forming organism such as *B. subtilis*, the population
may be induced to sporulate for storage and transport, and germinated before
reading. Whether the stored state survives sporulation and germination has not
been tested in simulation or at a bench and is disclosed here as an embodiment
to be reduced to practice, not as a demonstrated result.

### What has not been demonstrated

Stated plainly, because it bears on enablement. As of this draft's date, no part
of this system has been built or measured in a laboratory. All results recited
above are outputs of the inventors' simulations, whose assumptions and
limitations are documented in `docs/SCIENTIFIC_AUDIT_2026.md`. In particular:
the reinforcement element's promoter has not been selected; division is modeled
as inheritance of the mother's concentration plus noise rather than as measured
stochastic partition; and no reporter photobleaching, autofluorescence, or
imaging noise is included.

## Claims

1. A method of storing data in living cells, comprising:
   (a) providing a population of cells in an addressable region, each cell
       comprising a first gene encoding a first repressor operably linked to a
       first promoter and a second gene encoding a second repressor operably
       linked to a second promoter, wherein the first repressor represses the
       second promoter and the second repressor represses the first promoter,
       such that the population has a first stable state and a second stable
       state;
   (b) writing a bit value to the region by transiently applying an input that
       relieves repression of one of the first and second promoters, and
       thereafter removing the input, whereby the written state persists without
       further input;
   (c) destroying a portion of the cells of the region, leaving a surviving
       portion;
   (d) permitting the surviving portion to divide and repopulate the region,
       whereby each dividing cell transmits the written state to its daughters
       through inheritance of the first and second genes and of the repressor
       present at division; and
   (e) reading the bit value from the repopulated region.

2. The method of claim 1, wherein reading comprises detecting a first reporter
   operably linked to the first promoter and a second reporter operably linked to
   the second promoter, the first and second reporters being mutually
   distinguishable, and wherein reading does not destroy the population.

3. The method of claim 2, wherein the first and second reporters are
   spectrally distinguishable fluorescent proteins.

4. The method of claim 2, wherein at least one reporter is a bioluminescent
   enzyme and reading is performed without an excitation light source.

5. The method of claim 2, wherein reading comprises resolving individual cells
   and distinguishing a bimodal distribution of reporter output, indicating a
   bistable state, from a unimodal distribution.

6. The method of claim 1, wherein the cells are *Bacillus subtilis*.

7. The method of claim 1, wherein the first and second promoters are selected to
   have substantially matched transcriptional strength, such that the circuit is
   bistable rather than monostable.

8. The method of claim 1, wherein writing is addressed spatially to one of a
   plurality of regions of a substrate, each region storing one bit.

9. The method of claim 1, wherein destroying comprises one or more of mechanical
   disruption, desiccation, ionising radiation, chemical insult, and thermal
   insult.

10. The method of claim 1, further comprising, during the repopulating step,
    transiently increasing expression of whichever of the first and second genes
    is currently dominant in a cell, and relaxing said increase upon completion
    of repopulation.

11. The method of claim 1, further comprising, after writing and before reading,
    inducing the population to form spores, and germinating the spores prior to
    reading.

12. The method of claim 1, wherein reading is performed a plurality of times on
    the same population without rewriting between readings.

13. The method of claim 1, further comprising rewriting the region to the
    opposite bit value by transiently applying the input corresponding to the
    other of the first and second promoters.

14. A data storage article comprising a substrate carrying a plurality of
    addressable regions, each region containing a population of engineered cells
    according to claim 1(a), wherein the state of each region encodes one bit,
    and wherein the article is configured such that a region whose cell
    population is partially destroyed recovers its encoded bit upon regrowth of
    surviving cells of that region.

15. The article of claim 14, wherein each region further comprises first and
    second mutually distinguishable reporters operably linked respectively to the
    first and second promoters.

16. A system comprising the article of claim 14, a write device configured to
    apply a spatially addressed transient induction stimulus to a selected
    region, and a read device configured to detect the reporter output of a
    selected region without destroying it.
