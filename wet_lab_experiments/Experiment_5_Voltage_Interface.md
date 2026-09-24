# Experiment 5: Voltage Interface

**Tests:** the link `docs/SCIENTIFIC_AUDIT_2026.md` Part 9 describes as
having no prior art in any organism.
**Bench protocol this is drawn from:** `experiments/BENCH_PROTOCOL_BSUBTILIS.md`, Stage B4.
**Prerequisite:** Experiment 1 (toggle confirmed) at minimum; ideally
Experiments 1-3 all pass first, since this stage costs more.

## The goal, plainly

Everything before this experiment re-tests things already well-established
in other labs. This is the first experiment that tests something nobody,
anywhere, has ever built: wiring the genetic switch's output to an actual
electrical channel in the cell membrane, so flipping the gene switch also
flips a real, measurable voltage.

## Strain switch required

Move the construct to a **NCIB 3610-derived background**. W168 (used in
Experiments 1-4) does not form the biofilm structure this part needs.
3610 is poorly transformable (plasmid-encoded ComI inhibitor), so route
constructs in by SPP1 phage transduction from a W168 donor, or into a
competence-restored 3610 derivative. Confirm the exact route with the
collaborating lab before ordering anything.

## Build

- Couple one toggle arm's output to expression of a potassium channel.
  Named candidate: **yugO**, a TrkA-domain K+ efflux channel downstream of
  *mstX*, repressed by SinR (Lundberg, Becker & Choe 2013, *PLoS ONE*
  8(5):e60993, DOI 10.1371/journal.pone.0060993).
- **Before committing to a BBB promoter for the toggle arms**, check whether
  it is itself SinR/Spo0A-regulated. Many biofilm-stage promoters are. If
  so, the engineered circuit and native signaling share an upstream
  regulator, not just a membrane, and the two are not independent.

## Read

- **Thioflavin T (ThT) fluorescence** as a membrane-potential indicator
  (the reagent the biofilm electrical-signaling literature uses).
- **Two-electrode electrical impedance spectroscopy**, per Akabuogu, Zhang,
  Krašovec, Roberts & Waigh 2024, *Nano Letters* 24(7):2234-2241,
  DOI 10.1021/acs.nanolett.3c04446.

## Three caveats to build into the protocol

1. **ThT is not calibrated to absolute millivolts.** The `V_HIGH = -10 mV`
   / `V_LOW = -80 mV` values in `bsubtilis_01_gardner_toggle_circuit.py`
   come from the planarian model, not a *B. subtilis* measurement. Report
   ThT readings in relative units only, do not convert to millivolts.
2. **ThT perturbs the cells it measures** (Han & Payne 2022 report an
   elongation-rate effect, DOI 10.1089/bioe.2021.0027). Include a no-dye
   growth control.
3. **ThT's potentiometric interpretation has been challenged in spores**
   (Li, He, Aryal, Wicander, Korza & Setlow 2023, *mBio* 14(5):e02220-23)
   — that paper's scope is spores, not vegetative biofilm cells, so run an
   independent voltage control rather than dropping ThT.

## Pass criteria

A measurable, reproducible difference in membrane potential between the two
written states, in the same direction every time, larger than the strain's
own cell-to-cell variability.

## What fail means, and why it's still valuable

This is the experiment most likely to fail, and it's worth running
precisely because a clean failure here is the single most useful result
available: it would mean the genetic memory works, but reading it out
electrically needs a different approach.

## Cost and time

A real step up from Experiments 1-4: new strain, new equipment. Not yet
quoted anywhere in this project.
