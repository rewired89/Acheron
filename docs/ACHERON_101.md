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
