# DRAFT, NOT FILED

**Provisional patent application, draft C**
Prepared 21 September 2026. Not reviewed by a patent attorney. Not filed.
Application number: none.
This is the most speculative of the three drafts and has the closest prior art.
Read `patents/drafts_2026/PATENTABILITY_ASSESSMENT_2026.md` section 3 before
filing it, and file it narrow or not at all.

---

## Title

Encoding Data as a Genetically Determined Phase Relationship to an Endogenous
Bioelectric Oscillation in a Cell Population

## Inventors

Dayana Sanchez, Jacqueline Solano

## Field

Reading data stored in a population of living cells electrically, in the presence
of the population's own endogenous electrical oscillation, by encoding the data
in the phase relationship between a cell's electrical response and that
oscillation rather than in an absolute voltage level.

## Background

*Bacillus subtilis* biofilms run an endogenous electrical oscillation. Starving
interior cells release potassium and hyperpolarise, and the signal propagates
outward as a wave, temporarily suppressing neighbouring cells' nutrient uptake so
that nutrients reach the interior. Reported propagation speed is on the order of
tens of microns per minute and the reported period is on the order of hours, with
onset once a biofilm reaches a threshold size (Ford, Fisher, Prindle and Chopp,
*Bulletin of Mathematical Biology* 83(5):60 (2021), DOI
10.1007/s11538-021-00887-3; Mulder, Peters Kostman, Almodaimegh, Edge and Larkin,
*PLOS Computational Biology* 21(12):e1013746 (2025), DOI
10.1371/journal.pcbi.1013746). The channel carrying the signal is yugO
(Lundberg, Becker and Choe, *PLoS ONE* 8(5):e60993 (2013), DOI
10.1371/journal.pone.0060993).

This oscillation is a problem for any scheme that encodes data as an absolute
membrane-potential level, because the oscillation moves a cell's potential
independently of whatever the data says it should be. Simulation by the
inventors (`simulations/bsubtilis_08_native_oscillation_interference.py`) found a
single-instant voltage read of an otherwise correct stored bit collapsing to
near chance at ambient oscillation amplitudes well below the documented range,
and further simulations found that integrating the read over close to a full
oscillation period recovers accuracy
(`simulations/bsubtilis_09_eis_readout_interference.py`), that timing a fast read
to a predicted quiet moment does not
(`simulations/bsubtilis_11_phase_locked_readout.py`), and that substantially
weakening the coupling helps only at the milder end of the amplitude range
(`simulations/bsubtilis_12_decoupled_channel_readout.py`).

**The closest prior art, which must be distinguished.** Yang, Bialecka-Fornal,
Weatherwax, Larkin, Prindle, Liu, Garcia-Ojalvo and Süel, "Encoding membrane
potential-based memory within a microbial community," *Cell Systems*
10(5):417-423 (2020), DOI 10.1016/j.cels.2020.04.002, expose a region of a
living *B. subtilis* biofilm to brief blue light, which leaves a fraction of
yugO subunits persistently conducting in those cells. Exposed and unexposed
cells then respond to potassium oscillations in anti-phase, anti-correlated at
zero lag and maximally correlated at half the imposed period. The authors
explicitly frame this as producing "a clear signal that is either 'on' or 'off,'
as in traditional digital memory," readable at single-cell resolution for over
three hours.

Yang et al. therefore anticipate the generic proposition that a cell's phase
relationship to this oscillation can carry a bit, in this organism. What they do
not disclose is a phase state that is **determined by a genetic regulatory
state, rewritable through that regulatory state, and inherited by daughter cells
at division.** Their state is a persistent protein-level modification of existing
channel protein, which their own discussion distinguishes from positive feedback
and which dilutes at division, and their biofilm cells are described as
predominantly non-replicating. That is the distinction this application claims.

## Summary

A bit is stored as the state of a mutually inhibitory two-repressor
transcriptional circuit, as in draft A of this family. The circuit's output is
coupled to the cell's potassium response such that the state of the circuit
determines not the cell's absolute membrane potential but the **sign of the
cell's response to the ambient potassium oscillation**: in one circuit state the
cell responds in phase with the oscillation, and in the other it responds in
anti-phase.

The bit is read by recording the cell's electrical trace over an interval
spanning a portion of the oscillation period, recording a reference trace of the
ambient oscillation separately, and taking the sign of the correlation between
the two. The oscillation that defeats absolute-level encoding thereby becomes the
carrier that makes the reading possible, and an ambient oscillation of larger
amplitude improves rather than degrades the reading.

In simulation (`simulations/bsubtilis_18_phase_encoded_readout.py`), holding the
circuit model and noise magnitudes identical to the inventors' level-encoding
simulation and changing only what the voltage tracks, phase encoding read
correctly at essentially all of the documented ambient amplitude range while
level encoding stayed near chance, and phase encoding failed at zero ambient
amplitude, which is the expected behaviour of the control since with no carrier
there is no phase to read. These are simulation results, stated as such. The
genetic-circuit-to-phase-response coupling has not been built in any organism.

## Detailed description

### Storage element and write

As in draft A: a first repressor under a first promoter and a second repressor
under a second promoter, each repressing the other's promoter, giving two stable
states, written by a transient induction pulse and thereafter self-maintaining,
and inherited by daughter cells at division.

### Coupling the circuit state to the sign of the potassium response

The circuit's two states are coupled to the cell's potassium handling such that
the two states produce opposite-sign responses to the same ambient potassium
change. Embodiments disclosed:

**Conductance-mode coupling.** One circuit state drives expression of a
potassium channel or channel variant whose conductance leaves the cell passively
following extracellular potassium, and the other state does not, leaving the cell
under active counter-regulation. Cells in the first state and cells in the second
state then respond oppositely to the same potassium wave, which is the same
physical mechanism Yang et al. produce optically, driven here from a genetic
regulatory state instead.

**Transporter-mode coupling.** One circuit state drives an efflux element and the
other drives an influx or retention element, so that an ambient potassium
increase depolarises one population and hyperpolarises the other.

**Regulator-mode coupling.** One circuit state drives a regulator of the native
channel's own activity, inverting the cell's response to the wave without
introducing a heterologous channel.

### Read

Reading comprises:

1. recording a reference trace of the ambient oscillation, from a region not
   carrying stored data, from an added reference reporter, or from the population
   average;
2. recording the trace of the region to be read over an interval;
3. computing the correlation between the two traces; and
4. assigning the bit from the sign of that correlation.

The read is non-destructive and repeatable. It does not require knowing the
oscillation's phase in advance, which is the bootstrapping problem that defeats
timed fast reads, because the reference trace is measured concurrently rather
than predicted.

### Requirements and costs of this scheme, disclosed

Three, taken from the inventors' own simulation sweeps, all of them unmeasured
for a genetically driven version:

**Read duration.** Correlation-based reading requires an interval long enough to
span a meaningful fraction of the oscillation period. In simulation a read on the
order of an hour performed well and a read of ten minutes was near chance. This
makes the scheme suitable for a stored archive read occasionally, and unsuitable
for fast random access.

**Measurement noise ceiling.** Performance degraded once measurement noise rose
past roughly the level of a weak ambient oscillation, at the low end of the
amplitude range.

**Coupling strength.** The scheme requires the stored bit to strongly determine
the cell's potassium response. In simulation, weak coupling degraded accuracy
substantially.

**A requirement that conflicts with another line of this project's work, stated
plainly.** The inventors' other work on level-based readout recommends weakening
or deleting yugO to reduce interference. This scheme requires the opposite: the
native oscillation must be present and reasonably strong, because it is the
carrier. A single strain cannot do both. Whichever readout is pursued sets the
chassis, and this application's embodiments therefore require a chassis retaining
the native oscillation.

### What has not been demonstrated

No part of this scheme has been built. The genetic-circuit-to-channel coupling
that makes the circuit state determine the response sign does not exist in any
organism, in this project or in the prior art. Yang et al. produce the
anti-phase behaviour optically and at the protein level, not genetically. The
three requirements above are simulation-derived and unmeasured. This is disclosed
so that the specification is not read as claiming a reduction to practice that
has not occurred.

## Claims

1. A method of reading data stored in a population of living cells subject to an
   endogenous bioelectric oscillation, comprising:
   (a) storing a bit in a region of the population as the state of a circuit
       comprising a first repressor operably linked to a first promoter and a
       second repressor operably linked to a second promoter, each repressor
       repressing the other's promoter;
   (b) coupling the state of the circuit to the cell's ion transport such that a
       first state of the circuit causes the cell to respond to the oscillation
       with a first sign and a second state causes the cell to respond with the
       opposite sign;
   (c) obtaining a reference trace of the oscillation;
   (d) obtaining an electrical trace of the region over an interval; and
   (e) assigning the stored bit from the sign of the correlation between the
       reference trace and the region's trace.

2. The method of claim 1, wherein the oscillation is the population's own
   endogenous potassium-mediated oscillation and is not externally imposed.

3. The method of claim 1, wherein the coupling of step (b) causes the cell in one
   circuit state to passively follow extracellular potassium and in the other
   circuit state to counter-regulate its membrane potential.

4. The method of claim 1, wherein the coupling of step (b) comprises expression of
   a potassium channel under the control of one arm of the circuit.

5. The method of claim 1, wherein the coupling of step (b) comprises expression of
   an efflux element under one arm of the circuit and a retention or influx
   element under the other arm.

6. The method of claim 1, wherein the reference trace is obtained concurrently
   with the region's trace from a region of the population not carrying stored
   data.

7. The method of claim 1, wherein the interval of step (d) spans at least a
   substantial fraction of one period of the oscillation.

8. The method of claim 1, wherein reading is non-destructive and is repeated on
   the same region without rewriting.

9. The method of claim 1, wherein the stored bit is transmitted to daughter cells
   at division through inheritance of the circuit, whereby the phase relationship
   encoding the bit is re-established in the daughter cells.

10. The method of claim 9, further comprising destroying a portion of the region
    and permitting surviving cells to repopulate it, whereby the stored bit and
    its phase relationship are restored in the repopulated region.

11. The method of claim 1, wherein the cells are *Bacillus subtilis* of a strain
    retaining a functional native potassium channel required for the endogenous
    oscillation.

12. The method of claim 1, further comprising rewriting the stored bit by
    transiently applying an induction input to one arm of the circuit, whereby the
    cell's phase relationship to the oscillation is inverted.

13. An engineered cell comprising a first repressor gene operably linked to a
    first promoter, a second repressor gene operably linked to a second promoter
    wherein each repressor represses the other's promoter, and an ion transport
    element under the control of the circuit such that the circuit's state
    determines the sign of the cell's membrane potential response to an ambient
    potassium oscillation.

14. A system comprising a population of the cells of claim 13, a reference sensor
    arranged to record the ambient oscillation, a sensor arranged to record the
    electrical trace of an addressed region, and a processor configured to assign
    a bit value from the sign of the correlation between the two recorded traces.
