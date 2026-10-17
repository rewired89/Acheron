# Acheron Project: Critical Scientific Audit
## Senior Interdisciplinary Scientist Review

**Date:** January 2026
**Reviewer Perspective:** Developmental biology + bioelectric signaling + biophysics + bioengineering + unconventional computing

**Purpose:** Honest assessment of what's been answered, what's assumed, what's right/wrong, and what comes next.

---

## Executive Summary: The Brutal Truth

**What you've built:** A comprehensive, well-engineered **simulation architecture** for bioelectric memory with clever fault-tolerance mechanisms.

**What you haven't proven:** That any of this works in actual living tissue.

**Critical gap:** 100% simulation, 0% wetware validation.

**Biggest risk:** Confusing morphogenetic memory (which Levin proved exists) with arbitrary information storage (which you're assuming works the same way).

---

## Part 1: Audit Against Critical Scientific Questions

### Question 1: Information Capacity

**What the project claims:**
- 130 bits demonstrated in simulation (Phase 1)
- Scalable to thousands of bits with Bio-RAID (Phase 2)
- Multi-bit storage with 3x3 cell clusters per bit

**Scientific reality check:**

✅ **RIGHT:**
- Using spatial encoding (separate cell clusters per bit) is sound
- Gap junction coupling theory supports pattern isolation if g_gap is low enough
- BETSE physics is legitimate for modeling diffusion-reaction systems

❌ **WRONG/UNPROVEN:**
- You've shown patterns persist *in simulation*, not in living planarian cells
- Real cells have biological noise (gene expression stochasticity, metabolic fluctuations)
- Your simulation assumes ion channel densities are constant - they're not in real cells
- Cell-to-cell variability in real tissue is 20-50% (your simulation has 0%)

**Gap:** No experimental data on how many distinguishable voltage states a real planarian cell can maintain.

---

### Question 2: Write Mechanism (Optogenetic Stimulation)

**What the project claims:**
- ChR2 (blue light) → depolarize to -10mV
- Halorhodopsin (yellow light) → hyperpolarize to -80mV
- 1-5 seconds per bit write time

**Scientific reality check:**

✅ **RIGHT:**
- Optogenetics is the correct approach for writing voltage patterns
- ChR2 and Halorhodopsin are well-characterized tools
- Light-gated ion channels work in non-neural cells

❌ **WRONG/ASSUMPTIONS:**
- You assume planarian cells can be transfected with opsins (have you checked transfection protocols?)
- You assume opsins express uniformly (they don't - heterogeneity is 30-70% expression levels)
- You assume light penetrates uniformly (tissue scattering is significant beyond 100-200 μm)
- You assume voltage *stays* at -10mV or -80mV after light turns off (not guaranteed)

**Critical unknowns:**
1. Can planarian somatic cells be stably transfected with opsins?
2. What's the actual voltage response curve (light intensity → voltage)?
3. How long does the voltage change persist after light pulse ends?

**Gap:** Zero experimental data on optogenetic control in planarian *somatic* cells (neurons yes, somatic cells unknown).

---

### Question 3: Read Mechanism (Voltage Sensing)

**What the project claims:**
- Voltage-sensitive dyes (ANNINE-6, QuasAr)
- Camera imaging at <1 second per bit
- Threshold: >-40mV = '1', <-40mV = '0'

**Scientific reality check:**

✅ **RIGHT:**
- Voltage-sensitive dyes exist and work in tissue
- Thresholding is standard approach for binary readout
- Majority voting across 3x3 cluster adds noise tolerance

⚠️ **QUESTIONABLE:**
- QuasAr and ANNINE-6 require genetic encoding or external application
- External dyes (ANNINE-6) require reapplication (not compatible with long-term storage)
- Genetic dyes (QuasAr) require transfection (same issue as write mechanism)
- Your -40mV threshold is arbitrary - real cells might not have bimodal voltage distribution

**Gap:** No experimental characterization of voltage distribution in planarian tissue at rest and after perturbation.

---

### Question 4: Stability Timescale (24+ Hours)

**What the project claims:**
- 24+ hour persistence without active maintenance
- Integrity ratio >0.7 after 24 hours (simulation)
- Patterns stabilize into morphogenetic attractors

**Scientific reality check:**

✅ **RIGHT (in principle):**
- Levin showed morphogenetic patterns (head/tail identity) persist for weeks
- Gap junction-coupled networks can have multiple stable attractors
- Non-excitable cells don't need ATP to maintain voltage (unlike neurons)

❌ **CRITICAL ASSUMPTION:**
- **You're conflating two different things:**
  1. **Morphogenetic attractors** (natural developmental patterns evolved over millions of years)
  2. **Arbitrary voltage patterns** (your custom binary data)

**The key question you haven't answered:**
- Do *arbitrary* voltage patterns stabilize the same way natural morphogenetic patterns do?
- Or do arbitrary patterns decay back to the cell's natural attractor state?

**This is the single most important question in your entire project.**

**Biological plausibility:**
- Morphogenetic attractors are stable *because* they're encoded in gene regulatory networks
- Your arbitrary patterns have no gene regulatory backup - they're just transient voltage perturbations
- Analogy: You're trying to store data in a ball rolling on a landscape with natural valleys (morphogenetic attractors) - your data might just roll back into the nearest valley

**What you need:**
- Experimental data showing *arbitrary* voltage patterns persist in planarian tissue
- Not Levin's experiments (those were manipulating natural developmental signals)
- Your own experiments writing random patterns and measuring decay

**Gap:** No evidence that arbitrary patterns persist. This is a foundational assumption.

---

### Question 5: Error Rate and Bio-RAID

**What the project claims:**
- 0% logical errors with 3-way replication + majority voting
- 85% "healthy-3-live" time under space harsh conditions
- REGEN-IN-PLACE protocol for self-healing

**Scientific reality check:**

✅ **RIGHT:**
- Bio-RAID architecture is clever engineering
- Majority voting is standard error correction
- Regeneration is planarians' superpower

✅ **IMPRESSIVE:**
- Separation of bio_health vs pattern_fidelity is conceptually sound
- Environment-adaptive degradation models show good thinking
- Patent claims are well-structured

❌ **BUT:**
- All metrics are from simulation with idealized assumptions
- Real tissue regeneration takes days-weeks (your simulation may compress this)
- During regeneration, voltage patterns ARE disrupted (not modeled accurately)
- Cell migration during healing creates connectivity changes (not in your model)

**Gap:** No experimental validation of self-healing with data retention.

---

### Question 6: Energy Requirements

**What the project claims:**
- "Low energy" compared to neurons
- 1-5 mW power consumption (Phase 4 hybrid)

**Scientific reality check:**

⚠️ **UNCLEAR:**
- You haven't modeled ATP consumption rates
- Optogenetic write operations require significant light power (mW-W range for DMD)
- Voltage imaging requires excitation light (more power)
- Cell culture requires temperature control, media perfusion (not free)

**What you need:**
- System-level power budget (not just cells, but entire hardware stack)
- Compare to actual alternatives (FRAM, MRAM for space applications)

**Gap:** No power analysis beyond hand-waving "lower than neurons."

---

### Question 7: Temperature and Environmental Stability

**What the project claims:**
- Extreme environment survival (space, radiation, deep-sea)
- Temperature tolerance from planarian biology

**Scientific reality check:**

⚠️ **OVERSTATED:**
- Planarians tolerate 4-25°C (not extreme heat or cold)
- Space has -270°C to +120°C extremes (planarians would freeze or denature)
- Radiation tolerance: some studies show planarians handle 1000 Gy (impressive), but:
  - Your *patterns* might not survive radiation damage (cell death → pattern loss)
  - Bio-RAID helps, but you need 3 healthy tiles (what if radiation kills all 3?)

**More realistic framing:**
- Planarians are more robust than neurons (true)
- But they're not magic - they need water, moderate temps, nutrients
- Better to say: "Robust for *certain* extreme environments" (deep-sea yes, vacuum no)

**Gap:** No environmental stress testing data.

---

## Part 2: What You Got Right

### 1. ✅ BETSE Simulation Approach is Valid
- Using BETSE-inspired physics is credible
- Gap junction coupling, ion diffusion, membrane dynamics are real
- Your parameter optimization (g_gap, R_mem, tau_relax) shows good engineering

### 2. ✅ Bio-RAID Architecture is Clever
- 3-way replication + majority voting is enterprise-grade fault tolerance
- REGEN-IN-PLACE protocol is novel and patent-worthy
- Separation of bio_health from pattern_fidelity is conceptually sound

### 3. ✅ Performance Engineering Strategies are Sound
- Parallelism (100 tiles simultaneously) is correct way to scale throughput
- Micro-tiles (0.5mm instead of 2mm) reduces settling time
- Hydrogel bridges for low-resistance coupling is smart

### 4. ✅ Patent Strategy is Well-Thought-Out
- 3 patents filed (Bio-RAID core, self-healing, environment-adaptive)
- Claims are specific enough to be defensible, broad enough to be valuable
- Freedom to operate: no blocking patents (you checked)

### 5. ✅ Hybrid Architecture (Phase 4) Shows Vision
- Combining planarians (storage) + neurons (compute) + silicon (control) is novel
- Recognizes strengths of each substrate
- Addresses speed concerns without abandoning core innovation

### 6. ✅ Strategic IP Protection (bioRxiv manuscript)
- You correctly separated concepts (shareable) from implementation (trade secrets)
- Protective disclaimer is good strategy
- Patents filed before publication (critical)

---

## Part 3: What You Got Wrong (or Haven't Proven)

### 1. ❌ Assuming Arbitrary Patterns Work Like Morphogenetic Patterns

**The problem:**
- Levin proved *natural* morphogenetic patterns persist (head/tail identity)
- You're assuming *arbitrary* patterns (your binary data) persist the same way
- These might not be equivalent

**Why this matters:**
- Morphogenetic patterns are evolutionarily encoded in gene networks
- Your patterns are artificial voltage perturbations with no genetic backup
- They might decay back to the cell's natural attractor state

**What you need:**
- Literature review: Has anyone stored *arbitrary* information in bioelectric gradients?
- Theoretical analysis: Do your patterns lie in stable attractor basins?
- Experimental test: Write random pattern, measure decay curve

### 2. ❌ Underestimating Biological Variability

**Your simulation assumes:**
- All cells have identical ion channel densities (not true - 20-50% variability)
- All gap junctions have same conductance (not true - varies 2-10x)
- No gene expression noise (not true - cells are stochastic)

**What this means:**
- Real tissue will have higher error rates than your 0% simulation result
- Some cells will be "bad bits" (can't hold voltage reliably)
- You'll need more redundancy than you think

### 3. ❌ Speed Estimates May Be Optimistic

**Your claim:** 10-20 bits/sec with performance engineering

**Reality check:**
- Voltage settling time in real tissue is slower than simulation (damping, viscosity)
- Gap junction conductance in vivo is lower than you assume (tortuous extracellular paths)
- Majority voting across 3x3 cluster requires 9 stable measurements (serial or parallel?)

**More realistic:** 1-5 bits/sec with heavily engineered system

### 4. ❌ Missing System-Level Energy Budget

**You claim:** Low power

**What's missing:**
- Optogenetic write: DMD requires 1-10W (dominates system power)
- Voltage imaging: Camera + excitation light + optics = 1-5W
- Cell culture: Incubator, pumps, media circulation = 10-100W
- Control electronics: FPGA, ADC/DAC = 1-10W

**Total system power:** 20-125W (not mW)

**Comparison:** MRAM space-certified module = 0.1-1W

**Conclusion:** Your system is NOT low-power when you include write/read hardware.

### 5. ❌ Regeneration Behavior with Arbitrary Patterns is Unknown

**You assume:**
- Planarians regenerate AND preserve your data patterns

**What Levin actually showed:**
- Planarians regenerate WITH natural morphogenetic patterns
- No one has tested regeneration with arbitrary voltage patterns stored

**Key experiment needed:**
- Store arbitrary pattern → damage tissue → let regenerate → read pattern
- Does it come back correctly? Partially? Not at all?

---

## Part 4: Are Planarians the Best Choice?

### Option 1: Planarian Somatic Cells (Your Current Choice)

**Pros:**
- ✅ Best regeneration capability (fragments → whole organism)
- ✅ Levin's extensive literature (scientific foundation)
- ✅ Non-neural (not trying to compete with neural biocomputers)
- ✅ Radiation tolerant (1000 Gy demonstrated)

**Cons:**
- ❌ Slow bioelectric dynamics (minutes-hours, not milliseconds)
- ❌ Difficult to culture long-term in vitro (prefer whole organism environment)
- ❌ Transfection protocols for somatic cells are not well-established
- ❌ No existing voltage characterization data for arbitrary pattern storage

**Verdict:** Good choice IF you can prove arbitrary patterns persist (big if).

---

### Option 2: Engineered Cell Lines (e.g., HEK293, CHO)

**Pros:**
- ✅ Easy to transfect (optogenetics straightforward)
- ✅ Reproducible behavior (low cell-to-cell variability)
- ✅ Well-characterized ion channels
- ✅ Can engineer gap junction density precisely

**Cons:**
- ❌ No regeneration (need external self-healing mechanisms)
- ❌ Less stable bioelectric patterns (not evolved for morphogenetic memory)
- ❌ Less radiation tolerant than planarians
- ❌ Less compelling story for investors ("engineered cells" vs "planarian superpower")

**Verdict:** Easier to prove concept, but weaker market differentiation.

---

### Option 3: Cardiomyocytes (Heart Muscle Cells)

**Pros:**
- ✅ Strong gap junction coupling (natural syncytium)
- ✅ Stable resting potentials (-80 to -90 mV)
- ✅ Well-characterized electrophysiology
- ✅ Can be derived from iPSCs (scalable)

**Cons:**
- ❌ Constantly beating (pacemaker activity = noise)
- ❌ No regeneration capability
- ❌ High energy consumption (contractile machinery)

**Verdict:** Poor fit for persistent memory.

---

### Option 4: Hybrid Approach (Planarians + Synthetic Biology)

**Idea:**
- Start with planarian cells
- Engineer them with:
  - More stable ion channel configurations
  - Synthetic gene circuits that lock voltage states
  - Reporter proteins that indicate voltage state

**Pros:**
- ✅ Keep planarian regeneration
- ✅ Reduce reliance on "natural" morphogenetic attractors
- ✅ Engineer designer attractors with synthetic biology

**Cons:**
- ❌ Much harder (2-3 years of molecular biology)
- ❌ Requires deep planarian genetic toolkits (less developed than model organisms)

**Verdict:** Best long-term solution, but requires significant bioengineering expertise.

---

## **Recommendation: Stick with Planarians, BUT...**

Planarians are your best bet **if you can answer the key question first:**

**Do arbitrary voltage patterns persist in planarian somatic cells?**

If YES → Full steam ahead with current plan
If NO → Need synthetic biology to engineer designer attractors
If PARTIAL → Might work with enough error correction (Bio-RAID helps)

---

## Part 5: What Are the Next Steps?

### Immediate Priority (This Month)

**1. Literature Deep-Dive: "Arbitrary Bioelectric Pattern Persistence"**

**Questions to answer:**
- Has anyone stored arbitrary information in bioelectric gradients (not just morphogenetic)?
- What are the decay rates for non-natural voltage perturbations?
- Are there theoretical models for attractor stability in gap junction networks?

**Where to look:**
- Levin Lab papers (all of them - read carefully)
- Computational neuroscience (attractor networks in non-neural tissue)
- Bioelectricity + memory keywords

**Expected outcome:**
- If literature supports arbitrary patterns → proceed with confidence
- If literature is silent → you're in truly novel territory (higher risk, higher reward)
- If literature says it doesn't work → pivot required

---

**2. Minimal Viable Experiment Design (Paper Experiment)**

**Goal:** Define the absolute simplest wetware test to validate core assumption

**Proposed experiment:**
- 2mm × 2mm planarian tissue explant
- Optogenetic transfection (ChR2 only, skip Halorhodopsin for simplicity)
- Write ONE voltage pattern (depolarize center cluster)
- Measure voltage every 6 hours for 48 hours
- Compare to control (no light stimulation)

**Success criteria:**
- Voltage in center cluster stays >20 mV higher than periphery for 24+ hours
- If yes → foundational assumption validated
- If no → need to rethink entire approach

**Why this matters:**
- This experiment costs $10K-$30K (academic collaboration)
- Answers the $5M question (does arbitrary pattern storage work?)
- Must do this BEFORE raising Series A

---

**3. Lab Partnership Outreach**

**Target labs:**
1. **Levin Lab (Tufts)** - Best scientific fit, but may be IP-competitive (Morphoceuticals)
2. **Wyss Institute (Harvard)** - Bioengineering focused, less IP conflict
3. **Stanford Bio-X** - Good optogenetics infrastructure
4. **Janelia Research Campus** - Advanced imaging capabilities

**Pitch:**
- You: Provide theory, simulation, funding
- Them: Provide wetware expertise, facilities, credibility
- Joint publication (you get commercial rights, they get academic credit)

**Budget:** $50K-$150K for minimal proof experiment (6-12 months)

---

### Near-Term (3-6 Months)

**4. Gap Junction Characterization from Literature**

**Goal:** Extract real biological parameters for your simulation

**What you need:**
- Gap junction conductance (g_gap) in planarian tissue (measured values)
- Connexin expression levels (which connexins do planarians use?)
- Voltage coupling coefficients (how strongly do neighbor cells affect each other?)

**Why this matters:**
- Your current g_gap = 0.005 nS is a guess (optimized for simulation, not from data)
- Real values might be 10x higher or lower
- This changes your entire persistence prediction

**Expected outcome:**
- Update simulation with real biological parameters
- Rerun persistence tests
- See if conclusions still hold

---

**5. Competitive Intelligence: Morphoceuticals**

**Why they matter:**
- They're commercializing Levin's bioelectric work
- Focus on regenerative medicine (not computing)
- But might have overlapping IP on "bioelectric pattern control"

**What you need to know:**
- Their patent claims (USPTO search)
- Their technology scope (can they pivot to computing?)
- Potential partnership vs competition

**Action:**
- Read all Morphoceuticals patents
- Identify overlap with your claims
- Decide: collaborate or compete?

---

### Medium-Term (6-12 Months)

**6. Phase 3A Proof-of-Concept (After Wetware Validation)**

**Only proceed if minimal viable experiment succeeds**

**Goal:** 2-tile ABS with regenerating trace

**Why wait:**
- No point building Phase 3 if Phase 1 (arbitrary pattern storage) doesn't work
- Phase 3 assumes Phase 1 and Phase 2 are real

---

**7. NIAC Follow-Up**

**Current status:** Applied, no response yet

**Strategy:**
- Wait for their response
- If accepted → use their mentorship and network
- If rejected → ask for feedback, reapply next cycle with wetware data

**Don't let NIAC timeline drive technical decisions:**
- Better to have real data late than fake confidence early
- NIAC funds multiple phases (you can enter later with stronger results)

---

### Long-Term (12+ Months)

**8. Patent #4 and #5 - Wait for Wetware Validation**

**Current status:**
- Patent #4 (ABS) - design complete, ready to file
- Patent #5 (Hybrid Biocompute) - design complete, ready to file

**Strategic advice:**
- DO NOT file these patents until you have wetware proof of Phase 1
- Patents have 20-year term from filing date
- If Phase 1 doesn't work, these patents are worthless
- Better to wait, prove concept, THEN file with real data

**When to file:**
- After minimal viable experiment succeeds
- When you have preliminary wetware data to cite in application
- Before publishing Phase 3/4 results

---

## Part 6: The Biggest Scientific Risk

### You're Conflating Two Different Things

**1. Morphogenetic Bioelectric Patterns (Levin's Work)**
- These are developmental signals that control body plan
- Evolved over millions of years to be stable
- Backed by gene regulatory networks
- Example: Head vs tail identity in planarians

**2. Arbitrary Information Storage (Your Goal)**
- These are random voltage patterns encoding binary data
- Not evolutionarily selected for stability
- No gene regulatory backup
- Example: "10110101" stored as voltage clusters

**The critical question:**
- Are arbitrary patterns stable the same way morphogenetic patterns are?
- Or do they decay back to the cell's natural attractor?

**Analogy:**
- Morphogenetic patterns = Natural valleys in a mountainous landscape (stable)
- Arbitrary patterns = Temporary hills you're piling up (might erode)

**What makes morphogenetic patterns stable:**
- Gene networks reinforce the voltage pattern (positive feedback)
- Ion channel expression adjusts to stabilize the state
- Gap junction connectivity remodels to support the pattern
- These are SLOW processes (hours-days)

**Your arbitrary patterns might not trigger these stabilization mechanisms**
- You're applying voltage transiently (optogenetic pulse)
- Gene networks might not respond to such brief stimuli
- Pattern might decay before stabilization kicks in

**This is why the minimal viable experiment is critical:**
- If arbitrary patterns persist → your thesis is correct
- If they don't → you need synthetic biology to engineer stability

---

## Part 7: Honest Assessment for Investors/NIAC

### What You Can Honestly Claim

✅ "We've demonstrated in simulation that bioelectric voltage patterns CAN persist for 24+ hours in gap junction-coupled tissue models, using physics-based BETSE modeling validated by Levin Lab."

✅ "We've designed a Bio-RAID architecture that achieves 0% logical errors through 3-way replication and autonomous self-healing, with environment-adaptive fault models."

✅ "We've filed 3 USPTO patent applications covering Bio-RAID core system, self-healing recovery mechanisms, and environment-adaptive longevity."

✅ "We've identified a unique niche: planarian-based bioelectric memory for extreme environments, where regeneration and radiation tolerance provide advantages over neural biocomputing."

### What You CANNOT Honestly Claim (Yet)

❌ "We've proven bioelectric memory works in living tissue"
→ Change to: "We've designed experiments to validate this in living tissue"

❌ "Planarian cells can store arbitrary data for weeks"
→ Change to: "Simulations predict this is possible, pending experimental validation"

❌ "Our system is low-power compared to alternatives"
→ Change to: "Our cell substrate is low-power; system-level power budget depends on write/read hardware"

❌ "Self-healing with data retention is proven"
→ Change to: "Self-healing is a well-documented planarian capability; data retention during regeneration requires experimental validation"

### Recommended Framing for NIAC/Investors

**Current Stage:** "Pre-wetware validation"

**What's been done:**
- Comprehensive simulation framework (BETSE-inspired)
- Bio-RAID fault-tolerance architecture
- Patent applications filed (3)
- Performance engineering strategy (10-20 bits/sec roadmap)

**What's needed:**
- Lab partnership for minimal viable experiment ($50K-$150K)
- Validation that arbitrary voltage patterns persist in planarian tissue
- 6-12 months to proof-of-concept

**Honest risk disclosure:**
- "Key assumption: Arbitrary voltage patterns stabilize like natural morphogenetic patterns. Literature supports plausibility, but experimental validation is required."
- "If validated → clear path to Phase 2-3. If not → pivot to synthetic biology approach to engineer designer attractors."

**This is much stronger than overselling:**
- Shows you understand the science
- Demonstrates technical rigor
- Builds trust (critical for long-term partnerships)

---

## Final Verdict: What You've Built vs What You Need

### What You've Built: ⭐⭐⭐⭐ (4/5 stars)

**Strengths:**
- Excellent simulation architecture
- Clever Bio-RAID engineering
- Well-thought-out patent strategy
- Comprehensive vision (4-phase roadmap)
- Good strategic positioning (space/military/extreme environments)

**What keeps it from 5 stars:**
- Zero wetware validation (simulation ≠ reality)
- Critical assumption unproven (arbitrary pattern persistence)
- Missing system-level analysis (power, thermal, reliability)

### What You Need to Get to 5 Stars:

**1. Answer the Key Question (6-12 months, $50K-$150K)**
- Do arbitrary voltage patterns persist in planarian tissue for 24+ hours?
- This is the make-or-break experiment

**2. Real Biological Parameters (1-3 months, literature work)**
- Gap junction conductance from measurements (not guesses)
- Ion channel densities from planarian transcriptomics
- Update simulations with real data

**3. System-Level Engineering (3-6 months)**
- Power budget for entire system (not just cells)
- Thermal analysis (can cells survive in space hardware enclosure?)
- Reliability modeling with real failure modes

**4. IP Landscape Clarity (1 month)**
- Deep dive on Morphoceuticals patents
- Freedom to operate analysis
- Partnership vs competition decision

---

## Conclusion: You're 70% There

**You've done the hard part:**
- Identified a real gap in the market (persistent bioelectric memory)
- Designed a clever solution (Bio-RAID with planarians)
- Protected IP early (3 patents filed)
- Built comprehensive simulation framework

**What's missing:**
- The 30% that proves it actually works

**My recommendation:**
1. Do the literature deep-dive (this month)
2. Design minimal viable experiment (this month)
3. Secure lab partnership (3 months)
4. Run experiment (6-12 months)
5. **THEN** proceed with Phase 3/4 based on results

**If experiment succeeds:**
- You have a $500M-$1B company (Lockheed/Raytheon will buy)
- Clear path to Series A ($5M-$10M)
- First-mover in planarian computing

**If experiment fails:**
- Pivot to synthetic biology (engineer stability into cells)
- Or pivot to different organism (engineered cell lines)
- Still have Bio-RAID architecture and software IP (licensable)

**Either way, you need real data before raising serious money.**

---

## Part 8: Computational Follow-Up — Noise Floor Validation (August 2026)

This section reports results from actually running the simulation suite against
the question Part 6 raised ("do arbitrary patterns persist the same way
morphogenetic patterns do?") instead of leaving it as an open assumption.

### Finding 1: The 100% / 24h persistence claim is a zero-noise artifact

`simulations/planarian_02_noise_floor.py` re-runs the base persistence model
with realistic biological noise sources (ion channel shot noise, cell-to-cell
variability, metabolic fluctuation, thermal noise) injected.

| Scenario | Integrity @ 24h | SNR | Status |
|---|---|---|---|
| Ideal (zero noise — matches `planarian_01_bioelectric_persistence.py` claim) | 100.0% | 9.7:1 | PASS |
| Mild biological noise | 66.7% | 1.0:1 | FAIL |
| Realistic biological noise | 57.8% | 0.2:1 | FAIL |
| Severe biological noise | 51.5% | 0.1:1 | FAIL |

The original persistence result depends entirely on the noise-free assumption.
Under any realistic noise, integrity collapses to near-chance (~50%) for a
binary read. This confirms Part 6's "morphogenetic vs. arbitrary pattern"
conflation was the correct thing to worry about — the base model has no real
attractor, just a very slow leak, and noise beats slow.

### Finding 2: Weak/naturally-plausible bistability does not rescue it

The simulator's `bistable_k` parameter models an active positive-feedback
mechanism (ion channel autoregulation or synthetic toggle circuit) that holds
cells at their written state. Sweeping it further than the original three
test points:

| bistable_k | Integrity @ 24h | SNR | Status |
|---|---|---|---|
| 0.01 ("well-characterized bistable gene circuit," per model's own calibration) | 59.3% | 0.4:1 | FAIL |
| 0.05 | 63.3% | 0.9:1 | FAIL |
| 0.10 | 84.4% | 2.1:1 | FAIL |
| **0.20** | **98.9%** | **31.5:1** | **PASS** |
| 0.50 | 100.0% | 285.6:1 | PASS |

Reliable storage requires feedback roughly **15–20x stronger** than what the
model calibrates as a realistic, well-characterized engineered circuit.
Passive/naturally-occurring bistability is very unlikely to be sufficient —
this needs to be a deliberately engineered mechanism, not an assumption about
ordinary planarian ion channel behavior.

*Caveat: `bistable_k` is a phenomenological modeling knob, not a value with a
direct literature-measured biological equivalent. Treat the 15–20x figure as
a relative benchmark (how much stronger than "natural" is needed), not a
literal constant to design around.*

### Finding 3: Bio-RAID tile replication cannot compensate for signal-level noise

Tested true multi-tile replication (independent noise draws per tile,
majority vote across tiles — matching the documented Bio-RAID architecture,
not just a bigger local cluster):

| Profile | 1 tile | 3 tiles | 5 tiles | 9 tiles |
|---|---|---|---|---|
| Realistic (no bistable) | 51.2% | 45.0% | 51.2% | 50.0% |
| Realistic + moderate bistable (k=0.01) | 55.0% | 51.3% | 51.2% | 48.8% |

Flat at ~50% regardless of tile count. This is expected from first
principles (Condorcet's jury theorem): majority voting across independent
readings only helps when each individual reading already beats a coin flip.
Once per-tile signal has decayed into the noise floor, no amount of
replication manufactures signal that isn't there. **Bio-RAID protects against
losing a tile (radiation, physical damage); it cannot resurrect a bit whose
voltage separation has already been erased by noise.**

### Revised model: two independent subsystems, not one

Part 6 already warned about conflating morphogenetic and arbitrary pattern
stability. These results make it quantitative and split it into two
engineering problems that need separate solutions:

1. **Signal-level fix (not yet designed):** an engineered bistable circuit
   strong enough to create genuine double-well voltage attractors. This is
   the load-bearing missing piece — nothing currently in the project
   addresses it.
2. **Availability-level fix (already designed):** Bio-RAID tile replication,
   which remains valuable, but only *after* (1) is solved — it currently has
   nothing reliable to replicate.

### Existence proof that (1) is achievable — just not yet in planaria

Gardner, Cantor & Collins (2000, *Nature*, [DOI](https://doi.org/10.1038/35002131))
built a synthetic genetic toggle switch in *E. coli*: two mutually-repressing
promoters forming a true bistable circuit, flipped by a transient
chemical/thermal pulse, holding state indefinitely afterward. Their abstract
explicitly frames it as "a synthetic, addressable cellular memory unit" with
direct implications for biocomputing. This is proof that strong, engineered
bistability is buildable in a living cell — it has never been built in
planarian somatic tissue. That is a specific, scoped synthetic-biology gap,
not an open-ended unknown.

### Proposed experiment: toggle-circuit-in-planaria

**Goal:** Determine whether a Gardner-style bistable circuit, ported into
planarian somatic cells, creates voltage attractors that survive realistic
biological noise — replacing the currently unproven "passive persistence"
assumption with a measured one.

**Design:**
- Circuit: two mutually-inhibitory regulatory elements controlling
  depolarizing vs. hyperpolarizing ion channel expression (a
  bioelectric-coupled analog of the Gardner mutual-repressor toggle), so that
  a depolarized state upregulates further depolarization and a hyperpolarized
  state upregulates further hyperpolarization, with cross-inhibition between
  the two loops.
- Delivery: mRNA/plasmid electroporation or dsRNA-compatible construct into a
  small regenerating fragment (matches existing planarian genetic toolkit
  constraints better than viral transfection).
- Write: transient chemical, thermal, or optogenetic pulse to set state (0 or 1).
- Read: voltage-sensitive dye or genetically-encoded voltage indicator,
  imaged at 0h, 6h, 12h, 24h, 48h.
- Control: identical fragment, same write pulse, no circuit (passive decay
  baseline — this is what `planarian_01_bioelectric_persistence.py` currently assumes).
- **Success criteria:** bimodal, well-separated voltage distribution
  maintained ≥24h in ≥70% of tested clusters, with SNR ≥3:1 — i.e., the
  PASS threshold this simulation already defined, now measured instead of
  assumed.
- Budget/timeline: comparable to the original minimal viable experiment
  ($10K–$30K, 6–12 months), but now requires a synthetic-biology
  collaborator in addition to a bioelectric/regeneration lab, since circuit
  design is a prerequisite deliverable, not an assumption.

**Bottom line:** the project's own "Option 4 — Hybrid: planarians + synthetic
biology" is no longer just the cautious fallback choice — it is what the
quantitative noise-floor results point to directly.

---

## Part 9: From Placeholder to Real Circuit — Tool Selection (August 2026)

Part 8 identified the missing piece as "an engineered bistable circuit,"
represented in simulation only as an abstract number (`bistable_k`). This
section replaces that placeholder with an actual design, using two free
resources chosen for a specific reason each — not a general-purpose AI
model, because none exists that has been trained on data for a claim
nobody has tested yet (there is no "AlphaFold for bioelectric memory";
AlphaFold works because ~200k solved structures already existed to learn
from — the equivalent dataset here doesn't exist and would have to be
generated by this project, not queried from one).

**Tools selected:**
1. **Topology/dynamics: Gardner, Cantor & Collins (2000, *Nature*,
   [DOI](https://doi.org/10.1038/35002131))** — the original synthetic
   toggle switch, published as a two-repressor Hill-function ODE with a
   demonstrated bistable regime. Free (published paper, equations public).
2. **Chassis parts: the Bacillus BioBrick Box / BBB 2.0** (Radeck et al.
   2013, *J Biol Eng*, [DOI](https://doi.org/10.1186/1754-1611-7-29);
   Radeck et al. 2017, *Sci Rep*,
   [DOI](https://doi.org/10.1038/s41598-017-15107-z)) — free,
   BioBrick-compatible, chromosomally-integrating promoters actually
   characterized **in B. subtilis** (four constitutive, two inducible —
   PxylA/XylR and PliaI — spanning >3 orders of magnitude in measured
   strength). This is the correct chassis-matched source: Gardner's
   parts were characterized in *E. coli*, and this project's target is
   *B. subtilis*.
3. **Considered and set aside: Cello 2.0** (genetic circuit design
   automation, [DOI](https://doi.org/10.1038/s41596-021-00675-2)) — free
   and real, but its published gate libraries don't yet cover a
   B. subtilis chassis, so it doesn't apply directly here. Worth
   revisiting if/when a Bacillus-specific Cello gate library ships.

**What running the combined model found** (`simulations/bsubtilis_01_gardner_toggle_circuit.py`):

| Promoter strength ratio (arm 2 : arm 1) | Genetic fidelity @ 24h | Voltage-output fidelity @ 24h |
|---|---|---|
| 1.0 (matched) | 100% | 100% |
| 2.0 – 10.0 (mismatched, within BBB's characterized range) | 100% | 100% |
| 0.1 (severe mismatch) | 50% | 50% |

**The real finding isn't the 100% — it's the 0.1 row.** At severe promoter
mismatch, the circuit doesn't degrade gracefully, it loses bistability
entirely: only one attractor exists, so whichever bit is written, the
system always relaxes to the same state. Fidelity floors at 50% because
half the writes were already "correct" by coincidence. **This means
promoter selection from the BBB library isn't a detail to leave for the
lab — picking two similarly-strengthed promoters is a hard precondition
for the circuit to be a toggle switch at all**, not just for it to work
well. That's a concrete, actionable constraint this design step surfaced
that the placeholder `bistable_k` number could never have revealed, since
it assumed bistability existed by construction.

**What this does and doesn't resolve:**
- ✅ Replaces a guessed number with a real topology + real, chassis-matched,
  quantitatively-characterized parts.
- ✅ Surfaces a concrete design constraint (promoter matching) before any
  wet-lab spend.
- ❌ The repressor circuit (Gardner) and the promoter strengths (BBB) have
  each been measured — separately, in different contexts. Nobody has
  measured this specific combination.
- ❌ The link from "repressor output" to "membrane voltage" — i.e., driving
  an actual ion channel's expression from the toggle switch — has never
  been built or measured by anyone. The simulation's `voltage_correct`
  column is currently just tracking the genetic state with a fast
  first-order filter, not a measured biophysical relationship. This is now
  the more specific unknown to test, replacing the vaguer "does an
  engineered bistable circuit work" question from Part 8.
- ⚠️ The transcriptional noise magnitude used has the same status as every
  other noise parameter in this project: a placeholder pending real
  measurement, not a validated value.

**Bottom line:** the missing piece is no longer one abstract number. It's
now two concrete, separately testable engineering tasks: (1) select/build a
matched-strength promoter pair from the BBB library and confirm real
bistability by reporter assay — doable with existing, off-the-shelf BBB
parts, no new biology required; (2) build and measure the repressor→ion
channel expression link, which is the one piece with no prior art at all.

---

## Part 10: Competitive Landscape — Closest Prior Art (August 2026)

Three real, verified pieces of related work surfaced this month, from
external feedback (DeepSeek) and independent user research, not something
this project's own literature scan caught first. Logged here properly
rather than left as chat history, since a diligent reviewer will find all
three on their own.

**1. Mycelium memristor.** LaRocco, Tahmina, Petreaca, Simonis & Hill
(2025), "Sustainable memristors from shiitake mycelium for high-frequency
bioelectronics," *PLOS ONE* 20(10): e0328965, DOI
[10.1371/journal.pone.0328965](https://doi.org/10.1371/journal.pone.0328965),
PMID 41071833. A self-repairing fungal memristor, 90±1% accuracy at up to
5.85 kHz, survives dehydration/rehydration. Closest public self-healing
bioelectric device — but it's an analog resistance element (one continuous
value), not an addressable binary memory with a write/read software layer,
and 90% accuracy is a real, disqualifying error rate for a memory system
(this project's own pass bar throughout has been ≥70% integrity AND ≥3:1
SNR — even that was "usable," not "good").

**2. DNA-sequence data storage in *B. subtilis*.** Yachie & Tomita (2007),
"Alignment-Based Approach for Durable Data Storage into Living Organisms,"
*Biotechnology Progress* — encoded Einstein's E=mc² as 120 bits, inserted
redundantly across multiple loci in the *B. subtilis* genome, decoded via
sequence alignment. Confirms arbitrary data storage in this exact organism
already exists — but as a DNA-**sequence** difference (archival, read via
destructive sequencing), not a **physiological state** difference (dynamic,
read non-destructively in real time). Different engineering problem: closer
to a printed archive than to RAM.

**3. BioCompute Inc.** (founded 2024, Bengaluru → San Francisco) — a
funded startup (WTF Fund, Grad Capital, 1517 Fund) commercializing exactly
category 2 at scale: a microfluidics chip using CRISPR to write/read
digital data in bacterial DNA, targeting data-center archival storage.
Same category as Yachie & Tomita, now with real capital and a product
roadmap behind it.

**The pattern across all three:** every existing example of "data in a
living organism" is either (a) an analog device with no addressable write
layer, or (b) DNA-sequence storage, which is fundamentally archival, not
a dynamic, rewritable state. Nothing found stores arbitrary data as a
physiological/bioelectric state the way this project's actual approach
does.

**Could the DNA-sequence approach (2/3) be borrowed as Acheron's write
mechanism instead?** Worth being precise about what that would and
wouldn't buy:
- For *B. subtilis*: little changes. Bacterial genetic engineering,
  including CRISPR, is already routine, and this project's existing
  circuit design already assumes it's feasible.
- For planaria: this is where it matters, and reveals a DIFFERENT
  bottleneck than the one this project has been testing. If data is
  stored as pure DNA sequence, "does regeneration preserve it" is nearly
  guaranteed already — that's just DNA replication fidelity, standard
  transgene inheritance, not an open question. **The real, currently
  unsolved bottleneck moves to whether the sequence can be written into a
  planarian genome at all.** Checked directly (August 2026): "CRISPR-based
  functional genomics have yet to be reported in planarians" — some
  narrower CRISPR/Cas applications exist (e.g., rRNA depletion for
  sequencing prep), and stable transgenesis has been achieved via older
  transposon/electroporation methods with a marker gene, but reliable,
  arbitrary-sequence CRISPR knock-in, the actual "write" step this
  approach would need, is not yet established in this organism.

**Bottom line:** borrowing DNA-sequence storage doesn't skip past a hard
problem, it trades this project's current hard problem (does a bioelectric
state hold under noise) for a different hard problem specific to planaria
(can the genome be reliably edited at all). Both are real open questions;
neither is free. The bioelectric/physiological-state approach remains the
one that produces a genuinely dynamic, rewritable memory rather than an
archival write-once record, which is the actual point of this project.

---

## Part 11: Methylation Memory — Real Fidelity Numbers, and Where They Break (August 2026)

Part 10 identified DNA methylation (the mechanism BioCompute's B2A pipeline
actually reads, via Nanopore + Modkit methylation calling, not CRISPR as an
earlier secondhand summary had wrongly claimed) as a candidate memory
mechanism distinct from both the engineered Gardner toggle-switch and raw
DNA-sequence storage: a chemical tag layered on top of existing DNA,
natively copied to daughter cells by maintenance methyltransferases at
every division, without altering the underlying genetic code. Real
precedent exists for a *self-perpetuating epigenetic bistable switch* built
this way in nature: Hernday, Krabbe, Braaten & Low (2002), "Self-
perpetuating epigenetic pili switches in bacteria," PNAS 99(Suppl 4):
16470-6, DOI 10.1073/pnas.182427199, PMC139910 — the *E. coli* pap pilin
operon, which holds a heritable ON/OFF phase state purely through Dam
methylation patterns surviving replication, no synthetic circuit required.

**A citable per-division maintenance-methylation fidelity number was
searched for and found** — not for this exact system, but for closely
related ones:
- Laird, Pleasant, Clark, Sneeden, Hassan, Manley, Vary, Morgan, Hansen &
  Stöger (2004), "Hairpin-bisulfite PCR: assessing epigenetic methylation
  patterns on complementary strands of individual DNA molecules," PNAS
  101(1):204-9, DOI 10.1073/pnas.2536758100, PMC314163. Direct,
  single-molecule measurement: maintenance methylation efficiency ≈0.96
  per site per cell division for a hypermethylated CpG island (human
  FMR1 gene, lymphocytes).
- Watanabe, Okochi-Takada, Yagi, Furuta & Ushijima (2006), "Decreased
  fidelity in replicating DNA methylation patterns in cancer cells leads
  to dense methylation of a CpG island," Curr Top Microbiol Immunol
  310:199-210, DOI 10.1007/3-540-31181-5_10. Clonal-expansion measurement
  in non-cancer human cell lines: error rates <1.0×10⁻³ per site per
  generation (>99.9% fidelity) for PROMOTER CpG islands specifically.
- Westphal, Sauvey, Champion, Ehrenreich & Finkel (2016), "Genomewide Dam
  Methylation during Long-Term Stationary Phase," mSystems 1(6), DOI
  10.1128/mSystems.00130-16, PMC5155068 — the mechanistically closer
  *bacterial* system (*E. coli* Dam/GATC, the same enzyme family the
  Hernday pap switch depends on). No single numeric fidelity reported, but
  qualitatively strong: "virtually all" GATC sites stay methylated across
  the entire bacterial life cycle, including death phase and long-term
  starvation, confirmed by mass spectrometry.

**Caveats, stated plainly:** the two quantified numbers are human/mammalian
CpG methylation (Dnmt1-family enzymes), not bacterial Dam. *B. subtilis*
does not natively carry the Dam/Dcm system these numbers, or the Hernday
pap switch, depend on — Dam is essentially restricted to *E. coli* and
other gammaproteobacteria. A *B. subtilis* implementation of this mechanism
would need a maintenance methyltransferase engineered in, which is an
additional dependency, not a free win borrowed from BioCompute's existing
read pipeline. There is also no single universal fidelity even within one
species — it depends on genomic context (promoter vs. non-promoter,
hyper- vs. hypomethylated baseline).

**Simulated (`simulations/methylation_01_bit_encoding.py`,
`simulations/methylation_02_regeneration_transfer.py`), using both real
numbers as anchors instead of one assumed value:** a single-lineage bit
held across generations, and a full colony-damage-then-regrowth-by-division
scenario (mirroring `bsubtilis_07_colony_regrowth.py`'s structure), swept
across surviving fractions from 0% to 100%. Result, at *B. subtilis*'s
~30-minute doubling time over a 24-hour (~48-generation) window:
- **At 99.9% fidelity** (Watanabe et al.'s best-case number): the bit
  survives regrowth intact (~95-97% combined accuracy) from even a 2%
  surviving population.
- **At 96% fidelity** (Laird et al.'s directly-measured number, a
  DIFFERENT real context from the 99.9% figure): the signal decays to
  chance (~50%, a coin flip) by ~48 generations, **regardless of surviving
  fraction** — even a colony that suffered zero damage (100% survival)
  loses the bit on this timescale, because the failure mode is per-division
  drift compounding over many divisions, not insufficient survivors.

**This is a genuinely different failure mode than the Gardner-circuit
colony result.** In `bsubtilis_07_colony_regrowth.py`, surviving fraction was
the binding constraint (recovery held down to ~2% survivors). Here,
maintenance fidelity is the binding constraint, and more surviving cells
cannot rescue a fidelity that's too low — the same qualitative lesson
Bio-RAID redundancy already taught for the bioelectric circuit (Part 8:
Condorcet's jury theorem — voting across copies that are each only
marginally better than chance doesn't help). Two real, published fidelity
numbers exist, and they land on opposite sides of this project's pass/fail
line. Which one (if either) *B. subtilis* would actually deliver is not
knowable from literature alone — it is a wet-lab measurement, not a
desk-research question, exactly like the noise-floor parameters flagged
throughout this audit.

---

## Part 12: Real Non-Destructive Readout Method, and a New Interference Risk From the Colony's Own Biology (August 2026)

Three papers, brought to this audit by the founder, add real evidence and
one previously-unflagged design risk.

**A real, non-destructive, low-cost readout method exists.** Akabuogu,
Zhang, Krašovec, Roberts & Waigh (2024), "Electrical Impedance Spectroscopy
with Bacterial Biofilms: Neuronal-like Behavior," Nano Letters 24(7):
2234-2241, DOI 10.1021/acs.nanolett.3c04446, PMID 38320294. Two simple
electrodes plus a small AC/DC voltage sweep (electrical impedance
spectroscopy) reveal a "negative capacitance" signature in *E. coli*
DH5α biofilms that exists ONLY when cells are alive and metabolically
active, and depends specifically on the voltage-gated potassium channel
Kch: knocking it out raises contact resistance 15-fold (471±4 Ω wild-type
vs. 7500±28 Ω knockout), and killing the cells with disinfectant removes
the signature entirely. The authors explicitly propose this as a cheap
Live/Dead-assay alternative that avoids fluorescent dyes. For this
project, it's a candidate THIRD readout mechanism, alongside optical
voltage-dye imaging and destructive sequencing: cheap electrodes, no
dye, no sample destruction, repeatable on the same living colony.

**Independent, quantitative confirmation that voltage-based signaling
really propagates in *B. subtilis* biofilms**, from two papers modeling
the Prindle lab's potassium-wave discovery: Ford, Fisher, Prindle & Chopp
(2021), "A Two-Dimensional Model of Potassium Signaling and Oscillatory
Growth in a Biofilm," Bulletin of Mathematical Biology 83(5):60, DOI
10.1007/s11538-021-00887-3, PMID 33856558; and Mulder, Peters Kostman,
Almodaimegh, Edge & Larkin (2025), "An agent-based model of metabolic
signaling oscillations in *Bacillus subtilis* biofilms," PLOS
Computational Biology 21(12):e1013746, DOI 10.1371/journal.pcbi.1013746,
PMID 41343600. Real measured/simulated numbers: propagation speed ~10-50
microns/minute, oscillation period ~2-4 hours, onset once a biofilm
reaches ~500 microns wide. Mechanism: nutrient-starved interior cells
release potassium and hyperpolarize; the signal spreads outward, briefly
suppressing neighbors' nutrient uptake so food reaches the interior.

**The new risk this surfaces:** this oscillation is not hypothetical or
engineered, it is the colony's own normal metabolic regulation, running
continuously and independently of anything Acheron builds. Since it also
runs through voltage-gated potassium channel activity, the same broad
category of machinery `bsubtilis_01_gardner_toggle_circuit.py`'s "hypothetical
ion-channel expression link" would need, an engineered bit sharing the
same membrane could have its VOLTAGE READOUT disturbed by the colony's
own signaling, independent of whether the underlying genetic circuit is
working correctly.

**Simulated (`simulations/bsubtilis_08_native_oscillation_interference.py`):** added
the real period range (2-4h) as an external sinusoidal perturbation to a
written, otherwise-healthy `GardnerToggleCell`'s membrane voltage only
(deliberately NOT fed back into the u/v repressor state — see the file's
docstring for why that stricter, more conservative scope was chosen).
Amplitude was swept from 10mV up to 70mV (this project's own engineered
signal's full range, V_HIGH=-10mV to V_LOW=-80mV) since neither source
paper reported an exact millivolt figure for the natural swing.

Result: the **genetic memory (u/v state) stayed at 100% fidelity
throughout, exactly as it should by construction** (a useful sanity
check that this file works as intended). But the **voltage readout**,
sampled every 10 minutes across a 24-hour run to catch intermittent
corruption rather than one lucky/unlucky snapshot, **collapsed toward a
coin flip (50-59%) at just 10-20mV of ambient oscillation, well below
the 70mV worst case**, across all three tested periods (2h, 3h, 4h).

**What this means, plainly:** if the engineered circuit and the colony's
native signaling aren't electrically decoupled somehow, the DATA could
still be sitting there correctly in the genetic circuit while a voltage
readout returns garbage, simply because it caught the reading at the
wrong moment in the colony's own natural rhythm. That's a solvable
engineering problem (e.g., reading via a mechanism less sensitive to
transient voltage than raw membrane potential, averaging over a full
oscillation period before reading, or physically isolating cells from
neighbors' potassium flux) rather than a fatal flaw, but it is a concrete,
previously-unflagged wet-lab requirement, and it is a genuinely new
argument for the EIS readout method above: EIS measures a channel-activity
SIGNATURE tied to whether Kch is present and cells are alive, not a raw
instantaneous voltage value, which may prove less sensitive to this exact
failure mode. That specific comparison hasn't been tested yet.

---

## Part 13: EIS Readout Tested Against the Same Oscillation, and a Full Cross-Organism Comparison (August 2026)

**Does EIS survive the interference that broke single-snapshot voltage
reading?** Part 12 proposed electrical impedance spectroscopy (EIS) as a
candidate fix for the readout-corruption problem it found, reasoning that
an EIS measurement integrates over a frequency sweep rather than sampling
one instant. `simulations/bsubtilis_09_eis_readout_interference.py` tested that
reasoning directly against the same real oscillation (period 2-4h,
Ford et al. 2021; Mulder et al. 2025) instead of asserting it. **The
hopeful hypothesis did not hold up as expected.** Realistic EIS sweep
durations (the Akabuogu et al. 2024 protocol sweeps ~0.2-10 Hz, a
measurement of seconds to a few minutes) integrate over too short a
window to average out an hours-long biological oscillation — accuracy
stayed degraded (50-67%) at every window from 1 to 90 minutes, and only
recovered (92-100%) once the integration window reached ~180 minutes,
exactly one full oscillation period. **The honest conclusion: a single
real-world EIS measurement is NOT immune to this interference.** EIS's
real advantage isn't "one sweep sees through the oscillation" — it's that
EIS is cheap and non-destructive enough to repeat many times across a
multi-hour window and combine the readings, which single-shot destructive
sequencing could never do. That's a genuine advantage, just a more
specific and more modest one than the initial hypothesis, and this
project's discipline is to report that correction rather than the
more flattering version.

**Full cross-organism comparison.** `simulations/crossorganism_01_comparison_summary.py`
runs the three directly comparable regeneration/regrowth tests side by
side for the first time: planarian (bioelectric circuit, mean-field
coupling), B. subtilis (bioelectric circuit, division-based inheritance),
and B. subtilis (methylation, division-based, at both real fidelity
anchors from Part 11). Result, at surviving fractions from 0% to 100%:

| Mechanism | Recovery threshold (>=70%) | Grounding confidence |
|---|---|---|
| B. subtilis, circuit, division-based | ~2% surviving | Highest — coupling is mechanistically forced (division copies existing protein), not a free parameter |
| B. subtilis, methylation, 99.9% fidelity anchor | ~2% surviving (93-97% combined) | Medium — real number, wrong organism (mammalian CpG, not B. subtilis) |
| B. subtilis, methylation, 96% fidelity anchor | None in this sweep — fails regardless of survivors | Medium — same caveat, different real context, opposite outcome |
| Planarian, circuit, mean-field coupling | ~2% surviving (numerically ties the B. subtilis circuit row at 100%) | Lowest — coupling strength is a borrowed assumption, not measured in real planarian tissue |

Numerically, planarian ties the B. subtilis circuit's 100% and beats the
methylation mechanism's real-number anchor. That is NOT the same as
planarian being equally trustworthy — same output number, much less
confidence behind it. Ranked by how much wet-lab risk each row is still
hiding, lowest to highest: **B. subtilis circuit < B. subtilis methylation
< planarian circuit.**

**A gap stated plainly, not filled in:** `bsubtilis_08_native_oscillation_interference.py`
and `bsubtilis_09_eis_readout_interference.py` only exist for B. subtilis, because
that's where the underlying biofilm potassium-signaling literature is.
No comparable planarian interference test exists yet — not because
planarians are assumed safe from an equivalent problem, but because no
citation for a planarian equivalent was found anywhere in this project's
research. Building one without a citation would be exactly the kind of
unlabeled assumption this audit has consistently avoided elsewhere, so
it's reported here as an open gap instead.

---

## Part 14: The Ion Channel Finally Has a Name, and Its Own Promoter Sits on the Circuit's Regulatory Node (September 2026)

**Where this came from:** Acheron Nexus (this project's RAG research
assistant) added a SubtiWiki collector, and searching the curated
B. subtilis gene records it surfaces around the biofilm potassium
pathway led back to a real paper nobody had pulled into this project
before: Lundberg, Becker & Choe (2013), "MstX and a Putative Potassium
Channel Facilitate Biofilm Formation in Bacillus subtilis," PLoS ONE
8(5):e60993, DOI 10.1371/journal.pone.0060993, PMID 23737939.

**What it establishes.** Two prior audit entries (Part 12) named the
mechanism generically — "the voltage-gated potassium channel," citing
the Prindle lab's discovery and its modeling follow-ups — without ever
naming the gene, because none of those three papers name it either
(they model the wave, not the channel's own genetics). Lundberg et al.
2013 do: the channel is **yugO**, a TrkA-domain K+ efflux channel
encoded immediately downstream of **mstX** in a two-gene operon. Three
facts from that paper matter directly to this project's own simulations:

1. The **mstX-yugO operon has a confirmed SinR binding site** (verified
   by ChIP) and is transcriptionally **repressed by SinR** — the same
   master biofilm regulator that also represses the epsA-O and
   tapA-sipW-tasA matrix operons this project's BBB-chassis promoter
   choices (`bsubtilis_01_gardner_toggle_circuit.py`) are drawn from.
2. Once expressed, YugO's K+ efflux **activates the histidine kinase
   KinC**, which phosphorylates Spo0A, whose phosphorylated form
   represses SinR — a real, published positive-feedback loop, not an
   assumed one.
3. `mstX-yugO` transcription is low during log-phase growth and rises
   specifically under biofilm-forming conditions, confirmed by RT-PCR
   and RNA harvested at both growth stages.

**What this changes, and what it doesn't.**
`bsubtilis_01_gardner_toggle_circuit.py`'s "hypothetical ion-channel-expression link"
now has a named, literature-characterized candidate channel and
promoter instead of no candidate at all — a materially more concrete
starting point for anyone eventually trying to wire the toggle's output
to a real channel. It does NOT mean that link is validated: nobody has
measured a Gardner-topology circuit driving yugO specifically. And
`bsubtilis_08_native_oscillation_interference.py`'s explicitly-scoped-out question —
whether the biofilm's native oscillation could feed back into the
engineered circuit's own genetic state, not just its voltage readout —
is now known to have a real analogue in the literature (yugO's own
expression is itself gated by the SinR/Spo0A node), even though no
paper yet shows that specific feedback path reaching an engineered
circuit. Both files have been updated in place with these citations
and the distinction between "a real candidate now exists" and "the
link is validated" preserved exactly as strictly as everywhere else in
this audit.

**The actionable takeaway:** before committing to a specific BBB
promoter for the engineered toggle, check whether it is itself
SinR/Spo0A-regulated (many biofilm-stage promoters are, by construction
of what BBB characterized). If it is, the interference risk flagged in
Part 12 is not just "shared membrane real estate" — it is a shared
upstream transcriptional regulator, and that is a concrete, checkable
design constraint this audit did not have language for before this
SubtiWiki-sourced search.

---

## Part 15: External Review (DeepSeek), the Combined Experiment Is the Wrong Ask, and a Fluorescent Reporter as an Overlooked Readout Path (September 2026)

Feedback from DeepSeek, brought to this audit by the founder, reviewed
against the project's actual current state rather than accepted at face
value.

**Claim 1: the project is trying to prove three things in one experiment,
and should not be.** The feedback argues for testing the circuit, the
readout, and damage/regrowth survival as three separate questions, only
combining them once each is independently proven. This is a correct
description of a real problem, not a restatement of something already
fixed. `docs/INVESTOR_PITCH.md`'s current Roadmap section ("Roadmap: The
One Experiment That Changes Everything") asks for exactly the combined
experiment this feedback warns against: build the matched-promoter
Gardner circuit, damage the colony, let it regrow, and read the result
back with EIS, all inside one $10K-$30K, 6-12 month ask. `docs/pitch/
Acheron_Validation_Proposal.docx` is built from that same combined
framing. Neither has been revised in response to this yet, see the
recommendation below.

**Claim 2: EIS is too weak a signal, buried in the colony's own noise.**
This matches, and does not add new information beyond, this audit's own
Part 13 finding: a single realistic EIS sweep (seconds to a few minutes,
per the Akabuogu et al. 2024 protocol) does not survive the colony's
native potassium-wave oscillation (2-4h period), and accuracy only
recovers once the integration window reaches roughly one full oscillation
period (about 180 minutes). The feedback's proposed fix, an engineered
high-conductance channel plus a lock-in amplifier reading at that
channel's own characteristic frequency, is a more specific version of the
narrower, real advantage Part 13 already identified for EIS: repeatable,
non-destructive measurement over a long window, not one-shot immunity to
the oscillation. Read this as independent convergence on the same
finding, which is worth noting, not as new evidence. **One specific
number in the feedback is not verified and should not be repeated as a
project claim without a citation**: that the engineered circuit changes
membrane impedance "a few percent" against "20-40%" native biofilm
heterogeneity. Neither figure traces to a citation in the feedback itself
or to anything already in this project's simulations, per the
no-numeric-invention rule in `docs/THIRD_PARTY_METHODS.md`.

**Claim 3: use a fluorescent reporter (GFP/RFP) as the first readout,
before attempting a non-destructive electrical readout.** Checked against
`docs/pitch/Acheron_Validation_Proposal.docx`, this is not new to the
project: its Stage 0 ("*B. subtilis* toggle confirmation") already reads
bistability through a transcriptional reporter assay, lacZ/lux, not the
voltage-linked EIS path, before any electrical readout is attempted. That
document predates this feedback and reaches the same structural
conclusion independently. What the feedback adds is narrower than first
read: GFP/RFP specifically instead of lacZ/lux (a real, minor variant,
fluorescence gives a continuous, imageable signal, lacZ/lux typically an
endpoint or plate-reader one, but both are transcriptional reporters
solving the same problem the same way), and the explicit argument for why
this class of readout is the right first step: every voltage-linked path
(dye imaging, EIS) depends on first solving the repressor-to-ion-channel
expression link, which Part 9 flagged as having "no prior art at all," and
which Parts 12-13 then showed is vulnerable to the colony's own
potassium-wave interference once built. A transcriptional reporter
sidesteps that unbuilt link entirely for a first proof-of-concept. That
reasoning is worth having stated explicitly, even though the project's own
staged plan had already arrived at reporter-first by a different route.

**Claim 4: DNA sequence recording (CRISPR-based) and methylation as
alternative memory mechanisms.** Matches, without adding new information,
what Parts 10-11 already established: DNA-sequence storage is archival
and write-once (Yachie & Tomita 2007; BioCompute Inc.), methylation is the
rewritable epigenetic mechanism, and its fidelity numbers are already
characterized in Part 11 with the same caveat this feedback also lands
on, that the fidelity anchor which would actually apply to *B. subtilis*
is unmeasured. No revision needed to those sections.

**The staged plan the feedback proposes (its own Stage 0 computational,
already done; Stage 1 fluorescent toggle build; Stage 2 damage/regrowth
with the same fluorescent readout; Stage 3 non-destructive ion-channel/EIS
readout; Stage 4 addressable array; $27K-$55K, 13-18 months total) is
structurally sound**, and consistent with how this project has actually
made progress so far, Parts 8 through 14 each isolated one variable at a
time rather than testing everything at once. Its specific dollar and
month figures are the feedback author's own estimates, not sourced to
anything in this project's own cost research, and its stage numbering is
the feedback's own, not this project's: it does not line up one-to-one
with the project's existing Stage 0-3 plan in
`docs/pitch/Acheron_Validation_Proposal.docx` (whose Stage 0 is the
B. subtilis toggle/reporter build, Stage 1 is HEK293 persistence, Stage 2
is the planarian minimal viable experiment, and Stage 3 is the
voltage-interface build), which predates this feedback and was not
replaced by it, only reinforced on the "split the readout out" point.

**Action taken:** `docs/INVESTOR_PITCH.md`'s Roadmap section previously
asked for one combined experiment, matched-promoter circuit, damage,
regrowth, and EIS readout together, in a single $10K-$30K ask, which
contradicted the project's own already-staged plan in
`docs/pitch/Acheron_Validation_Proposal.docx` and is exactly the pattern
this feedback (Claim 1) warned against. Founder confirmed revising both
documents (September 2026). The Roadmap section now presents the
project's existing four-stage plan instead of the combined ask, and the
Validation Proposal gained a third empirical claim (Claim C, readout
timing) plus a matching risk-disclosure bullet, both citing Part 13's
oscillation-interference finding directly, since that finding predates
this feedback but had not yet been reflected in either investor-facing
document.

---

## Part 16: The Fluorescent Reporter Readout, Simulated (September 2026)

Part 15's Claim 3 argued a transcriptional reporter (GFP/RFP) sidesteps
the interference problem the voltage-linked readout has, but that was
reasoning, not a run simulation. `simulations/bsubtilis_10_reporter_readout.py`
is the missing one: the same Gardner repressor ODE as
`bsubtilis_01_gardner_toggle_circuit.py`, read out through a two-arm GFP/RFP
transcriptional reporter (maturation + growth-dilution kinetics) instead
of through the hypothetical repressor-to-ion-channel-to-voltage link.

**Result:** reporter fidelity tracks genetic fidelity exactly, matching
`bsubtilis_01_gardner_toggle_circuit.py`'s own voltage-fidelity numbers in the
undisturbed case (100% at matched-to-10x promoter ratios, 50% at the 0.1
severe-mismatch ratio, both with and without transcriptional noise), and
stays at 100% across a swept maturation half-life (5-60 minutes) and
measurement noise (0-30%), both explicitly unmeasured placeholders for
this system rather than literature values.

**What this does and doesn't establish:** in the undisturbed case
simulated here, both readouts are equally clean, so this result alone
doesn't favor one over the other. The actual case for reporter-first is
the one `bsubtilis_08_native_oscillation_interference.py` and `bsubtilis_09_eis_readout_interference.py`
already made: only the voltage-linked readout has an identified,
cited corruption mechanism (the biofilm's own potassium-wave signaling
acting on membrane voltage). No cited source proposes that mechanism
also acting on transcription, translation, or chromophore maturation, so
`bsubtilis_10_reporter_readout.py` deliberately does not add an
oscillation term to the reporter pathway, on the same "don't simulate an
unproposed coupling" discipline `bsubtilis_08_native_oscillation_interference.py`
already applies to keeping the oscillation out of the genetic (u/v)
state. This is a design/sensitivity tool, not a wet-lab measurement,
same status as every other simulation in this project.

---

## Part 17: Phase-Locked Reading - Testing Whether Timing Dodges the Oscillation (September 2026)

Founder question, tested directly rather than just reasoned about: instead
of averaging a voltage read over the native oscillation's full ~3h period
(Part 13's fix), could a quick read timed to the oscillation's predicted
zero-crossing skip the problem instead of averaging through it?
`simulations/bsubtilis_11_phase_locked_readout.py` tests this on the identical
trajectories `bsubtilis_09_eis_readout_interference.py` already generates, comparing
three strategies head to head: a blind random-moment snapshot, the
180-minute averaging fix, and a quick read scheduled at the oscillation's
predicted quiet moments, swept across how much timing error that
prediction carries (0 to 90 minutes).

**Result: the hopeful hypothesis mostly did not hold up.** Even with
perfect timing knowledge (zero error), the quick read only matched the
180-minute average at the lowest tested amplitude (10mV, where it hit
100%). At 20mV and above, a perfectly-timed quick read landed at ~50%, a
coin flip, no better than the blind baseline and sometimes slightly
worse. Likely reason: the oscillation is added into the cell's voltage
continuously, every minute, not just at the read instant, so by the time
the external wave's value returns to zero, the cell's own voltage has
already been dragged around for most of a half-cycle and hasn't settled
back. A single sample stays contaminated by that residual drift
regardless of where in the cycle it's taken.

**This sharpens Part 13's finding rather than contradicting it:** the
problem was never really about the waveform's instantaneous value at
sample time, it's about how much cumulative drift has built up, and only
integrating over enough of the cycle to average that out actually works.
Timing a quick read cleverly is not a shortcut around that, at least not
in this model.

**The one real exception:** at the lowest tested amplitude (10mV), timing
does help substantially and tolerates real timing error gracefully (86%
at +/-5 min, 71% at +/-15 min). That keeps this idea relevant, just not
as a way to tolerate the full documented interference range, more as a
reason to also pursue keeping the native signal's effective amplitude
small in the first place, e.g., a different, non-shared ion channel, or a
yugO-knockout chassis strain (both raised in the same founder
conversation, neither simulated or wet-lab tested yet).

**What this doesn't and can't resolve:** whether a real colony's
oscillation is regular enough for a "predicted schedule" to mean anything
over 24 hours, and how a real protocol would establish the phase at all
without already having a working non-destructive readout, a genuine
bootstrapping problem no simulation resolves, stated plainly in the file's
own docstring rather than glossed over.

---

## Part 18: Reducing the Native Signal's Coupling Strength, Instead of Timing Around It (September 2026)

Part 17 ruled out timing as a fix. This tests the founder's other two
ideas from the same conversation: engineer the circuit's voltage output
through a different ion channel than yugO (the one carrying the native
signal, Lundberg, Becker & Choe 2013), or delete yugO from the
engineering strain entirely. Both do the same thing to this project's
model: reduce how much of the native oscillation actually reaches the
engineered circuit's voltage. Neither mechanism's real-world coupling
reduction has ever been measured, so
`simulations/bsubtilis_12_decoupled_channel_readout.py` sweeps a residual-coupling
fraction (100% = today's worst-case shared-channel assumption, 0% = a
perfect knockout/isolation) instead of assuming a number, at a moderate
(30mV) and the worst-case documented (70mV) real oscillation amplitude.

**Result, and it depends on how strong the interference actually is:**
- At the moderate amplitude (30mV), cutting coupling down to just 10% of
  today's assumed strength, nowhere near a perfect knockout, is enough to
  make even a fast, 1-minute read work well (94% accuracy, up from 54% at
  full coupling). You do not need to eliminate the native signal, just
  substantially weaken it.
- At the worst-case documented amplitude (70mV), that same partial
  reduction is not enough, a fast read stays poor (55-61%) all the way
  down to 10% coupling, and only recovers at a complete, 0% coupling
  knockout. At this amplitude, the 180-minute averaging fix from Part 13
  still works regardless of coupling level, so it remains the fallback
  that doesn't depend on how well a knockout or channel swap performs in
  practice.

**Bottom line:** reducing the native signal's coupling strength is a
genuinely more promising lever than the timing trick Part 17 tested, at
real-world amplitudes on the milder end of the documented range. At the
worst-case end, it is not a substitute for the long-averaging fix, only a
possible complement to it, and how much real coupling reduction a
different channel or a yugO knockout would actually achieve is a wet-lab
question this project cannot resolve computationally, along with the
knockout's own documented biofilm-formation cost (Lundberg et al. 2013).

---

## Part 19: Does Levin's Lab Have a Planarian Equivalent of the B. subtilis Interference Problem? Searched, Not Found (September 2026)

Founder question, checked directly against PubMed rather than assumed:
does Levin's own lab already document a native, competing electrical
signal in planarians, comparable to the potassium-wave interference this
audit found for B. subtilis (Parts 12-13)? Part 13 already flagged this
as an open gap ("no comparable planarian interference test exists yet...
no citation for a planarian equivalent was found"). Multiple PubMed
searches this session (varying terms: bioelectric noise, voltage
imaging, membrane potential variability, spontaneous electrical
activity, all crossed with "planarian" and/or "Levin") turned up two
real, relevant, previously-uncited papers, but not a direct hit.

1. Oviedo, Nicolas, Adams & Levin (2008), "Live Imaging of Planarian
   Membrane Potential Using DiBAC4(3)," CSH Protocols, DOI
   10.1101/pdb.prot5055, PMID 21356693, PMC10468776. A real Levin-lab
   imaging protocol whose own abstract states the method produces
   "qualitative... variations in time-averaged membrane potential" and
   requires "proper controls." This confirms Levin's own lab already
   treats raw planarian voltage imaging as noisy enough to need
   time-averaging and controls, the same general strategy (integrate
   over time rather than trust one snapshot) this project's own EIS fix
   (Part 13) independently arrived at for B. subtilis. It does not name
   a specific competing signal or its timescale, so it supports the
   averaging strategy in general without answering the specific
   question asked.
2. Grodstein & Levin (2021), "Stability and robustness properties of
   bioelectric networks: A computational approach," Biophysics Reviews
   2(3):031305, DOI 10.1063/5.0062442, PMID 38505634, PMC10903393. A
   Levin-lab computational analysis using the regenerating planarian as
   its example system, studying how bioelectric patterning stays
   correct despite changing cell number and anatomical configuration
   during regeneration. Full text was not retrievable (abstract only),
   so this project cannot yet say whether it characterizes an
   electrical noise source the way this audit needs, only that its
   subject (robustness of the pattern to structural change during
   regeneration) reads as closer to this project's own Part 6 question
   (do arbitrary patterns persist through damage the way natural ones
   do) than to a documented competing background signal. Worth a closer
   read if the planarian track is revisited.

**Bottom line: the search did not find a planarian equivalent of the
B. subtilis potassium-wave problem.** That is consistent with, not a
correction to, what Part 13 already said, this project's literature
search still has not found one, which is different from planarians being
established as free of an equivalent issue. Both papers above are real
and worth citing if the planarian track is picked back up, neither
closes the gap Part 13 flagged.

---

## Part 20: The Fluorescent Reporter, Tested Through Damage and Regrowth (September 2026)

Two results existed separately and had never been combined: Part 8's/
`bsubtilis_07_colony_regrowth.py`'s finding that the genetic memory survives
division-based damage/regrowth down to 2% surviving cells, and Part
16's/`bsubtilis_10_reporter_readout.py`'s finding that a GFP/RFP
reporter tracks that genetic state accurately when nothing disturbs the
colony. Neither answers the question that actually matters for a real
experiment: after a colony is smashed down and regrows, does the GLOWING
COLOR still say the right thing, not just the genes underneath it.
`simulations/bsubtilis_13_reporter_colony_regrowth.py` runs that combined test
directly, extending `bsubtilis_07_colony_regrowth.py`'s existing
daughter-inherits-the-mother's-concentration treatment (already used for
the repressor state u/v) to the reporter pools as well, for consistency,
not as a new assumption.

**Result: reporter fidelity tracks genetic fidelity exactly.** Both
recover to 100% from as little as 2% surviving cells up through no
damage at all, a 0% gap between the two columns at every surviving
fraction tested. The fluorescent readout does not add any additional
fragility on top of what the underlying circuit already tolerates.

**What this means for the roadmap:** this is the computational case for
treating a damage-and-regrowth test with a fluorescent/reporter readout
as a reasonable next step for B. subtilis specifically, something the
existing staged plan (`docs/pitch/Acheron_Validation_Proposal.docx`)
does not yet have, its Stage 2 (damage/regrowth) is planarian-specific,
not B. subtilis. **What this doesn't resolve:** the same limitation
already stated in `bsubtilis_07_colony_regrowth.py`, division here is
deterministic inheritance plus ongoing noise, not stochastic partition
noise (real, unequal splitting of protein between daughters), and this
file adds no new wet-lab-only factors of its own (photobleaching,
autofluorescence, population imaging noise) that a real microscopy
protocol would also have to contend with.

---

## Part 21: The Electrical Reader, Damage/Regrowth, and the Native Oscillation, All Three Combined (September 2026)

Continuing the pattern from Part 20 (which did this for the fluorescent
reporter): three previously-separate results, `bsubtilis_07_colony_regrowth.py`
(damage/regrowth), `bsubtilis_08_native_oscillation_interference.py` (single-snapshot
voltage reads collapse under the native oscillation), and
`bsubtilis_09_eis_readout_interference.py` (a ~180-minute average recovers accuracy),
had never been run together on the SAME simulated colony.
`simulations/bsubtilis_14_voltage_colony_regrowth.py` does that: damages a colony,
regrows it by division while the native oscillation runs continuously
throughout both regrowth and settling, then reads the result both ways.

**Result: each piece behaved exactly as its own source file predicted.**
Genetic fidelity stayed at 100% throughout (the oscillation is only ever
added to voltage, never fed into u/v, matching every prior file's
scoping choice). A single voltage snapshot collapsed to ~50% at every
damage level and both tested amplitudes (30mV, 70mV). The 180-minute
averaged read recovered to ~100% at every damage level, undisturbed by
having gone through actual damage and regrowth first.

**The one genuinely new finding: the existing 6-hour settle budget has
zero margin at the worst damage level this model can represent.** Worse
damage takes longer to regrow (more doubling rounds needed before the
colony is back to full size), which eats into the fixed 6-hour window
`bsubtilis_07_colony_regrowth.py` already uses. At the most extreme
survival this model can represent (a single surviving cell, the floor
`run_colony_trial`'s `max(1, ...)` allows), regrowth to 64 cells takes
exactly 6 doubling rounds, 180 minutes, at the project's already-assumed
30-minute doubling time, leaving EXACTLY 180 minutes of settle time,
precisely enough for one 180-minute EIS-style average and not a minute
more. This is not a coincidence discovered after the fact, it falls out
of `bsubtilis_07_colony_regrowth.py`'s own SETTLE_WINDOW_HOURS=6h choice
relative to Part 13's 180-minute finding, but it had never been checked
directly before this file, and it means there is currently no slack: if
real regrowth is any slower than the assumed 30-minute doubling time, or
a real colony needs a moment before the electrical read can begin, this
exact combination (worst-case damage plus the long averaging fix) would
not fit inside the budget this project's own roadmap documents already
assume.

---

## Part 22: Stochastic Partition Noise at Division - Does Uneven Splitting Break Recovery? (September 2026)

Every damage/regrowth simulation so far (Parts 8, 20, 21) gives each
daughter cell exactly the mother's own repressor concentration at
division, explicitly flagged in each of those files as a simplification:
real division splits actual molecule counts randomly, not perfectly
evenly. `simulations/bsubtilis_15_partition_noise_regrowth.py` replaces that
simplification with the real math for it: Huh & Paulsson (2011,
"Non-genetic heterogeneity from stochastic partitioning at cell
division," Nature Genetics 43(2):95-100, DOI 10.1038/ng.729, PMID
21186354) derive that binomial partitioning (each molecule independently
50/50 into either daughter) contributes noise with variance kappa =
1/<X>, <X> being the molecule's average copy number, applied here to
BOTH resulting daughters at every division, not just the newly-created
one, using an explicitly swept, unmeasured conversion from this project's
dimensionless u/v units to an assumed real molecule count (this project
has no citation for that conversion; real bacterial transcription factor
copy numbers span single digits to thousands depending on the protein).

**Result: the circuit's own bistability makes it robust to this noise
down to a strikingly low copy number.** (Deterministic-inheritance colony model, no bursts, no mRNA stage; the molecular
model of Part 31 asks a different question and needs about 12 to 100 mean molecules
depending on burst size.) At ~5 molecules per cell and
above, recovery stayed at 99-100%, matching the noise-free result,
across every damage level tested (2% to 100% surviving). Manually
verified the noise itself is real and large at this scale (single
divisions swinging a daughter's value across the circuit's full range),
not a modeling no-op, before trusting the result. Only at an extreme,
probably-unrealistic ~1 molecule per cell did recovery degrade (66-87%),
and even there it never collapsed to chance.

**A genuinely new, non-obvious pattern at the ~1-molecule extreme: worse
damage made the noise problem WORSE, not better** (66% at 2% survival vs.
100% at no damage), the opposite direction from every other stressor
this project has tested. The reason: worse damage means fewer surviving
lineages, each of which needs MORE divisions to regrow back to full
colony size, and more divisions means more independent chances for
partition noise to compound within that lineage. This is a different
mechanism than Part 21's time-budget finding, that one was about
regrowth eating into a fixed clock; this one is about noise accumulating
per generation, and it only shows up at the extreme end of this sweep.

**What this doesn't resolve:** binomial partitioning is Huh & Paulsson's
own best-case, most-ordered scenario, their paper states real
segregation is often less ordered (clustered/vesicle-bound molecules,
kappa > 1/<X>), so this result is a floor on the real effect, not a
ceiling. Which real copy number applies to this project's actual chosen
promoter pair is unmeasured, and this file does not yet extend the test
to the fluorescent reporter or voltage readouts layered on top.

---

## Part 23: A Damage-Sensing Reinforcement Circuit, Tested Against Part 22's Weak Point (September 2026)

Founder's own idea from earlier this session: instead of only relying on
ordinary division to carry the bit through damage, could cells detect
"I'm damaged" and actively do something about it? `simulations/
bsubtilis_16_damage_sensing_reinforcement.py` builds and tests the simplest version:
a proposed circuit addition, modeled on the real, well-characterized
bacterial SOS response (RecA/LexA, Maslowska, Makiela-Dzbenska &
Fijalkowska 2019, DOI 10.1002/em.22267; Kaushik, Tiwari & Tiwari 2022,
DOI 10.1016/j.ijbiomac.2022.07.176), that transiently boosts whichever
toggle arm currently dominates during the regrowth window, then relaxes
once regrowth completes. This is a design proposal using real biological
machinery, not a cited existing result, stated plainly in the file.

Tested directly against Part 22's one documented weak point: ~1
effective molecule of repressor per cell, where partition noise degraded
recovery to 66-87%. **Result: a 10x promoter-strength boost during
regrowth fully rescues that weak point, back to 100% at every damage
level tested, including the worst case (2% survivors).** A 5x boost
already recovers to 97-99%. The no-boost (1x) column reproduces Part
22's original finding as expected, confirming the two files are testing
the same weak point consistently.

**What this means:** the one real fragility this project's own noise
testing has found so far has a concrete, biologically-grounded proposed
fix, not just a hoped-for one. **What this doesn't resolve:** this is a
proposed circuit, not a built or measured one. It does not identify
which specific B. subtilis stress promoter would drive it in practice,
does not model the SOS response's own real activation/decay kinetics
(this file uses a simple on/off switch tied to regrowth completion, a
modeling assumption, not a cited timing fact), and raises a real new
question of its own: would a circuit reinforced this strongly resist a
legitimate new WRITE attempt after healing, when the goal is to change
the bit rather than protect it? Not tested here.

---

## Part 24: The Readout Method Checked Against Published Work, and a Prior-Art Correction (September 2026)

Parts 12, 13, 17 and 18 are this project's own search for a way to read the
bit electrically despite the colony's native potassium-wave oscillation. This
part is the literature check that should have run alongside them: what do
published engineered-cell-state experiments actually use as a readout, and
what do the cheap versions of those methods cost? Written up in full in
`docs/READOUT_METHODS_LITERATURE_CHECK.md`. Summary of what it found:

**No canonical engineered-memory paper reads state as membrane potential.**
Gardner, Cantor & Collins (2000), the toggle switch
`bsubtilis_01_gardner_toggle_circuit.py` is modeled on, read GFP by flow cytometry.
Bonnet, Subsoontorn & Endy (2012) read mutually exclusive GFP/RFP by flow
cytometry and microscopy. Huang et al. (2025), already cited here, read a
reporter. The electrical route has no precedent as a bit readout anywhere
this check could find.

**The bacterial-bioelectricity field says absolute membrane-potential
quantification is itself unsettled.** Cianflone, Keller, Subramaniam &
Paternò (2026), "Bacterial bioelectricity, the first 15 years," *Frontiers in
Photobiology* 4:1834373, DOI 10.3389/fphbi.2026.1834373, states that the
standard Nernstian dyes (ThT, DiBAC, TMRM) "tend to measure the steady-state
Vm rather than fast transients" and can be "altered by membrane permeability
changes, the activity of the efflux pump or other variations in the membrane
physiology independent from the Vm," that they "may influence bacterial
growth even at low concentrations," and that across the field "many studies
excel at dynamics but remain limited in absolute Vm quantification." The
interference problem Parts 12 and 13 found is one instance of a broader
measurement problem, not a quirk of this project's model.

**Three alternatives, ranked, with the blunt cost picture:** (1) two-color
fluorescent reporter, already simulated in Part 16 and already the Stage 0
plan, cheap on reagents and gated entirely by instrument access, with flow
cytometry out of reach and a phone-camera substitute unable to show the
single-cell bimodality that is the actual evidence for bistability; (2)
bioluminescence read on an open-source luminometer, the only end-to-end
home-budget-reachable option, cited at approximately $40 to assemble
(Weissová et al. 2022, LuminoCell, *Life Science Alliance* 5(8):e202201421)
with its own stated ~40 pW/s detection limit, population-level only, and
validated on mammalian cultures rather than bacterial lux; (3) moving the
state into DNA orientation via a serine-integrase latch, read by PCR, the
cheapest quantitative readout and the only mechanism on the list with
multi-generation persistence actually measured in a living organism, at the
cost of changing what the stored state is and reading destructively.

**A correction to Part 10.** Part 10 concludes that every existing example of
data in a living organism is either an analog device with no addressable
write layer, or archival DNA-sequence storage. Bonnet, Subsoontorn & Endy
(2012), "Rewritable digital data storage in live cells via engineered control
of recombination directionality," *PNAS* 109(23):8884-8889, DOI
10.1073/pnas.1202344109, PMID 22615351, is a third category that sentence
does not cover, and it was absent from this repository until now. It is
addressable, digital, rewritable across multiple set/reset duty cycles
(set >95%, reset ~85% to >90% efficiency), heritable over 100+ cell
divisions with no input and no selection, and read non-destructively by
fluorescence. It is one bit per register rather than a scalable array and it
is not a bioelectric state, so Acheron's approach is not duplicated by it,
but Part 10's "nothing found stores arbitrary data as a dynamic, rewritable
state" is too strong as written and should be narrowed before any investor
or examiner finds the paper first.

**Recommendation, not an action taken:** take the electrical readout off the
critical path for Stage 0. Parts 12, 13, 17 and 18 were a good-faith search
for a fix, and the fix that survives the full documented interference range
is to read a reporter instead, with the voltage interface as a later research
goal. Nothing in the pitch materials, `README.md` or this audit's earlier
parts was edited to match that view.

---

## Part 25: The Closest Prior Art Yet, Missed Until Now, and It Says the Native Oscillation Might Be the Readout Rather Than the Problem (September 2026)

**Where this came from:** the founder asked a plain question, why nobody has
connected a genetic switch to an actual electrical signal in a cell when
optogenetics and neuroscience do exactly that. Checking the question properly
instead of restating Part 9's "no prior art at all" surfaced a paper this
project has never cited, from the same lab whose work Parts 12 through 21 are
all built on.

**The paper:** Yang, Bialecka-Fornal, Weatherwax, Larkin, Prindle, Liu,
Garcia-Ojalvo & Süel (2020), "Encoding membrane potential-based memory within
a microbial community," *Cell Systems* 10(5):417-423, DOI
10.1016/j.cels.2020.04.002, PMID 32343961, PMC7286314. Same lab as Prindle et
al. 2015, same strain (NCIB 3610), same channel (yugO).

**How this sits with Part 24, which was written in parallel and points the
other way.** Part 24 recommends taking the electrical readout off Stage 0's
critical path in favour of a two-color reporter. That recommendation stands,
and this part does not overturn it. Part 24's case is against reading an
ABSOLUTE membrane-potential level, which is the same scheme the simulation
below also finds collapses to 54-65% under the native oscillation. Phase
encoding is a different scheme with a different failure mode, and it is more
speculative than anything Part 24 assessed, since nobody has built the
genetic-circuit-to-phase-response link at all. Read the two parts together as:
reporter-first for the cheap stage, level-based electrical readout
deprioritised, phase-based electrical readout added to the research queue
behind both. Part 24 also found a second missed paper (Bonnet, Subsoontorn &
Endy 2012) narrowing Part 10's novelty claim, independent of the one below.

### What they actually demonstrated

Taken from the paper's own text, not from its abstract alone:

- A 5-second blue light (438 nm) exposure to a region of a living *B. subtilis*
  biofilm produces a persistent change in those cells' membrane potential,
  measured with the Nernstian dye Thioflavin T at 10 uM.
- The effect is yugO-specific and genetically confirmed: a delta-yugO deletion
  strain shows no noticeable membrane potential change on light exposure, and
  excess extracellular potassium blocks the response while excess sodium does
  not. Controls with propidium iodide and Sytox rule out cell death, and added
  glutamine returns the cells to resting potential.
- Their model's reading of the mechanism: light leaves a fraction of yugO
  subunits permanently conducting, so exposed cells passively follow
  extracellular potassium while unexposed cells retain active control and
  counter-regulate.
- The consequence: exposed and unexposed cells respond to potassium
  oscillations in **anti-phase**. Cross-correlation is anti-correlated at zero
  lag and maximally correlated at 50 minutes lag, half their imposed
  100-minute period. This held against both an artificially imposed
  oscillation (alternating 150 mM and 8 mM external potassium) and the
  biofilm's own natural one.
- Spatial patterns stayed readable at single-cell resolution for over 3 hours.
- Their own discussion frames this for biological computing: the anti-phase
  behavior "allows us to produce a clear signal that is either 'on' or 'off,'
  as in traditional digital memory."

### What this does to Part 9's "no prior art" claim

It narrows it, and the narrowing has to be stated plainly because a diligent
investor or reviewer will find this paper.

**What is no longer novel:** writing an arbitrary spatial pattern into a living
*B. subtilis* biofilm's membrane potential, reading it back non-destructively
at single-cell resolution, keeping it readable for hours through the colony's
own potassium oscillations, and framing that as digital memory for biological
computing. All of that is published, in the target organism, since 2020.

**What is still open, and it is real rather than a consolation:**
1. **Their memory is not genetic.** It is a persistent protein-level
   modification of existing channels, and their discussion says so directly:
   it "does not arise from positive feedback, but rather from enduring
   modifications at the protein level." The Gardner-toggle link this project
   proposes is a different mechanism.
2. **Theirs would not survive division.** A protein modification dilutes out as
   cells divide. Their own discussion notes biofilm cells are "predominantly
   non-replicating," which is part of why the pattern persists at all. This
   project's whole differentiator, data surviving damage and regrowth (Parts 8,
   20, 22), is exactly what their mechanism cannot do.
3. **Hours, not indefinite.** Over 3 hours observed, with the model predicting
   longer. This project's own bar has always been 24 hours and beyond.
4. **No demonstrated rewrite cycle.** Light writes; glutamine returns cells to
   resting potential, which hints at an erase, but a repeated write-0/write-1
   cycle on the same cells is not shown.
5. **No addressing, encoding or error-correction layer.** A visible pattern is
   not the same as an addressable memory with a read/write interface.

**The honest summary line for investor-facing material:** the claim to make is
no longer "nobody has stored data as a bioelectric state." It is "the state has
been written and read, and it does not survive cell division, which is the
property this project is actually after."

### Two things it confirms that this project had only proposed

- **yugO.** Part 14 named yugO as the candidate channel from Lundberg et al.
  2013. This paper independently calls it "the only known potassium channel"
  in the organism and uses a delta-yugO knockout as its key control. The
  identification was right.
- **The strain split flagged in `experiments/BENCH_PROTOCOL_BSUBTILIS.md`.** Their work is
  in NCIB 3610, not W168, consistent with that document's section 1.

### The strategic inversion, and a simulation testing it

Parts 12, 13, 17, 18 and 21 all treat the native potassium oscillation as noise
to average out, time around, or engineer away. Yang et al. do the opposite: the
oscillation is what makes their bit readable, because the bit IS the cell's
phase relationship to it. That is a carrier wave, not interference.

`simulations/bsubtilis_18_phase_encoded_readout.py` tests that framing inside this project's
own model. It keeps the Gardner ODE and the same noise magnitudes as
`bsubtilis_01_gardner_toggle_circuit.py`, and changes only what the voltage tracks: instead
of the stored bit selecting a static V_HIGH or V_LOW, it selects whether the
cell responds in phase or anti-phase with the ambient oscillation. The readout
is the sign of the correlation between the cell's voltage trace and a
separately measured reference trace. Both schemes are run under identical
conditions, with read start times spread across the oscillation period so
neither gets an accidentally phase-locked read.

**Result, 60-minute read, 10mV-equivalent measurement noise:**

| Ambient amplitude | Level encoding (existing scheme) | Phase encoding (new) |
|---|---|---|
| 0 mV (no oscillation) | 100% | 50% |
| 10 mV | 65% | 86% |
| 30 mV | 54% | 99% |
| 50 mV | 55% | 100% |
| 70 mV | 58% | 100% |

The inversion holds cleanly. The level-encoding column reproduces
`bsubtilis_08_native_oscillation_interference.py`'s own 50-59% collapse, which is the
consistency check that the two files agree. The phase-encoding 50% at zero
amplitude is the control behaving correctly: with no carrier there is no phase
to read, so it must fail there, and it does.

**What phase encoding costs, from the same file's other sweeps:** a read of
roughly 60 minutes or more (a 10-minute read is near chance), measurement noise
held under about 20mV-equivalent at the low end of the amplitude range, and a
strong coupling between the stored bit and the cell's potassium response (at
10% coupling it degrades to 49-76%). None of those three has been measured,
here or in the source paper, for a genetically driven version of this.

### A direct conflict this creates with Part 18

`bsubtilis_12_decoupled_channel_readout.py` recommends weakening or deleting yugO to reduce
how much native signal reaches the engineered circuit. Yang et al. show a
delta-yugO strain does not respond to the write stimulus at all.

So **for level encoding yugO is the problem, and for phase encoding yugO is the
mechanism.** The two strategies are mutually exclusive, and they point at
different chassis strains. Part 18's recommendation is not withdrawn, it is
now conditional on which encoding scheme the project commits to, and that
choice has to be made before a strain is chosen rather than after.

### What is still unbuilt, stated as strictly as everywhere else

Yang et al. wrote their bit with light onto native channels. Nobody has wired a
genetic circuit's state to a cell's in-phase versus anti-phase potassium
behavior. That link is unbuilt and unmeasured, the same status as the
repressor-to-ion-channel link in `bsubtilis_01_gardner_toggle_circuit.py`, and
`bsubtilis_18_phase_encoded_readout.py` says so in its own docstring. What changed is that
the unbuilt link now has a demonstrated physical mechanism sitting underneath
it in the same organism, rather than none at all. Also not tested: whether a
phase-encoded bit survives damage and regrowth the way the genetic state does.
---

## Part 26: Rebuilding the San Diego Optical Write in This Project's Own Code, What Reproduced and What Did Not (September 2026)

**Where this came from:** the founder asked whether the Yang et al. 2020 work
covered in Part 25 can be used as the basis for a simulation of the WRITE step
in *B. subtilis*, and whether their data could be reused or a test built from
their results.

### First, what is actually available

Their paper's own Data and Code Availability statement reads, verbatim: "This
study did not generate new code nor software. All raw data are available upon
request from the Lead Contact." There is no deposited dataset and no released
code. Their model's parameter table is supplementary Table S1, which is not in
the open-access full text (retrieved as PMC7286314 via PubMed Central).

So their data cannot be reused. What can be reused is the structure of the
model, which their STAR Methods describes in full prose, and the observables
they report in the main text. That is enough to reimplement the mechanism and
then check the reimplementation against their published results, which is what
`simulations/bsubtilis_21_optical_write_replication.py` does.

### What reproduced

Four of the five things they report come out of the reimplementation directly:

| Signature they report | Reproduced | Value here |
|---|---|---|
| Light exposure hyperpolarises exposed cells | Yes | about 8 mV separation |
| delta-yugO strain shows no response | Yes | 0.00 mV shift |
| Excess extracellular potassium blocks the hyperpolarisation | Yes | shift inverts to +3.8 mV at 150 mM |
| Pattern holds at steady state for hours | Yes | flat from 30 to 200 minutes |
| Anti-phase, cross-correlation peak at half the 100-minute period | **No** | +0.91 at zero lag, peak at 95 minutes |

The sodium half of their chemical-clamp control is untestable here by
construction: this is a potassium-only model, so it cannot produce a sodium
effect and no claim is made about it.

### The signature that did not reproduce, and why that is worth writing down

Their anti-phase result is the one this project cares most about, because
`simulations/bsubtilis_18_phase_encoded_readout.py` and Part 25's strategic
inversion both rest on it. The reimplementation does not produce it, and a
12-point sweep across three orders of magnitude of potassium influx coupling,
pumping rate and channel conductance never reaches anti-phase at any setting.

The reason is structural rather than a matter of tuning. With intracellular
potassium near the textbook 300 mM, the potassium reversal potential under a
150 mM external shock sits well above the resting potential, so opening
channels can only depolarise a cell. Their explanation requires the opposite:
unexposed cells must *hyperpolarise* under excess external potassium by
actively opening channels and releasing ions. A reduced model with a pumped
intracellular setpoint cannot produce that, whatever its rate constants.

**This is a gap in the reimplementation, not a challenge to their result.**
They report the anti-phase behaviour experimentally, with microfluidics
alternating 150 mM and 8 mM potassium, not only in simulation, and the
cross-correlation peak at 50 minutes is their measurement. The honest statement
is that this project cannot currently rebuild the mechanism behind it, and the
missing piece is a specific, askable thing: the parameter values in their Table
S1. That is a concrete reason to write to the Lead Contact (Gurol Suel, UC San
Diego) rather than a vague wish for collaboration.

**Consequence for Part 25 and for bsubtilis_18.** Part 25's phase-encoding
result is not withdrawn, but its standing is now weaker than it read. It was
computed with an *imposed* sinusoid and a bit that selects in-phase or
anti-phase behaviour by assumption. This part tried to derive that anti-phase
from the potassium mechanism and could not. So phase encoding rests on the
published experiment plus an assumed coupling, with no working mechanistic
model in this repository behind it. It stays behind the two-colour reporter in
the queue, which is where Part 24 already put it, and for a second reason now.

### What the division test found, which is the part that matters

Their memory is a protein-level modification of existing channels, and their
Discussion says biofilm cells are "predominantly non-replicating," which is
part of why the pattern lasts. Acheron needs the bit to survive regrowth, which
means division. Running the optical write forward through generations:

| Generation | Modified channel fraction | Optical write separation | Genetic latch separation |
|---|---|---|---|
| 0 | 0.800 | -8.47 mV | -8.47 mV |
| 1 | 0.450 | -1.73 mV | -8.47 mV |
| 2 | 0.275 | -0.27 mV | -8.47 mV |
| 3 | 0.188 | -0.06 mV | -8.47 mV |
| 8 | 0.103 | -0.01 mV | -8.47 mV |

At a 5 mV or 2 mV readout threshold the optical write is unreadable after one
generation; at 1 mV it survives one. At a 30-minute doubling time that is hours,
not days.

**This result does not depend on the uncalibrated constants.** A fixed
population of modified channel subunits halves as a fraction of the total pool
every time the cell doubles its channels with newly synthesised, unmodified
ones. That is arithmetic on the mechanism they themselves describe. The genetic
column is flat by construction, because it assumes the latch is inherited, and
that assumption is exactly what `simulations/bsubtilis_07_colony_regrowth.py`
models and what no wet lab has tested.

So the head-to-head is: their write step works and is published in this
project's target organism; their retention step is the one this project claims
to improve on, and the improvement is real in principle and unmeasured in
practice.

### Honest limits of the new file

- Every rate constant except RT/F at 30 C, the two potassium concentrations,
  the 100-minute period and the 50-minute lag is an uncalibrated placeholder.
  No number from that file should be quoted as measured.
- The 8 mV write separation is a property of the placeholder constants, not a
  prediction. Only its sign and its persistence are meaningful.
- The file does not show that a genetic latch can drive channel state at all.
  That link is unbuilt and unmeasured, the same status it has in
  `simulations/bsubtilis_01_gardner_toggle_circuit.py`.

## Part 27: Noise as a Feature, Not Just a Threat, and a Native B. subtilis Circuit That Might Beat the Imported One (September 2026)

**Where this came from:** the founder read a Quanta Magazine piece
("Cells in Living Things Fight Noise with Noise," Emily Singer, reprinted
by Scientific American) on Michael Elowitz's noise research and asked
whether any of it changes this project's approach. Chasing the two
claims that matter most through PubMed surfaced two real, directly
relevant primary papers this audit had not cited before, plus a live
side-by-side simulation of both.

**What it establishes.**

1. Sueel, Garcia-Ojalvo, Liberman & Elowitz (2006), "An excitable gene
   regulatory circuit induces transient cellular differentiation,"
   Nature 440(7083):545-550, DOI 10.1038/nature04588, PMID 16554821.
   This is B. subtilis's OWN native competence circuit (comK), not
   borrowed from E. coli the way `gardner_toggle_circuit.py`'s toggle
   switch is. Structurally it is excitable, not bistable: fast positive
   feedback (ComK self-activation) plus a slower negative feedback (an
   exit pathway) that returns the cell to vegetative growth, with noise
   triggering entry. The abstract reports the authors "re-engineered the
   gene circuit to specifically block exit" as a test of their model,
   i.e. they demonstrated, in real B. subtilis, that disabling the
   negative-feedback arm converts a transient noise-driven pulse into a
   state the cell does not spontaneously leave.

2. Elowitz, Levine, Siggia & Swain (2002), "Stochastic gene expression
   in a single cell," Science 297(5584):1183-1186, DOI
   10.1126/science.1070919, PMID 12183631. Confirms the intrinsic vs.
   extrinsic noise split described in the secondary article, using a
   real two-color-reporter method in E. coli: intrinsic noise is
   randomness inherent to one gene's own expression, uncorrelated
   between two identically-regulated genes in the same cell; extrinsic
   noise is a shared, whole-cell fluctuation (e.g. total RNA polymerase
   or ribosome availability) that moves every gene in that cell together.

Two further claims from the secondary (non-peer-reviewed) article could
NOT be independently verified this session, PubMed searches for both
came back empty, so they are logged as unverified, not established: (a)
that a noisier comK circuit variant outperformed an engineered quieter
one under stress (attributed to a follow-up Sueel/Elowitz study), and
(b) that noise magnitude is partly an inherent property of a specific
promoter, independent of its mean strength (attributed to Ido Golding's
work). Neither is used as fact anywhere in this project; both are open
items pending a real citation.

**What this changes, and what it doesn't.**

`gardner_toggle_circuit.py`'s `transcriptional_noise_std` applies two
INDEPENDENT random draws each step, one per repressor. That is
structurally intrinsic-noise-only in Elowitz et al.'s terms, it has never
modeled a shared, correlated (extrinsic-style) source. `simulations/
intrinsic_extrinsic_noise.py` (new) tests this directly by subclassing
`GardnerToggleCell` (unmodified) and adding one shared random draw
applied to both repressors together. Result, run this session: at matched
promoter strength (ratio=1.0), fidelity stayed at 100% even with
extrinsic noise equal in magnitude to the existing intrinsic term, no
degradation found in this range. A mismatched-but-still-passing ratio
(10.0) did drop slightly, from 100% to 93%, when extrinsic noise reached
its highest tested value. Honest reading: at the magnitudes tested here
(chosen to match the existing tx_noise_std range, not measured values),
promoter mismatch remains the dominant, already-documented failure mode;
extrinsic noise is a real, previously unmodeled second-order effect, not
(at these untested-for-real magnitudes) a new dominant one. This does not
resolve the question, it narrows it: the real answer depends on actual
measured extrinsic noise in the specific BBB promoters used, which nobody
has measured yet.

The comK precedent does NOT mean the Gardner toggle switch should be
dropped. comK is real and native, but it is excitable/transient by
design, built for a temporary competence window, not proven as a durable
multi-generation memory element, and nobody has built or tested an
exit-blocked comK variant for data storage, let alone through damage and
regrowth. `simulations/bsubtilis_22_comK_excitable_circuit.py` (new) models the
qualitative topology only (a generic fast-activator/slow-inhibitor
excitable-system form, NOT the paper's own fitted equations, which are
unavailable, this paper has no open-access full text in PubMed Central).
Run this session: the normal (exit-active) variant showed the expected
transient, noise-driven behavior, high shortly after a write pulse, then
decaying and re-triggering unpredictably (0%, 62%, 12% "still high" at
1h/6h/24h across trials). The exit-blocked variant stayed at 100% "still
high" at all three checkpoints, matching the Gardner toggle's own 100%
on the identical 24h persistence test. That is a plausibility result
from a generic model, not a validated one, it shows the qualitative
mechanism the paper describes (excitable to locked, via blocking exit)
is simulatable and consistent, not that this specific numeric model is
correct.

**The actionable takeaway:** the fastest, cheapest next validation step
available is not the full damage-and-regrowth wet-lab test already in
the roadmap, it is Elowitz's own two-color-reporter assay, run on the
actual BBB promoters intended for the toggle circuit, single-cell
imaging, in B. subtilis. That would replace the currently-assumed
`tx_noise_std` placeholder with a real, measured, per-promoter number,
split into intrinsic and extrinsic components, and would also settle
whether the two unverified claims above (noisier-survives-better,
promoter-specific noise) hold for the parts this project actually plans
to use. It is cheaper and faster than the $10K-$30K/6-12 month
experiment below, and its result would directly inform which promoter
pair to commit to before spending that budget. Separately, whether an
exit-blocked comK variant is worth pursuing alongside (or instead of)
the Gardner toggle is now a real, better-grounded-than-a-guess open
question rather than an untested idea, worth a literature-only deep dive
(does anyone have open-access full text or a preprint with the actual
fitted parameters) before any wet-lab time is spent on it.

---

## Part 28: Four More Founder-Sourced Papers From the Elowitz Lineage, and What Each One Changes (September 2026)

The founder supplied four PDFs directly (not found via literature search),
all from the same research lineage as Part 27's Elowitz et al. 2002 and
Suel et al. 2006 citations. Each was read in full and checked against what
this project already has, rather than assumed relevant on the strength of
the author list. Two answered "nothing new, already the basis for planned
work." Two produced real, usable additions, described below with the new
simulation files they motivated.

**1. Elowitz, Levine, Siggia & Swain (2002), "Stochastic Gene Expression in
a Single Cell," Science 297:1183-1186, DOI 10.1126/science.1073263.**
Already this project's basis for wet_lab_experiments/Experiment_2's
two-color-same-promoter control and Part 27's intrinsic/extrinsic noise
framing. No new action; confirms the project is already built on the
correct primary source rather than a secondary description of it.

**2. Swain, Elowitz & Siggia (2002), "Intrinsic and extrinsic contributions
to stochasticity in gene expression," PNAS 99(20):12795-12800, DOI
10.1073/pnas.162041399.** New. This is the theoretical companion to #1,
giving closed-form expressions connecting noise magnitude to real
biochemical parameters (transcription rate, burst size, gene copy number,
protein/mRNA lifetime ratio, cell-cycle phase) instead of an assumed
constant. `simulations/bsubtilis_25_transcription_translation_noise_scaling.py`
(new) uses the paper's own well-known asymptotic simplification,
eta_int^2 ~= (1+b)/<P> (b = burst size, also independently derived by
Thattai & van Oudenaarden 2001, which Swain et al. cite), to check whether
`bsubtilis_01_gardner_toggle_circuit.py`'s uncited `transcriptional_noise_std=3.0`
placeholder is a plausible order of magnitude. Run this session: across
burst sizes from 1 to 50 (the paper's own stated "may be of order tens"
range for E. coli, not a B. subtilis measurement), the placeholder came
out 3x to 17x SMALLER than the formula implies, an underestimate across
the whole range tested, not just at the high end. Taken at face value,
this means the project's existing fidelity numbers (M1/M2 at 100%, M3 at
50%) could be optimistic if real burst size is anywhere in the literature-
typical range, and sharpens exactly what wet_lab_experiments/Experiment_2
needs to measure (real burst size and mean expression level for the actual
BBB promoter pair) to replace this whole comparison with one real number.
The same file also quantifies, via the paper's eta^2 ~ 1/n scaling, that
chromosomal (single-copy) integration is not noise-neutral relative to a
multi-copy plasmid, a real, measured cost of the design choice
`experiments/BENCH_PROTOCOL_BSUBTILIS.md` Section 2.2 already makes on
qualitative grounds (avoiding copy-number drift during Stage B2 regrowth).
Caveat stated in the file itself: the (1+b)/<P> form omits the paper's own
cell-cycle correction, which its Eq. 22 shows can move a naive estimate by
up to 65%, so treat this as a bound, not a precise prediction.

**3. Dunlop, Cox, Levine, Murray & Elowitz (2008), "Regulatory activity
revealed by dynamic correlations in gene expression noise," Nature
Genetics 40(12):1493-1498, DOI 10.1038/ng.281.** New. Describes a
time-resolved diagnostic (not a snapshot): the time-lagged cross-
correlation function between two genes in the same cell distinguishes an
actively repressing link (a delayed anticorrelation dip) from no link at
all (only a near-zero-lag positive peak from shared noise), without
perturbation, validated on their own real synthetic circuit.
`simulations/bsubtilis_26_noise_crosscorrelation_diagnostic.py` (new)
implements their own cross-correlation formula and runs it on this
project's own `GardnerToggleCell` trajectories. Run this session: M1
(matched) and M3 (severe mismatch) both showed the expected anticorrelated
dip, cleanly distinguished from an unregulated control (no dip, only a
positive peak), reproducing the paper's core validation result on this
project's construct. It did NOT distinguish M1 from M3 from each other:
`bsubtilis_01_gardner_toggle_circuit.py`'s promoter-ratio parameter
rebalances relative strength, it never switches the repression term off,
so the mechanical coupling is mechanically present at every ratio; M3's
real failure (Part 9) is losing steady-state SEPARATION between the two
basins, a different question than "does a regulatory link exist at all."
This is a genuine, non-obvious finding: the method is a real complement to
Experiment 1's flow-cytometry read (which does measure basin separation),
not a substitute for it, and is worth flagging as an additional, optional
analysis method if Experiment 1's bench work includes time-lapse imaging.
Also citable for something `experiments/BENCH_PROTOCOL_BSUBTILIS.md`
Section 2.2 already argues qualitatively: their own Fig. 3c/4d show
plasmid-borne genes carry higher extrinsic noise than chromosomally
integrated ones, a real measured precedent for the chromosomal-
integration choice.

**4. Suel, Kulkarni, Dworkin, Garcia-Ojalvo & Elowitz (2007), "Tunability
and Noise Dependence in Differentiation Dynamics," Science 315(5819):
1716-1719, DOI 10.1126/science.1137455.** New, and the highest-value find
of the four. This is the direct experimental follow-up to Part 27's Suel
et al. 2006 citation, which `bsubtilis_22_comK_excitable_circuit.py` could
only model qualitatively because 2006's paper has no open-access full
text. This 2007 paper's own note 15 gives the actual functional-form ODEs
for the comK/comS circuit (Hill-function positive autoregulation of ComK,
Hill-repressed comS, both degraded through a shared competitive MecA-
ClpC-ClpP term), real structure this project did not have before, even
without the paper's fitted numeric constants (in its SOM, not part of
what was supplied). `simulations/bsubtilis_24_comK_suel2007_equations.py`
(new) implements these real equations and, with illustrative parameters
tuned to reproduce the paper's own qualitative regime map, reproduces all
three of its reported dynamical regimes as a single parameter (aK, comK's
basal expression rate) is increased: quiescent/excitable at baseline
(rare spontaneous entry, consistent with the real ~3% per-division
initiation rate), oscillatory at an intermediate value (frequent
noise-driven entry/exit, matching the paper's own Hyper-aK strain at
intermediate induction, their Fig. 2A), and permanently LOCKED at a high
value, a SECOND, independently-documented route to a persistent comK
state, distinct from Part 27's "block exit" mechanism from the 2006
paper. The paper's own explanation for the lock: once aK exceeds ComK's
own activated production rate, degradation can no longer bring it back
down regardless of comS. Also logged, not yet modeled: the paper's
"CompRok" strain (one added Rok-mediated negative-feedback arm onto comK)
cut competence-duration variability roughly in half (13.9 +/- 3.4h vs.
20.2 +/- 9.9h wild-type, their own measured numbers) without changing the
mean, a real precedent for "an added feedback arm makes a stochastic
circuit's timing more precise," relevant if a future comparison is drawn
against `bsubtilis_16_damage_sensing_reinforcement.py`'s proposed
reinforcement circuit. This project's own illustrative aK multiples do
not quantitatively match the paper's reported induction curve; only the
qualitative three-regime structure is claimed.

**Net effect of this part:** two real analytical/mechanistic tools
(Swain 2002's noise-scaling formula, Dunlop 2008's activity diagnostic)
and one real upgrade to the comK track's grounding (Suel 2007's actual
equations, plus a second citable lock mechanism). None of the four papers
required correcting anything already in the audit; they extend Part 27
rather than revise it.

---

## Part 29: Hostile External Review, and Three Robustness Sweeps That Came Out of It (October 2026)

**What triggered it.** The founder pasted the project summary into an outside
AI model and asked for a hostile review. Most of what came back restated gaps
this audit already lists (the unbuilt circuit-to-voltage link, the W168 versus
NCIB 3610 strain mismatch, damage modelled as removing cells only, the zero
margin regrowth budget, the assumed phase coupling). Four points were new or
sharper than the audit, and one of those, that the placeholder noise makes
every fidelity number optimistic, had never been tested. Three points were
wrong: the SOS response in `bsubtilis_16` is the damage SENSOR, not a
duplicate of something the cell already does; the stored state is a
protein-level toggle, not a voltage (voltage is only the planned readout);
and the two-colour reporter assay is cheaper than the toggle but not free.
Experiment 1 needs neither the voltage link nor the strain match.

**What was built.** Three new simulations, all sweeps, none measured:
`bsubtilis_27_noise_robustness_sweep.py` (also holds the parameterised
regrowth engine, which at defaults reproduces `bsubtilis_07` and `_14`),
`bsubtilis_28_regrowth_timing_sweep.py`, `bsubtilis_29_stressed_survivors.py`.
Every axis in them is a sweep axis, not a prediction.

**Result 1, noise (Part 28 found the placeholder 3.3x to 16.8x too low; this reading is superseded in part by Part 31, which shows the failure point belongs to the Gaussian noise model and that the 3.3x to 16.8x comparison used unlike quantities).**
Single-cell genetic fidelity at 24 h, passing bar 70 percent:

| promoter ratio | 1x | 2x | 3x | 5x | 10x | 20x |
|---|---|---|---|---|---|---|
| 1.0 (matched) | 100% | 100% | 100% | 100% | 60% | 53% |
| 2.0 | 100% | 100% | 100% | 87% | 53% | 52% |
| 5.0 | 100% | 100% | 83% | 70% | 50% | 55% |
| 10.0 | 100% | 77% | 65% | 52% | 50% | 52% |
| 0.1 | 50% | 50% | 50% | 50% | 47% | 47% |

Colony recovery after damage and regrowth (matched promoters, 6 h window, so
not directly comparable to the 24 h table): 100 percent at 1x through 5x for
2, 5 and 20 percent survivors, 84 to 85 percent at 10x, 55 to 57 percent at
20x. **Reading it honestly:** the earlier 100 percent figures hold only if
real noise is under roughly 5x the placeholder. At the lower end of the
Part 28 bound (3.3x) matched and moderately mismatched promoters still pass
and a 5x mismatch is marginal. At the upper end (16.8x) nothing in the
single-cell table passes. So the answer to "does Experiment 1 pass" now
depends on a number nobody has measured, which is exactly what the
two-colour reporter assay in Stage B0 measures. Promoter MATCHING matters
more at higher noise, because mismatch fails earlier (ratio 10 fails at 2x).

**Result 2, the regrowth budget (doubling time 30/45/60 min, settling delay
0/30/60 min).** Reporter (genetic) fidelity stayed at 100 percent and the
colony regrew in all 54 grid cells, including 60 minute doubling from a
single cell, where it finishes with essentially zero minutes to spare. The
electrical readout is a different story: the 180 minute averaged read works
only when the budget leaves the full window. Any shortfall, even to 151
minutes, dropped it to a coin flip (50 percent) at the worst damage level,
and a 45 minute doubling time alone is enough to break it at 2 and 5 percent
survivors. At 20 percent survivors it survived delays up to 60 minutes at
45 minute doubling at 30 mV, but failed at 70 mV with 166 minutes of window,
so it is fragile near the edge. **The zero-margin finding stands and is
stronger than stated in Part 21: the electrical readout needs the
undisturbed 30 minute doubling time, and the reporter readout does not.**
This is a second, independent reason (after the interference problem in
Parts 12 and 13) why the reporter readout is the recommended first readout.

**Result 3, stressed survivors (slower division, higher noise, voltage
shift, applied to survivors for a stress window after damage).**
- A growth penalty up to 3x slower did not change genetic fidelity (100
  percent) at any survival level.
- A 10x noise rise during a 180 minute stress window cost about four points
  (96 percent) for both readouts. If the stress lasts the whole 6 hour window,
  with 2x slower growth and 10x noise, genetic fidelity fell to 85 to 87
  percent, still above the 70 percent bar.
- A voltage shift of 20 mV in either direction changed nothing. A shift of
  40 mV in either direction, lasting through the read, took the long-window
  voltage read to 50 percent. The reason is inherited, not new:
  `V_HIGH=-10 mV` and `V_LOW=-80 mV` sit 35 mV on either side of the decision
  midpoint, and both numbers came from the planarian model with no B.
  subtilis measurement behind them. A transient shift that ends before the
  read has no effect.
- **Reading it honestly:** the reporter readout is robust to everything
  swept here except combined sustained high noise. The voltage readout is
  fragile to any sustained shift of about 35 mV or more, which nobody knows
  is or is not what damaged B. subtilis cells do. This does not replace
  Stage B2 arm 2b, which measures it.

**Protocol changes made in response (not results).** Experiment 1 and Stage B0
now run to 72 hours with dilution, require the bimodal distribution to hold
across three consecutive timepoints spanning at least 48 hours, and add a
washout-and-reread arm and an inducer hysteresis arm (a slow monostable
circuit can pass a 24 hour snapshot, it cannot fake a toggle's
history-dependent curve), plus optional single-cell tracking. Experiment 3 and
Stage B2 gain a locus-stability check (colony PCR of both integrated arms
after each regrowth round) so a lost or rearranged construct is not mistaken
for a memory failure. `bsubtilis_18_phase_encoded_readout.py` is relabelled a
sensitivity analysis under an assumed coupling, per Part 26.

**Not done, and still open:** the review's strongest strategic point.
Bonnet, Subsoontorn & Endy (2012) already showed a heritable, rewritable DNA
recombinase latch with non-destructive fluorescent readout, and a DNA latch
also survives damage and regrowth for the same reason a protein toggle
does. "Survives division" therefore does not separate this project from that
work. What would is a stated functional advantage of a protein toggle with
damage-sensing reinforcement (`bsubtilis_16`) over a DNA latch, and none is
established. Until one is, the honest framing is that the project's value is
in testing self-detecting, self-reinforcing memory through damage, not in
beating existing DNA memory on stability.

---

## Part 30: Fitness Cost and Selection, the Gap Neither the Audit Nor the Protocol Covered (October 2026)

**What triggered it.** A second round of outside review, this time of the Part
29 fixes. It conceded two earlier points and raised one genuinely new one,
which a search confirmed: no file in the audit, bench protocol, experiments or
simulation map mentioned fitness cost, burden, selection or a competition
assay. Every simulation assumes the circuit is free and that no cell ever
loses it. In a real culture, a cell that mutates a promoter, silences the
reporters or loses the integrant can outgrow cells that carry the bit, and in a
cytometry histogram that looks exactly like state loss. A 72 hour pass or fail
could therefore be uninterpretable in both directions. The review's other
points were either already done (relabelling `bsubtilis_18`, sweep-axis
labelling of `bsubtilis_29`) or repeated the earlier SOS misreading (SOS is the
damage sensor in `bsubtilis_16`, not a duplicate of a natural response).
Its claim that the two-colour assay belongs in a "same cost class as the
toggle" is a guess, nothing has been quoted.

**What was built.** `bsubtilis_30_fitness_cost_selection.py`, a population
model with written-state circuit cells, flipped circuit cells and circuit-lost
cells. Lost cells grow (1 + s) times as fast; circuit cells become lost at
rate mu per division. Reports the ungated read (all cells, what a naive
cytometry read gives) against the gated read (reporter-positive only). **Both
s and mu are sweep axes. Neither is measured.** The result is a map, not a
prediction.

**Results (deterministic expectation unless stated).**
- Selection only bites over long cultures. After 7 generations, which is what
  a damage and regrowth run involves, 98 to 100 percent still hold the bit
  across the whole grid except at mu of 1e-2 (84 to 93 percent), so at
  plausible fitness costs and loss rates **selection during the regrowth window
  itself does not dominate the result**. That is a narrower claim than "the
  regrowth test is not threatened" (the first wording of this part, corrected
  after review), because it says nothing about who survives the damage. The 72
  hour run in Experiment 1 is threatened directly, because it is 36 to 144
  generations depending on doubling time.
- **Survivor bias (section F) is the larger risk for Experiment 3, and it is
  not modelled in direction.** If the survivors of damage are not a random
  sample, selection that happened BEFORE the damage carries through. Starting
  from a culture that has already run 72 generations, random survivors
  (bias 1) at s of 0.10 and mu of 1e-4 leave 49 percent lost among survivors and
  35 percent holding the bit after 7 generations of regrowth; at s of 0.10 and
  mu of 1e-5 it is 9 percent lost and 84 percent holding; at s of 0.03 and mu of
  1e-4 it is 2 percent lost and 97 percent holding. Over-representation of lost
  cells among survivors makes it worse (bias 10 at s of 0.10, mu of 1e-5: 49
  percent lost, 35 percent holding) and under-representation makes it better
  (bias 0.5: 5 percent lost, 91 percent holding). The practical consequence is
  procedural: run damage on freshly written cultures with few generations
  between write and insult, and measure the lost share before damage and among
  survivors. The size and direction of real bias is unknown; both directions are
  swept.
- With no growth advantage for lost cells (s of 0), the bit survives 72
  generations at 99 percent or better for mu up to 1e-4, and 93 percent at
  mu of 1e-3.
- A 3 percent advantage with mu of 1e-4 holds 98 percent at 72 generations and
  81 percent at 144. A 10 percent advantage with mu of 1e-5 holds 91 percent
  at 72 generations and 1 percent at 144. A 10 percent advantage with mu of
  1e-3 leaves 9 percent at 72 generations.
- Generations until the ungated read drops below the 70 percent bar range from
  about 10 (s of 0.30, mu of 1e-2) to more than 2,000 (s of 0, mu of 1e-4 or
  lower). With s of 0.03 and mu of 1e-4 it is 165 generations; with s of 0.10
  and mu of 1e-5 it is 88.
- With a finite dilution bottleneck of 10,000 cells the time to the bar is
  noisy (for example median 110 generations with a 5th to 95th percentile of
  76 to 324 at s of 0.10, mu of 1e-5), and at s of 0.30, mu of 1e-6 nine of 30
  replicates never reached it. At a bottleneck of 1,000,000 the spread nearly
  vanishes (89, range 85 to 93). **The manual serial dilution regime in
  Experiment 1 sets how noisy this is, and that noise is a handling artifact.**
- Gating decides the interpretation: at s of 0.10, mu of 1e-3, 72 generations,
  the ungated read is 9 percent while the gated read is 100 percent with no
  flipping and 62 percent at a flip rate of 1e-2 per generation. A low
  ungated read with a high gated read means the circuit was lost, not the bit.

**Reading it honestly.** Whether a 72 hour result means anything depends on two
numbers nobody has measured, the fitness cost and the loss rate. The new
competition assay and growth-rate comparison in Experiment 1 measure the first
directly; the second needs the gated cytometry counts and, if loss is seen,
sequencing of reporter-negative isolates. It also matters for any later claim
about long-term storage, not just this experiment: a stored bit in a growing
culture has a half-life set by selection, independent of how stable the toggle
itself is.

**Protocol changes made in response (first round).** Experiment 1 and Stage B0 now make the
inducer hysteresis arm the primary pass criterion for M1 and M2, with a
specified method (pilot dose-response, ON-history and OFF-history populations,
equilibration confirmed by two successive reads); state the 72 hour culture
method (manual serial dilution at fixed intervals, OD and generations
recorded, spore check; microfluidic chemostat noted as cleaner but not needed
first); add growth-rate comparison against parental W168, a competition assay
against an isogenic differently marked reference, and a cytometry gate that
counts cells negative for both reporters separately from flipped cells; and
make the 70 percent bar apply to both reporter-positive and all cells, with
results met only after excluding lost cells reported as uninterpretable.
Experiment 3 and Stage B2 gain the same gate. The Experiment 1 cost estimate is
now marked a floor that predates these additions.

**Protocol changes made in a third review round.** A further review found six
problems with those changes, all accepted: (1) the pass bar now reports two
numbers at every timepoint, the product number (all live cells in the written
state, gates pass or fail) and the mechanism number (circuit-positive cells in
the written state), with an interpretation guide, because the same fail can
mean a working toggle with unstable expression or a broken toggle; (2) the
cytometry gate is now four bins (A high B low, A low B high, both low, both
high or intermediate), because the both-high bin is the clearest sign that
mutual repression is failing and the circuit is a co-expresser, and a
viability or nucleic-acid stain plus scatter now excludes dead cells, debris
and spores that would otherwise inflate the both-low bin; (3) hysteresis now
requires a step-response calibration of the circuit's settling time first, with
every level held at least three times the slowest plateau time, and single-cell
cytometry at every level (a washout cannot calibrate a toggle, because a toggle
never forgets); (4) the "selection does not threaten regrowth" wording above is
corrected and a survivor-bias control added to Experiment 3 and Stage B2; (5)
the competition assay is now specified (reference strain, label swap and
reference-versus-reference noise floor, sequencing for isogenicity, DNase I and
no competence conditions, same regime as Experiment 1); (6) sporulation is now
managed, not just checked: measured at every passage by heat-shock plating
against untreated plating, with a maximum acceptable fraction set by the lab
and founders before the run (deliberately left blank, since any number would be
invented) and a rule for changing the design if it is exceeded. The Experiment 1
cost floor now also covers the calibration, spore monitoring and strain
sequencing. The review also pressed the voltage question; see
`docs/VOLTAGE_DECISION_MEMO.md`, which lays out the choice and does not make it.

**A fourth review round.** The reviewer said each earlier round produced a sketch
that needed a second pass to become a specification. Roughly half of the new
points were right, two were already in the files, and one (that the
survivor-bias sweep was only optional) was out of date, because it had already
been built. Accepted, and written into Experiment 1 and Stage B0:
- a **pre-registered interpretation table** that maps each bin pattern to a
  conclusion (working toggle, asymmetric, monostable, co-expresser, graded,
  slow relaxation, expression loss, construct failure, culture problem), fixed
  before data. One correction to the reviewer: [dark] means lost or silent
  circuit, not "graded"; graded is the intermediate pattern;
- the **gating hierarchy** (all events, singlets, live cells, scatter exclusion of
  debris and spores, compensation, four bins), with thresholds from parental,
  fully induced and single-color controls;
- the **calibration is independent of the hysteresis run**, uses its own cultures,
  fixes the equilibration time in advance, and has a sample-count formula (a
  count, not a price, since nothing has been quoted);
- the **sporulation threshold is now a rule, not a blank**: the upper end of the
  parental W168 spore fraction measured in a pilot in the same regime, with ranked
  fallbacks (tighten dilution, shorten the run and limit the claim, change medium
  and redo the baseline, move to continuous culture) and a statement of what each
  costs;
- the **competition assay is a checklist** where every row must be "yes" before it
  runs, now including the reference fluorophore's own cost against unlabelled
  parental W168;
- a **recommendation in the voltage memo** (Path C, reporter first), not adopted
  until the founders record a decision;
- **Experiment 1 is split**: 1a (M1 and M3, calibration, hysteresis, 24 hour read)
  is the cheap go/no-go gate; 1b (M2, the 72 hour run, fitness, competition and
  sporulation) runs only if 1a passes.

**Survivor composition in the cell-level engine (`bsubtilis_30`, section G).**
The earlier sweep (section F) tracked population fractions only. Section G puts
the question into the regrowth engine: each survivor is independently
wrong-state, or already lost, with probability q. Mean fidelity and the share of
colonies clearing the 70 percent bar:

| survivors | q=0 | q=0.05 | q=0.10 | q=0.25 | q=0.50 |
|---|---|---|---|---|---|
| 1 (2%) | 100 / 100 | 93 / 93 | 90 / 90 | 83 / 83 | 38 / 38 |
| 3 (5%) | 100 / 100 | 96 / 88 | 92 / 77 | 78 / 50 | 48 / 13 |
| 13 (20%) | 100 / 100 | 96 / 100 | 91 / 100 | 75 / 65 | 46 / 5 |

Recovery tracks survivor composition, because division copies whatever the
survivors hold. The project's central number, "2 percent survivors recover to 100
percent", is therefore exactly as good as the assumption that those survivors are
all correct. With one survivor the outcome is all or nothing; with more survivors
the mean is the same and the spread narrows, which helps when survivors are mostly
right and hurts when they are not. Wrong-state and lost survivors give identical
numbers on this ungated read (both fail to hold the bit) and differ only in the
gated mechanism number. The survivor probabilities are sweep axes, not
measurements; the plated-survivor comparison in Experiment 3 and Stage B2 is what
measures them.

**Not accepted as stated.** The suggestion that stopping to write more protocol
detail is the next step. The remaining unfixed items (the spore threshold number,
the neutral integration site, the sample counts) are values only the lab can set,
and a flow-cytometry-literate microbiologist reviewing the protocol is worth more
than another pass by an outside AI.

**A fifth review round, and the last outside AI pass this protocol should get.**
The reviewer found two real errors and one real README gap, and pushed on a third
point where only part of its argument holds. Accepted:
- **Compensation is not a gate.** It is a matrix computed from single-color
  controls and applied to the fluorescence data before any fluorescence gate. The
  gating order is now: compensation applied to the data, then events, singlets,
  live cells, spore and debris exclusion, then the fluorescence bins. The spore
  exclusion method is named (a scatter gate drawn with a purified spore control),
  and the trigger channel for bacteria is left to the lab.
- **The calibration is a gate, not a component.** Experiment 1 is now Pilot P0
  (dose-response, response-time calibration on its own cultures, parental W168
  spore baseline), then 1a, then 1b. If the settling time is longer than a
  vegetative culture can be sustained, hysteresis cannot be run in batch and the
  design changes before anything else is spent. The calibration is of the same
  order of size as the hysteresis test it sets up, so staging protects the budget
  for 1b and not for 1a. No cost figure is attached, because none has been quoted.
- **M2 earns a place in 1a, M3 stays.** M2 is the realistic case and answers how
  much promoter mismatch the circuit tolerates (the noise sweeps in Part 29 make
  that matter more, since mismatch fails earlier as noise rises). All three
  variants are built together and read at 24 hours in 1a. M3 is kept in 1a because
  it is the negative control for the hysteresis assay: a loop on M1 alone cannot
  show the assay returns one curve for a circuit known to be monostable. M2's
  hysteresis is deferred to 1b, and M2 is now reported rather than required
  to proceed, since the gate question is M1 against M3. That downgrade of M2 from a
  required pass to a reported result is a design choice a practitioner should check.
- **Path C is a funding and sequencing choice, not a resolution of the novelty
  question.** The voltage memo now says so: the novelty claim is provisional until
  a decision is recorded, no investor-facing material may claim voltage novelty or
  an advantage over a DNA latch, and the "founder's description never mentions
  voltage" argument is withdrawn as evidence (it is silent on mechanism by design
  and supports neither path).
- **The README never mentioned Bonnet et al. 2012.** It argued the differentiator
  only against Yang et al. 2020, so its headline claim was stated without
  addressing the closest overlap. A short section now does.
- **A reviewer handoff note** (`docs/PROTOCOL_REVIEW_HANDOFF.md`) lists the values
  only a lab can set and the specific questions to ask a practitioner.

The reviewer also agreed that further AI review rounds have stopped paying and that
the protocol has grown past the original experiment. The next review should be by a
person who has run a toggle in *B. subtilis* and used cytometry on bacteria.

**Final small corrections before the human review (sixth outside pass).** The
reviewer called itself done, and a search of what it said against the repo and the
literature kept four changes and refused two things:
- **Kept: P0 builds M1 only.** The earlier "build all three together" contradicted
  P0 being a spend gate, and the P0 calibration formula had quietly required M3.
  M2 and M3 are built after P0 passes. A lab saying a batch build is cheaper
  overrides this default, and the handoff asks them.
- **Kept: spore exclusion is scatter plus a third fluorescence channel, validated
  by heat-shock plating.** Scatter alone cannot separate spores from
  stationary-phase cells, and plating is destructive so it can only validate the
  gate. A spore reporter built on GFP would collide with the toggle's own sfGFP
  reporter, so any reporter must be a third color.
- **Kept: a never-pulsed control** for every strain (and in P0), to set the floor
  for apparent bimodality and show the default state. The no-circuit false-positive
  rate for the both-high bin comes from parental W168 and single-color controls.
- **Kept: the handoff names exactly where the gating, bin table, pass criteria and
  open values live,** so the reviewer sees the same experiment.
- **Refused: the proposed Bonnet differentiator.** The reviewer said a recombinase
  latch is irreversible per site and needs new registers for new bits, while a
  toggle can be flipped repeatedly. That is wrong. Bonnet et al. 2012 is a
  rewritable memory built with a recombination directionality factor, with
  separate set and reset steps (PMC3384180), and a toggle also needs one circuit
  per bit. Putting it in the README would have been a false claim. The README
  keeps saying that no advantage over a DNA latch is established.
- **Not pending:** the reviewer listed the survivor sweep as open. It is done
  (section G of `bsubtilis_30`).

**Still open.** The review also noted that the locus PCR in Part 29 does not
catch point mutations or silencing. The loss-of-circuit gate and
sequencing of reporter-negative isolates cover that, but only if loss
actually occurs at a detectable rate. And the question raised in Part 29 still
stands: whether the final product needs voltage at all, or a
reporter-read genetic state is enough, which decides how much of the
Bonnet et al. (2012) overlap matters.

---

## Part 31: The Noise Setting's Scale, Found While Planning Model Cross-Checks (October 2026)

**Status: PARTLY RESOLVED the same day (see "Follow-up" at the end of this part). The step-size
dependence is understood and the old sweeps survive it. A cross-check with different mathematics
then found something bigger: the noise-tolerance conclusions are specific to the Gaussian noise
model. No earlier simulation file has been edited.**

**How it was found.** The founder asked whether the simulations could be stress-tested
with different mathematics. While preparing the answer, the noise term in
`GardnerToggleCell.step` (`bsubtilis_01`) was checked against the standard way to
discretize a noisy equation, and two problems appeared.

**Problem 1: the noise depends on the step size.** The random kick is added to the
derivative and then multiplied by dt (`u += (drift + noise) * dt`). A correctly
discretized stochastic equation scales the noise by the square root of dt, so that
the noise intensity per unit time does not change when the step changes. Here it
does. Measured (single seed, same total simulated time, standard deviation of the
repressor level in the written state): at `tx_noise` 3.0 it was 1.43 at dt 0.02, 1.19
at 0.01 and 0.69 at 0.005; at `tx_noise` 30 it was 9.39, 8.56 and 6.80. Every
simulation uses dt 0.02, so comparisons between runs stay internally consistent and
the sweeps in `bsubtilis_27` to `_30` remain valid as statements about this model.
But `tx_noise` is not a physical quantity. It cannot be compared with a measured
noise without recalibrating at that step size.

**Problem 2: `bsubtilis_25` compares unlike quantities.** It computed the
protein-level standard deviation implied by Swain et al.'s formula (10.0 to 50.5,
from CV squared = (1 + b) / <P>, with the model's level of 50 treated as a molecule
count) and divided it by `tx_noise` (3.0), which is the size of a random kick per
step, not a level standard deviation. Measured over a 24 hour equivalent (40 runs
each), the in-state standard deviation of the repressor level was 2.58 at
`tx_noise` 3, 5.55 at 6, 7.26 at 9, 8.38 at 15, 8.16 at 21 and 7.43 at 30. In level
terms the implied range is therefore about 4x to 20x of the placeholder (10 / 2.58
and 50.5 / 2.58), or roughly 7x to 35x if the placeholder's level noise is taken
from the shorter run (1.43). The stated 3.3x to 16.8x is close at the low end by
luck but is the wrong quantity.

**Why it matters more than the ratio (SUPERSEDED, read the follow-up).** This paragraph reads the
additive-noise model's failure point as if it applied to cells. The follow-up shows an exact
molecular model of the same toggle does not fail there. The level standard deviation stops growing
near 8 because the circuit starts to flip. Share of runs that flipped in a 24 hour
equivalent (40 runs each): 0% at `tx_noise` 3, 6 and 9; 12% at 15; 55% at 21; 90% at
30; 100% at 45 and above. So the modelled toggle is lost at a level standard
deviation of about 8, and the whole implied range from Swain (10 to 50) sits beyond
that. If the model's level of 50 really were a molecule count, the modelled toggle
would not hold.

**What this does and does not say.** The level of 50 is a model unit, not a molecule
count. Real repressor numbers per cell are unmeasured (Experiment 4) and may be far
higher, and the formula's CV falls as the molecule count rises, so the implied noise
could be much smaller. The comparison therefore cannot say how far real noise is
from the model's. It says the outcome depends on two unmeasured numbers, molecules
per cell and burst size, and that "holds to about 5x the placeholder" is a statement
about this model's `tx_noise` at dt 0.02, not about cells.

**What needed doing (done in the follow-up below, except where marked).**
1. Reformulate the noise so it does not depend on dt: a stochastic differential
   equation with square-root-of-dt scaling, or an exact stochastic simulation in
   molecule counts using published burst parameters.
2. Redo the noise comparison in level terms.
3. Rerun the `bsubtilis_27` to `_30` sweeps on the corrected noise and compare.
4. Add the wider model cross-checks: analytic bistability conditions, an exact
   stochastic (Gillespie) simulation, first-passage theory for the flip rate, an
   alternative circuit form with mRNA, and an independent reimplementation from a
   plain-English specification. Agreement between those would show the math and the
   code are consistent. It would not show the biology is right.

**Follow-up (same day): what the cross-checks found.** Two new files:
`bsubtilis_31_dt_independent_noise_rerun.py` and
`bsubtilis_32_analytic_and_gillespie_crosscheck.py`. All numbers below are simulation results,
with the sampling noise that comes from 40 to 60 runs per cell.

*1. The step-size problem is real but does not damage the earlier sweeps.* A dt-independent
version of the noise (square-root-of-dt scaling, subclassing the original class, which is
unmodified) reproduces the original trajectories to machine precision at the reference step
(checked on two seeds). Integrated 4x more finely, the same equation gives the same picture:
single-cell fidelity still holds to about 5x the placeholder for matched promoters and collapses
by 10x, mismatched promoters still fail sooner (individual cells move by up to about 16 points,
which is the sampling noise of 40 runs), colony recovery is 99 to 100 percent to 5x, 83 to 85
percent at 10x and 51 to 55 percent at 20x (original 84 to 85, 55 to 57), and the headline cells
of the timing and stress sweeps reproduce (colour read 100 percent throughout, voltage read 50
percent when the window is short or voltage is shifted 40 mV, 100 percent otherwise; the one
difference is the 10x-noise-for-180-minutes cell, 100 percent against an original 96, which is
inside sampling noise at 12 runs). The measured demonstration of the problem: the original class's
repressor-level standard deviation at tx 3 was 2.27, 1.41, 0.87, 0.48 as dt halved from 0.02, while
the dt-independent class gave 2.27, 2.34, 2.50, 2.48. So the sweeps are valid for the Gaussian
model; the issue was that `tx_noise` had no physical scale.

*2. Pen-and-paper math agrees with the simulation on the toggle's structure.* Solving for the
fixed points (u = a1/(1+v^2), v = a2/(1+u^2), a1 = 50) gives an exact bistable window in the
promoter strength ratio of 0.247 to 16.25. The noise-free simulation matched it at all 16 ratios
tried, including two it had never been run at (0.20 gives one state and 0.25 gives two, 15
gives two and 18 gives one). Ratio 0.1, the "dead switch" of Part 9, is analytically monostable.
The noise-free distance from each stable state to the saddle (46.5, 44.0, 37.8, 27.4 for ratios
1, 2, 5, 10) ranks the mismatched variants in the same order as their failure under noise in the
simulation (10x, 5x, 3x, 2x). This is real agreement between independent methods, on the
structural claim that promoter matching is the make-or-break design rule.

*3. On noise, the methods do NOT agree.* An exact stochastic simulation (Gillespie) of the same
toggle in molecule counts, with protein bursts of mean size b, measured CVs that match the
exact protein-only result CV^2 = b/<P> (for example CV 0.139 against 0.141 at 50 molecules and
b = 1). Swain, Elowitz & Siggia's (1+b)/<P> is the same result with an extra Poisson mRNA
stage, so the two agree only for large b; `bsubtilis_25` used the mRNA form without an mRNA stage
in the model. Final-state fidelity after a 24 hour equivalent, by mean ON-repressor molecules:

| burst b | holds at 90 percent or better down to about |
|---|---|
| 1 | 12 molecules |
| 5 | 25 molecules |
| 10 | 50 molecules |
| 20 | 98 molecules |

That is roughly 5 times the burst size, in a model where the repression threshold is 1/50 of the
ON level. The Gaussian simulation fails at a level CV of about 0.32; the exact model at about 0.58 to
0.60 (burst 5 to 20), and never in the grid at burst 1. A chemical-Langevin version (Gaussian but
with noise proportional to the reaction fluxes) fails like the additive simulation, not like
the exact model, so it is the Gaussian approximation itself, not the additive form, that matters.
Mean level of the repressed repressor (noise-free value 0.020): exact model 0.000, chemical
Langevin 0.62, additive simulation 0.66 at tx 9 and 1.61 at tx 21. A Gaussian kick with a floor at
zero cannot represent a species that is almost always absent, so it raises the repressed arm by
tens of times, which suppresses the active arm and makes flips far likelier. That is the likely
reason (inferred from these numbers, not isolated by a further experiment).

*What this changes.*
- **The "holds to about 5x, fails by 10x to 20x" result (Parts 29 and 30) is a property of the
  Gaussian noise model, not of cells.** In an exact molecular model of the same toggle, noise at
  realistic molecule counts does not break it. That weakens Part 29's Result 1 and Part 28's
  "optimistic placeholder" worry, and it withdraws the "3x to 17x too low" headline: it compared
  a kick size with a level spread, and in CV terms it depends entirely on molecules per cell.
- **It does not make the toggle safe.** The first exact model had no mRNA stage and no extrinsic
  (shared) noise (both added and tested in the second follow-up below; `bsubtilis_23` had found a
  real but second-order effect in the Gaussian model), and it still has no division and partition
  noise, and it fixes the ON level at 50 times the repression threshold. The molecule counts above are model results. Whether
  real repressor numbers (Experiment 4) and burst sizes (Experiment 2) are above them is the open
  question, and the fix for the failing part is now sharper: measure those two numbers.
- **The structural conclusions stand and are supported by a second method within this
  parameterization:** promoter matching is the make-or-break rule, with a computable window
  (0.247 to 16.25 for Hill 2 and equal loss rates; it moves with both, see the fourth
  follow-up below and `bsubtilis_35`).
- **Which noise model to trust is itself a result:** the exact molecular model is the more faithful
  description of the reactions it represents, and the Gaussian ones are known to fail near zero
  copies. Unit-free CV is the right yardstick for comparing any of them with a measurement.

*Still open (updated in the second follow-up below).* Division with partition noise in the
molecular model, promoter switching, and cell-to-cell differences. The cross-checks that were
proposed and not run: first-passage theory for the flip rate, and an independent
reimplementation from a plain-English specification. The earlier sweeps (`bsubtilis_27` to `_30`)
were not changed; their noise axis should be read as "Gaussian noise" until a molecular version
of the colony engine exists.

**Second follow-up (same day): does the exact model's robustness survive an mRNA stage and shared
noise?** New file `bsubtilis_33_mrna_and_extrinsic_noise_gillespie.py`, an exact stochastic
simulation with transcription, mRNA decay (gamma_m = 20, so an mRNA lives 1/20 of a protein
lifetime, an assumption), translation (one protein per event, k_p = b * gamma_m) and protein
decay, plus an optional shared factor that scales transcription of both repressors (an
Ornstein-Uhlenbeck process with mean 1). Results are simulation results; cells with 40 runs carry
roughly plus or minus 5 to 8 points of sampling noise.

*Formula check.* For an unregulated gene the measured CV follows the exact two-stage result
CV^2 = (1 + b * gamma_m / (gamma_m + gamma_p)) / <P>, for example 0.138 against 0.139 at about 100
molecules with b = 1, and 0.436 against 0.440 with b = 20. Swain, Elowitz & Siggia's (1 + b) / <P>
is within a few percent of it, so the formula used in `bsubtilis_25` is right for a model with an
mRNA stage (the earlier problem was the comparison, not the formula). The protein-only model of
`bsubtilis_32` follows b / <P> and underestimates noise when b is small (0.099 against 0.138 at 100
molecules, b = 1).

*Toggle with an mRNA stage.* Fidelity at 90 percent or better holds down to about 12, 25, 25 and 50
mean ON repressor molecules for bursts of 1, 5, 10 and 20 (protein-only model: 12, 25, 50, 98).
Everything at 100 molecules or more is 98 to 100 percent. Within sampling noise the mRNA stage does
not reduce the robustness found in `bsubtilis_32`.

*Shared noise.* Letting both repressors' transcription rise and fall together (shared factor CV 0.2
or 0.5, correlation time 1 or 5 protein lifetimes) left fidelity at 92 to 100 percent in all six
molecule-count and burst-size cells tested, down to 50 molecules. The worst cells were 92 percent
(50 molecules, burst 5, CV 0.5, one lifetime) and 92 percent (200 molecules, burst 5, CV 0.5, five
lifetimes), so shared noise cost up to about 8 points, comparable to the few points it cost in the
Gaussian model (Part 27) and well inside what would break the toggle.

*Reading.* The exact model's robustness survives an mRNA stage and shared noise at the parameter
values tried. That makes the Part 31 conclusion firmer: the Gaussian model's early failure comes
from the Gaussian approximation near zero copies, not from anything the exact model leaves out
that these two additions put back. It still does not show cells behave this way. Not yet tested:
division and partition noise at the molecule level, promoter switching (telegraph) noise,
plasmid copy number, cell-to-cell differences, and a different dynamic range (the model fixes the
maximum output at 50 times the repression threshold, and the analytic window of Part 31 narrows as
that ratio falls). The mRNA decay rate and the shared-factor parameters are assumptions.

### Part 31, third follow-up: division with uneven splitting of molecules

`bsubtilis_34_division_partition_noise_gillespie.py` adds the first item on that list to the exact
model. Cell volume grows from 1 to 2 and the cell divides; mRNA and protein are split between
daughters, one lineage is followed. Production scales with volume, repression uses concentration.
Growth supplies a share f of the protein loss (f = 1 is a 35 minute doubling at the repo's time
mapping; protein degradation is 1 - f so total loss stays 1). Four conditions, 40 runs per cell:
no division, even split (same dilution, no partition noise), binomial split at f = 0.5 and f = 1.

*Result.* Fidelity at 90 percent or better down to about (mean ON molecules, bursts 1, 5, 10, 20):
no division 12, 50, 50, 50; even split 12, 12, 25, 25; binomial f = 0.5 12, 25, 25, 50; binomial
f = 1 12, 12, 25, 50. At 100 molecules or more every condition is 98 to 100 percent. Binomial
splitting did not do measurably worse than even splitting (differences of up to about 10 points
in single cells at 12 to 25 molecules, in both directions, are within the sampling noise of 40 runs).
Mean ON concentration stayed within about 8 percent of nominal.

*Reading.* Partition noise does not break the exact model at the values tried, which fits
`bsubtilis_15` and Huh and Paulsson's result that binomial splitting is the mild case. Division
did not make the model worse than having none; the no-division rows look slightly weaker at
bursts of 5 to 10, which this run does not explain and which should not be read as growth helping
the circuit (the cause was not isolated; faster loss through dilution plus the fixed total rate
is one candidate). Not tested: discrete gene copy number across the cell cycle, a population with
selection (see `bsubtilis_30`), promoter switching, a lower dynamic range, and any real value for
molecules per cell or burst size, which only Experiments 2 and 4 can supply.

### Part 31, fourth follow-up: falsification controls, window dependence, intervals, flip rate

An outside review of the molecular results made four fair points; `bsubtilis_35_falsification_window_and_flip_rate.py`
answers them. Also logged here: the "3x to 17x too low" noise headline of Part 28 (`bsubtilis_25`) is withdrawn
(Part 31), and `bsubtilis_25` now carries a superseded header. The "about 5 molecules per cell" result of
`bsubtilis_15` and Part 22 belongs to the colony model without bursts and does not carry over to the molecular
model; the two answer different questions (recovery after damage versus holding 24 hours) and the molecular
range of 12 to 100 mean molecules, depending on burst size, is the more demanding. Burst size for
*B. subtilis* is unmeasured, so the demanding end (burst 20) is not proven to be the realistic one either way.
The damage-sensing boost of `bsubtilis_16` was tested only against the colony model; whether it helps in the
molecular model is untested.

*Window depends on the model.* The exact bistable window (ratio of promoter strengths, equal loss rates) is
none for Hill 1, 0.533 to 2.54 for Hill 1.5, 0.247 to 16.2 for Hill 2, 0.104 to 73.7 for Hill 3 and 0.067 to
9.46 for Hill 4. With Hill 2, making the weak arm's repressor lost 4 times faster gives 0.121 to 1.03; 4 times
slower gives 0.496 to 260. A ratio of 0.1 (the nominal M3 of Experiment 1) is inside the window at Hill 4 and at
Hill 3 with a 4-fold loss-rate difference, and a ratio of 0.01 was outside in all thirteen cases. So the
severe-mismatch control is only a negative control if the real window resembles the modelled one. Experiment 1
and Stage B0 now say so, require measuring each arm's promoter strength, ask for a ratio of 0.01 or lower if
the parts allow, and add an operator-deleted arm as a window-independent negative control. "Independently
supported" in Part 31 has been narrowed to "within this parameterization".

*Falsification control.* The molecular model was run where theory says the toggle must fail. Hill 1 at ratio
1: 72 percent at 24 hours (95 percent interval 57 to 84), 48 percent at four times the horizon; the
antisymmetric mode relaxes at only about 0.14 per protein lifetime, so a 24 hour read still carries memory,
which is slow forgetting and not bistability. Ratios outside the window (0.01, 0.1, 0.2 and 30 at Hill 2,
0.01 and 0.05 at Hill 3, ratio 2 at Hill 1): 50 to 52 percent in every cell. Inside: 98 percent at 0.5 and 80
percent at 0.3 (Hill 2, just inside the 0.247 edge), and at Hill 3 52 percent at 0.15, 80 at 0.2 and 100 at
0.5. Hill 3 moves the molecular window down as the analytic part predicts (0.2 fails at Hill 2, works at Hill
3), and near an edge the molecular model fails slightly before the analytic one, as noise would narrow the
window. The two models therefore fail together where they should, which is a real test but still not a test
of biology. A caution found on the way: the root finder in the first draft missed the ON fixed point at Hill 4
(floating-point rounding put F exactly at zero); fixed by extending the search range.

*Intervals.* The `bsubtilis_34` binomial grid with 100 runs per cell and Wilson 95 percent intervals: the
whole interval sits at or above 90 percent from 25 molecules at burst 1 (93 to 99), 50 molecules at burst 5
(95 to 100), 50 at burst 10 (93 to 99) and 100 at burst 20 (93 to 99). At burst 20 and 50 molecules the
estimate is 91 percent (84 to 95), so the earlier "about 50" for burst 20 is the optimistic reading and 100 is
the conservative one. Thresholds should be read as ranges.

*Flip rate.* Long runs (300 time units, about 250 hours, 40 runs per cell, binomial split) with the first
committed flip as the event give rates per hour with exact Poisson intervals: 12 molecules burst 5: 0.0062
(0.0042 to 0.0088) per hour; 25 molecules burst 5: 0.0009 (0.0004 to 0.0018); 50 molecules burst 5: 0.0003
(0.0001 to 0.0009); 100 molecules burst 5: no flips in 10,000 hours, upper bound 0.0004 per hour; 25 molecules
burst 20: 0.011 (0.0078 to 0.015); 50 molecules burst 20: 0.0021 (0.0012 to 0.0034); 100 molecules burst 20:
0.0006 (0.0002 to 0.0014); 200 molecules burst 20: one flip, 0.0001 per hour. Implied 24 hour retention agrees
with measured fidelity to within about 10 points in both directions (a flip can reverse, and fidelity reads the
state at one moment, so they are not the same quantity). Retention beyond 24 hours is an extrapolation that
assumes a constant rate; a zero-flip cell gives only a bound. A closed-form (Kramers-type) rate is still not
derived.

*Further review round (closing points).* (a) Whether the weak arm "does any work" at a severe mismatch: halving
its production at ratios 0.01, 0.1 and 0.2 changes the strong arm's steady state by a relative 3e-8, 3e-6 and
1.2e-5, and at 0.3 (inside the window) by 2.7e-5. A steady-state sensitivity check is therefore not an
indicator of bistability in this circuit: it is tiny on both sides of the window edge, because the strong arm
sits near its ceiling and the weak arm near zero either way. What distinguishes the two sides is whether a
pulse of the weak arm can hold the switched state, which is what Experiment 1 tests. The check does not show
that the weak arm is irrelevant to the design, and it says nothing about real parts. (b) Monostable is now
defined by memory, at a fixed burst size of 10 (Omega 4, no division, 40 runs per cell, horizons 24, 48, 96 and
192 h): monostable if the 96 h fidelity interval contains 50 percent or fidelity fell by more than 10 points
between 24 h and 96 h; bistable only if it is clearly above chance and the drop is 10 points or less. The
first version of this rule, a drop of more than 10 points, was wrong and failed on its first data: Hill 1 was
already at chance at 24 h (50, 52, 42, 50 percent), showed no drop, and would have been called bistable. Hill 2
stayed at 100, 98, 98, 95 percent (drop 3 points at 96 h). The earlier 72 percent for Hill 1 was at burst 5,
where relaxation is slower; fixing the burst size is what makes the comparison readable. (c) Flip-rate runs are right-censored at 250 h; zero flips in
10,000 cell-hours gives a 95 percent upper bound of about 3e-4 per hour (one-sided), and lower rates are
bounds, not estimates. (d) Equal protein loss assumes equal growth dilution and identical repressor
degradation; with two different repressors (for example LacI and TetR) the degradation rates must be measured,
and unequal degradation is also a design lever that can move the window. (e) A bistable M3 at a measured ratio
of 0.01 or lower falsifies the simulation's window claim, a model correction, not a retraction of the project.

### Part 31, fifth follow-up: colony regrowth and the damage-sensing boost in the molecular model

`bsubtilis_36_molecular_colony_regrowth.py` reruns the project's headline (a small fraction of survivors regrows
into a colony that holds the bit) and the proposed damage-sensing boost (`bsubtilis_16`) in the exact molecular
model, additively: no earlier file was changed and the earlier numbers stand as results of those models.
Survivors (all assumed correct) found lineages that divide with binomial partitioning to about 64 cells, then
follow one daughter each over 6 hours of settling (11.4 protein lifetimes in all, about 9.5 hours, shorter than
the 24 hours of `bsubtilis_34`). Recovery is the fraction of final cells holding the bit; the 100 percent
survivor row is the no-damage baseline over the same time.

*Result.* In the five cells of the main table (25 to 200 mean molecules; burst 5 at 25 and 50, burst 20 at 50,
100 and 200), mean recovery was 98 to 100 percent at every survivor level tested (2, 5, 20 and 100 percent), with
worst single colonies at 89 to 100 percent in 12 colonies per cell. Recovery after damage was no worse than the undamaged baseline, which is the point of
`bsubtilis_30` section G: with correct survivors, regrowth adds little loss beyond the single-lineage hold. At
the most marginal cell tested (25 molecules, burst 20, 2 percent survivors) mean recovery was 91 percent
(worst colony 75), and the boost raised it to 95, 97 and 97 percent at multipliers 2, 5 and 10 (worst colony 89,
94 and 89) in 20 colonies per setting. That is a suggestive gain at one marginal cell, not an established
one; at the other cells there was little to rescue (97 to 100 percent without it).

*Reading.* The Gaussian-model figures for the headline (`bsubtilis_07`, `27`) were more pessimistic than the
molecular model near zero copies, and the colony conclusion holds there too. This is still conditional on
survivors being correct, no selection, no crowding, no gene copy number, and molecule counts and burst sizes
that nobody has measured (swept, not bracketing reality). The boost remains a proposal; its gain here says
nothing about whether an SOS-type promoter can be wired to a toggle arm, and any wrong-state cell would be
reinforced toward the wrong state.

### Part 31, sixth follow-up: more than one bit in a cell

Until here every result was for one toggle. `bsubtilis_37_multibit_word_storage.py` gives a first, rough idea of
what N bits in one cell implies, in the exact molecular model (burst 5, 24 hour equivalent, growth and
binomial division, 30 random words per setting). Two questions.

*Shared budget.* With a fixed total of B mean ON repressor molecules shared by N toggles (B / N each), the
whole word stayed right in 100 percent of words for N up to 4 at every B tested (200, 400, 800), and at N = 8
in 100 percent at B = 800, 93 percent at B = 400 (50 molecules per toggle) and 90 percent at B = 200 (25
molecules per toggle); per-bit fidelity was 99 to 100 percent throughout. The word result matched the
independent-bits prediction (per-bit fidelity to the power N) in every cell, so no interference appeared when
the toggles are independent. Intervals at 30 words are wide (89 to 100 percent at the 100 percent cells).

*Crosstalk.* This is where it breaks. If a foreign toggle's repressors count with weight eps at another toggle's
promoters, 8 bits at 100 molecules each held 100 percent of words at eps = 0, 90 percent at eps = 0.003, 30
percent at 0.01 (per-bit 89 percent), and 0 percent at 0.03 and 0.1 (per-bit 54 to 55 percent, near chance).
The cause is simple arithmetic and should be read as a rule of thumb, not a discovery: each toggle's ON
repressor sits at about 50 times the repression threshold (the model's fixed dynamic range), so the foreign
repressors from the other N - 1 toggles add up to roughly (N - 1) x 50 x eps threshold units of repression at
EVERY promoter; once that approaches 1 the toggle loses its two states. That gives a tolerable eps of about 1 /
(50 (N - 1)), about 0.003 for 8 bits, and shrinking as N grows. It depends on the assumed dynamic range of 50.

*Reading.* Under this model, the molecule budget is not what limits a multi-bit word at these sizes; repressor
orthogonality is. Whether enough well-separated repressor pairs exist in *B. subtilis* is a biology question the
model cannot answer: its pairs are free, and eps is a sweep axis, not a measurement. Not modelled: shared
transcription and translation machinery beyond the molecule budget, growth burden from extra circuits, gene
copy number, selection against the heavier cell, readout, and error-correcting codes (which would let a word
survive a few wrong bits at the price of more toggles). Experiment 4 (molecules per cell) and a crosstalk
measurement between candidate repressor pairs would turn these axes into numbers.

---

## Next Action: One Experiment Changes Everything

**The experiment:**
- 2mm × 2mm planarian tissue
- Write one voltage pattern (optogenetic or electrical)
- Measure decay over 48 hours
- Compare to control

**Cost:** $10K-$30K (academic collaboration)

**Time:** 6-12 months (including cell culture setup, transfection, optimization)

**Outcome:** Validates or invalidates entire project thesis

**Do this first. Everything else depends on it.**

---

**End of Audit**

*"The difference between science and engineering is that science asks 'Can we?' and engineering asks 'How do we?' You've done excellent engineering. Now you need to do the science."*
