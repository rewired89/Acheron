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

`simulations/noise_floor_characterizer.py` re-runs the base persistence model
with realistic biological noise sources (ion channel shot noise, cell-to-cell
variability, metabolic fluctuation, thermal noise) injected.

| Scenario | Integrity @ 24h | SNR | Status |
|---|---|---|---|
| Ideal (zero noise — matches `bioelectric_persistence.py` claim) | 100.0% | 9.7:1 | PASS |
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
  baseline — this is what `bioelectric_persistence.py` currently assumes).
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

**What running the combined model found** (`simulations/gardner_toggle_circuit.py`):

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

**Simulated (`simulations/methylation_bit_encoding.py`,
`simulations/methylation_regeneration_transfer.py`), using both real
numbers as anchors instead of one assumed value:** a single-lineage bit
held across generations, and a full colony-damage-then-regrowth-by-division
scenario (mirroring `bacterial_colony_regrowth.py`'s structure), swept
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
colony result.** In `bacterial_colony_regrowth.py`, surviving fraction was
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
category of machinery `gardner_toggle_circuit.py`'s "hypothetical
ion-channel expression link" would need, an engineered bit sharing the
same membrane could have its VOLTAGE READOUT disturbed by the colony's
own signaling, independent of whether the underlying genetic circuit is
working correctly.

**Simulated (`simulations/native_oscillation_interference.py`):** added
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
one instant. `simulations/eis_readout_interference.py` tested that
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

**Full cross-organism comparison.** `simulations/organism_comparison_summary.py`
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

**A gap stated plainly, not filled in:** `native_oscillation_interference.py`
and `eis_readout_interference.py` only exist for B. subtilis, because
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
   choices (`gardner_toggle_circuit.py`) are drawn from.
2. Once expressed, YugO's K+ efflux **activates the histidine kinase
   KinC**, which phosphorylates Spo0A, whose phosphorylated form
   represses SinR — a real, published positive-feedback loop, not an
   assumed one.
3. `mstX-yugO` transcription is low during log-phase growth and rises
   specifically under biofilm-forming conditions, confirmed by RT-PCR
   and RNA harvested at both growth stages.

**What this changes, and what it doesn't.**
`gardner_toggle_circuit.py`'s "hypothetical ion-channel-expression link"
now has a named, literature-characterized candidate channel and
promoter instead of no candidate at all — a materially more concrete
starting point for anyone eventually trying to wire the toggle's output
to a real channel. It does NOT mean that link is validated: nobody has
measured a Gardner-topology circuit driving yugO specifically. And
`native_oscillation_interference.py`'s explicitly-scoped-out question —
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
