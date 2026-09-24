# Experiment A: Arbitrary Voltage Pattern Persistence in Engineered Monolayer

**Goal:** Prove that arbitrary voltage patterns can persist 24+ hours in gap junction-coupled cell networks

**System:** HEK293 cells engineered with gap junctions and optogenetics

**Timeline:** 3-6 months (setup + optimization + data collection)

**Budget:** $2K-$10K (see detailed breakdown below)

---

## Overview

### Why HEK293 Monolayer First?

**Advantages over planarians:**
- ✅ Standard cell culture (any lab can do this)
- ✅ Easy transfection (well-established protocols)
- ✅ Fast growth (passage every 3-4 days)
- ✅ Reproducible (low biological variability)
- ✅ Can iterate quickly (try different conditions)

**What this proves:**
- Do arbitrary voltage patterns persist in gap junction networks?
- If YES → Physics supports your thesis, move to planarians
- If NO → Know it's a fundamental problem, not just planarian-specific

---

## Experimental Design

### Phase 1: Baseline Voltage Characterization (Weeks 1-4)

**Goal:** Measure natural voltage distribution in HEK293 cells

**Setup:**
- HEK293 cells in standard culture (DMEM + 10% FBS)
- Confluent monolayer in 35mm glass-bottom dishes
- No stimulation, just observe natural state

**Measurements:**
1. **Voltage-sensitive dye imaging:**
   - Dye: DiBAC₄(3) (affordable, $200/mg, lasts months)
   - Protocol: Add 200 nM dye, incubate 30 min, image
   - Camera: Fluorescence microscope (use lab's existing equipment)

2. **Data to collect:**
   - Image 100-500 cells per dish
   - Measure fluorescence intensity (proxy for voltage)
   - Take images every 1 hour for 24 hours
   - Repeat 3 independent replicates

**Analysis:**
- Calculate mean ± std dev of voltage
- Plot: voltage histogram (distribution)
- Calculate: temporal noise (how much does voltage fluctuate over time?)
- Calculate: spatial noise (cell-to-cell variation)

**Expected outcome:**
- Baseline voltage: -40 to -60 mV range
- Temporal noise: 5-10 mV std dev
- Spatial noise: 10-20 mV std dev

**Success criteria:**
- ✅ Have baseline reference data
- ✅ Understand natural noise floor
- ✅ This tells you how big your pattern signal needs to be

---

### Phase 2: Gap Junction Engineering (Weeks 5-8)

**Goal:** Create cells with controllable gap junction coupling

**Method:** Transfect HEK293 with Connexin-43

**Why Connexin-43?**
- Most well-characterized gap junction protein
- Forms strong electrical coupling
- Available in standard plasmids (Addgene)

**Protocol:**

1. **Get Connexin-43 plasmid:**
   - Source: Addgene (plasmid repository, academic discount)
   - Cost: $65 per plasmid
   - Example: pCMV-Cx43-GFP (fusion with GFP to visualize expression)

2. **Transfection:**
   - Method: Lipofectamine 3000 (standard, works well with HEK293)
   - Protocol:
     - Seed cells at 70% confluency
     - Add plasmid + Lipofectamine mix
     - Incubate 48 hours
     - Check GFP expression (confirms Cx43 present)

3. **Validation:**
   - Test gap junction function with dye transfer assay:
     - Load one cell with calcein (fluorescent dye)
     - Watch it spread to neighbors via gap junctions
     - Measure coupling: how many cells get dye?

   - OR use electrophysiology (if lab has patch clamp):
     - Measure coupling coefficient between cell pairs
     - Target: >0.1 (strong coupling)

**Expected outcome:**
- 30-70% transfection efficiency (typical for HEK293)
- Visible gap junction plaques (GFP puncta at cell borders)
- Functional coupling (dye spreads to 5-10 neighbors)

**Success criteria:**
- ✅ Cells are electrically coupled via gap junctions
- ✅ Can control coupling strength (number of connexins)

---

### Phase 3: Optogenetic Write Interface (Weeks 9-12)

**Goal:** Install light-controlled voltage manipulation

**Method:** Transfect with Channelrhodopsin-2 (ChR2)

**Why ChR2 only (not Halorhodopsin)?**
- Simplify first experiment: just test depolarization (high voltage)
- ChR2 is more robust, better-characterized
- Can add Halorhodopsin later for two-state system

**Protocol:**

1. **Get ChR2 plasmid:**
   - Source: Addgene
   - Cost: $65 per plasmid
   - Example: pAAV-EF1a-ChR2(H134R)-mCherry
   - mCherry tag lets you see which cells have ChR2

2. **Co-transfection:**
   - Transfect with BOTH Connexin-43 AND ChR2 plasmids
   - Ratio: 1:1 (equal amounts of each)
   - Some cells will get both, some just one, some neither

3. **Build simple LED stimulator:**
   - Blue LED (470 nm, $10 on Amazon)
   - Power supply ($20)
   - Arduino for timing control ($25)
   - Mount on microscope (use lab's scope)

4. **Test optogenetic response:**
   - Flash blue light (10 ms pulse)
   - Record voltage with DiBAC₄(3) dye
   - Measure: How much does voltage change?
   - Optimize: light intensity, pulse duration

**Expected outcome:**
- ChR2-positive cells depolarize in response to blue light
- Voltage change: +20 to +40 mV (brings cells from -50 to -10 mV)
- Effect lasts 1-10 seconds after light pulse

**Success criteria:**
- ✅ Can reliably write high voltage state with light
- ✅ Voltage change is larger than baseline noise

---

### Phase 4: Pattern Persistence Test (Weeks 13-16)

**Goal:** THE KEY EXPERIMENT - Does arbitrary pattern persist 24+ hours?

**Experimental setup:**

```
┌─────────────────────────────────────────┐
│   HEK293 Monolayer (Cx43 + ChR2)       │
│                                         │
│   ┌─────────────────────┐               │
│   │   CENTER REGION     │               │
│   │   (depolarized)     │               │
│   │   Blue light ON     │               │
│   │   Target: -10 mV    │               │
│   └─────────────────────┘               │
│                                         │
│   PERIPHERY REGION                      │
│   (resting)                             │
│   No light                              │
│   Target: -50 mV                        │
│                                         │
└─────────────────────────────────────────┘
```

**Protocol:**

**Day 0: Write Pattern**
1. Prepare dish with confluent Cx43+ChR2 cells
2. Identify center region (1mm × 1mm area)
3. Apply blue light to center only (use photomask or focused beam)
4. Duration: 10 seconds continuous illumination
5. Immediately image entire dish (t = 0 baseline)

**Days 0-2: Measure Decay**
- Image every 30 minutes for first 6 hours
- Then every 6 hours for 48 hours
- Total: ~20 timepoints

**Imaging protocol:**
- Add DiBAC₄(3) dye (stays in media, continuous readout)
- Fluorescence microscopy (10× objective, covers whole dish)
- Measure: fluorescence intensity in center vs periphery
- Convert to voltage using calibration curve

**Data to collect:**
- V_center(t) = average voltage in center region
- V_periphery(t) = average voltage in periphery
- ΔV(t) = V_center(t) - V_periphery(t) = pattern strength
- Plot ΔV(t) vs time

**Controls:**
1. **No gap junctions:** HEK293 without Cx43 (pattern should decay FASTER)
2. **No light:** Same setup but no blue light (no pattern created)
3. **Dead cells:** Fixed cells (pattern should not persist)

---

### Phase 5: Data Analysis (Weeks 17-20)

**Quantitative metrics:**

1. **Persistence time (τ):**
   - Fit decay curve: ΔV(t) = ΔV₀ × e^(-t/τ)
   - τ = time constant (how long pattern lasts)
   - Target: τ > 24 hours (pattern persists)

2. **Pattern integrity at 24h:**
   - Calculate: ΔV(24h) / ΔV(0h) = retention ratio
   - Target: >0.7 (70% retention = success)
   - If <0.3 → Pattern has decayed (failure)

3. **Spatial diffusion:**
   - Measure voltage gradient from center to edge
   - Calculate: diffusion constant D (mm²/hr)
   - Ask: Does pattern stay localized or blur out?

4. **Signal-to-noise ratio:**
   - SNR = ΔV / σ_noise
   - Need SNR > 3 for reliable readout
   - If SNR < 2 → Pattern is lost in noise

**Statistical analysis:**
- N = 3-5 independent dishes per condition
- Error bars: standard error of mean
- Significance: t-test between experimental and control

---

## What Success Looks Like

### ✅ **SUCCESS: Pattern persists 24+ hours**

**Data:**
- ΔV(24h) > 20 mV (center still clearly higher than periphery)
- τ > 24 hours (slow decay)
- SNR > 3 (distinguishable above noise)

**Interpretation:**
- ✅ Arbitrary voltage patterns CAN persist in gap junction networks
- ✅ Physics supports your core thesis
- ✅ Ready to move to planarian tissue (Experiment B)

**Next steps:**
- Publish: "Persistent arbitrary voltage patterns in bioelectric networks"
- Patent: "Method for storing information in gap junction-coupled cells"
- Proceed: Phase 2 (Bio-RAID), Phase 3 (ABS)

**Investor pitch:**
- "We've experimentally proven bioelectric pattern persistence"
- "Validated in both simulation and wetware"
- "Ready to scale to planarian self-healing substrate"

---

### ❌ **FAILURE: Pattern decays in <6 hours**

**Data:**
- ΔV(6h) < 10 mV (pattern mostly gone)
- τ < 6 hours (fast decay)
- SNR < 2 (lost in noise)

**Interpretation:**
- ❌ Arbitrary patterns are NOT stable in passive gap junction networks
- ❌ Need active mechanisms to maintain patterns

**Pivot options:**

1. **Add synthetic biology stabilization:**
   - Engineer voltage-gated gene circuits
   - Voltage state triggers gene expression that reinforces that state
   - Makes arbitrary patterns behave like morphogenetic patterns

2. **Use active refresh (DRAM-like):**
   - Re-write patterns every few hours
   - Still useful for space applications (no human intervention)
   - Lower power than keeping neurons alive

3. **Try different encoding:**
   - Instead of steady voltage, use oscillatory patterns
   - Frequency encoding (1 = 10 Hz, 0 = 1 Hz)
   - Oscillations might be more stable than DC levels

4. **Different substrate:**
   - Try cardiomyocytes (stronger coupling)
   - Try engineered cells with synthetic ion channels
   - Or accept that planarians won't work, pivot to pure synthetic bio

---

## Budget Breakdown

### Minimal Budget (Use Existing Lab Resources): **$2K-$3K**

**Assumes:**
- Partner lab provides: microscope, incubator, basic media/supplies
- You provide: plasmids, specialized reagents, your labor

| Item | Cost | Notes |
|------|------|-------|
| Connexin-43 plasmid (Addgene) | $65 | One-time |
| ChR2 plasmid (Addgene) | $65 | One-time |
| Lipofectamine 3000 transfection kit | $400 | 100 transfections |
| DiBAC₄(3) voltage dye | $200 | 10 mg, lasts ~50 experiments |
| Blue LED stimulator (DIY) | $50 | Arduino + LED |
| Glass-bottom dishes (10 pack) | $150 | For imaging |
| Cell culture consumables (tips, tubes) | $500 | Ongoing |
| HEK293 cells (from ATCC) | $500 | One-time purchase |
| Contingency | $500 | For troubleshooting |
| **TOTAL** | **$2,430** | Realistic minimal budget |

---

### Full Budget (If Setting Up From Scratch): **$8K-$10K**

**Includes:**
- Basic fluorescence microscope + camera ($5K used)
- Incubator ($1K used)
- All reagents ($2K)
- Consumables ($1K)

**This assumes NO lab partnership - you're doing it all yourself**
- Not recommended - lab access is critical
- Better to find partner lab and use $2K-$3K budget

---

## Timeline

### Best Case (Everything Works): **16 weeks = 4 months**

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1: Baseline characterization | 4 weeks | Voltage distribution data |
| Phase 2: Gap junction engineering | 4 weeks | Functional coupling validation |
| Phase 3: Optogenetics | 4 weeks | Light-controlled depolarization |
| Phase 4: Persistence test | 4 weeks | 24-hour time series data |
| Phase 5: Analysis + writeup | 4 weeks | Paper draft, figures |
| **TOTAL** | **20 weeks** | **5 months to publication** |

### Realistic (With Optimization Iterations): **6-9 months**

- Allow time for troubleshooting transfection
- Optimize light intensity, pulse duration
- Repeat experiments to confirm results

---

## What You'll Actually See (Visual Description)

### **Week 0: Setting Up**

You're in a cell culture room:
- Biosafety cabinet (clean air hood)
- Incubator (37°C, 5% CO₂)
- Microscope on the bench

You have:
- Flask of HEK293 cells (growing in pink media)
- Plasmids (tiny tubes of DNA in freezer)
- Transfection reagent (blue box in fridge)

---

### **Week 4: First Transfection**

You pipette plasmid + Lipofectamine mix onto cells
- Wait 48 hours
- Check under fluorescence microscope
- See green cells (Cx43-GFP) glowing at cell borders
- Success rate: 30-50% of cells are green

---

### **Week 8: Gap Junction Validation**

Dye transfer test:
- Inject one cell with fluorescent dye (use microinjection or patch pipette)
- Watch under microscope for 30 minutes
- Dye spreads to neighboring cells via gap junctions
- Count: reaches 5-10 neighbors
- ✅ Gap junctions are working

---

### **Week 12: First Light Response**

Connect blue LED to microscope:
- Set up Arduino timer
- Flash light (10 ms pulse)
- Add voltage dye (DiBAC₄(3))
- Watch cells change color (depolarization)
- ChR2 works! Cells respond to light

---

### **Week 16: THE EXPERIMENT**

**Day 0, Hour 0:**
- Dish on microscope
- Apply blue light to center (1mm × 1mm spot)
- Take first image: center is bright (high voltage), periphery is dim (resting)

**Day 0, Hour 6:**
- Take image again
- Center is still somewhat bright, but dimmer
- Pattern is blurring at edges

**Day 1, Hour 24:**
- THE CRITICAL MEASUREMENT
- Is center still distinguishable from periphery?
- Analyze intensity: center vs edge difference

**Outcome A (SUCCESS):**
- Center: still 30% brighter than periphery
- Pattern visible by eye
- ✅ Persistence confirmed

**Outcome B (FAILURE):**
- Center: no longer distinguishable
- Whole dish looks uniform
- ❌ Pattern decayed

---

### **Week 20: Data Looks Like This**

**Plot 1: Voltage over time**
```
Voltage (mV)
   ^
-10│    ╭─────────────────────────────
   │   ╱                              ← Center (stays high)
-30│  │
   │ ╱
-50├────────────────────────────────── ← Periphery (stays low)
   │
-70│
   └─────────────────────────────────> Time (hours)
    0   6   12   18   24   30   36
```

**Plot 2: Pattern strength (ΔV)**
```
ΔV (mV)
   ^
 40│ ●
   │  ╲
 30│   ╲●
   │    ╲
 20│     ╲●────●────●────●  ← SUCCESS (plateaus above 20mV)
   │      ╲
 10│       ╲●
   │        ╲●●●           ← FAILURE (decays to 0)
  0│         ────●●●──────
   └─────────────────────────────────> Time (hours)
    0   6   12   18   24   30   36
```

**Plot 3: Spatial profile (at t=24h)**
```
Voltage (mV)
   ^
-10│      ╭────────╮      ← Center still elevated
   │     ╱          ╲
-30│    │            │
   │   ╱              ╲
-50├──────            ──────
   └─────────────────────────> Distance from center (mm)
   -2  -1   0    1   2
```

---

## Critical Success Factors

### What Must Work:

1. ✅ **Transfection efficiency >30%**
   - If too low: not enough cells have proteins
   - Solution: Optimize transfection conditions, try different reagents

2. ✅ **Gap junction coupling functional**
   - If cells aren't coupled: pattern can't form
   - Solution: Increase Cx43 expression, check connexin localization

3. ✅ **Optogenetic response >20mV**
   - If voltage change is too small: pattern lost in noise
   - Solution: Optimize light intensity, try different ChR2 variants

4. ✅ **Low baseline noise (<10mV std dev)**
   - If cells are too noisy: can't distinguish pattern
   - Solution: Improve culture conditions, temperature stability

5. ✅ **Imaging stability over 48h**
   - If cells die or drift: can't measure persistence
   - Solution: Use stage-top incubator, maintain CO₂/temp

---

## Red Flags (Early Warning Signs)

### During Setup:

⚠️ **Cells grow slowly or die frequently**
- Likely: Contamination or bad media
- Fix: Check sterile technique, replace media

⚠️ **Transfection efficiency <10%**
- Likely: Old reagents or wrong cell density
- Fix: Use fresh Lipofectamine, optimize seeding density

⚠️ **No dye transfer between cells**
- Likely: Gap junctions not forming
- Fix: Increase Cx43 expression, longer incubation time

⚠️ **No light response (ChR2)**
- Likely: Low expression or wrong wavelength
- Fix: Check mCherry fluorescence, verify LED wavelength

### During Experiment:

⚠️ **Pattern disappears in <1 hour**
- Likely: Gap junction coupling too strong (overdamped)
- Fix: Reduce Cx43 expression, try lower connexin density

⚠️ **Pattern spreads across entire dish**
- Likely: Gap junction coupling too strong (diffuses too fast)
- Fix: Reduce Cx43 expression or increase distance between regions

⚠️ **Cells detach or die during imaging**
- Likely: Phototoxicity or wrong conditions
- Fix: Reduce light exposure, improve environmental control

---

## Troubleshooting Guide

### Problem: Pattern decays in <6 hours

**Possible causes:**
1. Gap junction coupling too strong → Reduce Cx43
2. Membrane resistance too low → Add ion channel blockers
3. Ion channels actively driving voltage back to rest → Need to characterize which channels

**Experiments to diagnose:**
- Vary Cx43 expression level (low, medium, high)
- Add pharmacology (gap junction blockers, ion channel blockers)
- Measure membrane resistance directly (patch clamp)

### Problem: Can't distinguish center from periphery even at t=0

**Possible causes:**
1. Light didn't depolarize cells enough → Increase light intensity
2. Voltage change dissipated too fast → Need faster imaging
3. ChR2 expression too low → Increase transfection efficiency

**Experiments to diagnose:**
- Image immediately after light pulse (<1 second)
- Try longer light pulse (1 second instead of 10 ms)
- Sort cells for high ChR2 expression (flow cytometry)

---

## Alternative Approaches (If Standard Protocol Fails)

### Option 1: Use Electrical Stimulation Instead of Optogenetics

**Why:**
- Optogenetics requires transfection (might be bottleneck)
- Electrical stimulation works on any cell

**Method:**
- Use microelectrode array
- Apply voltage pulse to center region
- Measure persistence same way

**Pros:**
- Faster setup (no transfection needed)
- Works immediately

**Cons:**
- Less spatial precision
- Harder to scale to patterns

---

### Option 2: Use Pharmacology Instead of Optogenetics

**Why:**
- Even simpler than optogenetics
- Many drugs alter membrane voltage

**Method:**
- Apply potassium chloride (KCl) to depolarize center region
- Use ion channel drugs (pinacidil, ivermectin)
- Measure how long voltage change persists

**Pros:**
- No transfection needed
- Very fast to test

**Cons:**
- Drug diffuses away (not stable write)
- Can't do precise spatial patterns

---

## Success Criteria Summary

### Minimum Viable Proof:

✅ **Pattern integrity >50% at 24 hours**
- ΔV(24h) / ΔV(0h) > 0.5

✅ **Signal-to-noise ratio >3**
- Pattern distinguishable above baseline noise

✅ **Reproducible across 3+ independent experiments**
- Not a fluke - it actually works

### Stretch Goals:

🎯 **Pattern integrity >70% at 48 hours**
- Even better than expected

🎯 **Can write multiple independent patterns**
- Two separate regions hold different voltages

🎯 **Can "read-write-read" cycle**
- Write pattern, measure it, write again (doesn't damage cells)

---

## What Happens After Success?

### Immediate (Weeks 21-24):

1. **Write paper:**
   - Title: "Persistent arbitrary voltage patterns in gap junction-coupled cell networks"
   - Target: bioRxiv preprint → Biophysical Journal

2. **File provisional patent:**
   - "Method for storing binary information in bioelectric networks"
   - Cost: $300 (DIY) or $2K (lawyer)

3. **Update simulations:**
   - Use measured decay constant (τ) to calibrate BETSE
   - Rerun Bio-RAID simulations with real parameters

### Next Experiment (Months 6-12):

4. **Experiment B: Planarian tissue validation**
   - Same protocol, but with planarian explant instead of HEK293
   - Tests regeneration hypothesis (your unique value prop)

5. **Experiment C: Multi-bit storage**
   - Write 8-bit byte (encode "A" = 01000001)
   - Prove multiple patterns don't interfere

### Funding (Months 6-12):

6. **Approach investors with data:**
   - "We've experimentally proven bioelectric pattern persistence"
   - Show decay curves, statistics, reproducibility
   - Ask: $250K-$500K seed round for Experiment B + Bio-RAID prototype

7. **Reapply to NIAC (if first application rejected):**
   - Now you have wetware data (much stronger application)
   - Phase I: $175K for 9 months

---

## Final Checklist Before Starting

### Have you:

- [ ] Identified partner lab (see Orlando lab list below)
- [ ] Confirmed access to fluorescence microscope
- [ ] Confirmed access to cell culture facility (incubator, hood)
- [ ] Budgeted $2K-$3K for reagents
- [ ] Allocated 10-20 hours/week for 4-6 months
- [ ] Written 1-page proposal for lab partner (what's in it for them?)
- [ ] Prepared to iterate (first attempt might not work)
- [ ] Have backup plan if pattern doesn't persist (pivot options)

### Questions to ask potential lab partner:

- [ ] Do you have fluorescence microscope with time-lapse capability?
- [ ] Can I use your cell culture facility (incubator, hood)?
- [ ] Do you have HEK293 cells, or should I order them?
- [ ] What would authorship look like on publication? (Offer co-authorship)
- [ ] Can I use your Lipofectamine, or should I buy my own?
- [ ] How much bench space can you allocate?
- [ ] Any restrictions on when I can access the lab?

---

## This is the path to proof

**If this experiment works → You've validated your entire thesis**

**If it doesn't work → You've learned critical information and can pivot intelligently**

**Either way, this is better than more simulation**

Now let's find you a lab in Orlando...
