# Decision Memo: Is Voltage the Point of Acheron?

**Status:** a decision for the founders. This memo lays out the choice, what each
path costs, and a recommendation (Path C, below). The recommendation is not
adopted until the founders record a decision in the last section. Written
October 2026 from the audit (`docs/SCIENTIFIC_AUDIT_2026.md`, Parts 24 to 30) and
the patentability assessment.

## The question

Every simulation of a voltage readout assumes a link that nobody has built: the
state of the engineered circuit setting a measurable membrane voltage. The first
experiment (Experiment 1) does not need that link, because it reads a
fluorescent reporter. So running it does not settle the question, it only delays
it. When Experiment 1 passes, the project will have a working reporter-read
toggle, and whether that is interesting or a rerun of existing work depends on
whether voltage is the point.

## Why it has to be decided before strains are ordered

The two paths want different chassis.

- The BioBrick promoter parts were characterized in *B. subtilis* W168.
- The potassium-wave literature behind the voltage and phase work used NCIB
  3610 (Prindle et al. 2015, Yang et al. 2020).
- Level encoding wants the yugO channel weakened or deleted. Phase encoding needs
  yugO intact (audit Part 25).

Choosing W168 now and voltage later means re-characterizing the promoter parts in
a new background after the money for the first strains is spent.

## One fact from the founder's own words

The core hypothesis, as the founder stated it (21 September 2026), is: write bits
into a living thing, damage it, the organism detects the damage by itself,
transfers the data into its own regrowth, and the information is kept. Voltage is
not in that sentence. The organism is interchangeable, and so, on that wording,
may be the physical form of the stored state. Whether voltage is essential to the
vision, or one of several ways to hold the state, is the founders' call.

## Path A: voltage is central

- **What it means:** the project is about a bioelectric state. The stored state
  must be written to, and read from, membrane voltage.
- **Needs:** the circuit-to-voltage link (never built by anyone; Stage 3 in the
  roadmap is still "to be scoped"; Experiment 5), a resolved readout
  (level encoding or phase encoding), and a chassis decision between W168 and
  3610.
- **Experiments in play:** 1 first (it still gates everything), then 5 and 6.
- **Closest prior art:** Yang et al. 2020 already wrote and read voltage patterns
  in *B. subtilis* biofilms. What survives is that their memory is a
  protein-level modification that would not survive division.
- **Weak points on record:** the voltage link is unbuilt; the electrical readout
  needs the undisturbed doubling time and the reporter readout does not (audit
  Part 29); phase encoding rests on an assumed coupling with no working
  mechanistic model behind it (Part 26); a sustained voltage shift of about 35 mV
  breaks the readout in simulation, using voltage targets inherited from the
  planarian model.
- **Patent drafts it favors:** draft C (phase-referenced encoding, narrow,
  closest prior art) and draft A.

## Path B: a reporter-read genetic state is the product

- **What it means:** the stored state is held in the cell's own circuit and read
  with a fluorescent reporter. Voltage is dropped or moved to a future option.
- **Needs:** nothing that is not already planned. W168 and the characterized parts
  are fine. The strain mismatch stops mattering for the main line.
- **Experiments in play:** 1 to 4 and 7; 5 and 6 become optional.
- **Closest prior art:** Bonnet, Subsoontorn & Endy (2012) built a heritable,
  rewritable DNA recombinase latch with non-destructive fluorescent readout. A
  DNA latch also survives damage and regrowth for the same reason a protein
  toggle does, so "survives division" does not separate the two (audit Part 29).
- **Weak point on record:** no functional advantage over a DNA latch is
  established. What could separate them is the damage-detecting, self-reinforcing
  part (`bsubtilis_16`, patent draft B), which is simulated and unbuilt.
- **Cost of choosing it:** the word "bioelectric" would have to leave the pitch,
  README and the interview guide, and the deck's framing would change.
- **Patent drafts it favors:** draft A and draft B. Draft C is dropped.

## Path C: reporter first, voltage held open

Run Path B as the gate, keep voltage as a later option (Stage 3), and decide the
chassis for the voltage work only if Experiment 1 to 3 pass.

- **What it buys:** nothing is spent on the unbuilt link before there is a working
  toggle.
- **What it costs:** if voltage later needs 3610, the promoter parts must be
  re-characterized there, and the first strains will not carry over unchanged.
  This path accepts that cost.

## Side by side

| | Path A | Path B | Path C |
|---|---|---|---|
| Chassis | likely 3610, yugO intact or deleted by encoding choice | W168 | W168 now, maybe 3610 later |
| Unbuilt link needed | yes | no | later, maybe |
| Closest prior art | Yang 2020 | Bonnet 2012 | both, in sequence |
| Biggest risk | link never works | no advantage over a DNA latch | spending twice on the chassis |
| Pitch wording | "bioelectric memory" stays | "bioelectric" leaves | staged, voltage as option |
| Patent drafts | A, C | A, B | A, B, then C if earned |

## Questions only the founders can answer

1. Is voltage essential to what Acheron is, or one way to hold the state?
2. If voltage were dropped, would the project still be the project?
3. Is a reporter-read toggle with damage-triggered reinforcement a product worth
   building, given Bonnet 2012 exists?
4. If Path A, which of level or phase encoding, and therefore which chassis?
5. When must the strain order go in? The decision belongs before it.

## What would change the recommendation

- A measured fitness cost and loss rate that make long-term holding fail for any
  genetic circuit would weaken Paths B and C together.
- A mechanistic model that reproduces the anti-phase result from the potassium
  dynamics (audit Part 26) would strengthen Path A.
- A real functional advantage over a DNA latch, such as faster rewriting,
  damage-triggered repair or a use a latch cannot serve, would strengthen B.

## Recommendation: Path C, reporter first, voltage held open

This is Claude's recommendation. It is not a decision.

1. **It is consistent with how the founder defines Acheron, which does not settle
   it.** Write, damage, detect, transfer, keep. That is a functional description
   and is silent on mechanism by design. It does not require voltage, and it does
   not require a reporter either. It is therefore no evidence for Path B over
   Path A. It only means that running reporter experiments first does not
   contradict the project's own definition.
2. **It is the cheapest ordering.** Experiment 1a gates every path. If the toggle
   does not work, no path survives, and nothing has been spent on the unbuilt
   voltage link.
3. **It does not wait on Experiment 1 for information it cannot give.** A passing
   Experiment 1 does not choose between A and B, so the choice is made on the
   definition of the project, now, not on that result. A failing Experiment 1a ends
   all three paths together.
4. **The cost is accepted in advance.** If a voltage path is later chosen and needs
   NCIB 3610 with the yugO channel intact, the promoter parts must be
   re-characterized in that background and the first strains will not carry over.
   That cost is the price of not guessing now, and it is smaller than building the
   voltage link before knowing the toggle works.
5. **Wording follows the path.** Until the decision changes, written material
   should describe the stored state as held in the cell's own circuit and read
   with a reporter, with voltage as a planned later readout, not as the present
   claim.

### What Path C does not settle (read this before using it)

Path C is a **funding and sequencing** choice, not a resolution of the novelty
question. The novelty question is binary:

- If the product is a reporter-read genetic state, the project overlaps
  functionally with Bonnet, Subsoontorn & Endy (2012) (a heritable, rewritable DNA
  recombinase latch with non-destructive fluorescent readout), and any novelty
  claim must be written against that paper, not only against Yang et al. 2020.
- If the product is voltage, the novelty claim is real and the repressor-to-channel
  link is the whole bet.

Under Path C neither claim is made. So, until the founders record a decision:
- **The novelty claim is provisional.** "Survives division and regrowth" does not
  by itself separate Acheron from Bonnet et al. (2012), which also survives
  division. The README states this.
- **No investor-facing material may claim voltage novelty.** That includes the
  deck, the pitch document, the campaign drafts and the interview guide.
- **No material may claim a functional advantage over a DNA latch** unless one has
  been shown. None has.
- Deferral is allowed to last only as long as the reporter work lasts. If the
  decision is still open when Experiment 1a returns, the memo is overdue.

**Conditions that would move the project to Path A:** Experiments 1a to 3 pass and
the founders judge voltage essential; a mechanistic model reproduces the anti-phase
result (audit Part 26); Stage 3 is scoped and funded.
**Conditions that would move it to Path B for good:** a functional advantage over a
DNA latch is found that does not depend on voltage; or the founders decide voltage
is not part of the project.

## Decision record (to be filled in by the founders)

- Decision (A, B or C):
- Date:
- Who decided:
- One-line reason:
- Revisit when:
