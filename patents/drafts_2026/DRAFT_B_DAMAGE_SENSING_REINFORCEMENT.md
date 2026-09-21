# DRAFT, NOT FILED

**Provisional patent application, draft B**
Prepared 21 September 2026. Not reviewed by a patent attorney. Not filed.
Application number: none.
Depends on draft A in this folder for the underlying storage element.

---

## Title

Damage-Responsive Reinforcement of a Stored Genetic State During Population
Regrowth

## Inventors

Dayana Sanchez, Jacqueline Solano

## Field

Preserving the fidelity of data stored as a genetic regulatory state in a
population of living cells during the period in which that population is
regrowing after damage.

## Background

Draft A of this family describes storing a bit as the state of a mutually
inhibitory two-repressor circuit, and recovering that bit after damage by
allowing surviving cells to divide and repopulate the region. That mechanism
depends on each division transmitting the mother cell's state to both daughters.

The transmission is not perfect. The state is carried by a finite pool of
repressor protein, and at division that pool is divided between two daughters.
Where the pool is large, the split is close to even and both daughters resume the
mother's state. Where the pool is small, the split is proportionally noisier, and
a daughter can receive too little of the dominant repressor to hold the state,
whereupon the opposing arm takes over and that daughter, and its descendants,
carry the wrong bit. Simulation by the inventors
(`simulations/bsubtilis_15_partition_noise_regrowth.py`) found recovery
degrading in this way at approximately one effective repressor molecule per
cell.

This risk is concentrated in a specific window. Ordinary steady-state growth of
an undamaged population dilutes errors across a large number of cells already
holding the correct state. Regrowth after severe damage does the opposite: a
small number of survivors undergo many successive divisions, so an error
introduced in an early division is amplified into a large fraction of the
regrown population. The period of greatest vulnerability is therefore exactly the
period of regrowth.

The bacterial SOS response is a real, well characterised system in which DNA
damage is detected and drives a transcriptional program. RecA senses
single-stranded DNA arising from damage and promotes cleavage of the LexA
repressor, de-repressing the SOS genes (Maslowska, Makiela-Dzbenska and
Fijalkowska, *Environmental and Molecular Mutagenesis* (2019), DOI
10.1002/em.22267; Kaushik, Tiwari and Tiwari, *International Journal of
Biological Macromolecules* (2022), DOI
10.1016/j.ijbiomac.2022.07.176). No known prior art couples a damage-responsive
regulatory element to a memory circuit's own current state for the purpose of
preserving stored data through regrowth.

## Summary

A reinforcement element is added to the storage circuit of draft A. The element
is driven by a promoter that is activated by cellular damage or by the stress
conditions accompanying damage, and its output transiently increases the
expression of whichever arm of the memory circuit is currently dominant in that
cell, and only that arm.

The element is therefore self-referential rather than externally addressed: it
does not know or need to know which bit is stored. It amplifies the state
already present. During regrowth, this raises the repressor pool in each
dividing cell, so that the partition of that pool between daughters is
proportionally less noisy and each daughter more reliably resumes the mother's
state. When the damage signal decays, the element relaxes and the circuit
returns to its ordinary operating point, so the elevated expression is a
transient cost paid only when it is needed.

In simulation (`simulations/bsubtilis_16_damage_sensing_reinforcement.py`), a ten
fold transient increase in expression of the dominant arm during the regrowth
window restored full recovery of the stored bit at the condition where partition
noise had degraded it, including at the most severe damage level tested, and a
five fold increase recovered most of the loss. These are simulation results. No
wet-lab measurement of this element exists as of the date of this draft, and the
specific damage-responsive promoter to be used has not been selected.

## Detailed description

### Element

Each cell of the addressable region comprises, in addition to the storage circuit
of draft A:

- a damage-responsive promoter, being a promoter whose transcriptional activity
  increases in response to DNA damage, envelope stress, desiccation, or another
  condition accompanying the damage events against which the store is to be
  protected; and
- a reinforcement output operably linked to that promoter and arranged such that
  its effect is applied to whichever of the first and second repressor arms is
  currently dominant in that cell.

### Arrangements that make the reinforcement state-selective

Three arrangements are disclosed, each achieving the same selectivity by a
different route.

**Arrangement one, symmetric amplifier under mutual repression.** A copy of the
reinforcement output is placed on each arm, each copy driven by the
damage-responsive promoter and each additionally repressed by the opposing
repressor. Because the opposing repressor is abundant only in the non-dominant
arm's state, only the copy on the dominant arm escapes repression, so damage
amplifies the dominant arm alone.

**Arrangement two, shared activator with state-gated targets.** The
damage-responsive promoter drives a single activator, and each arm's promoter
carries a binding site for that activator. The arm that is currently
transcriptionally active is the arm whose promoter the activator can act on, so
the activator's effect is confined to the dominant arm.

**Arrangement three, damage-gated stabilisation.** The damage-responsive
promoter drives a factor that reduces degradation of repressor protein generally,
without distinguishing the arms. Because the dominant arm's repressor is present
at far higher concentration, a proportional reduction in degradation increases
the dominant pool far more in absolute terms than the minority pool, preserving
the ratio that encodes the state while raising the absolute molecule count that
partition noise acts on.

### Operation

Before damage, the damage-responsive promoter is inactive and the circuit
operates at its ordinary level.

On damage, surviving cells experience the damage or stress condition, the
promoter activates, and the dominant arm's expression rises. Through the regrowth
period, each division partitions a larger repressor pool, reducing the
probability that a daughter falls below the threshold needed to hold the state.

On completion of regrowth, the damage or stress condition abates, the promoter's
activity decays, and expression returns to the ordinary level.

### Limitations disclosed

Three, stated because they are real and because a reader will otherwise find
them.

First, the reinforcement is modeled in simulation as an on/off switch tied to
completion of regrowth. A real damage-responsive promoter has its own activation
and decay kinetics, which have not been modeled here and which determine whether
the element is still active during the divisions that matter.

Second, a strongly reinforced circuit may resist a legitimate subsequent write.
The same mechanism that protects the stored bit against noise opposes an
intentional change of the bit. In one embodiment, writing is therefore performed
only after the reinforcement has relaxed, or the write stimulus is applied at an
amplitude sufficient to overcome the reinforced state. This trade-off has not
been tested.

Third, in the spore-forming embodiment the relationship between this element and
the sporulation regulatory network is not characterised, and one candidate
potassium channel promoter relevant to this project's readout sits on the same
SinR/Spo0A regulatory node from which the circuit's chassis promoters are drawn
(Lundberg, Becker and Choe, *PLoS ONE* 8(5):e60993 (2013), DOI
10.1371/journal.pone.0060993). Promoter selection must account for that overlap.

## Claims

1. A method of preserving data stored in a population of living cells, wherein
   the data is stored as the state of a circuit comprising a first repressor
   operably linked to a first promoter and a second repressor operably linked to
   a second promoter, the first repressor repressing the second promoter and the
   second repressor repressing the first promoter, the method comprising:
   (a) providing in each cell a damage-responsive promoter and a reinforcement
       output operably linked thereto;
   (b) upon damage to the population, activating the damage-responsive promoter
       in surviving cells, whereby expression of whichever of the first and
       second repressors is currently dominant in a given cell is transiently
       increased in that cell;
   (c) permitting the surviving cells to divide and repopulate, whereby the
       increased repressor pool reduces the probability that a daughter cell
       adopts the opposite state; and
   (d) relaxing said transient increase upon abatement of the damage condition.

2. The method of claim 1, wherein the reinforcement output comprises a first copy
   operably linked to the damage-responsive promoter and repressible by the
   second repressor, and a second copy operably linked to the damage-responsive
   promoter and repressible by the first repressor, whereby only the copy
   corresponding to the dominant arm is expressed.

3. The method of claim 1, wherein the damage-responsive promoter drives an
   activator, and each of the first and second promoters comprises a binding site
   for said activator, whereby the activator acts on whichever promoter is
   currently active.

4. The method of claim 1, wherein the reinforcement output reduces degradation of
   repressor protein without distinguishing between the first and second
   repressors, whereby the absolute quantity of the dominant repressor is
   increased while the ratio encoding the state is preserved.

5. The method of claim 1, wherein the damage-responsive promoter is responsive to
   DNA damage.

6. The method of claim 5, wherein the damage-responsive promoter is a promoter of
   the bacterial SOS response.

7. The method of claim 1, wherein the damage-responsive promoter is responsive to
   one or more of envelope stress, desiccation, oxidative stress, and heat shock.

8. The method of claim 1, wherein the cells are *Bacillus subtilis*.

9. The method of claim 1, wherein the transient increase is applied only while
   the population is below a target density and is relaxed upon reaching that
   density.

10. The method of claim 1, further comprising writing a new value to the circuit
    after said relaxing, whereby the write stimulus is not opposed by the
    reinforcement.

11. An engineered cell comprising a first repressor gene operably linked to a
    first promoter, a second repressor gene operably linked to a second promoter
    wherein each repressor represses the other's promoter, a damage-responsive
    promoter, and a reinforcement output operably linked to the damage-responsive
    promoter and arranged to increase expression selectively of whichever of the
    first and second repressor genes is currently dominant in the cell.

12. A population of the cells of claim 11 arranged in an addressable region of a
    substrate, wherein the state of the circuit in said region encodes one bit of
    data.
