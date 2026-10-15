# Acheron Interview Guide

One document to study from. Short sentences, one analogy per idea. Read it
top to bottom once, then use the Q&A and the study plan. Deeper detail lives in
`ACHERON_101.md` (the concept chapters), `REASONING_MAP.md` (the story) and
`SCIENTIFIC_AUDIT_2026.md` (the authority if anything disagrees).

**The one rule:** say what is simulated, what is cited, and what is unknown.
Never round a claim up. Admitting a limit is the strongest thing you can do in
the room, because this project's whole identity is that it found and published
its own mistakes.

---

## 1. Say it three ways

**10 seconds.**
Acheron tests whether a living cell can hold a bit of data, survive being
damaged, and still have that data after it grows back.

**30 seconds (non-technical).**
A hard drive dies if you break it. A living colony can regrow. We ask: can you
write a 0 or a 1 into living bacteria so that even after most of them die, the
survivors regrow and the 0 or 1 is still there? Nobody has tested that. We have
simulated it, and we are asking for a small amount of money to test it in a real
lab.

**2 minutes (technical).**
We engineer a genetic toggle switch (Gardner, Cantor and Collins 2000) into
*B. subtilis*. Two genes repress each other, so the cell sits in one of two
stable states. That is the bit. When a cell divides, the proteins holding the
state go into both daughters, so the state survives growth by physics, not by
assumption. Our simulations say a colony cut down to 2% of its cells regrows
with the bit intact. Everything is simulated. The first funded experiment
(about $2K to $5K) checks the one design rule our model flagged as
make-or-break: that the two promoters are matched in strength. We started with
a different idea (voltage held passively in flatworm tissue), our own noise test
broke it, and we published that. The closest prior art is Yang et al. 2020,
which wrote a bit into this same organism, but their bit is lost when cells
divide. Ours is built to survive division.

---

## 2. The hypothesis in four steps

Founder's words, confirmed: one hypothesis, any organism. *B. subtilis* is
first because it is cheap and fast, not because planaria were dropped.

| Step | Plain English | Status |
|---|---|---|
| 1. Write | Put a 0 or 1 into living cells | Gardner 2000 did the switch in *E. coli*. Cited, not ours. |
| 2. Damage | Kill most of the cells | Simulated only |
| 3. Detect and transfer | Organism notices damage by itself and carries the data into its regrowth | Division carries data: simulated. Self-detection: proposed circuit, simulated, never built |
| 4. Keep | After regrowth the bit reads back correctly | Simulated only. **Never tested in any organism by anyone.** |

Analogy: a notebook (the colony). Write a note (the bit). Tear out most pages
(damage). Every remaining page photocopies itself as the notebook regrows
(division). Does the note survive the copying?

---

## 3. The science, one line each

Learn these in this order. Each builds on the one before.

- **Cell.** A sealed bag of chemistry with a wall. Smallest unit of life.
- **Bacterium.** A one-room cell. No nucleus, no inner rooms. Simple, fast,
  easy to rewire.
- ***B. subtilis*.** A harmless soil bacterium. One of the best-studied bacteria
  on Earth, so the tools and parts already exist. It also forms spores that
  survive extreme conditions (the hardware concept cites spaceflight survival,
  Deshevaya et al. 2024).
- **DNA / gene.** DNA is the recipe book. A gene is one recipe. It builds one
  protein.
- **Protein.** The worker. Builds things, runs reactions, forms the doors in the
  cell wall.
- **Promoter.** A volume knob in front of a gene. Sets how often it is read.
- **Repressor.** A protein that mutes another gene's promoter. A mute button.
- **Ion.** An atom with extra or missing electrons, so it carries charge.
  Potassium (K+) is the one that matters here. An ion is not an electron.
- **Ion channel.** A protein door in the cell wall that lets one kind of ion
  through. Opens and closes.
- **Ion pump.** A door with a motor. Pushes ions the hard way, uphill, using
  energy.
- **Membrane potential.** Different ion counts inside versus outside create a
  voltage across the wall. A stretched rubber band. Living cells always hold
  some.
- **Bistable.** A system that rests in only two states, like a light switch.
  Not a dimmer.
- **Toggle switch.** Two genes that each mute the other. Whoever wins stays on
  and keeps the other muted. Flip it with a push and it stays flipped. Two
  people arm-wrestling where the winner holds.
- **Reporter.** A gene that makes a colour (GFP, RFP). A mood ring. Lets you
  see the switch state without a voltmeter.

Ion channels, one more time, for the "ion gates" question: the cell keeps
potassium high inside and lower outside. Open a potassium channel and K+ leaks
out, which shifts the voltage. A channel is a gate, an ion is the traveller, the
voltage is the result. Acheron's candidate gate is **yugO**, a potassium channel
in *B. subtilis*.

---

## 4. What is the bit, and what must we prove

**The bit.** In the toggle, repressor A winning = state 0, repressor B winning =
state 1. Read by colour (reporter) first, by membrane voltage later.

**Eight things must be true for the hypothesis to hold.** Each one is a gate.
If one fails, we stop and learn, we do not spend on the next.

| # | Must be true | Where it is tested |
|---|---|---|
| 1 | The switch really has two stable states in a real cell | Experiment 1 |
| 2 | You can flip it on purpose and it stays flipped (rewritable) | Experiment 1 |
| 3 | It holds over time, against real noise | Experiment 2 |
| 4 | It survives cell division | Experiment 3, arm 2a |
| 5 | It survives real damage and regrowth | Experiment 3, arm 2b |
| 6 | Enough molecules per cell to make it robust | Experiment 4 |
| 7 | You can read it without destroying the sample | Experiments 1 (colour), 5 and 6 (voltage) |
| 8 | The cell notices damage and reinforces the bit by itself | Experiment 7 |

Gates 1 to 5 are the core. Gate 5 is the project's real claim.

---

## 5. Why *B. subtilis*

Give reasons from the repo, not slogans.

1. **Parts exist.** The Bacillus BioBrick Box has promoters already measured in
   this organism. We design from real numbers, not placeholders.
2. **Inheritance is physics.** When the cell divides, the proteins holding the
   state go into both daughters. The planarian route needed an unmeasured
   assumption (how strongly cells pull each other's voltage). Our own
   cross-organism ranking put *B. subtilis* first for that reason.
3. **Cheap and fast.** Cells double in about half an hour in the model. A lab can
   test in weeks, not years.
4. **It already has an electrical system.** Published work (Prindle et al. 2015)
   shows biofilms pass potassium waves through ion channels. That gives us a
   channel to wire into, and a hazard to manage.
5. **Prior art is on our side and against us.** Yang et al. 2020 proved a
   voltage bit can live in this organism. That de-risks the biology and narrows
   our novelty.

**Honest weaknesses.** The BioBrick parts were characterised in strain W168, but
the biofilm literature used strain NCIB 3610, and 3610 is hard to transform. We
have not resolved this. Why not *E. coli*? Gardner already did it there, and the
biofilm electrical literature we rely on is in *B. subtilis*. If asked why not
something else, say you chose the best-grounded option and ranked the others
openly.

---

## 6. The simulations, in one table

All simulated. None measured. Scoreboard for the ones you will be asked about.

| What we asked | Answer | File | Worth |
|---|---|---|---|
| Does a bit held passively in flatworm tissue last 24h? | Perfect with zero noise. Coin flip (about 50%) with realistic noise. **Retired.** | `planarian_01`, `planarian_02` | Strongest evidence of honesty. Lead with it. |
| Do three copies and a vote fix it? | No. Voting cannot rescue copies that are already near chance. | `planarian_08` | Closes a tempting escape |
| Does an engineered toggle hold two states? | Yes, if promoter strengths are matched. Badly mismatched collapses to one state. | `bsubtilis_01` | The make-or-break design rule. Basis of the $2K to $5K ask. |
| Does the bit survive a colony cut to 2%? | Yes, recovery stays above the 70% bar down to about 2% survivors | `bsubtilis_07` | The differentiator. Still a model. |
| What if molecules split unevenly at division? | Fine down to about 5 molecules per cell. Weak near 1 molecule. | `bsubtilis_15` | Real weak point, honestly found |
| Can a damage-sensing circuit fix that weak point? | Yes in simulation (10x boost restores full recovery). Not built. | `bsubtilis_16` | Proposal. Untested question: would it block a legitimate rewrite? |
| Can we read it by colour? | Yes, tracks the genes exactly, through damage and regrowth | `bsubtilis_10`, `bsubtilis_13` | Why the first experiment uses a reporter |
| Can we read it by voltage? | Hard. The colony's own potassium rhythm corrupts a quick read. Averaging over about 3 hours fixes it but eats the time budget. | `bsubtilis_08` to `12` | Why voltage readout is Stage 3, not Stage 0 |
| Does a cheap electrode sweep avoid that? Does clever timing? | No to both. Reported as failures. | `bsubtilis_09`, `bsubtilis_11` | Two honest negatives |
| What if the bit is the phase against that rhythm? | Works, and improves as the rhythm strengthens. But it needs the channel intact, level encoding needs it deleted. | `bsubtilis_18` | An open fork. Choose before ordering a strain. |
| Can we rebuild the published optical write? | Mostly. Their bit is gone after one or two divisions, a genetic bit is not. A mechanistic anti-phase explanation did not reproduce. | `bsubtilis_21` | Supports our differentiator, weakens phase encoding |
| Is the circuit a good computer? | Barely. About 8% better than guessing the mean. | `bsubtilis_19` | Do not pitch this as computing. It is memory. |

**Plain answer to "can I trust simulations?"** A simulation tells you what
follows from your assumptions. It cannot tell you the assumptions are true. Every
noise magnitude here is assumed. Experiment 2 and 4 exist to replace those
assumptions with measurements.

---

## 7. The tests

- `tests/` holds **17 unit tests across 3 files**, all passing (checked today).
- They cover the `analysis/` methods only: hidden-state model, memory geometry,
  reservoir benchmarks. Those are methods adapted from published work and
  cross-checked against the originals.
- **They do not test the biology.** The simulations are not unit-tested, they
  are experiments. Say that plainly if asked.
- Run them: `python -m pytest tests/ -q`

The real test of the project is the wet lab.

---

## 8. The wet-lab experiments, and what you are asking for

None have been run. Every predicted result is a simulation result.

| # | Experiment | Question | Cost today |
|---|---|---|---|
| 1 | Toggle Confirmation | Does the switch really switch, in real cells? | **$2K to $5K, 6 to 10 weeks** (planning estimate, not quoted by a lab) |
| 2 | Persistence and Noise | Does it hold over time, and what is the real noise? | Not priced |
| 3 | Damage and Regrowth | Does the bit survive damage and regrowth? Pass bar: at least 70% of cells correct after regrowth from as few as 2% survivors | Not priced |
| 4 | Repressor Copy Number | How many molecules per cell do the job? | Not priced |
| 5 | Voltage Interface | Can the switch control a real potassium channel (yugO)? Nobody has built this. | Not priced |
| 6 | Oscillation and Readout | Does the colony's own rhythm scramble the reading? | Not priced |
| 7 | Reinforcement Circuit | Does a "heal harder" circuit fix the weak point? | Not priced |

**Do not invent prices for 2 to 7.** Say: "Only Experiment 1 has a planning
estimate. The rest get quoted by the partner lab after Experiment 1 passes."

**The ask.** Not a seed round. Three small things:
1. Fund Experiment 1 (about $2K to $5K).
2. A paid synthetic-biology consultant to pressure-test the design.
3. Lab access for standard bacterial cloning.

**Why Experiment 1 first.** Cheapest, fastest, uses free parts, tests the exact
make-or-break rule, and avoids the voltage-readout problem by using colour.

**What a "no" means.** Experiment 1 failing means the parts plus topology do not
give a switch. We stop at about the cost of a laptop. That fast cheap no is the
design, not a failure.

**Where the old docs disagree with the current plan.** The older pitch roadmap
labels Stage 2 as a planarian experiment at $10K to $30K. The wet-lab folder is
*B. subtilis* first. If asked about the $10K to $30K, say it is the older
planarian-stage estimate, and that the *B. subtilis* damage-and-regrowth
experiment has no price yet.

---

## 9. Hard questions, with straight answers

**Isn't this already done?**
Partly, and we say so. Yang et al. 2020 wrote bits into *B. subtilis* with
light and read them for over 3 hours. Bonnet et al. 2012 stored rewritable data
in living cells with recombinases. What neither shows is a state that stays
rewritable and readable without destruction while surviving division and
regrowth. That is our narrower claim.

**Why not DNA storage, like Biomemory or BioCompute?**
That is archival. You write once and read by destroying the sample. We want
something closer to RAM: write, read in place, rewrite. Different product.

**Where is your data?**
We have no wet-lab data. We have simulations and an audit of what they do and
do not prove. Experiment 1 produces the first real data.

**Why should I believe simulations from a team that was wrong before?**
Because the team found the error itself. The original claim (24 hours, near-zero
error) was disproved by our own noise test, documented, and drove the pivot.
We do not ask you to trust the numbers, we ask you to fund the test that replaces
them.

**What is the single biggest risk?**
The link from the genetic switch to a measurable voltage has never been built in
any organism. That is Experiment 5. The colour readout avoids it for now.

**What would make you stop?**
Experiment 1 showing no two stable states, or Experiment 3 arm 2a failing
(division alone loses the bit). Either one ends the *B. subtilis* path as
designed.

**How much data can it hold?**
We do not have a measured capacity and will not invent one. The honest scope
today is whether one bit survives. Capacity is a question after that.

**What is the market?**
We do not claim a forecast. Real reference points only: Cortical Labs' CL-1
sells at $35,000 per unit, and the radiation-hardened space electronics market is
sized at roughly $1.2B to $2.0B in 2026 across analyst estimates. The upside is
conditional on the experiments passing.

**Why would anyone want this?**
Memory in places no one can repair: spacecraft, deep sea, remote sensors. Silicon
cannot self-repair. A spore-based substrate needs no power at rest. This is a
concept, no prototype exists, and the hardware deck says so.

**What about patents?**
Three provisionals were filed in 2025, pending examination. Our own gap analysis
found they recite planarian tissue and absolute-voltage encoding, which we have
since retired, and one Background cites a prior-art reference we could not
verify. New drafts exist but are not filed or attorney-reviewed. Say "filed,
pending examination" for the three, and "drafts, not filed" for the new ones.
Never say withdrawn.

**You are a cybersecurity student. Why should anyone trust your biology?**
I built the simulations and the audit, and I wrote down every place they could
be wrong. I am not claiming bench expertise. That is why the ask includes a paid
synthetic-biology consultant and a partner lab. (Confirmed facts only: current
Miami Dade College student, AS in Cybersecurity. Do not mention UCF.)

**Is it safe?**
*B. subtilis* is a widely used, non-pathogenic lab and industrial organism, and
the plan is contained lab work. Confirm biosafety level with the partner lab
rather than answering in detail.

**Is the planarian idea dead?**
No. The hypothesis is organism-independent. *B. subtilis* goes first because it
is cheapest to test. Planaria are the less-grounded fallback because their
cell-coupling assumption has never been measured.

**What is the strain problem?**
Parts were measured in W168, biofilm electrical work used NCIB 3610. We have not
resolved which to use, and Experiment 5 requires a strain switch.

**Level encoding or phase encoding?**
Undecided on purpose. They want opposite things from the same channel. The
reporter-first plan sidesteps the choice for Experiment 1.

---

## 9b. The simulations, and five "I don't know" moments

**"How did you code the simulations, and what are they based on?"**
- "They are Python with NumPy and SciPy. Each one takes an equation from a published paper, steps it forward in small time steps, and adds random noise."
- "The toggle switch is Gardner et al. 2000. Uneven splitting at division is Huh and Paulsson 2011. The noise scaling check is Swain et al. 2002."
- "I built them with AI coding help. I set the question, check the result against the paper, and log the limits in the audit." The repo history shows the commits authored by Claude, so never claim you hand-wrote everything.

Follow-ups:
- **Are the numbers measured?** "Promoter strengths come from the Bacillus BioBrick Box. The noise levels are assumed and labelled that way. Experiments 2 and 4 replace them with measurements."
- **Did you validate them?** "The 17 unit tests cover the analysis methods, checked against the original published code. The biology simulations have not been checked against lab data. That is what the wet lab is for."
- **Why trust them?** "Don't. Fund the test that replaces them. One simulation already overturned our own first result, and it is documented."
- **How many are there?** "About 40 simulation files in four tracks. Three carry the argument: the toggle switch, the colony regrowth, and the noise test that retired our first idea."
- **Can experts check them?** "Yes. Every one is in the repo, and the audit says which parameters are published and which are assumed." (Confirm repo access before offering it, the repo is private.)

Do not say "all of them are based on real measured data." Some parameters are published measurements, but the noise magnitudes and the link from circuit to voltage are assumptions, and the audit says so.

**Five "I don't know" moments**
1. **A specific number** (molecules per cell, voltage levels, memory capacity): "That isn't measured yet. In the simulation it is an assumption, and Experiment 4 measures it."
2. **Lab technique** (cloning steps, flow cytometry settings): "That is for the partner lab and the consultant we want to hire. I can tell you what the experiment must show, not how to run it."
3. **Why the yugO channel?** "It is the candidate channel from the literature (Lundberg et al. 2013). We found no published example of anyone wiring it to a genetic switch, and Experiment 5 tests that."
4. **Biosafety and regulation:** "*B. subtilis* is a common non-pathogenic lab organism. I would confirm the biosafety level with the partner lab and the institution before saying more."
5. **Market size or revenue:** "I don't have a validated number and I won't invent one. The reference points I trust are the CL-1 price and the analyst estimates for radiation-hardened space electronics."

**General rule when you don't know:** "I don't know that yet, here is what I do know." Or: "I'd rather check than guess, I'll send you the answer with the source." Then send it. AI agreement is not verification: say you treat AI output as unverified until you have checked the paper. Your best proof is that you found a fabricated citation in a filed patent.

---

## 10. Never say

- "Nobody has stored data as a bioelectric state." False since Yang 2020.
- "24 hours with under 1% error." Retired, zero-noise artefact.
- "Proven" about anything in `simulations/`. Say "simulated".
- "2% is the limit." It is the lowest level tested, not a measured limit.
- Any capacity, market size or lab cost for Experiments 2 to 7.
- That the patents were withdrawn or that the new drafts were filed.
- That a prototype or hardware exists.
- Em dashes in anything you send.

---

## 11. Seven-day plan

| Day | Do | Time |
|---|---|---|
| 1 | Sections 1 to 3 here. Watch the cell, DNA and ion videos below. Say the 30-second pitch out loud five times. | 90 min |
| 2 | Membrane potential, ion channels, pumps. Draw the cell wall with K+ inside and outside from memory. | 90 min |
| 3 | Gene, promoter, repressor, toggle switch. Draw the toggle from memory and explain why mismatch kills it. | 90 min |
| 4 | Sections 4 to 6 here. Read `REASONING_MAP.md`. Explain the planarian collapse and the pivot in two minutes. | 90 min |
| 5 | Sections 7 to 8. Skim `wet_lab_experiments/Experiment_1` and `_3`. Say the ask in one breath. | 90 min |
| 6 | Section 9. Answer every question aloud, no notes. Record yourself once. | 90 min |
| 7 | Mock interview with Jacqueline asking section 9 in random order. Review section 10. Rest. | 60 min |

---

## 12. Videos

I could not verify individual YouTube links from this environment, and I will
not guess URLs that may be wrong. Below is channel plus an exact search phrase.
Paste the phrase into YouTube and take the first result from that channel. Watch
at 1.25x. Five to fifteen minutes each.

**Cells and bacteria**
- Amoeba Sisters: "Amoeba Sisters cell structure and function", "Amoeba
  Sisters prokaryotes vs eukaryotes"
- Crash Course Biology (Hank Green): "Crash Course Biology cell structure",
  "Crash Course Biology prokaryotes"
- Khan Academy: "Khan Academy prokaryotic and eukaryotic cells"

**Why *B. subtilis***
- "Bacillus subtilis model organism" and "Bacillus subtilis sporulation lecture"
  (university lecture channels)
- iBiology: "iBiology bacterial cell differentiation"
- Background: [Bacillus subtilis on Wikipedia](https://en.wikipedia.org/wiki/Bacillus_subtilis)

**DNA, genes, promoters**
- Amoeba Sisters: "Amoeba Sisters DNA vs RNA", "Amoeba Sisters gene expression"
- Khan Academy: "Khan Academy gene regulation operon"
- Ninja Nerd or Armando Hasudungan: "lac operon explained" (the classic
  repressor and promoter example, same logic as the toggle)

**Ions, channels, voltage**
- Khan Academy: "Khan Academy resting membrane potential", "Khan Academy
  electrotonic and action potential" (the second exists, per search)
- Ninja Nerd: "Ninja Nerd resting membrane potential"
- Amoeba Sisters: "Amoeba Sisters membrane transport", "sodium potassium pump"
- Neuroscientifically Challenged: "ion channels 2-minute neuroscience"

These are neuron videos, but the physics is the same one used in bacteria.
When they say "neuron", think "any cell with a voltage".

**Synthetic biology, toggle switch, noise**
- "Jim Collins synthetic biology toggle switch" and "Tim Gardner genetic toggle
  switch" (the a16z podcast with Collins covers it, per search)
- Uri Alon (Weizmann): "Uri Alon systems biology lecture network motifs"
- Michael Elowitz (Caltech): "Elowitz gene expression noise talk"
- Background: [Gardner, Cantor, Collins 2000](https://www.doi.org/10.1038/35002131)

**Bacterial electrical signalling**
- "Gurol Suel bacteria electrical signaling" and "Suel lab biofilm potassium
  waves" (UC San Diego channel). Search found news coverage, not a verified
  talk. Read [Quanta: bacteria use brainlike bursts of electricity](https://www.quantamagazine.org/bacteria-use-brainlike-bursts-of-electricity-to-communicate-20170905/)
  instead if no video turns up.

**Regeneration, the original inspiration**
- "Michael Levin bioelectricity planaria regeneration talk" (Levin's own
  channel and Lex Fridman's interview with him)

**Data storage in living things (the competitors)**
- "DNA data storage explained" (Catalog, Biomemory, Twist)

**Learning order if short on time:** cell, DNA and gene, resting membrane
potential, lac operon, toggle switch, then Levin. Skip the rest until the
interview is over.

---

## 13. Words you will hear, translated

- **Chassis:** the host organism that carries the circuit.
- **Construct / plasmid:** a small loop of DNA carrying the circuit into the cell.
- **Transformation:** getting that DNA into the cell.
- **Flow cytometry:** shooting cells past a laser one at a time to measure each
  one's colour. Shows whether the population splits into two clear groups
  (bistable) or one smear.
- **Bimodal:** two humps in the data. What a working toggle looks like.
- **Biofilm:** a bacterial community stuck together in a slime layer.
- **Insult:** the lab word for the damage.
- **Go/no-go gate:** a stage whose result decides if you spend on the next one.
- **Null result:** a clean "no". Worth money because it saves money.
