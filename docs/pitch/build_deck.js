// Generator for Acheron_Pitch_Deck.pptx. Requires `npm install pptxgenjs`
// (run from wherever this script is executed, e.g. a scratch directory,
// not necessarily this docs/pitch/ folder). Run with `node build_deck.js`,
// it writes Acheron_Pitch_Deck.pptx to the current working directory, copy
// that over this folder's existing file. Before shipping a rebuild, run the
// pptx skill's scripts/office/validate.py against the output and read the
// full markitdown text dump end to end, LibreOffice's PDF conversion (and
// therefore visual/pixel QA) is unreliable in this environment.
const pptxgen = require("pptxgenjs");

// ---- Palette: "Bioelectric", deep space navy + living-signal teal ----
const NAVY = "0B1F3A";       // dark bg
const NAVY2 = "132A4D";      // card on dark bg
const WHITE = "FFFFFF";
const OFFWHITE = "F4F6F7";   // light bg
const INK = "16232F";        // body text on light bg
const MUTED = "5B6B77";      // muted/caption text
const TEAL = "2EC4B6";       // primary accent (bioelectric signal)
const TEAL_DARK = "1C8F84";
const AMBER = "E8A33D";      // "what we found / caution" accent
const CORAL = "E8604C";      // negative/risk accent

const HEAD_FONT = "Cambria";
const BODY_FONT = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
const PW = 13.33, PH = 7.5;

function bgSlide(dark) {
  const s = pres.addSlide();
  s.background = { color: dark ? NAVY : OFFWHITE };
  return s;
}

function pageNum(s, n, dark) {
  s.addText(String(n).padStart(2, "0"), {
    x: PW - 0.9, y: PH - 0.5, w: 0.6, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 10, color: dark ? "6E7F91" : "9AA7AF", align: "right",
  });
}

function kicker(s, text, x, y, color) {
  s.addText(text.toUpperCase(), {
    x, y, w: 6, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 12, bold: true, color, charSpacing: 2,
  });
}

// ============================================================ Slide 1, Title
{
  const s = bgSlide(true);
  s.addShape("rect", { x: 0, y: 0, w: PW, h: PH, fill: { color: NAVY } });
  // signal-wave motif: a few soft teal circles, bioelectric feel
  s.addShape("ellipse", { x: 10.6, y: -1.2, w: 5.5, h: 5.5, fill: { color: TEAL, transparency: 90 }, line: { type: "none" } });
  s.addShape("ellipse", { x: 11.8, y: 3.6, w: 3.2, h: 3.2, fill: { color: TEAL, transparency: 88 }, line: { type: "none" } });
  s.addShape("ellipse", { x: -1.5, y: 4.8, w: 4, h: 4, fill: { color: TEAL, transparency: 92 }, line: { type: "none" } });

  kicker(s, "Incubator Pitch, September 2026", 0.9, 1.0, TEAL);
  s.addText("Acheron", {
    x: 0.85, y: 1.5, w: 11, h: 1.3, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 62, bold: true, color: WHITE,
  });
  s.addText("Self-Healing Bioelectric Memory", {
    x: 0.9, y: 2.75, w: 10.5, h: 0.7, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 24, color: "CFE3E0",
  });
  s.addText("Persistent, regenerative data storage in living cells, for places nobody can send a repair technician.", {
    x: 0.9, y: 3.5, w: 9.2, h: 0.6, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 14, italic: true, color: "8FA6AE",
  });

  s.addShape("line", { x: 0.9, y: 4.35, w: 5.4, h: 0, line: { color: TEAL, width: 2 } });
  s.addText([
    { text: "Founder & Lead Researcher: ", options: { color: "8FA6AE" } },
    { text: "Dayana Sanchez", options: { color: WHITE, bold: true } },
  ], { x: 0.9, y: 4.55, w: 6.6, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13 });
  s.addText([
    { text: "Contact: ", options: { color: "8FA6AE" } },
    { text: "sanchezleal1989@gmail.com", options: { color: WHITE } },
  ], { x: 0.9, y: 4.9, w: 6.6, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13 });
  s.addText([
    { text: "Co-Founder, Head of Business: ", options: { color: "8FA6AE" } },
    { text: "Jacqueline Solano", options: { color: WHITE, bold: true } },
  ], { x: 0.9, y: 5.25, w: 6.6, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13 });
  s.addText([
    { text: "Contact: ", options: { color: "8FA6AE" } },
    { text: "jackiea.solano@gmail.com", options: { color: WHITE } },
  ], { x: 0.9, y: 5.6, w: 6.6, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13 });
  s.addText([
    { text: "Repository: ", options: { color: "8FA6AE" } },
    { text: "github.com/rewired89/Acheron", options: { color: WHITE } },
  ], { x: 0.9, y: 5.95, w: 6.6, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13 });
  pageNum(s, 1, true);
}

// ============================================================ Slide 2, The Problem
{
  const s = bgSlide(false);
  kicker(s, "The Problem", 0.7, 0.5, TEAL_DARK);
  s.addText("Every biocomputing product today runs on neurons, cells built for speed, not for storage", {
    x: 0.7, y: 0.85, w: 11.9, h: 0.9, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 26, bold: true, color: INK,
  });

  const rows = [
    [{ text: "Company", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Substrate", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Lifespan", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Price", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["Cortical Labs", "Human neurons on silicon (CL-1)", "6 months", "$35,000 / unit"],
    ["Koniku", "Neuron-silicon sensing chips", "~2 years", "Not public"],
    ["FinalSpark", "Brain organoids", "Not public", "Cloud access only"],
  ];
  s.addTable(rows, {
    x: 0.7, y: 2.0, w: 8.6, h: 2.0,
    fontFace: BODY_FONT, fontSize: 13, color: INK, border: { type: "solid", color: "D8DEE1", pt: 1 },
    autoPage: false, rowH: 0.5, valign: "middle",
  });

  s.addShape("roundRect", { x: 9.6, y: 2.0, w: 3.05, h: 4.6, rectRadius: 0.08, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("Why this fails for\nlong-duration storage", {
    x: 9.85, y: 2.25, w: 2.6, h: 0.9, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 15, bold: true, color: TEAL,
  });
  const bullets = [
    "Neurons need continuous energy to hold any signal at all",
    "Fixed replacement clock, no self-repair, ever",
    "Requires life support: temperature, pH, oxygen control",
    "None of this survives radiation, vacuum, or physical damage",
  ];
  s.addText(bullets.map((t, i) => ({ text: t, options: { bullet: { code: "2022" }, color: "DCE7E5", breakLine: i < bullets.length - 1, paraSpaceAfter: 10 } })), {
    x: 9.85, y: 3.15, w: 2.6, h: 3.2, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12,
  });

  s.addText("Spacecraft, seafloor sensors, and remote infrastructure share one hard requirement both silicon and neurons fail: nobody can service the hardware in person.", {
    x: 0.7, y: 4.35, w: 8.6, h: 1.6, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 15, color: MUTED, italic: true,
  });
  pageNum(s, 2, false);
}

// ============================================================ Slide 3, The Idea
{
  const s = bgSlide(false);
  kicker(s, "The Idea", 0.7, 0.5, TEAL_DARK);
  s.addText("Some living tissue holds a voltage pattern for weeks, and regrows itself after damage", {
    x: 0.7, y: 0.85, w: 11.9, h: 0.9, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 25, bold: true, color: INK,
  });

  const steps = [
    ["1", "Natural precedent", "Planarian flatworms store body-plan identity (\"grow a head here\") as a bioelectric pattern. Cut one in half, the pattern survives and rebuilds correctly in both halves."],
    ["2", "Our question", "Can the same kind of system, voltage state plus strong regenerative inheritance, hold arbitrary binary data, not just the organism's own natural signal?"],
    ["3", "Why it would matter", "A substrate that needs no power to hold state, and repairs itself after physical damage, is a fundamentally different answer to extreme-environment storage."],
  ];
  let x = 0.7;
  const cardW = 3.9, gap = 0.25;
  steps.forEach(([num, title, body]) => {
    s.addShape("roundRect", { x, y: 2.0, w: cardW, h: 4.5, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "DCE3E6", width: 1 }, shadow: { type: "outer", color: "1B2B33", opacity: 0.12, blur: 6, offset: 3, angle: 90 } });
    s.addShape("ellipse", { x: x + 0.3, y: 2.3, w: 0.55, h: 0.55, fill: { color: TEAL }, line: { type: "none" } });
    s.addText(num, { x: x + 0.3, y: 2.3, w: 0.55, h: 0.55, isTextBox: true, margin: 0, align: "center", valign: "middle", fontFace: HEAD_FONT, fontSize: 20, bold: true, color: WHITE });
    s.addText(title, { x: x + 0.3, y: 3.0, w: cardW - 0.6, h: 0.6, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 16, bold: true, color: INK });
    s.addText(body, { x: x + 0.3, y: 3.6, w: cardW - 0.6, h: 2.7, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, color: MUTED, lineSpacingMultiple: 1.15 });
    x += cardW + gap;
  });
  pageNum(s, 3, false);
}

// ============================================================ Slide 3b, The Full Goal (storage is step 1, not the finish line)
{
  const s = bgSlide(false);
  kicker(s, "The Full Goal", 0.7, 0.5, TEAL_DARK);
  s.addText("Storing a bit is step one. The real target is a cell that writes, hands off, and heals itself for reuse", {
    x: 0.7, y: 0.85, w: 11.9, h: 0.95, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 21, bold: true, color: INK,
  });

  const goalSteps = [
    ["1. Write", "A bit is written into the cell's engineered voltage-holding circuit."],
    ["2. Transfer on split", "When the organism naturally regenerates or divides, the data travels with it into the new organism, not just genetic material, the written state itself."],
    ["3. Self-heal for reuse", "The original cell/colony recovers back to a clean baseline afterward, so it can be written to again rather than being a one-time-use component."],
  ];
  let x = 0.7;
  const cardW = 3.9, gap = 0.25;
  goalSteps.forEach(([t, d]) => {
    s.addShape("roundRect", { x, y: 2.0, w: cardW, h: 2.5, rectRadius: 0.08, fill: { color: NAVY }, line: { type: "none" } });
    s.addText(t, { x: x + 0.28, y: 2.25, w: cardW - 0.56, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 16, bold: true, color: TEAL });
    s.addText(d, { x: x + 0.28, y: 2.8, w: cardW - 0.56, h: 1.6, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12, color: "CFE0DD", lineSpacingMultiple: 1.15 });
    x += cardW + gap;
  });

  s.addShape("roundRect", { x: 0.7, y: 4.75, w: 12.0, h: 2.0, rectRadius: 0.08, fill: { color: OFFWHITE }, line: { color: "DCE3E6", width: 1 } });
  s.addText("In plain English", { x: 1.0, y: 4.95, w: 11.4, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 14.5, bold: true, color: TEAL_DARK });
  s.addText([
    { text: "Living cell", options: { bold: true, color: INK } }, { text: " = a reusable notebook.  ", options: { color: MUTED } },
    { text: "Writing a bit", options: { bold: true, color: INK } }, { text: " = a pencil note in it.  ", options: { color: MUTED } },
    { text: "The organism splitting/regrowing", options: { bold: true, color: INK } }, { text: " = photocopying the notebook.  ", options: { color: MUTED, breakLine: true } },
    { text: "The new organism", options: { bold: true, color: INK } }, { text: " = a new notebook that already has the note copied in.  ", options: { color: MUTED } },
    { text: "Self-healing", options: { bold: true, color: INK } }, { text: " = the original notebook erases its own note and is ready to write a new one.", options: { color: MUTED } },
  ], { x: 1.0, y: 5.4, w: 11.4, h: 1.25, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13.5, lineSpacingMultiple: 1.3 });

  s.addText("This full cycle hasn't been tested in a wet lab yet. It's the goal the roadmap experiment works toward.", {
    x: 0.7, y: 6.95, w: 12, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 11.5, italic: true, color: MUTED,
  });
  pageNum(s, 4, false);
}

// ============================================================ Slide 4b, What's Simulated vs. What's Measured
{
  const s = bgSlide(true);
  kicker(s, "Read This Before Any Number Ahead", 0.7, 0.5, AMBER);
  s.addText("Every number in this deck, so far, comes from a computational model. None of it has been measured in a wet lab yet", {
    x: 0.7, y: 0.9, w: 11.9, h: 0.95, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 22, bold: true, color: WHITE,
  });

  s.addShape("roundRect", { x: 0.7, y: 2.15, w: 5.85, h: 4.05, rectRadius: 0.08, fill: { color: NAVY2 }, line: { type: "none" } });
  s.addText("Simulated (100% of results below)", { x: 1.0, y: 2.4, w: 5.3, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 15.5, bold: true, color: TEAL });
  const simItems = [
    "Bit integrity under noise: 100% (zero-noise) vs. ~50% (realistic noise)",
    "Toggle-circuit fidelity: 100% (matched/mismatched-within-range) vs. 50% (severe mismatch)",
    "Cross-organism recovery threshold: ~2% surviving cells, for all three mechanisms",
    "EIS voltage-read collapse: 50-59% under native biofilm oscillation",
  ];
  s.addText(simItems.map((t, i) => ({ text: t, options: { bullet: { code: "2022" }, color: "CFE0DD", breakLine: i < simItems.length - 1, paraSpaceAfter: 9 } })), {
    x: 1.0, y: 2.95, w: 5.3, h: 3.1, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12, lineSpacingMultiple: 1.15,
  });

  s.addShape("roundRect", { x: 6.75, y: 2.15, w: 5.9, h: 4.05, rectRadius: 0.08, fill: { color: NAVY2 }, line: { color: AMBER, width: 1 } });
  s.addText("Measured (0% of results below)", { x: 7.05, y: 2.4, w: 5.3, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 15.5, bold: true, color: AMBER });
  s.addText([
    { text: "Nothing yet.\n\n", options: { bold: true, color: WHITE, breakLine: true } },
    { text: "The $10K-$30K wet-lab experiment on the roadmap slide is the first physical test of any of this, in any organism. Until it runs, every figure on the surrounding slides is a model's prediction, not a result.", options: { color: "CFE0DD" } },
  ], { x: 7.05, y: 2.95, w: 5.3, h: 3.1, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13, lineSpacingMultiple: 1.2 });

  s.addShape("roundRect", { x: 0.7, y: 6.4, w: 11.95, h: 0.75, rectRadius: 0.08, fill: { color: "18314F" }, line: { color: AMBER, width: 1 } });
  s.addText([
    { text: "Why we're leading with this:  ", options: { bold: true, color: AMBER } },
    { text: "simulation tells us where to spend wet-lab money wisely, it is not evidence the mechanism works in a real cell.", options: { color: "E7ECEF" } },
  ], { x: 0.95, y: 6.4, w: 11.5, h: 0.75, isTextBox: true, margin: 0, valign: "middle", fontFace: BODY_FONT, fontSize: 13 });
  pageNum(s, 5, true);
}

// ============================================================ Slide 5, Scientific Foundation
{
  const s = bgSlide(false);
  kicker(s, "Scientific Foundation", 0.7, 0.5, TEAL_DARK);
  s.addText("Three independently published results this concept is built on", {
    x: 0.7, y: 0.85, w: 11.9, h: 0.7, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 25, bold: true, color: INK,
  });

  const items = [
    ["Bioelectric body-plan control", "Levin et al., multiple papers 2006-2023 (Tufts)", "Voltage gradients control regeneration outcomes in planaria, replicated across multiple labs, the two-headed-worm result is the most cited example."],
    ["Engineered genetic bistability", "Gardner, Cantor & Collins, 2000, Nature", "A synthetic 2-repressor circuit in E. coli holds one of two states indefinitely once flipped, a solved, 25-year-old result, described by its authors as an addressable cellular memory unit."],
    ["Non-destructive electrical readout", "Akabuogu et al., 2024, Nano Letters", "A simple two-electrode impedance measurement distinguishes live from dead bacterial biofilm, tied to one specific ion channel's activity, no dye, no sample destruction."],
  ];
  let y = 1.85;
  items.forEach(([title, cite, body]) => {
    s.addShape("rect", { x: 0.7, y: y + 0.05, w: 0.06, h: 1.35, fill: { color: TEAL }, line: { type: "none" } });
    s.addText(title, { x: 1.0, y, w: 4.0, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 15.5, bold: true, color: INK });
    s.addText(cite, { x: 1.0, y: y + 0.42, w: 4.0, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 11.5, italic: true, color: TEAL_DARK });
    s.addText(body, { x: 5.2, y, w: 7.4, h: 1.4, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13, color: MUTED, valign: "top", lineSpacingMultiple: 1.15 });
    y += 1.6;
  });
  s.addText([
    { text: "Modeling approach: ", options: { bold: true, color: TEAL_DARK } },
    { text: "physics-based, BETSE-inspired simulation (gap-junction diffusion, ion-channel membrane dynamics), the same framework underlying the Levin Lab's own BETSE tool, cross-validated against tasmorpho (Blattner, 2026, bioRxiv), an independently published BETSE-based method whose reference values we reproduce to 6 decimal places.", options: { color: MUTED } },
  ], { x: 0.7, y: 6.55, w: 12.0, h: 0.6, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 11, italic: true, lineSpacingMultiple: 1.15 });
  pageNum(s, 6, false);
}

// ============================================================ Slide 6, What we found (dark, honest)
{
  const s = bgSlide(true);
  kicker(s, "What We Found When We Tested Our Own Claim", 0.7, 0.5, AMBER);
  s.addText("Our first simulation's headline result doesn't survive realistic noise", {
    x: 0.7, y: 0.9, w: 11.9, h: 0.9, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 26, bold: true, color: WHITE,
  });

  s.addShape("roundRect", { x: 0.7, y: 2.1, w: 3.7, h: 4.4, rectRadius: 0.08, fill: { color: NAVY2 }, line: { type: "none" } });
  s.addText("100%", { x: 0.9, y: 2.35, w: 3.3, h: 1.0, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 46, bold: true, color: TEAL });
  s.addText("Bit integrity in a zero-noise simulation", { x: 0.9, y: 3.35, w: 3.3, h: 0.9, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, color: "AEC2C8" });
  s.addShape("line", { x: 0.95, y: 4.35, w: 3.2, h: 0, line: { color: "2A4463", width: 1 } });
  s.addText("~50%", { x: 0.9, y: 4.55, w: 3.3, h: 1.0, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 46, bold: true, color: CORAL });
  s.addText("Bit integrity with realistic biological noise added, a coin flip", { x: 0.9, y: 5.55, w: 3.3, h: 0.9, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, color: "AEC2C8" });

  s.addText([
    { text: "Why it fails:\n\n", options: { bold: true, color: WHITE, breakLine: true } },
    { text: "Passive bioelectric persistence isn't enough on its own, the base model has no real attractor, just a very slow leak, and noise beats slow. ", options: { color: "CFE0DD", breakLine: true, paraSpaceAfter: 10 } },
    { text: "We found this ourselves, by stress-testing our own model, before any outside reviewer did.", options: { color: "CFE0DD" } },
  ], {
    x: 4.85, y: 2.1, w: 7.8, h: 3.0, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 15, lineSpacingMultiple: 1.2,
  });

  s.addShape("roundRect", { x: 4.85, y: 5.15, w: 7.8, h: 1.4, rectRadius: 0.08, fill: { color: "18314F" }, line: { color: AMBER, width: 1 } });
  s.addText([
    { text: "The fix is specific, not a mystery:  ", options: { bold: true, color: AMBER } },
    { text: "an actively engineered bistable circuit, not passive cell behavior. See next.", options: { color: "E7ECEF" } },
  ], { x: 5.1, y: 5.15, w: 7.3, h: 1.4, isTextBox: true, margin: 0, valign: "middle", fontFace: BODY_FONT, fontSize: 14 });
  pageNum(s, 7, true);
}

// ============================================================ Slide 7, The Fix
{
  const s = bgSlide(false);
  kicker(s, "The Fix", 0.7, 0.5, TEAL_DARK);
  s.addText("An engineered bistable circuit, built from parts that already exist", {
    x: 0.7, y: 0.85, w: 11.9, h: 0.8, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 25, bold: true, color: INK,
  });

  s.addShape("roundRect", { x: 0.7, y: 1.9, w: 7.3, h: 4.7, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "DCE3E6", width: 1 } });
  s.addText("Two parts, already characterized separately", { x: 1.0, y: 2.1, w: 6.8, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 15, bold: true, color: INK });
  const parts = [
    ["Topology", "Gardner, Cantor & Collins (2000), two mutually-repressing promoters, demonstrated bistable regime, equations public."],
    ["Chassis parts", "Bacillus BioBrick Box (Radeck et al. 2013, 2017), free, chromosomally-integrating promoters, characterized in B. subtilis specifically (this project's target organism, not E. coli)."],
  ];
  let py = 2.65;
  parts.forEach(([t, d]) => {
    s.addText([{ text: t + ", ", options: { bold: true, color: TEAL_DARK } }, { text: d, options: { color: MUTED } }],
      { x: 1.0, y: py, w: 6.8, h: 0.95, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, lineSpacingMultiple: 1.15 });
    py += 1.05;
  });
  s.addShape("line", { x: 1.0, y: py + 0.05, w: 6.8, h: 0, line: { color: "E4E9EA", width: 1 } });
  s.addText("What running the combined model found", { x: 1.0, y: py + 0.2, w: 6.8, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 15, bold: true, color: INK });
  s.addText([
    { text: "The real finding isn't that a matched circuit works (it does, 100% fidelity at 24 hours), it's what happens at severe promoter mismatch: ", options: { color: MUTED, breakLine: true } },
    { text: "the circuit doesn't degrade gracefully, it loses bistability entirely and always relaxes to the same state.", options: { bold: true, color: INK } },
  ], { x: 1.0, y: py + 0.65, w: 6.8, h: 1.3, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, lineSpacingMultiple: 1.2 });

  // right stat column
  s.addShape("roundRect", { x: 8.25, y: 1.9, w: 4.4, h: 2.2, rectRadius: 0.08, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("100%", { x: 8.5, y: 2.05, w: 3.9, h: 0.85, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 36, bold: true, color: TEAL });
  s.addText("Fidelity at 24 hours, matched promoters (BBB range 1.0x-10x)", { x: 8.5, y: 2.85, w: 3.9, h: 1.1, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12, color: "CFE0DD" });

  s.addShape("roundRect", { x: 8.25, y: 4.3, w: 4.4, h: 2.3, rectRadius: 0.08, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("50%", { x: 8.5, y: 4.45, w: 3.9, h: 0.85, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 36, bold: true, color: CORAL });
  s.addText("Fidelity at severe promoter mismatch (0.1x), a design constraint found before any wet-lab spend", { x: 8.5, y: 5.25, w: 3.9, h: 1.2, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 11.5, color: "CFE0DD" });
  pageNum(s, 8, false);
}

// ============================================================ Slide 7b, Why B. subtilis, not E. coli
{
  const s = bgSlide(false);
  kicker(s, "Chassis Choice", 0.7, 0.5, TEAL_DARK);
  s.addText("Why B. subtilis, not E. coli, the organism the original toggle switch was built in", {
    x: 0.7, y: 0.85, w: 11.9, h: 0.9, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 23, bold: true, color: INK,
  });

  const cols = [
    ["Chassis-matched parts", "Gardner's original 2000 toggle switch was built and characterized in E. coli. But the free, chromosomally-integrating promoter library this project actually uses, the Bacillus BioBrick Box (Radeck et al. 2013, 2017), was characterized in B. subtilis specifically. Porting to E. coli would mean re-characterizing every promoter from scratch, work nobody has funded.", TEAL_DARK],
    ["Built to survive extremes", "B. subtilis sporulates under starvation, desiccation, heat, and radiation stress, a real, well-documented survival mechanism E. coli lacks. That's a direct match to this project's extreme-environment storage thesis (spacecraft, seafloor, remote infrastructure), not a cosmetic preference.", TEAL_DARK],
    ["The trade-off we're not hiding", "B. subtilis's biofilm-forming behavior helps physical resilience and self-healing, but it's also the source of the native potassium-wave oscillation this deck already flags as a readout risk two slides from now. We chose the organism with the better extreme-survival and parts story, and disclosed the cost that comes with it.", CORAL],
  ];
  let x = 0.7;
  const w = 3.9;
  cols.forEach(([t, d, c]) => {
    s.addShape("roundRect", { x, y: 2.05, w, h: 4.3, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "DCE3E6", width: 1 } });
    s.addShape("rect", { x, y: 2.05, w: w, h: 0.09, fill: { color: c }, line: { type: "none" } });
    s.addText(t, { x: x + 0.28, y: 2.35, w: w - 0.56, h: 0.6, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 15.5, bold: true, color: INK });
    s.addText(d, { x: x + 0.28, y: 3.0, w: w - 0.56, h: 3.1, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12, color: MUTED, lineSpacingMultiple: 1.2 });
    x += w + 0.24;
  });
  s.addText("Net effect: B. subtilis costs us a known, already-quantified readout complication in exchange for chassis-matched genetic parts and a real extreme-survival mechanism. We think that's the better trade, and we're showing our work either way.", {
    x: 0.7, y: 6.55, w: 12, h: 0.7, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, italic: true, color: MUTED,
  });
  pageNum(s, 9, false);
}

// ============================================================ Slide 8, Cross-organism ranking (chart)
{
  const s = bgSlide(false);
  kicker(s, "Honest Risk Ranking", 0.7, 0.5, TEAL_DARK);
  s.addText("We ranked our own three candidate mechanisms by how much wet-lab risk each still hides", {
    x: 0.7, y: 0.85, w: 11.9, h: 0.85, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 23, bold: true, color: INK,
  });

  s.addText("Grounding confidence (qualitative, not a measured score)", {
    x: 0.7, y: 1.9, w: 6.7, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 11.5, italic: true, color: MUTED,
  });
  const confRows = [
    ["B. subtilis, engineered circuit", "Highest", 1.0, TEAL],
    ["B. subtilis, methylation", "Medium", 0.6, AMBER],
    ["Planarian, bioelectric circuit", "Lowest", 0.3, CORAL],
  ];
  let cy = 2.35;
  const barMaxW = 5.6;
  confRows.forEach(([label, tier, frac, color]) => {
    s.addText(label, { x: 0.7, y: cy, w: 6.7, h: 0.3, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, bold: true, color: INK });
    s.addShape("roundRect", { x: 0.7, y: cy + 0.35, w: barMaxW, h: 0.5, rectRadius: 0.04, fill: { color: "E4E9EA" }, line: { type: "none" } });
    s.addShape("roundRect", { x: 0.7, y: cy + 0.35, w: barMaxW * frac, h: 0.5, rectRadius: 0.04, fill: { color }, line: { type: "none" } });
    s.addText(tier, { x: 0.7 + barMaxW * frac + 0.1, y: cy + 0.32, w: 1.0, h: 0.55, isTextBox: true, margin: 0, valign: "middle", fontFace: BODY_FONT, fontSize: 12, bold: true, color: INK });
    cy += 1.1;
  });
  s.addText("All three numerically tie at ~2% surviving-cell recovery threshold, that number alone doesn't rank them; grounding confidence, shown above, does.", {
    x: 0.7, y: cy + 0.05, w: 6.7, h: 0.65, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 11, italic: true, color: MUTED, lineSpacingMultiple: 1.15,
  });

  const rows = [
    [{ text: "Mechanism", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Grounding confidence", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["B. subtilis, engineered circuit", "Highest, inheritance is mechanistically forced (division copies existing protein)"],
    ["B. subtilis, methylation", "Medium, real fidelity numbers exist, but from a different species"],
    ["Planarian, bioelectric circuit", "Lowest, cell-coupling strength is a borrowed assumption, never measured"],
  ];
  s.addTable(rows, {
    x: 7.65, y: 1.95, w: 5.0, h: 4.5,
    fontFace: BODY_FONT, fontSize: 11.5, color: INK, border: { type: "solid", color: "D8DEE1", pt: 1 },
    autoPage: false, valign: "middle", rowH: [0.6, 1.3, 1.3, 1.3],
  });
  s.addText("Our original organism choice (planarian) is currently our weakest-evidence option. We're reporting that now, before spending wet-lab money on it.", {
    x: 0.7, y: 6.6, w: 12, h: 0.6, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13, italic: true, color: MUTED,
  });
  pageNum(s, 10, false);
}

// ============================================================ Slide 9, New risk found
{
  const s = bgSlide(false);
  kicker(s, "Stress-Testing Our Own Design", 0.7, 0.5, TEAL_DARK);
  s.addText("A risk nobody asked about: the colony's own biology can scramble the read, even when the data is fine", {
    x: 0.7, y: 0.85, w: 11.9, h: 0.95, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 22, bold: true, color: INK,
  });

  const cols = [
    ["The natural signal", "B. subtilis biofilms run a continuous potassium-wave electrical signal of their own (Prindle lab, 2015), independent of anything Acheron builds.", TEAL_DARK],
    ["What we found", "In simulation, this natural oscillation can corrupt an instantaneous voltage reading even when the underlying engineered circuit's data is 100% intact.", CORAL],
    ["The fix, and its limit", "Reading via impedance (EIS) instead of raw voltage helps, but a single fast EIS sweep isn't immune either, it needs to integrate across a full oscillation cycle (~3h) to recover accuracy.", TEAL_DARK],
  ];
  let x = 0.7;
  const w = 3.9;
  cols.forEach(([t, d, c]) => {
    s.addShape("roundRect", { x, y: 2.05, w, h: 4.3, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "DCE3E6", width: 1 } });
    s.addShape("rect", { x, y: 2.05, w: w, h: 0.09, fill: { color: c }, line: { type: "none" } });
    s.addText(t, { x: x + 0.28, y: 2.35, w: w - 0.56, h: 0.6, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 15.5, bold: true, color: INK });
    s.addText(d, { x: x + 0.28, y: 3.0, w: w - 0.56, h: 3.1, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, color: MUTED, lineSpacingMultiple: 1.2 });
    x += w + 0.24;
  });
  s.addText("Fidelity at 10-20mV of ambient oscillation (well below the circuit's own 70mV signal range) collapsed to 50-59% for single-snapshot voltage reads, this is a solvable engineering problem, not a fatal one, but a real, previously-unflagged design requirement.", {
    x: 0.7, y: 6.55, w: 12, h: 0.7, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, italic: true, color: MUTED,
  });
  pageNum(s, 11, false);
}

// ============================================================ Slide 9b, What we've already proven, in two languages
{
  const s = bgSlide(false);
  kicker(s, "What We Already Have", 0.7, 0.45, TEAL_DARK);
  s.addText("Four computational results, explained for a scientist and for everyone else", {
    x: 0.7, y: 0.8, w: 11.9, h: 0.7, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 22, bold: true, color: INK,
  });

  const head = [
    { text: "Finding", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
    { text: "Technical (for a scientist)", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
    { text: "Plain English (for everyone else)", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
  ];
  const rows = [
    ["Passive persistence fails",
      "24h bit integrity collapses from 100% (zero-noise) to ~50-58% under realistic channel/metabolic/thermal noise.",
      "A cell just holding a charge on its own is like a coin balanced on its edge, it falls over almost immediately."],
    ["Engineered circuit works across its whole practical design range",
      "Gardner topology + Bacillus BioBrick Box parts holds state at 100% fidelity at 24 hours for any promoter pair within the BBB's entire characterized 1.0x-10.0x strength range; only pushing far outside the catalog, to a severe 0.1x mismatch, collapses fidelity to 50%, a monostable dead switch.",
      "The circuit is a light switch held by two springs. Any pair of springs from the parts catalog, even fairly different strengths, holds the switch fine. Only deliberately grabbing two wildly mismatched springs, far outside what the catalog offers, gets the switch stuck at \"off\"."],
    ["Bacteria beats planaria on evidence, for now",
      "Cross-organism sweep: B. subtilis engineered circuit ranks highest-confidence (inheritance is mechanistically forced by cell division); planarian circuit ranks lowest (coupling strength is an unmeasured assumption).",
      "Betting on the organism with a measured mechanism is like betting on a scale you've calibrated, not one you're guessing the weight of."],
    ["A new, real risk found before it was asked about",
      "B. subtilis biofilms' native potassium-wave signaling (Prindle et al. 2015) corrupts single-snapshot voltage reads at just 10-20mV, even when the underlying circuit data is 100% intact.",
      "Circuit = Radio station = Reading the signal at the wrong moment is like tuning in during a burst of static. The message was sent correctly; you just have to listen at the right time."],
  ];
  s.addTable([head, ...rows.map(r => r.map(c => ({ text: c })))], {
    x: 0.7, y: 1.65, w: 12.0, h: 5.0,
    fontFace: BODY_FONT, fontSize: 10.5, color: INK, border: { type: "solid", color: "D8DEE1", pt: 1 },
    autoPage: false, valign: "middle", colW: [2.6, 4.9, 4.5], rowH: [0.5, 1.15, 1.15, 1.15, 1.15],
  });
  pageNum(s, 12, false);
}

// ============================================================ Slide 10, Competitive landscape
{
  const s = bgSlide(false);
  kicker(s, "Real Storage Competitors", 0.7, 0.5, TEAL_DARK);
  s.addText("Nobody else is storing arbitrary data as a dynamic, rewritable bioelectric state", {
    x: 0.7, y: 0.85, w: 11.9, h: 0.85, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 23, bold: true, color: INK,
  });

  const rows = [
    [{ text: "Player", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "What they store", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Read mechanism", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Gap vs. Acheron", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["Mycelium memristor\n(LaRocco et al. 2025)", "Analog resistance state", "Continuous signal", "90% accuracy; no addressable write layer"],
    ["BioCompute Inc. / Biomemory\n(w/ Yachie & Tomita 2007 precedent)", "DNA sequence (archival)", "Destructive sequencing", "Write-once archive, not rewritable state"],
    [{ text: "Acheron", options: { bold: true, color: TEAL_DARK } }, "Dynamic physiological/\nbioelectric state", "Non-destructive (dye or EIS)", { text: "Rewritable + self-healing, the combination nobody else has", options: { bold: true } }],
  ];
  s.addTable(rows, {
    x: 0.7, y: 1.9, w: 12.0, h: 3.55,
    fontFace: BODY_FONT, fontSize: 12, color: INK, border: { type: "solid", color: "D8DEE1", pt: 1 },
    autoPage: false, valign: "middle", rowH: [0.6, 0.95, 0.95, 0.95],
  });

  s.addShape("roundRect", { x: 0.7, y: 5.65, w: 12.0, h: 1.35, rectRadius: 0.08, fill: { color: OFFWHITE }, line: { color: "DCE3E6", width: 1.1 } });
  s.addText([
    { text: "Not included above, on purpose:  ", options: { bold: true, color: TEAL_DARK } },
    { text: "Cortical Labs, Koniku, and FinalSpark all build neuron-based wetware for cognition and sensing (playing games, detecting explosives, training AI), a different product category, not a memory-storage competitor. Their hardware is still worth studying, see next slide.", options: { color: INK } },
  ], { x: 0.95, y: 5.65, w: 11.5, h: 1.35, isTextBox: true, margin: 0, valign: "middle", fontFace: BODY_FONT, fontSize: 12.5, lineSpacingMultiple: 1.2 });
  pageNum(s, 13, false);
}

// ============================================================ Slide 11, Why We're Actually Different
{
  const s = bgSlide(false);
  kicker(s, "Differentiation & Borrowable Research", 0.7, 0.5, TEAL_DARK);
  s.addText("Only two of these are competitors. The third is research worth borrowing from anyway", {
    x: 0.7, y: 0.85, w: 11.9, h: 0.95, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 21, bold: true, color: INK,
  });

  const diffCards = [
    ["Adjacent research, not a competitor", "Cortical Labs (CL-1), Koniku",
      "Different product entirely, neuron-based cognition/sensing, not memory storage, so not a rival. Their hardware is still worth studying: CL-1 uses electrode arrays to write/read electrical signals into living tissue; Koniku holds a patent (JP6858769) for cleaner signal-to-noise electrode recording from noisy tissue, directly relevant to Acheron's own oscillation-interference problem."],
    ["Mycelium memristor", "LaRocco et al. 2025, PLOS ONE",
      "Real, and genuinely impressive, 90±1% accuracy, survives dehydration. But it's an analog device: one continuous resistance value, no addressable write layer. 90% accuracy also fails as binary storage (wrong 1 time in 10 isn't usable). Acheron targets an addressable, individually read/writable bit, not a continuous signal."],
    ["DNA-sequence storage", "BioCompute Inc. / Biomemory (Yachie & Tomita 2007 precedent)",
      "Real, funded, already storing arbitrary data in a genome, and gaining ground fast (Biomemory acquired Catalog Technologies in 2026, targeting commercial launch by year end). But it's archival: written once, read only by destroying the sample via sequencing. Acheron is solving a different problem on purpose, a dynamic, rewritable, non-destructively-readable state, not a write-once archive."],
  ];
  let x = 0.7;
  const cardW = 3.9, gap = 0.25;
  diffCards.forEach(([t, cite, body]) => {
    s.addShape("roundRect", { x, y: 2.0, w: cardW, h: 4.5, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "DCE3E6", width: 1 }, shadow: { type: "outer", color: "1B2B33", opacity: 0.12, blur: 6, offset: 3, angle: 90 } });
    s.addShape("rect", { x, y: 2.0, w: cardW, h: 0.09, fill: { color: TEAL }, line: { type: "none" } });
    s.addText(t, { x: x + 0.28, y: 2.28, w: cardW - 0.56, h: 0.65, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 15.5, bold: true, color: INK });
    s.addText(cite, { x: x + 0.28, y: 2.9, w: cardW - 0.56, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 10.5, italic: true, color: TEAL_DARK });
    s.addText(body, { x: x + 0.28, y: 3.35, w: cardW - 0.56, h: 2.95, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 11.5, color: MUTED, lineSpacingMultiple: 1.15 });
    x += cardW + gap;
  });
  pageNum(s, 14, false);
}

// ============================================================ Slide 12, Market opportunity (real cited numbers, evidence not sizing)
{
  const s = bgSlide(true);
  kicker(s, "Evidence The Need Is Real, Not A Market-Size Claim", 0.7, 0.5, TEAL);
  s.addText("We are not sizing a market yet. Here are two real, externally-verifiable numbers showing the underlying need", {
    x: 0.7, y: 0.9, w: 11.9, h: 0.9, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 22, bold: true, color: WHITE,
  });

  s.addShape("roundRect", { x: 0.7, y: 2.0, w: 5.75, h: 4.4, rectRadius: 0.08, fill: { color: NAVY2 }, line: { type: "none" } });
  s.addText("$350K / 5 yrs", { x: 1.0, y: 2.3, w: 5.2, h: 0.9, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 32, bold: true, color: TEAL });
  s.addText("What one customer already pays to avoid downtime, on a different product", { x: 1.0, y: 3.15, w: 5.2, h: 0.5, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13, bold: true, color: WHITE });
  s.addText("Cortical Labs' CL-1 (neuron-based cognition, not memory storage): $35,000/unit, replaced every 6 months, zero self-repair. Not a price for storage, a data point that this market already tolerates paying real money to avoid unplanned downtime, from a substrate that can't heal itself.", {
    x: 1.0, y: 3.7, w: 5.2, h: 2.5, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, color: "CFE0DD", lineSpacingMultiple: 1.2,
  });

  s.addShape("roundRect", { x: 6.75, y: 2.0, w: 5.9, h: 4.4, rectRadius: 0.08, fill: { color: NAVY2 }, line: { type: "none" } });
  s.addText("$1.2B–$2.0B", { x: 7.05, y: 2.3, w: 5.3, h: 0.9, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 32, bold: true, color: TEAL });
  s.addText("The whole radiation-hardened electronics market, not a memory-specific figure", { x: 7.05, y: 3.15, w: 5.3, h: 0.6, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13, bold: true, color: WHITE });
  s.addText("Growing ~4-5.6% CAGR into the early 2030s (Grand View Research, Fortune Business Insights, Research and Markets), driven by LEO satellite constellations (Starlink, Kuiper, OneWeb) needing more radiation-tolerant memory. Memory is only a slice of this figure, and we are not estimating that slice. We're citing it as evidence the demand driver is real and growing, nothing more.", {
    x: 7.05, y: 3.8, w: 5.3, h: 2.5, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12, color: "CFE0DD", lineSpacingMultiple: 1.2,
  });

  s.addText("Neither number is a forecast for Acheron. This upside is entirely conditional on the roadmap experiment below succeeding, and we haven't tried to price it in advance. We're asking for what it costs to find out.", {
    x: 0.7, y: 6.5, w: 12, h: 0.75, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, italic: true, color: "AEC2C8", lineSpacingMultiple: 1.15,
  });
  pageNum(s, 15, true);
}

// ============================================================ Slide 13, Roadmap (dark, stat callouts)
{
  const s = bgSlide(true);
  kicker(s, "Roadmap", 0.7, 0.5, TEAL);
  s.addText("The one experiment that changes everything", {
    x: 0.7, y: 0.9, w: 11.9, h: 0.85, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 28, bold: true, color: WHITE,
  });
  s.addText("Build the matched-promoter toggle circuit in B. subtilis, write a bit, damage the colony, let it regrow, read the bit back non-destructively via EIS.", {
    x: 0.7, y: 1.7, w: 11.5, h: 0.6, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 14, color: "AEC2C8",
  });

  const stats = [["$10K-$30K", "Cost, reagents, cloning, lab bench access"], ["6-12 mo", "Timeline to a clear yes/no answer"], ["2", "Outcomes only, validate the mechanism, or cleanly redirect to methylation, next by our own ranking"]];
  let x = 0.7;
  stats.forEach(([num, label]) => {
    s.addShape("roundRect", { x, y: 2.6, w: 3.9, h: 2.5, rectRadius: 0.08, fill: { color: NAVY2 }, line: { type: "none" } });
    s.addText(num, { x: x + 0.3, y: 2.85, w: 3.3, h: 1.0, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 34, bold: true, color: TEAL });
    s.addText(label, { x: x + 0.3, y: 3.75, w: 3.3, h: 1.2, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, color: "CFE0DD", lineSpacingMultiple: 1.15 });
    x += 4.1;
  });

  s.addText("Deliberately the cheapest, fastest experiment that produces a real answer, not a moonshot ask.", {
    x: 0.7, y: 5.4, w: 11.5, h: 0.5, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 14, italic: true, color: "8FA6AE",
  });
  pageNum(s, 16, true);
}

// ============================================================ Slide 13b, Biosafety & Containment
{
  const s = bgSlide(false);
  kicker(s, "Biosafety & Containment", 0.7, 0.5, TEAL_DARK);
  s.addText("Engineering bacteria to hold data raises real containment questions. We're addressing them before any wet-lab work starts", {
    x: 0.7, y: 0.85, w: 11.9, h: 0.95, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 21, bold: true, color: INK,
  });

  const cols = [
    ["Organism & containment level", "B. subtilis lab strains, including the strain 168 background used with the Bacillus BioBrick Box parts, are non-pathogenic and handled at Biosafety Level 1 (BSL-1), the lowest containment tier, standard in academic synthetic-biology teaching labs."],
    ["Kill-switch, planned, not yet built", "A release-prevention mechanism (e.g. an auxotrophic dependency or inducible kill-switch) is a design requirement we're scoping into the toggle-circuit build for the roadmap experiment, not an afterthought added later."],
    ["Regulatory path", "Wet-lab work proceeds under the partner lab's Institutional Biosafety Committee (IBC) review and the NIH Guidelines for recombinant/synthetic nucleic acid research, the standard oversight path for this kind of academic or contract lab work. Storing data confers no pathogenicity, virulence, or toxin production, there is no dual-use mechanism here."],
  ];
  let x = 0.7;
  const w = 3.9;
  cols.forEach(([t, d]) => {
    s.addShape("roundRect", { x, y: 2.05, w, h: 4.3, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "DCE3E6", width: 1 } });
    s.addShape("rect", { x, y: 2.05, w: w, h: 0.09, fill: { color: TEAL_DARK }, line: { type: "none" } });
    s.addText(t, { x: x + 0.28, y: 2.35, w: w - 0.56, h: 0.6, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 15, bold: true, color: INK });
    s.addText(d, { x: x + 0.28, y: 3.0, w: w - 0.56, h: 3.1, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12, color: MUTED, lineSpacingMultiple: 1.2 });
    x += w + 0.24;
  });
  s.addText("None of this is unusual for synthetic biology. We're naming it now so it's never a surprise later.", {
    x: 0.7, y: 6.55, w: 12, h: 0.5, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13, italic: true, color: MUTED,
  });
  pageNum(s, 17, false);
}

// ============================================================ Slide 14, What we're asking for + IP status
{
  const s = bgSlide(false);
  kicker(s, "What We're Asking For", 0.7, 0.5, TEAL_DARK);
  s.addText("Deliberately small, not a seed round", {
    x: 0.7, y: 0.85, w: 11.9, h: 0.8, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 27, bold: true, color: INK,
  });
  s.addText("We are not raising a general-purpose seed round right now. This stage needs something narrower and cheaper:", {
    x: 0.7, y: 1.65, w: 11.5, h: 0.5, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13.5, color: MUTED,
  });

  const asks = [
    ["1", "Funding for the wet-lab validation experiment", "The ~$10K-$30K described on the roadmap slide: reagents, plasmid synthesis/cloning, lab bench access."],
    ["2", "Budget to hire a paid synthetic-biology consultant", "A real expert's time to review and help execute the toggle-circuit build, not just informal mentoring hours. We'd rather pay for a few weeks of real expertise than move forward on a design nobody with domain experience has pressure-tested."],
    ["3", "Lab access & partnership introductions", "Standard bacterial transformation and plasmid cloning, B. subtilis is a workhorse organism, a far more common skill than planarian-specific culture."],
  ];
  let y = 2.3;
  asks.forEach(([num, t, d]) => {
    s.addShape("ellipse", { x: 0.7, y: y, w: 0.5, h: 0.5, fill: { color: TEAL }, line: { type: "none" } });
    s.addText(num, { x: 0.7, y: y, w: 0.5, h: 0.5, isTextBox: true, margin: 0, align: "center", valign: "middle", fontFace: HEAD_FONT, fontSize: 18, bold: true, color: WHITE });
    s.addText(t, { x: 1.45, y: y - 0.05, w: 10.8, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 16, bold: true, color: INK });
    s.addText(d, { x: 1.45, y: y + 0.4, w: 10.8, h: 0.65, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, color: MUTED, lineSpacingMultiple: 1.15 });
    y += 1.2;
  });

  s.addShape("roundRect", { x: 0.7, y: 6.05, w: 12.0, h: 0.95, rectRadius: 0.08, fill: { color: "EAF6F4" }, line: { color: TEAL_DARK, width: 1.25 } });
  s.addText([
    { text: "IP status:  ", options: { bold: true, color: TEAL_DARK } },
    { text: "patent applications filed with the USPTO covering the Bio-RAID fault-tolerance architecture, self-healing recovery protocol, and environment-adaptive longevity system.", options: { color: INK } },
  ], { x: 0.95, y: 6.05, w: 11.5, h: 0.95, isTextBox: true, margin: 0, valign: "middle", fontFace: BODY_FONT, fontSize: 12.5, lineSpacingMultiple: 1.1 });
  pageNum(s, 18, false);
}

// ============================================================ Slide 15, Team + closing
{
  const s = bgSlide(true);
  s.addShape("ellipse", { x: 10.6, y: -1.2, w: 5.5, h: 5.5, fill: { color: TEAL, transparency: 92 }, line: { type: "none" } });
  kicker(s, "Team", 0.7, 0.55, TEAL);

  s.addText("Dayana Sanchez", { x: 0.7, y: 0.9, w: 6.0, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 23, bold: true, color: WHITE });
  s.addText("Founder & Lead Researcher", { x: 0.7, y: 1.38, w: 6.0, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, color: TEAL });
  s.addText("Originated the core concept; led all technical work to date, the simulation architecture, the encoder software, and the audit process that found and corrected this project's own central assumption before anyone outside the project did.", {
    x: 0.7, y: 1.78, w: 6.0, h: 2.0, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 11.5, color: "CFE0DD", lineSpacingMultiple: 1.2,
  });

  s.addText("Jacqueline Solano", { x: 6.95, y: 0.9, w: 5.7, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 23, bold: true, color: WHITE });
  s.addText("Co-Founder, Head of Business", { x: 6.95, y: 1.38, w: 5.7, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, color: TEAL });
  s.addText("Leads business operations.", {
    x: 6.95, y: 1.78, w: 5.7, h: 1.4, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 11.5, color: "CFE0DD", lineSpacingMultiple: 1.2,
  });

  s.addShape("line", { x: 0.7, y: 4.15, w: 11.95, h: 0, line: { color: "2A4463", width: 1 } });
  s.addText("What we're looking for in a program", { x: 0.7, y: 4.35, w: 11.95, h: 0.4, isTextBox: true, margin: 0, fontFace: HEAD_FONT, fontSize: 16, bold: true, color: WHITE });
  s.addText("A team and a network that treats rigorous, honestly-reported science as a strength worth backing, not a liability to hide. That's the partner we're looking for.", {
    x: 0.7, y: 4.8, w: 11.95, h: 0.8, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13.5, italic: true, color: "AEC2C8", lineSpacingMultiple: 1.2,
  });

  s.addText([
    { text: "Dayana Sanchez: sanchezleal1989@gmail.com", options: { color: WHITE, bold: true, breakLine: true, paraSpaceAfter: 4 } },
    { text: "https://github.com/rewired89/Acheron.git", options: { color: "AEC2C8", breakLine: true, paraSpaceAfter: 4 } },
    { text: " ", options: { breakLine: true, paraSpaceAfter: 4 } },
    { text: "Jacqueline Solano: jackiea.solano@gmail.com", options: { color: WHITE, bold: true } },
  ], { x: 0.7, y: 6.0, w: 9.5, h: 1.4, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13 });
  pageNum(s, 19, true);
}

pres.writeFile({ fileName: "Acheron_Pitch_Deck.pptx" }).then(() => console.log("done"));
