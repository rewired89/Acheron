# Acheron 101

A tiny-book primer on the science and ideas behind Acheron, written for
one reader, in short chapters: what a concept means, what it connects to,
and a simple analogy chain to lock it in.

---

## Chapter 1: Cells 101

**What a cell is (one line):**
A cell is the smallest self-running unit of life, a tiny bag that keeps
its own chemistry separate from the outside world so it can do things on
purpose.

**Key parts, in your style:**

- **Cell membrane** = the wall = a bouncer. It's a thin fatty layer that
  decides what gets in and out. Nothing crosses without permission.
- **Cytoplasm** = the inside = the workshop. It's the jelly-like fluid
  inside the wall where all the actual work (building, storing, reacting)
  happens.
- **DNA** = the internal instructions = the recipe book. Every cell
  carries one, and it never leaves the kitchen (the cell).
- **Bacteria** = the smallest living factory = a one-room house. One
  room, no separate rooms inside (no nucleus, no internal walls),
  everything happens in the open cytoplasm. This is why bacteria are
  simpler and faster to engineer than human cells, which are more like a
  house with locked interior doors.

**The connection that matters for this book:**
Acheron doesn't use human cells or neurons. It uses bacteria
(*B. subtilis*), specifically because a one-room house is easier to
rewire than a multi-room house. Every later chapter about "engineering a
circuit into a cell" assumes this one-room layout.

**Analogy chain:**
Cell = sealed bag = tiny factory. Membrane = factory wall with one
bouncer at the door. DNA = the factory's instruction manual, copied and
kept safe inside. Bacteria = a one-room factory, easy to rewire. Human
cell = a factory with locked departments, harder to rewire.

---

## Chapter 2: Ions & Charge 101

**What an ion actually is (correcting a common mix-up):**
An ion is not an electron. An electron is a tiny negative particle.
An ion is a whole atom or molecule that has gained or lost electrons, so
it ends up electrically charged. Lose an electron, you become a positive
ion. Gain one, you become a negative ion.

**Key parts, in your style:**

- **Electron** = the smallest negative charge = a marble. It's the thing
  that moves.
- **Ion** = an atom or molecule after it gains or loses marbles = a
  charged box. Positive ion (lost marbles) or negative ion (gained
  marbles).
- **Ion channel** = a protein tunnel through the cell membrane = the
  actual door. This is the part that behaves like a door, not the ion
  itself. Some channels only let one type of ion through (a lock that
  only fits one key).
- **Ion pump** = a protein that pushes ions through against the flow,
  using energy = a bouncer with a motor. It actively shoves specific ions
  in or out even when they don't want to go that way naturally.

**The connection that matters for this book:**
A cell's membrane keeps different ion concentrations on each side (more
of one ion outside, more of another inside). That imbalance is the raw
material for voltage. Chapter 3 (Voltage & Membranes 101) is just this
imbalance, measured.

**Analogy chain:**
Electron = marble. Ion = a box with extra marbles (negative) or missing
marbles (positive). Ion channel = a door in the wall shaped for one kind
of box. Ion pump = a bouncer with a motor, forcing boxes through even
uphill. Membrane = the wall holding different box-counts on each side,
which is where voltage comes from.

---

## Chapter 3: Voltage & Membranes 101

**What voltage actually is (one line):**
Voltage is just a measured difference in charge between two points. In a
cell, it's the difference in charge between the inside and the outside
of the membrane, created by the ion imbalance from Chapter 2.

**Key parts, in your style:**

- **Membrane potential** = the cell's voltage = a stretched rubber band.
  It's the tension that builds up because there are more negative ions
  inside than outside (in most resting cells). That tension is stored
  energy, ready to be released or used.
- **Resting potential** = the cell's baseline voltage = the rubber band's
  relaxed-but-still-stretched state. A living cell is never at zero
  volts, it sits at a steady negative voltage (commonly around -70
  millivolts in many cells) and actively maintains it using the ion
  pumps from Chapter 2.
- **Depolarization** = the voltage moving toward zero or positive = the
  rubber band snapping looser. Ions rush across the membrane, the charge
  gap shrinks. This is how a cell "fires" a signal.
- **Bioelectric state** = the cell's voltage treated as a piece of
  information, not just biology = a light switch's position. Off/on,
  low/high voltage, read as data instead of just as physiology.

**The connection that matters for this book:**
Acheron's core idea depends on reading a cell's voltage as if it were a
stored bit (a 0 or a 1). Chapter 2's ion imbalance is the physical cause;
this chapter's voltage is the measurable effect; the next chapters
(Bistable Switches) are about forcing that voltage to stay locked at one
of two states on purpose, instead of drifting.

**Analogy chain:**
Ion imbalance (Chapter 2) = the cause. Voltage = a stretched rubber band
= the stored tension that imbalance creates. Resting potential = the
band's normal stretched state, held there by the ion pumps working
constantly. Depolarization = the band snapping looser as ions cross.
Bioelectric state = the band's position, read as a light switch: this
tension level means "1," that one means "0."

---

## Chapter 4: DNA & Genes 101

**What DNA actually is (one line):**
DNA is a long molecule made of a 4-letter code (A, T, C, G) that stores
the instructions for building and running a cell.

**Key parts, in your style:**

- **Gene** = a chunk of DNA that codes for one specific protein = a
  single recipe in the recipe book. One recipe, one dish (protein).
- **Protein** = the thing a gene actually builds = the finished dish.
  Proteins are the workers: they build structures, speed up reactions,
  form the ion channels and pumps from Chapter 2.
- **Promoter** = a DNA switch sitting in front of a gene, controlling how
  often it's read = a volume knob. Turn it up, the cell makes more of
  that protein. Turn it down or off, it makes less or none.
- **Expression** = a gene actually being read and turned into protein =
  the recipe being cooked. A gene sitting unused in the DNA is a recipe
  in the book that nobody's cooking yet.

**The connection that matters for this book:**
Acheron's plan is to add a new, custom gene circuit into the cell's
existing recipe book. A promoter (volume knob) is what an engineer can
attach in front of a custom gene to control it deliberately, rather than
letting the cell decide on its own. Chapter 5 (Genetic Circuits 101) is
about wiring several of these gene + promoter pairs together on purpose.

**Analogy chain:**
DNA = the recipe book. Gene = one recipe in it. Protein = the dish that
recipe produces. Promoter = the volume knob in front of the recipe,
controlling how often it gets cooked. Expression = the recipe actually
being cooked right now, not just sitting on the page.

---

## Chapter 5: Genetic Circuits 101

**What a genetic circuit actually is (one line):**
A genetic circuit is a small set of genes wired together so their
promoters (volume knobs) control each other, the same way electronic
circuits wire components together so they control each other.

**Key parts, in your style:**

- **Repressor** = a protein that turns a promoter's volume knob down or
  off = a mute button. It's made by one gene and physically blocks
  another gene's promoter.
- **Feedback loop** = when a gene's output eventually affects its own
  input = a thermostat. The result of the circuit reaches back and
  changes the circuit's own next step.
- **Synthetic biology** = deliberately designing and inserting a genetic
  circuit that doesn't occur naturally = writing new sheet music for an
  existing orchestra (the cell). The musicians (proteins, ribosomes) are
  already there; you're handing them a new score.
- **BioBrick** = a standardized, reusable genetic circuit part = a Lego
  brick. Interchangeable pieces (a promoter, a gene, a repressor) that
  different labs can snap together in different combinations.

**The connection that matters for this book:**
Chapter 4's single gene + promoter pair was one instrument. A genetic
circuit is several of those wired so they mute or unmute each other. The
specific circuit Acheron is built around, two genes that each repress
the other, is a **toggle switch**: a circuit designed to sit stably in
one of two states and flip only when deliberately pushed. That's exactly
the "1 or 0, held on purpose" idea from Chapter 3's bioelectric state.
Chapter 7 (Bistable Switches 101) covers that specific circuit in depth.

**Analogy chain:**
Gene + promoter (Chapter 4) = one instrument with one volume knob.
Repressor = a mute button one instrument can press on another. Genetic
circuit = several instruments wired to mute and unmute each other on
purpose. Feedback loop = a thermostat, where the room's temperature
changes what the thermostat does next. BioBrick = a Lego piece, so
circuits can be built from interchangeable parts instead of from
scratch.

---

## Chapter 6: The Core Idea 101

**What Acheron actually is (one line):**
Acheron is a research project testing whether arbitrary binary data (any
0s and 1s, not just biological information) can be stored as a
rewritable, self-healing signal inside living tissue, mainly *B.
subtilis* bacteria.

**Key parts, in your style:**

- **Data storage medium** = whatever physically holds the 0s and 1s = a
  hard drive's platter. A USB stick uses electrical charge trapped in a
  chip. Acheron is testing whether a living cell's own voltage
  (Chapter 3) or gene circuit state (Chapter 5) can play that same role.
- **Self-healing storage** = a storage medium that repairs its own
  damage = a hard drive that regrows a scratched platter back to
  working order. Regular hard drives can't do this. Living tissue, in
  principle, can, because cells regenerate and divide.
- **Bioelectric memory** = using a cell's voltage state (Chapter 3) as
  the stored bit = writing to the rubber band's tension instead of to a
  magnetic platter.
- **Epigenetic memory** = using a gene circuit's on/off state (Chapter 5)
  as the stored bit, instead of voltage = writing to which recipes are
  currently being cooked, instead of to the rubber band.

**The connection that matters for this book:**
This is Acheron's actual bet: take the voltage concept from Part 1
(Chapters 1-3) or the gene-circuit concept from Chapters 4-5, and use
either one as a data bit that survives damage and regrowth, something no
conventional hard drive or flash chip can do. Nobody has fully proven
this works yet, that's the whole point of the rest of this book: what's
been tested, what broke, and what's still an open question.

**Analogy chain:**
Hard drive = dead storage, can't heal itself. Living cell = storage that
can heal itself, if it can be made to hold a bit reliably. Bioelectric
memory = storing that bit in voltage (the rubber band from Chapter 3).
Epigenetic memory = storing that bit in a gene circuit's state (the muted
or unmuted instruments from Chapter 5). Acheron = testing whether either
version of "living hard drive" actually works.

---

## Chapter 7: Bistable Switches 101

**What a bistable switch actually is (one line):**
A bistable switch is a circuit built to rest comfortably in only two
states (fully on or fully off) and resist sitting anywhere in between,
the way a real light switch snaps to one side instead of hovering in
the middle.

**Key parts, in your style:**

- **Gardner toggle switch** = the specific two-gene circuit Acheron
  builds on = two people arm-wrestling. Two genes each make a repressor
  (Chapter 5's mute button) that mutes the other gene. Whichever one
  wins the arm-wrestle stays on and keeps the other muted, stably, until
  someone deliberately flips it.
- **Cooperativity** = how sharply a repressor's muting effect kicks in
  once it reaches a threshold = a light switch's snap, not a dimmer.
  High cooperativity is what makes the arm-wrestle end in a clean win
  instead of a permanent tie.
- **Promoter strength mismatch** = when the two genes' volume knobs
  (Chapter 4) aren't equally strong = an arm-wrestle where one arm is
  much stronger than the other. Real measured promoters used in this
  design vary in strength by more than three orders of magnitude, so a
  mismatch is a realistic risk, not a hypothetical one.
- **Monostable dead switch** = what happens when that mismatch is too
  large = the arm-wrestle has a foregone winner. The circuit stops being
  a switch at all and just permanently sits in one state, unable to
  store a second value.

**The connection that matters for this book:**
This is the actual engineering constraint the project's own simulation
(`simulations/gardner_toggle_circuit.py`) found: using real,
BioBrick-measured promoter strengths instead of a made-up placeholder
number reveals that mismatched promoters can collapse the switch into
the "monostable dead switch" failure above. Getting two promoters
close enough in strength is a real design requirement, not a detail.

**Analogy chain:**
Genetic circuit (Chapter 5) = two instruments muting each other.
Bistable switch = the same idea, but built specifically to snap
cleanly to one of two states, like an arm-wrestle with a clear winner.
Cooperativity = how sharp that snap is. Promoter mismatch = one arm
being much stronger than the other, which can rig the match every time.
Monostable dead switch = a rigged match: no real toggle left, no
second value it can ever store.

---

## Chapter 8: Why Planaria First, Then B. subtilis 101

**What actually happened (one line):**
Acheron started with planarian flatworms, then moved bacteria
(*B. subtilis*) to the front, because the planarian approach's core
assumption broke under closer testing and bacteria's didn't.

**Key parts, in your style:**

- **Passive persistence** = the original planarian idea: a cell just
  naturally holds a voltage state on its own = a phone left on a table,
  hoping the battery doesn't drain. The first simulation showed this
  could hold a bit for 24+ hours, but only in a perfectly quiet,
  noise-free model.
- **Noise floor** = the real-world electrical jitter every living cell
  actually has, that a clean simulation leaves out = static on a phone
  line. When realistic biological noise was added back in, that same
  "24+ hour" result collapsed to about a coin flip's worth of accuracy,
  the stored bit became unreliable.
- **Engineered bistable circuit** = the fix: instead of hoping a cell
  passively holds a state, actively build the toggle switch from
  Chapter 7 into it = installing a real deadbolt instead of hoping a
  door stays shut on its own.
- **Cell-coupling assumption** = the specific thing the planarian
  approach still depends on and has never been directly measured: that
  neighboring planarian cells reliably pass a bioelectric state to each
  other = assuming a bucket brigade works without ever testing whether
  one worker actually hands the bucket to the next.

**The connection that matters for this book:**
Ranking all three candidate approaches by how much unproven risk each
one still hides put the *B. subtilis* engineered toggle switch
(Chapters 5 and 7) as the best-grounded option, and the original
planarian passive-persistence idea as the weakest-evidence one. That's
why this book, and the project itself, now treats *B. subtilis* as the
main path and planaria as a less-grounded fallback, the reverse of
where the project started.

**Analogy chain:**
Passive persistence = a phone left on a table, hoping the battery
holds. Noise floor = the static that phone actually has to survive in
the real world, which the first, too-clean test left out. Engineered
bistable circuit = swapping "hoping it holds" for an actual deadbolt
(Chapter 7's toggle switch). Cell-coupling assumption = an unproven
bucket-brigade handoff the planarian path still leans on. Result:
bacteria's deadbolt is tested and holds up better than the worm's
bucket brigade, so bacteria now leads.

---

## Chapter 9: Reading the Signal 101

**What the readout problem actually is (one line):**
Even if a *B. subtilis* toggle switch (Chapter 7) correctly stores a bit,
correctly reading that bit back out can still fail, because the cell has
its own natural electrical activity that has nothing to do with the
stored data.

**Key parts, in your style:**

- **Readout** = the act of measuring a cell's voltage to find out which
  state it's in = checking a light switch's position. It should be a
  simple lookup, but only if nothing else is jiggling the switch while
  you look.
- **Native potassium-wave signaling** = a real, already-published
  electrical rhythm that *B. subtilis* colonies do naturally, for their
  own reasons, unrelated to anything this project builds = a neighbor's
  radio playing through the wall. It was there before Acheron, and it
  doesn't care about the stored bit.
- **Signal corruption** = when that unrelated rhythm distorts the voltage
  reading = static drowning out the actual radio station you're trying
  to tune in. The reading looks wrong even if nothing is actually broken.
- **Underlying state vs. reading** = the crucial distinction: the gene
  circuit's real stored state (Chapter 5-7) can still be intact and
  correct, while the voltage reading taken from it is corrupted = the
  light switch never moved, but someone's shaking the wall it's mounted
  on, so a glance at it gives you the wrong answer.

**The connection that matters for this book:**
This is a separate failure mode from Chapter 8's noise floor problem.
Chapter 8 was about the stored state itself degrading. This chapter is
about the stored state being fine, but the readout method (measuring
voltage) picking up interference from the bacteria's own normal biology
on top of it. Both have to be solved, and they're solved differently:
one needs a better-engineered circuit, the other needs a better or
different way to read the signal out.

**Analogy chain:**
Readout = glancing at a light switch to check its position. Native
potassium-wave signaling = a neighbor's radio bleeding through the wall,
present for reasons that have nothing to do with your switch. Signal
corruption = static that makes the switch's position hard to read
correctly. Underlying state vs. reading = the switch itself never
moved, only your ability to see it clearly did, which means the fix is
a better way to look, not a better switch.

---

## Chapter 10: What's Proven vs. What's Assumed 101

**What this chapter actually is (one line):**
A plain accounting of which claims in Chapters 6-9 rest on a real
citation or a labeled simulation result, and which ones are still
untested assumptions, so nothing gets overstated.

**Key parts, in your style:**

- **Proven (simulated)** = a result that came out of an actual model run,
  with its caveats stated = a test drive in a simulator. It tells you
  something real about how the design behaves under the assumptions you
  fed it, but it's not the same as driving the real car.
- **Proven (cited)** = a result backed by someone else's real,
  published lab work = borrowing a fact from a textbook you trust,
  instead of guessing.
- **Assumed** = something the project currently needs to be true, but
  nobody has actually tested = a bridge nobody has driven a truck over
  yet, even though the blueprint says it should hold.
- **Open question** = an assumption that's explicitly flagged instead of
  quietly relied on = a warning sign left on that untested bridge,
  instead of pretending the sign isn't needed.

**The status board so far:**

- Gardner toggle switch topology and promoter-mismatch risk (Chapter 7):
  **proven, simulated**, using real BioBrick-measured promoter numbers,
  not invented ones.
- Passive planarian persistence holding for 24+ hours (Chapter 8):
  **disproven under realistic noise**, simulated with and without noise,
  both results kept and reported.
- Native potassium-wave interference corrupting readout (Chapter 9):
  **proven, cited**, a real published *B. subtilis* phenomenon, not
  something invented for this project.
- Planarian cell-to-cell coupling reliably passing a bioelectric state
  (Chapter 8): **assumed, open question**, never directly measured in
  any organism.
- Whether an engineered circuit's state survives actual tissue damage
  and regrowth, not just ordinary cell division: **the single biggest
  open question**, nobody has tested this in any organism, in any lab,
  yet.

**The connection that matters for this book:**
That last item, damage-and-regrowth survival, is the one thing every
other chapter's optimism depends on. Chapter 11 is the actual wet-lab
experiment designed to answer it.

**Analogy chain:**
Proven (simulated) = a test drive in a simulator. Proven (cited) = a
fact borrowed from a trusted textbook. Assumed = an untested bridge the
blueprint says should hold. Open question = a warning sign left
honestly on that bridge instead of hidden. The damage-and-regrowth
question = the one bridge the whole project still needs someone to
actually drive across.
