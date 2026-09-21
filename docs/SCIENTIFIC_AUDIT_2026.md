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
down to a strikingly low copy number.** At ~5 molecules per cell and
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
