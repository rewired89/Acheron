# Simulation Map

Every simulation in this project, what it tested, and what it found. Each entry
gives the plain-English version first and the technical version second.

**How to read this file.** The plain-English line is what the result means. The
technical line is what a scientist would need to check or reproduce it, with the
caveat that limits the claim. Where a result is logged in
`docs/SCIENTIFIC_AUDIT_2026.md`, the Part number is given, and that document is
the authority if the two ever disagree.

**Everything here is simulation.** Nothing in this folder is a measurement of
living cells. The bench protocols that would produce real measurements are in
`experiments/`. How the whole project fits together is in `docs/REASONING_MAP.md`.

**Naming.** Files are named `<organism>_<number>_<topic>.py`. The number is
reading order within that track, roughly the order the work happened, so the
folder reads as a story rather than an alphabetical pile.

---

## The four tracks

| Prefix | What it is | Status |
|---|---|---|
| `planarian_` | The original approach: voltage patterns held in flatworm tissue by gap-junction coupling | Weakest evidence, kept as a fallback |
| `bsubtilis_` | The current primary approach: an engineered genetic toggle switch in bacteria | Best grounded, everything active is here |
| `methylation_` | An alternative memory mechanism: chemical tags on DNA copied at each division | Real fidelity numbers exist, both from the wrong organism |
| `crossorganism_` | Runs the tracks side by side and ranks them by hidden risk | This is where "B. subtilis first" came from |

---

# Planarian track

The original idea. A bit is a voltage level held in flatworm tissue. This track
is preserved because planaria remain the long-term target, but the project's own
cross-organism comparison ranks it as the least trustworthy of the three
mechanisms, because its central assumption (how strongly neighbouring cells pull
each other's voltage around) has never been measured in real planarian tissue.

### `planarian_01_bioelectric_persistence.py`
**What it tested, plainly:** whether a bit written as a voltage into a patch of
flatworm tissue would still be readable a day later, with nothing actively
holding it there.
**What it found, plainly:** yes, perfectly. That answer later turned out to be
an artifact of the model assuming zero noise. See `planarian_02`.
**Technically:** a simplified BETSE-inspired 2D gap-junction-coupled tissue
model, resistive nearest-neighbour coupling, no stochastic terms. Reports 100%
bit integrity at 24h. Superseded as a standalone claim by Part 8 of the audit.
Treat its output as the noise-free upper bound, not as a result.

### `planarian_02_noise_floor.py`
**What it tested, plainly:** the same thing again, but with realistic biological
messiness switched on.
**What it found, plainly:** the bit falls apart. After a day you are reading a
coin flip. This is the single most important negative result the project has.
**Technically:** injects four noise sources (ion-channel shot noise,
cell-to-cell variability, metabolic fluctuation, thermal noise) into
`planarian_01`'s model. Integrity falls from 100% at zero noise to 66.7% (mild),
57.8% (realistic) and 51.5% (severe), with SNR collapsing from 9.7:1 to 0.1:1.
Also sweeps a phenomenological feedback strength `bistable_k` and finds reliable
storage needs feedback roughly 15-20x stronger than the model calibrates as
naturally plausible. Audit Part 8. The 15-20x figure is a relative benchmark
against a modelling knob, not a measurable biological constant.

### `planarian_03_optogenetic_write_fidelity.py`
**What it tested, plainly:** how accurately you can actually write a bit with
light, before any question of whether it sticks.
**What it found, plainly:** writing is lossy too. Cells make different amounts
of the light-sensitive protein, and light gets dimmer deeper into tissue, so a
meaningful fraction of cells never reach the target voltage.
**Technically:** models ChR2 expression as log-normal, light attenuation by
Beer-Lambert (mu_tissue about 2.0 per mm at 470 nm), and ChR2 photocurrent
kinetics, reporting written-versus-intended fidelity. Run the file for the
current numbers.

### `planarian_04_tile_crosstalk_map.py`
**What it tested, plainly:** how far apart two stored bits have to sit before
they stop bleeding into each other.
**What it found, plainly:** there is a minimum spacing, and it sets the
storage density ceiling.
**Technically:** places two encoded tiles at varying separation under the tuned
gap-junction conductance and measures crosstalk percentage at 24h against a 5%
bar, converting the answer into bits per square millimetre. Run the file for
the current numbers.

### `planarian_05_monte_carlo_ber.py`
**What it tested, plainly:** not "does one bit survive" but "across a thousand
attempts, how often does it fail, and how bad is the worst case".
**What it found, plainly:** gives a real failure-rate distribution instead of a
single optimistic number, and says how much redundancy you would need.
**Technically:** 1000 independent trials drawing per-trial R_mem and g_gap
variability (log-normal, CV 25%), per-timestep ion-channel shot noise (sigma 5
mV), metabolic noise (uniform 5-15%) and write fidelity. Bit error defined as
the cluster majority vote crossing V_mid = -45 mV. Run the file for the
distributions.

### `planarian_06_regeneration_data_loss_window.py`
**What it tested, plainly:** if a chunk of tissue dies and grows back, how long
is the system running without its safety net.
**What it found, plainly:** a vulnerable window of roughly a day to a day and a
half, during which a second failure loses data.
**Technically:** models the detect-mobilise-divide-differentiate-re-encode
timeline with literature-derived timing distributions, giving a 24-33h window of
degraded redundancy. The 30-minute detection latency it assumes is a polling
schedule, not a measured signal-detection time, which is what
`bsubtilis_06_damage_detection_trigger.py` was written to challenge.

### `planarian_07_field_mediated_persistence.py`
**What it tested, plainly:** whether adding a second, published mechanism (cells
generating a shared electric field, not just touching their neighbours) makes
patterns last longer.
**What it found, plainly:** run the file. This one runs someone else's published
model unmodified rather than a reimplementation, which is the point of it.
**Technically:** drives Manicka and Levin's `cellularFieldNetwork` from
`third_party/electric_morphogenesis/` unmodified, with a written bit-cluster
pattern, comparing field-on against gap-junction-only persistence. Attribution
and what is vendored versus reimplemented are in `docs/THIRD_PARTY_METHODS.md`.

### `planarian_08_bio_raid_ecc.py`
**What it tested, plainly:** the RAID-style idea of keeping three copies of every
bit and voting, plus periodically repairing drift.
**What it found, plainly:** the architecture works as an architecture. What it
cannot do is rescue a bit whose signal has already been drowned in noise, which
`planarian_02` established separately.
**Technically:** multi-chamber simulator with 3-way replication and majority
voting, weekly scrubbing, donor selection thresholds, rebuild throttling, tile
degradation and state migration, over 90-day or 1-year horizons. Audit Part 8
Finding 3 is the limit on it: per Condorcet's jury theorem, voting across copies
that are each no better than chance manufactures nothing.

### `planarian_09_regrowth_state_inheritance.py`
**What it tested, plainly:** if the animal is cut and heals itself, does the new
tissue inherit the stored bit or come back blank.
**What it found, plainly:** it inherits, down to very few surviving cells. But
this result leans on an assumption nobody has measured.
**Technically:** models a fragment as a surviving fraction holding the correct
state plus a naive neoblast-derived fraction, coupled by a mean-field term
borrowed from the bacterial biofilm case. Recovers above the 70% bar from about
2% survivors. The coupling strength is the weakest assumption in the project and
is called out as such in audit Part 13. Reuses `bsubtilis_01`'s circuit
dynamics rather than inventing new physics.

### `planarian_10_bionet_propagation.py`
**What it tested, plainly:** whether living tissue could act as a cable linking
separate storage chips.
**What it found, plainly:** exploratory. This is the most speculative file in
the repository and nothing downstream depends on it.
**Technically:** voltage wave propagation along gap-junction-coupled cell chains
between Bio-RAID nodes. Belongs to the Phase 3 vision documents, not to any
current claim or roadmap item.

---

# B. subtilis track

The current primary approach, and where everything active is happening. A bit is
the state of an engineered genetic toggle switch inside bacteria. Chosen because
its inheritance mechanism is not an assumption: when a bacterium divides, the
proteins holding the state physically go into both daughters. That is what cell
division does, not a hypothesis about it.

### `bsubtilis_01_gardner_toggle_circuit.py`
**What it tested, plainly:** replacing the vague "we need some strong feedback"
placeholder with an actual circuit built from real, off-the-shelf parts.
**What it found, plainly:** the circuit works, and it surfaced a hard design
rule. If the two halves of the switch are badly mismatched in strength, it stops
being a switch at all. It quietly becomes a circuit with only one setting, so
whatever you write, you read back the same thing.
**Technically:** the Gardner, Cantor and Collins (2000) two-repressor ODE
(`du/dt = alpha1/(1+v^beta) - u`, `dv/dt = alpha2/(1+u^gamma) - v`, beta =
gamma = 2), with promoter strength ratios drawn from the Bacillus BioBrick Box's
characterised range. 100% fidelity at 24h for strength ratios 1.0 through 10.0;
at 0.1 bistability is lost entirely and fidelity floors at 50%. Audit Part 9.
The repressor-to-membrane-voltage link it maps to is unbuilt and unmeasured in
any organism; the candidate channel is yugO (audit Part 14). This file is the
dependency for almost everything below it.

### `bsubtilis_02_biofilm_tile_handoff.py`
**What it tested, plainly:** instead of holding one bit forever, hand the data
to a fresh patch of cells before the old patch needs to heal, then repeat.
**What it found, plainly:** the handoff works over a handful of cycles. Running
it much longer exposed a problem, which is the next file.
**Technically:** models self-propagating handoff via biofilm potassium-wave
signalling between colonies. Reports 100% fidelity over its own 5-cycle main().

### `bsubtilis_03_handoff_pool_imperfect_healing.py`
**What it tested, plainly:** the same handoff run 60 times instead of 5, with
healing modelled as imperfect rather than a clean reset.
**What it found, plainly:** a real asymmetry. Storing a 1 stays reliable, around
97%. Storing a 0 decays to about 68%. The cause is not the handoff at all: a
stored 0 spontaneously flips during the ordinary 24-hour hold.
**Technically:** 60 cycles with fresh tiles each handoff, isolating the effect
from pool reuse and imperfect healing. bit=1 holds near 97%, bit=0 decays to
about 68%, with individual runs showing the source tile's voltage already
flipped rails before the next handoff begins.

### `bsubtilis_04_bit_asymmetry_root_cause.py`
**What it tested, plainly:** why storing a 0 is more fragile than storing a 1.
**What it found, plainly:** the metabolic noise term is not symmetric about the
decision point, so it pushes a stored 0 toward the boundary harder than it
pushes a stored 1.
**Technically:** one-at-a-time ablation of each term in `BacterialTile.step()`,
comparing escape rates from V_HIGH versus V_LOW. Identifies metabolic noise's
coupling to V_REST as the primary driver. Tested but did not apply one candidate
fix, recentring V_REST to V_MID, which closes about 60% of the gap.

### `bsubtilis_05_asymmetry_structural_search.py`
**What it tested, plainly:** an automated search for what is left causing the
asymmetry after the main cause was found.
**What it found, plainly:** the remaining cause is the voltage clipping bounds
being lopsided around the decision point.
**Technically:** structural search over `BacterialTile.step()` variants,
following up `bsubtilis_04`'s untested speculation that the asymmetric clip
bounds (-120, 60, midpoint -30, not V_MID = -45) drive the residual gap.

### `bsubtilis_06_damage_detection_trigger.py`
**What it tested, plainly:** before you can heal, you have to notice you were
hurt. How fast can the system actually tell?
**What it found, plainly:** the previously assumed 30-minute detection time was
a guess about how often you check, not a measurement of how fast the signal is
detectable.
**Technically:** models the wound signal against background as an actual
signal-detection problem, challenging
`planarian_06_regeneration_data_loss_window.py`'s assumed Normal(30min, 10min)
polling latency.

### `bsubtilis_07_colony_regrowth.py`
**What it tested, plainly:** kill most of a bacterial colony, let the survivors
regrow it, and see whether the regrown colony still holds the right bit.
**What it found, plainly:** it does, even starting from as few as 2% of the
cells surviving.
**Technically:** runs `bsubtilis_01`'s dynamics through actual binary fission
events over a 30-minute doubling time within a fixed 6-hour post-insult window.
Recovery holds above the 70% bar from about 2% surviving fraction upward. Audit
Part 8. Division here is deterministic inheritance plus ongoing noise, not
stochastic partitioning, which is what `bsubtilis_15` was written to fix.

### `bsubtilis_08_native_oscillation_interference.py`
**What it tested, plainly:** bacteria run their own electrical signalling for
their own reasons, completely unrelated to anything this project builds. Does
that scramble the reading?
**What it found, plainly:** yes, badly. The data can be sitting there perfectly
intact in the genes while the voltage reading comes back as garbage, purely
because you looked at the wrong moment in the colony's natural rhythm.
**Technically:** adds the documented 2-4h potassium-wave period as a sinusoidal
perturbation to membrane voltage only, deliberately not fed into the repressor
state. Genetic fidelity stays at 100% throughout, confirming the scoping works;
the voltage readout collapses to 50-59% at just 10-20 mV of ambient amplitude,
well below the 70 mV worst case. Audit Part 12. The waveform is a sinusoid
because no source paper reports the true shape.

### `bsubtilis_09_eis_readout_interference.py`
**What it tested, plainly:** whether a cheap electrode-based reading method
dodges the problem, since it sweeps over a range rather than taking a snapshot.
**What it found, plainly:** it does not. The hoped-for answer failed. What
actually fixes it is reading for about three hours, one full cycle of the
colony's rhythm.
**Technically:** accuracy stays degraded (50-67%) at every integration window
from 1 to 90 minutes and only recovers (92-100%) at about 180 minutes, one full
oscillation period. Realistic EIS sweeps per Akabuogu et al. 2024 take seconds
to minutes, so a single real sweep is not immune. Audit Part 13. EIS's real
advantage is being cheap and non-destructive enough to repeat, not one-shot
immunity.

### `bsubtilis_10_reporter_readout.py`
**What it tested, plainly:** reading the bit by colour instead of by voltage,
using ordinary glowing proteins.
**What it found, plainly:** the colour tracks the genes exactly. And unlike the
voltage route, nothing published suggests the colony's electrical rhythm can
interfere with it.
**Technically:** same Gardner ODE, read through a two-arm GFP/RFP
transcriptional reporter with maturation and growth-dilution kinetics. Matches
`bsubtilis_01`'s fidelity numbers exactly (100% at matched to 10x ratios, 50% at
0.1) and holds across swept maturation half-life (5-60 min) and measurement
noise (0-30%). Audit Part 16. Deliberately omits an oscillation term because no
cited source proposes that mechanism acting on transcription or translation.

### `bsubtilis_11_phase_locked_readout.py`
**What it tested, plainly:** whether timing a quick read to the calm moment of
the colony's rhythm avoids the problem without a three-hour wait.
**What it found, plainly:** mostly no. Even with perfect timing, a quick read is
a coin flip at anything but the mildest interference, because the drift has
already built up before you look.
**Technically:** compares a blind snapshot, the 180-minute average and a quick
read scheduled at predicted zero-crossings, swept across 0-90 minutes of timing
error. Perfect timing matches the long average only at 10 mV (100%, degrading
gracefully to 86% at +/-5 min and 71% at +/-15 min); at 20 mV and above a
perfectly timed read lands at about 50%. Audit Part 17. The file's own docstring
flags the bootstrapping problem: you cannot know the phase without a working
readout.

### `bsubtilis_12_decoupled_channel_readout.py`
**What it tested, plainly:** rather than outsmarting the interference, shrink it
at the source, by routing the signal through a different channel or deleting the
channel that carries the noise.
**What it found, plainly:** promising, and it depends on how strong the real
interference turns out to be. At moderate levels you only need to weaken it, not
remove it. At the worst documented level nothing short of full removal works.
**Technically:** sweeps a residual-coupling fraction from 100% to 0% at 30 mV
and 70 mV. At 30 mV, cutting coupling to 10% takes a 1-minute read from 54% to
94%. At 70 mV, a fast read stays at 55-61% down to 10% coupling and only
recovers at 0%, with the 180-minute average remaining the coupling-independent
fallback. Audit Part 18. **Now in direct conflict with `bsubtilis_18`:** see
that entry.

### `bsubtilis_13_reporter_colony_regrowth.py`
**What it tested, plainly:** after a colony is smashed down and regrows, does
the glowing colour still say the right thing, not just the genes underneath.
**What it found, plainly:** yes, exactly as well as the genes do. The colour
readout adds no extra fragility.
**Technically:** the same surviving-fraction sweep as `bsubtilis_07` using the
reporter cell, reporting genetic and reporter fidelity side by side. Both
recover to 100% from 2% survivors upward, with a 0% gap at every level tested.
Audit Part 20. Does not model photobleaching, autofluorescence or imaging noise.

### `bsubtilis_14_voltage_colony_regrowth.py`
**What it tested, plainly:** damage, regrowth and the colony's own electrical
rhythm all at once on the same colony, which had never been done together.
**What it found, plainly:** each piece behaved as predicted separately, plus one
new thing: the project's own six-hour recovery budget has no slack left at all
in the worst case.
**Technically:** combines `bsubtilis_07`, `bsubtilis_08` and `bsubtilis_09` in
one trial with the oscillation running throughout regrowth and settling. Genetic
fidelity stays at 100%; the snapshot read collapses to about 50% at every damage
level and both amplitudes; the 180-minute average recovers to about 100%. From a
single surviving cell, regrowth to 64 cells takes exactly 6 doubling rounds
(180 min), leaving exactly 180 minutes of settle time, precisely one averaging
window and not a minute more. Audit Part 21.

### `bsubtilis_15_partition_noise_regrowth.py`
**What it tested, plainly:** when a cell divides, the molecules do not split
perfectly evenly. Does that randomness break the regrowth result?
**What it found, plainly:** no, and the circuit is surprisingly tough. It only
degrades if each cell holds about one copy of the key molecule, which is
probably unrealistic. It also turned up something counterintuitive: at that
extreme, worse damage makes the noise problem worse, the opposite of every other
stressor tested.
**Technically:** replaces deterministic inheritance with binomial partitioning
per Huh and Paulsson (2011), kappa = 1/<X>, applied to both daughters at every
division, sweeping an explicitly unmeasured molecules-per-unit conversion.
Recovery stays at 99-100% at about 5 molecules per cell and above across all
damage levels; at about 1 molecule it degrades to 66-87%, and there worse damage
hurts more because fewer surviving lineages need more divisions, compounding
noise. Audit Part 22. Binomial partitioning is Huh and Paulsson's best case, so
this is a floor on the effect, not a ceiling.

### `bsubtilis_16_damage_sensing_reinforcement.py`
**What it tested, plainly:** could cells notice they were damaged and actively
protect the stored bit while healing, instead of just riding it out?
**What it found, plainly:** yes, and it completely fixes the one real weak point
found so far.
**Technically:** a proposed circuit addition modelled on the bacterial SOS
response (RecA/LexA) that transiently boosts the dominant toggle arm during
regrowth then relaxes. Tested against `bsubtilis_15`'s worst case (about 1
molecule, 66-87% recovery): a 10x boost restores 100% at every damage level
including 2% survivors, and a 5x boost reaches 97-99%. Audit Part 23. This is a
design proposal using real machinery, not a built or measured circuit, it does
not name a specific B. subtilis stress promoter, and it raises an untested
question of its own: would a circuit reinforced this hard resist a legitimate
new write after healing?

### `bsubtilis_17_circuit_variant_predictor.py`
**What it tested, plainly:** which specific version of the circuit to build,
before spending wet-lab money, since the real experiment has to be run on one
design and not on "the circuit" in the abstract.
**What it found, plainly:** composes two already-validated simulations into a
design-space prediction across candidate promoter pairings.
**Technically:** composes `bsubtilis_01` and `bsubtilis_07` across promoter
variants. Predicts, does not measure.

### `bsubtilis_18_phase_encoded_readout.py`
**What it tested, plainly:** the opposite of everything above. Instead of
fighting the colony's electrical rhythm, use it. Store the bit as whether a cell
moves with the rhythm or against it, so the rhythm becomes the reference signal
rather than the noise.
**What it found, plainly:** it inverts the problem cleanly. The old method is
perfect with no rhythm and falls apart once it appears. This method is a coin
flip with no rhythm, which is the control working correctly, and becomes
essentially perfect as the rhythm gets stronger.
**Technically:** keeps the Gardner ODE and noise magnitudes and changes only
what the voltage tracks: the bit selects the sign of the cell's response to the
ambient oscillation. Read as the sign of the correlation against a separately
measured reference trace, with read start times spread across the oscillation
period so neither scheme gets an accidentally phase-locked read. At a 60-minute
read and 10 mV-equivalent measurement noise: level encoding 100% / 65% / 54% /
55% / 58% and phase encoding 50% / 86% / 99% / 100% / 100% at 0 / 10 / 30 / 50 /
70 mV. Audit Part 25. Based on Yang et al. 2020 (*Cell Systems*,
DOI 10.1016/j.cels.2020.04.002), who demonstrated the anti-phase mechanism in
this exact organism, though with light acting on native channels rather than a
genetic circuit. **The conflict with `bsubtilis_12`:** for level encoding yugO is
the interference source to delete; for phase encoding yugO is the mechanism that
makes it work. The two strategies are mutually exclusive and want different
chassis strains, and that choice has to be made before a strain is ordered.

### `bsubtilis_19_reservoir_benchmark.py`
**What it tested, plainly:** whether the circuit is any good at computing, not
just remembering.
**What it found, plainly:** barely. A single toggle circuit is a weak computer.
**Technically:** applies `analysis/reservoir_benchmarks.py`'s NARMA-10 benchmark
with `GardnerToggleCell` as the reservoir substrate. About 8% NRMSE improvement
over predicting the mean.

### `bsubtilis_20_write_axis.py`
**What it tested, plainly:** what is the most efficient way to push the circuit
from one state to the other.
**What it found, plainly:** the circuit is a sharp digital switch, so the
smooth-nudge method borrowed from another project does not fit it.
**Technically:** applies `analysis/memory_geometry.py`'s write-axis method to
`GardnerToggleCell`. The exactly-symmetric baseline is an unstable knife-edge,
and tasmorpho's continuous linear write-map does not fit this substrate's
ultrasensitive regime.

### `bsubtilis_21_optical_write_replication.py`
**What it tested, plainly:** whether the San Diego lab's published method for
writing a bit into these exact bacteria can be rebuilt in this project's own
code, and what happens to their kind of bit when the cells divide.
**What it found, plainly:** the write rebuilds cleanly, four of the five things
they report come straight out of the model, and their bit is unreadable after
one or two cell divisions while a genetic bit is not. That gap is the whole
reason this project exists.
**Technically:** reimplements the Hodgkin-Huxley-style potassium model described
in Yang et al. (2020) STAR Methods (Cell Systems 10(5):417-423, DOI
10.1016/j.cels.2020.04.002). The optical write is their own assumption that
irradiation fixes the channel open fraction `n` at a constant. Reproduces
signature 1 (light hyperpolarises, here by about 8 mV), 2 (a delta-yugO cell
with zero channel conductance shows no shift at all), 3 (150 mM external
potassium inverts the shift instead of hyperpolarising) and 4 (separation flat
from 30 to 200 minutes). Does NOT reproduce signature 5, their anti-phase
cross-correlation with a peak at half the 100-minute shock period: this model
gives correlation +0.91 at zero lag and a 95-minute peak, and a 12-point sweep
across three orders of magnitude of potassium influx coupling, pumping rate and
channel conductance never reaches anti-phase. The reason is structural: with
intracellular potassium near 300 mM the potassium reversal potential under a 150
mM shock sits above the resting potential, so opening channels can only
depolarise. Their explanation needs unexposed cells to hyperpolarise there, which
this reduced form cannot produce. Their Table S1 parameters are not in the
open-access text and their raw data is request-only, so this is a stated gap, not
a challenge to their experiment, which was microfluidic and not simulation-only.
The division comparison is the part that does not depend on any uncalibrated
constant: a protein-level mark halves in fraction every generation as unmodified
channels are synthesised, so the readable separation falls from about 8 mV to
under 2 mV in one generation and under 0.3 mV in two, while a latch that
re-establishes the state each generation does not fall at all. Every rate
constant in the file except RT/F, the two potassium concentrations, the 100
minute period and the 50 minute lag is an uncalibrated placeholder and is
labelled as one.

### `bsubtilis_22_comK_excitable_circuit.py`
**What it tested, plainly:** whether B. subtilis's own native switch, the one
that controls its ability to pick up outside DNA, could be a better starting
point for a memory circuit than the imported Gardner switch, since it already
works reliably inside this exact organism.
**What it found, plainly:** the native circuit is built to be temporary, not
permanent, but the same paper that discovered it also showed a specific tweak
that turns "temporary" into "does not turn off." That tweak, simulated here,
holds a written state as well as the Gardner circuit does.
**Technically:** a generic fast-activator/slow-inhibitor excitable-system
model (not the source paper's own fitted equations, which are unavailable, no
open-access full text exists for this PMID) of comK competence dynamics
(Sueel, Garcia-Ojalvo, Liberman & Elowitz 2006, *Nature* 440:545-50, DOI
10.1038/nature04588). The normal (exit-active) variant shows transient,
re-triggering behaviour, 0%/62%/12% "still high" at 1h/6h/24h across trials.
Setting `exit_gain=0` reproduces the paper's own "block exit" re-engineering
test and holds 100% "still high" at all three checkpoints, matching
`bsubtilis_01`'s own 100% on the identical 24h test. Audit Part 27. A
plausibility result from a generic model, not a validated circuit, nobody has
built or tested an exit-blocked comK variant for data storage, let alone
through damage and regrowth.

### `bsubtilis_23_intrinsic_extrinsic_noise.py`
**What it tested, plainly:** every noise number this project has used so far
assumes each gene's randomness is independent of the other's. Real cells also
have a second kind of noise, a shared, whole-cell wobble that hits every gene
at once. Does adding that change the picture?
**What it found, plainly:** not much, at the levels tested. The already-known
weak point (mismatched promoters) is still the dominant one. A borderline
case got slightly worse; the healthy, matched-promoter case did not budge.
**Technically:** subclasses `GardnerToggleCell` (unmodified) to add one shared
random draw per step to both repressors together, on top of the existing
independent per-gene draws, following the intrinsic/extrinsic distinction
Elowitz, Levine, Siggia & Swain (2002, *Science* 297:1183-6, DOI
10.1126/science.1070919) established with a real two-colour-reporter
experiment. At strength ratio 1.0, fidelity held 100% even with extrinsic
noise equal in magnitude to the existing intrinsic term; ratio 10.0 dropped
from 100% to 93% at the highest tested extrinsic level; ratio 0.1 stayed at
its already-broken 50%. Audit Part 27. Extrinsic noise magnitudes swept are
illustrative (matched to the existing tx_noise_std range), not measured, the
real numbers require the same two-colour-reporter assay run on this
project's actual promoters.

### `bsubtilis_24_comK_suel2007_equations.py`
**What it tested, plainly:** bsubtilis_22's comK model uses a generic,
made-up-shape equation because the paper that discovered comK's "block
exit" trick has no public full text. A different, later paper from the
same lab does have its equations public. Do those real equations, and a
different real trick from that paper (turning up one gene's baseline
activity), also produce a lasting locked state?
**What it found, plainly:** yes. Turning that one gene's activity up high
enough locks the circuit permanently, a second, independent real-world way
to get the same "stays on" property bsubtilis_22 gets from blocking exit.
At a middling activity level, the circuit instead flickers on and off
repeatedly, matching what the real paper's own strain actually did.
**Technically:** implements the real Hill-function comK/comS topology from
Suel, Kulkarni, Dworkin, Garcia-Ojalvo & Elowitz (2007, *Science*
315:1716-9, DOI 10.1126/science.1137455) note 15 (shared competitive
MecA-ClpC-ClpP degradation denominator coupling ComK and ComS), with
illustrative parameters (fitted constants are in the paper's SOM, not
supplied) tuned to reproduce its three reported regimes as aK is swept:
quiescent at baseline (0 spontaneous transitions/96h), oscillatory at an
intermediate value (~228 transitions/96h, ~51% time high), and locked at
a high value (1 transition, ~100% time high thereafter). Compared directly
against bsubtilis_22's exit-blocked model and bsubtilis_01's Gardner
toggle on the same 24h persistence test; all three hit 100%. Audit Part
28. This project's own aK multiples do not quantitatively match the real
strain's induction curve, only the qualitative regime structure.

### `bsubtilis_25_transcription_translation_noise_scaling.py`
**What it tested, plainly:** the noise number used everywhere in the
Gardner toggle simulations (3.0) has never been checked against any real
formula. A companion paper to the two-colour-noise paper gives the actual
math connecting real, measurable cell properties to how noisy gene
expression should be. Does the current guess hold up against that math?
**What it found, plainly:** not really. Across a range of realistic
settings, the real formula predicts noise 3 to 17 times higher than the
current guess, at every setting tested, not just the extreme end. It also
confirms something already argued informally: putting one copy of the
gene on the chromosome (this project's choice) is a real, quantifiable
noisier choice than a multi-copy plasmid, not a free one.
**Technically:** implements the well-known asymptotic simplification of
Swain, Elowitz & Siggia (2002, *PNAS* 99:12795-800, DOI
10.1073/pnas.162041399), eta_int^2 ~= (1+b)/\<P\>, b = burst size
(proteins per transcript, that paper's own reported E. coli range,
"order tens," used only to bound plausible scenarios, not a B. subtilis
measurement), and eta^2 ~ 1/n for gene copy number n. Swept against
GardnerParams' default alpha=50.0 as the mean-level anchor: implied
absolute noise std ranged 10.0-50.5 across burst sizes 1-50, versus the
current tx_noise_std=3.0 placeholder (3.3x-16.8x higher). Audit Part 28. NOTE (audit Part 31): that comparison put a per-step kick size next to a level spread, and in unit-free CV terms it depends on molecules per cell, so treat "3x to 17x too low" as withdrawn pending measurement.
Caveat stated in the file: this simplified form omits Swain et al.'s own
cell-cycle correction, which their Eq. 22 shows can move a naive estimate
by up to 65%, so treat this as a bound, not a precise prediction; the real
number requires wet_lab_experiments/Experiment_2's actual measurement.

### `bsubtilis_26_noise_crosscorrelation_diagnostic.py`
**What it tested, plainly:** every read of the toggle switch so far is a
snapshot at a fixed time. A different paper shows that watching two genes
over TIME in the same cell, and checking how they correlate with a delay,
can tell you whether one is actually repressing the other, without
touching anything. Does that trick work on this project's own simulated
switch?
**What it found, plainly:** yes, partly. It clearly tells apart "these two
genes are linked" from "these two genes are not linked at all." It does
NOT tell apart a healthy switch from a badly mismatched (broken) one,
because in this model the link itself never turns off, only how well
separated the two outcomes are changes, and that is a different question
this method doesn't answer, but flow cytometry already does.
**Technically:** implements Dunlop, Cox, Levine, Murray & Elowitz's (2008,
*Nature Genetics* 40:1493-8, DOI 10.1038/ng.281) own single-lineage
cross-correlation formula, run on full `GardnerToggleCell` trajectories
(unmodified) instead of 24h endpoints. M1 (matched, ratio=1.0) and M3
(severe mismatch, ratio=0.1) both produced a clear anticorrelated dip at
a nonzero lag (min R approx -0.67 at lag=14 for both); an unregulated
control (two independent relaxation processes, same noise magnitude, no
mutual-repression term) showed no dip, only a near-zero-lag positive peak
(max R approx 0.73). Audit Part 28. Demonstrates the method is applicable
to this project's construct; does not measure anything about real cells,
and does not replace Experiment 1's cytometry-based basin-separation read.

### `bsubtilis_27_noise_robustness_sweep.py`
**What it tested, plainly:** every "100 percent" result in this project used a
noise setting that a later check suggested is 3x to 17x too low. This reruns
the key results with noise turned up to 20 times that setting to see where the
circuit starts to fail.
**What it found, plainly:** the circuit holds up to about 5 times the original
noise, wobbles at 10 times, and is down to coin-flip territory by 20 times.
Badly mismatched promoters fail much sooner. IMPORTANT (audit Part 31): this
failure point belongs to the simulation's Gaussian noise model. An exact
molecule-by-molecule model of the same switch keeps working at much lower copy
numbers, so read this row as "what Gaussian noise does", not "what cells do".
Whether the first experiment passes depends on molecules per cell and burst
size, which nobody has measured.
**Technically:** single-cell 24 h genetic fidelity and colony recovery at noise
multipliers 1, 2, 3, 5, 10, 20 times `transcriptional_noise_std=3.0`, across
promoter ratios 1.0, 2.0, 5.0, 10.0 and 0.1. Matched promoters: 100% to 5x,
60% at 10x, 53% at 20x. Colony recovery (6 h window, matched): 100% to 5x,
84-85% at 10x, 55-57% at 20x. Also defines `run_colony_trial_ex`, a
parameterised regrowth trial that reproduces `bsubtilis_07` at defaults and is
reused by 28 and 29. Audit Part 29. The multipliers are a sweep axis, not
measured noise.

### `bsubtilis_28_regrowth_timing_sweep.py`
**What it tested, plainly:** the recovery after damage depends on cells
dividing every 30 minutes and being readable the instant the colony is back.
Neither is measured. What if division is slower, or the colony needs time to
settle?
**What it found, plainly:** the colony still regrows and the fluorescent
reporter still reads correctly in every case. The electrical readout is much
more fragile: it needs a full three hour reading window, and anything less
turns it into a coin flip.
**Technically:** doubling time 30/45/60 min x settling delay 0/30/60 min x
2/5/20% survivors x 30 and 70 mV native oscillation. Genetic fidelity 100% and
full regrowth in all 54 cells of the grid. The 180 min averaged voltage read
gives 50% whenever the window is shortened, including 151 min, and fails at
2 and 5% survivors from 45 min doubling onward. Audit Part 29. Doubling times
and delays are sweep axes, not measurements.

### `bsubtilis_29_stressed_survivors.py`
**What it tested, plainly:** the damage simulations assume survivors are
perfectly healthy. Real survivors would be stressed. What if they divide
slowly, get noisier, or have shifted voltage?
**What it found, plainly:** slower growth did not hurt the fluorescent
readout. Extra noise hurt it a little. A long-lasting voltage shift of about
40 millivolts breaks the electrical readout completely, because the two
voltage levels the model uses sit only 35 millivolts from the decision line,
and those levels were inherited from the old planarian model.
**Technically:** a stress window applies a doubling-time multiplier (1-3x), a
noise multiplier (1-10x) and a steady voltage shift (-40 to +40 mV) to
survivors, then they return to normal. Growth penalty alone: genetic 100%.
10x noise for 180 min: 96%. Sustained 2x slower + 10x noise + 40 mV for 360
min: 85-87% genetic, 50% voltage. 20 mV shifts: no effect. Audit Part 29. Every
magnitude is a sweep axis, not measured. Narrows, but does not close, Known
Gap 4; Stage B2 arm 2b still has to measure the real stress.

### `bsubtilis_30_fitness_cost_selection.py`
**What it tested, plainly:** every earlier simulation assumes the engineered
circuit is free and that no cell ever loses it. Real circuits cost the cell
something, and a cell that drops the circuit can outgrow its neighbours. Over
a long culture those drop-outs take over, and on a chart that looks the same
as the stored bit fading.
**What it found, plainly:** this does not matter for a short damage-and-regrowth
test (about 7 divisions) but matters a lot for a 72 hour culture. Whether it
matters depends on how much faster lost cells grow and how often cells lose the
circuit, and neither number has been measured. Counting cells that lost the
circuit separately from cells that flipped state is what tells the two causes
apart.
**Technically:** three cell classes (written-state circuit cells, flipped
circuit cells, lost cells) with a relative growth advantage s for lost cells and
a loss rate mu per division, swept over s of 0 to 0.30 and mu of 1e-6 to 1e-2.
Deterministic expectation plus a Wright-Fisher style stochastic version with a
finite dilution bottleneck. s of 0.03 with mu of 1e-4 holds 98% at 72
generations and 81% at 144; s of 0.10 with mu of 1e-5 holds 91% then 1%. At 7
generations, 98-100% holds everywhere except mu of 1e-2 (84-93%). Ungated versus gated
reads diverge sharply (9% versus 100% at s of 0.10, mu of 1e-3, 72 generations).
Audit Part 30. All axes are sweep axes, not measurements; the competition assay
in Experiment 1 measures s directly. Section F sweeps SURVIVOR BIAS: if the
cells that survive damage are not a random sample, selection that happened
before the damage carries into the regrowth result (from a 72-generation-old
culture at s of 0.10 and mu of 1e-4, only 35% hold the bit after regrowth even
with random survivors). The direction of real bias is unknown. Section G puts
the same question in the cell-level regrowth engine: each survivor is wrong-state
or already lost with probability q, and recovery fidelity just tracks that
composition (one survivor, q of 0.25: 83% of colonies still clear the 70% bar).
The "2% survivors recover to 100%" headline is exactly as good as the assumption
that survivors are all correct.

### `bsubtilis_31_dt_independent_noise_rerun.py`
**What it tested, plainly:** the noise knob in the toggle simulation changed its strength when the
computer's time step changed, which a noise setting should never do. This builds a version where it
does not, and reruns the key results with finer steps to see whether anything breaks.
**What it found, plainly:** the knob really did depend on the step, but the earlier results
survive. Run more finely, the same switch still holds to about 5 times the assumed noise and still
fails after, and the timing and stress findings reproduce. The knob just never had a physical scale.
**Technically:** `GardnerToggleCellSDE` subclasses `GardnerToggleCell` (unmodified) with
square-root-of-dt scaling; `transcriptional_noise_std` keeps its old meaning at dt 0.02 so old
values map exactly, and at `substeps=1` it reproduces the original trajectories to machine
precision. Level standard deviation at tx 3 against dt 0.02, 0.01, 0.005, 0.0025: original 2.27,
1.41, 0.87, 0.48; new 2.27, 2.34, 2.50, 2.48. Single-cell fidelity, colony recovery (99-100% to
5x, 83-85% at 10x, 51-55% at 20x) and headline timing and stress cells match the originals within
sampling noise. Audit Part 31.

### `bsubtilis_32_analytic_and_gillespie_crosscheck.py`
**What it tested, plainly:** do other kinds of math give the same answers as our simulation?
Pen-and-paper algebra for the switch's structure, and a molecule-by-molecule random simulation
for the noise.
**What it found, plainly:** the algebra and the simulation agree exactly on when the switch can hold
two states, including the rule that mismatched promoters kill it. On noise they disagree. Our
simulation fails at a noise level where the molecule-by-molecule version keeps working, because our
simulation's random kicks push the nearly-absent repressor up from zero. The molecule version holds
down to about 5 times the burst size in molecules (roughly 25 to 100 for bursts of 5 to 20).
**Technically:** (A) fixed points of u = a1/(1+v^2), v = a2/(1+u^2) with Jacobian eigenvalues
-1 +/- sqrt(d_u d_v): bistable window in a2/a1 of 0.247 to 16.25, matching the noise-free simulation
at 16 of 16 ratios, and the noise-free stable-to-saddle distance ranks ratios 1, 2, 5, 10 in the
same order as their simulated failure. (B) Gillespie with geometric bursts of mean b: measured CV
matches sqrt(b/<P>); fidelity at or above 90% down to about 12, 25, 50, 98 mean ON molecules for
b = 1, 5, 10, 20, against a Gaussian-model failure at CV about 0.32 (exact model about 0.58 to
0.60). (C) A chemical Langevin version fails like the additive model. (D) Mean repressed-arm level
(noise-free 0.020): exact 0.000, Langevin 0.62, additive 0.66 to 1.61. Audit Part 31. The exact
model has no mRNA stage, extrinsic noise or division, so its robustness is a model result.

---

# Methylation track

A different way to store the bit: a chemical tag attached to DNA, copied to
daughter cells at every division by the cell's own machinery, without changing
the genetic code underneath. Real precedent exists in nature.

### `methylation_01_bit_encoding.py`
**What it tested, plainly:** can a bit stored as a chemical tag survive being
copied over and over as cells divide?
**What it found, plainly:** it depends entirely on how accurate the copying is,
and the two real published accuracy figures land on opposite sides of
pass and fail.
**Technically:** models a single-lineage bit across generations using two real,
differently-sourced maintenance-fidelity anchors: 99.9% (Watanabe et al. 2006,
promoter CpG islands) and 96% (Laird et al. 2004, single-molecule hairpin
bisulfite PCR). Audit Part 11. Both anchors are mammalian CpG methylation
(Dnmt1-family), not bacterial Dam, and B. subtilis does not natively carry the
Dam/Dcm system, so a real implementation needs a methyltransferase engineered
in. That is a dependency, not a free win.

### `methylation_02_regeneration_transfer.py`
**What it tested, plainly:** the same thing through a full damage-and-regrowth
cycle.
**What it found, plainly:** a different failure mode from the genetic circuit.
Here, having more survivors does not help. If the copying accuracy is too low,
even an undamaged colony loses the bit, purely from drift compounding over many
divisions.
**Technically:** full colony damage-then-regrowth swept across surviving
fractions 0-100% over a 24h (about 48-generation) window at a 30-minute doubling
time. At 99.9% fidelity the bit survives from even 2% survivors (95-97%
combined). At 96% it decays to chance by about 48 generations regardless of
surviving fraction, including 100% survival. Audit Part 11. This is the same
lesson Condorcet's theorem taught for replication: redundancy cannot rescue a
per-copy accuracy that is too low.

---

# Cross-organism

### `crossorganism_01_comparison_summary.py`
**What it tested, plainly:** all three approaches side by side, ranked not by
which produces the nicest number but by how much untested risk each is still
hiding.
**What it found, plainly:** the bacterial circuit is the best-grounded option
and the original planarian approach is the weakest. This is the file that made
the project bacteria-first.
**Technically:** runs the three comparable regeneration/regrowth tests across
surviving fractions 0-100%. The B. subtilis circuit recovers from about 2%
survivors with the highest confidence, because coupling is mechanistically
forced by division rather than being a free parameter. Methylation at the 99.9%
anchor also recovers from about 2%, at the 96% anchor it never does. The
planarian circuit numerically ties the B. subtilis row at 100% but carries the
lowest confidence, because its coupling strength is borrowed rather than
measured. Ranked by hidden wet-lab risk, lowest to highest: B. subtilis circuit
< B. subtilis methylation < planarian circuit. Audit Part 13. Identical output
numbers do not mean identical trustworthiness, which is the whole point of the
file.

---

## Known gaps across the whole folder

Stated here so nobody has to rediscover them file by file.

1. **Every noise parameter is a placeholder.** `bsubtilis_27` shows the
   fidelity results hold only up to about 5x the placeholder. Transcriptional noise, channel
   noise, thermal noise, measurement noise and reporter maturation time are all
   unmeasured. Stage B1 in `experiments/BENCH_PROTOCOL_BSUBTILIS.md` exists to
   measure them.
2. **The voltage targets are inherited.** `V_HIGH = -10 mV` and `V_LOW = -80 mV`
   came from the planarian model and have no B. subtilis measurement behind them.
3. **The circuit-to-voltage link has never been built by anyone.** Every file
   downstream of `bsubtilis_01` that reports a voltage is tracking the genetic
   state through a first-order filter, not a measured biophysical relationship.
4. **Damage is modelled as removing cells and nothing else** in files 01-26.
   `bsubtilis_29_stressed_survivors.py` now sweeps survivor stress (slower
   growth, higher noise, voltage shift) but every magnitude there is a sweep
   axis, not a measurement. Arm 2b of Stage B2 in the bench protocol is
   designed to measure the real size of that blind spot.
5. **No fitness cost is measured.** `bsubtilis_30` sweeps it, but every
   earlier file treats the circuit as free and uses no loss-of-circuit class.
6. **The planarian coupling constant is borrowed, not measured.** It is the
   single weakest assumption in the project.
