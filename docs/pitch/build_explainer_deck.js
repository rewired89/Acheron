// Generator for Acheron_Plain_Explainer.pptx, a printable plain-language deck
// explaining the whole project to someone with no science background, written
// for Jacqueline. Every number in it traces to a citation or a labeled
// simulation result, same rule as the rest of docs/pitch/.
//
// The deck leads with Acheron stated as the founder states it (confirmed 21
// September 2026): one hypothesis, in four steps. Write data into an organism;
// the organism is damaged; it detects that damage itself; it regrows and carries
// the data into the new cells without losing it. The ORGANISM IS INTERCHANGEABLE,
// B. subtilis, planaria, or others later. Do not rewrite this deck as a
// B. subtilis deck, and do not present planaria as abandoned: B. subtilis is
// first because it is cheap and fast to test, which is a statement about
// evidence, not about the goal.
//
// Run with `node docs/pitch/build_explainer_deck.js`, it writes the .pptx next
// to itself. Before shipping a rebuild: run the pptx skill's
// scripts/office/validate.py against the output and read the full markitdown
// text dump end to end.
//
// Deliberately different palette from build_deck.js: this one is not an
// investor deck and should not look like one.

const pptxgen = require("pptxgenjs");
const path = require("path");

const INK = "132018";       // deep green-black, dominant on dark slides
const PAPER = "FFFFFF";
const TINT = "EDF2EE";      // pale green tint for cards
const GREEN = "1F8B5F";
const CORAL = "C8453C";
const MUTED = "5F6F66";
const PALE = "B9C7BF";      // muted text on dark slides

const HEAD = "Cambria";
const BODY = "Calibri";

const W = 13.3;
const M = 0.7;              // side margin
const COL = W - 2 * M;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Acheron";
pres.title = "Acheron, in plain language";
pres.subject = "Data that heals itself";

// --- helpers -----------------------------------------------------------------

function darkSlide() {
  const s = pres.addSlide();
  s.background = { color: INK };
  return s;
}

function lightSlide() {
  const s = pres.addSlide();
  s.background = { color: PAPER };
  return s;
}

// The one repeated motif: a small filled colony dot before a section header.
function sectionHead(s, text, y, onDark) {
  s.addShape(pres.ShapeType.ellipse, {
    x: M, y: y + 0.11, w: 0.17, h: 0.17, fill: { color: GREEN }, line: { color: GREEN },
  });
  s.addText(text, {
    x: M + 0.32, y: y, w: COL - 0.32, h: 0.42,
    fontFace: HEAD, fontSize: 23, bold: true,
    color: onDark ? PAPER : INK,
    isTextBox: true, margin: 0, valign: "middle",
  });
}

// One numbered sentence, laid out as number chip + sentence.
function sentence(s, n, label, text, y, h) {
  s.addShape(pres.ShapeType.ellipse, {
    x: M, y: y + 0.04, w: 0.44, h: 0.44,
    fill: { color: GREEN }, line: { color: GREEN },
  });
  s.addText(String(n), {
    x: M, y: y + 0.04, w: 0.44, h: 0.44,
    fontFace: HEAD, fontSize: 17, bold: true, color: PAPER,
    align: "center", valign: "middle", isTextBox: true, margin: 0,
  });
  s.addText(label.toUpperCase(), {
    x: M + 0.68, y: y, w: COL - 0.68, h: 0.24,
    fontFace: BODY, fontSize: 10.5, bold: true, color: MUTED,
    charSpacing: 1.4, isTextBox: true, margin: 0, valign: "middle",
  });
  s.addText(text, {
    x: M + 0.68, y: y + 0.26, w: COL - 0.68, h: h - 0.26,
    fontFace: BODY, fontSize: 16, color: INK,
    isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.08,
  });
}

function statCard(s, x, y, w, h, value, label, valueColor, valueSize) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.1,
    fill: { color: TINT }, line: { color: TINT },
  });
  s.addText(value, {
    x: x + 0.24, y: y + 0.22, w: w - 0.48, h: 0.78,
    fontFace: HEAD, fontSize: valueSize || 34, bold: true, color: valueColor,
    isTextBox: true, margin: 0, valign: "middle",
  });
  s.addText(label, {
    x: x + 0.24, y: y + 1.0, w: w - 0.48, h: h - 1.2,
    fontFace: BODY, fontSize: 12.5, color: MUTED,
    isTextBox: true, margin: 0, valign: "top", lineSpacingMultiple: 1.05,
  });
}

// --- 1. title ----------------------------------------------------------------
{
  const s = darkSlide();
  s.addText("Data that heals itself", {
    x: M, y: 2.25, w: 9.6, h: 1.5,
    fontFace: HEAD, fontSize: 50, bold: true, color: PAPER,
    isTextBox: true, margin: 0,
  });
  s.addText("Acheron, the whole idea in four steps", {
    x: M, y: 3.8, w: 9.6, h: 0.5,
    fontFace: BODY, fontSize: 19, color: GREEN,
    isTextBox: true, margin: 0,
  });
  s.addText("Written for Jacqueline. Nothing here needs a science background. If you only read the next slide, you already know enough to talk about it.", {
    x: M, y: 4.45, w: 8.6, h: 0.9,
    fontFace: BODY, fontSize: 13.5, color: PALE,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  });
  // three colony dots, the motif, sized down as decoration
  [0, 1, 2].forEach(function (i) {
    s.addShape(pres.ShapeType.ellipse, {
      x: 11.1 + i * 0.52, y: 2.55, w: 0.36, h: 0.36,
      fill: { color: i === 2 ? CORAL : GREEN }, line: { color: i === 2 ? CORAL : GREEN },
    });
  });
  s.addNotes("Title slide. The deck is a plain-language explainer, not an investor deck.");
}

// --- 1b. the four steps, the core of the deck --------------------------------
{
  const s = lightSlide();
  sectionHead(s, "Acheron is one idea, in four steps", 0.55, false);

  const steps = [
    ["Write", "You write data into a living thing.", "A tiny switch inside each cell. Flipped one way it is a 0, the other way a 1."],
    ["Damage", "Something damages it.", "Cut it, dry it out, blast it with radiation. Most of it dies."],
    ["Notice", "It notices the damage by itself.", "No machine watching it, nobody pressing a button. The organism senses the injury."],
    ["Regrow", "It regrows, and hands the data to the new cells.", "The survivors rebuild the whole thing, and the data is still there. Nothing is lost."],
  ];

  let y = 1.3;
  steps.forEach(function (st, i) {
    s.addShape(pres.ShapeType.ellipse, {
      x: M, y: y + 0.06, w: 0.52, h: 0.52,
      fill: { color: i === 3 ? CORAL : GREEN }, line: { color: i === 3 ? CORAL : GREEN },
    });
    s.addText(String(i + 1), {
      x: M, y: y + 0.06, w: 0.52, h: 0.52,
      fontFace: HEAD, fontSize: 20, bold: true, color: PAPER,
      align: "center", valign: "middle", isTextBox: true, margin: 0,
    });
    s.addText(st[0].toUpperCase(), {
      x: M + 0.8, y: y + 0.02, w: 1.6, h: 0.3,
      fontFace: BODY, fontSize: 10.5, bold: true, color: MUTED,
      charSpacing: 1.4, isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(st[1], {
      x: M + 0.8, y: y + 0.3, w: 6.1, h: 0.42,
      fontFace: HEAD, fontSize: 19, bold: true, color: INK,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(st[2], {
      x: M + 7.1, y: y + 0.08, w: 4.8, h: 0.75,
      fontFace: BODY, fontSize: 13, color: MUTED,
      isTextBox: true, margin: 0, valign: "middle", lineSpacingMultiple: 1.1,
    });
    y += 1.12;
  });

  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 5.95, w: 11.9, h: 0.95, rectRadius: 0.1,
    fill: { color: INK }, line: { color: INK },
  });
  s.addText("That is Acheron. A file that repairs itself, because the thing holding it is alive.", {
    x: M + 0.35, y: 6.1, w: 11.2, h: 0.65,
    fontFace: HEAD, fontSize: 18, bold: true, color: PAPER,
    isTextBox: true, margin: 0, valign: "middle",
  });
  s.addNotes("The core slide. If the reader only sees one page, this is the one.");
}

// --- 2. sentences 1 to 3 -----------------------------------------------------
{
  const s = lightSlide();
  sectionHead(s, "The same thing in nine sentences", 0.55, false);
  sentence(s, 1, "The idea",
    "Acheron is one hypothesis: write data into a living thing, and when it gets hurt, it heals and keeps the data.",
    1.35, 1.5);
  sentence(s, 2, "Writing",
    "The data goes in as a tiny switch built out of genes, sitting inside every cell, one switch for each 0 or 1.",
    3.05, 1.5);
  sentence(s, 3, "Damage",
    "Then something wrecks it and most of the cells die, which is the situation every other kind of storage simply does not survive.",
    4.75, 1.7);
  s.addNotes("Sentences 1 to 3 of nine.");
}

// --- 3. sentences 4 to 6 -----------------------------------------------------
{
  const s = lightSlide();
  sectionHead(s, "How it survives, and in what", 0.55, false);
  sentence(s, 4, "Self-detection",
    "The organism notices the injury on its own, with no machine watching it and nobody pressing a button.",
    1.35, 1.5);
  sentence(s, 5, "Regrowth",
    "It rebuilds itself from the survivors, and every new cell is handed the same switch position, so the data comes through intact.",
    3.05, 1.5);
  sentence(s, 6, "Which creature",
    "The creature is interchangeable, and germs are being tested first only because they are cheap and fast, while flatworms came first because they already regrow a whole body from one piece.",
    4.75, 1.7);
  s.addNotes("Sentences 4 to 6 of nine.");
}

// --- 4. sentences 7 to 9 -----------------------------------------------------
{
  const s = lightSlide();
  sectionHead(s, "What is proven, and where the money comes from", 0.55, false);
  sentence(s, 7, "Proved in simulation",
    "On the computer it works, with the data coming back perfectly from as few as 2 cells out of 100 surviving.",
    1.35, 1.5);
  sentence(s, 8, "Still unproven",
    "In a real laboratory nobody has ever tested it, in any organism, and that first test costs roughly $2,000 to $5,000.",
    3.05, 1.5);
  sentence(s, 9, "The money, honestly",
    "The money comes from research grants first, up to about $305,000 from one US government programme, and not from selling anything, because nothing in this field sells yet.",
    4.75, 1.7);
  s.addNotes("Sentences 7 to 9 of nine.");
}

// --- 5. the switch -----------------------------------------------------------
{
  const s = lightSlide();
  sectionHead(s, "The whole alphabet is two colours", 0.55, false);
  s.addText("Inside each cell sits a tiny switch built out of genes: two genes that each tell the other to be quiet. Whichever one is winning keeps winning, so the switch stays where you leave it. One position makes the cell glow green, the other makes it glow red.", {
    x: M, y: 1.25, w: 6.6, h: 1.9,
    fontFace: BODY, fontSize: 16, color: INK,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  });
  s.addText("Reading it does not kill anything, so the same dish can be read again and again.", {
    x: M, y: 3.3, w: 6.6, h: 1.0,
    fontFace: BODY, fontSize: 16, italic: true, color: MUTED,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  });

  const pairs = [
    { c: GREEN, v: "0", x: 8.2 },
    { c: CORAL, v: "1", x: 10.7 },
  ];
  pairs.forEach(function (p) {
    s.addShape(pres.ShapeType.ellipse, {
      x: p.x, y: 1.55, w: 1.9, h: 1.9,
      fill: { color: p.c }, line: { color: p.c },
    });
    s.addText(p.v, {
      x: p.x, y: 1.55, w: 1.9, h: 1.9,
      fontFace: HEAD, fontSize: 60, bold: true, color: PAPER,
      align: "center", valign: "middle", isTextBox: true, margin: 0,
    });
    s.addText(p.v === "0" ? "glows green" : "glows red", {
      x: p.x, y: 3.6, w: 1.9, h: 0.35,
      fontFace: BODY, fontSize: 12.5, color: MUTED,
      align: "center", isTextBox: true, margin: 0,
    });
  });
  s.addNotes("The switch and its readout. Colour is the answer.");
}

// --- 6. why division matters -------------------------------------------------
{
  const s = lightSlide();
  sectionHead(s, "Why splitting in half is the whole trick", 0.55, false);
  s.addText("When a cell divides, both halves keep the switch in the same position. So the data copies itself, for free, every time the organism grows. Nobody has to back it up.", {
    x: M, y: 1.25, w: 11.9, h: 0.95,
    fontFace: BODY, fontSize: 16, color: INK,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  });

  const rows = [
    { count: 1, note: "the damage happens, one cell lives" },
    { count: 2, note: "it splits, and both halves agree" },
    { count: 4, note: "an hour later" },
    { count: 8, note: "and on, until the data is whole again" },
  ];
  let y = 2.55;
  rows.forEach(function (row, ri) {
    const count = row.count;
    s.addText(ri === 0 ? "1 survivor" : count + " cells", {
      x: M, y: y - 0.02, w: 1.5, h: 0.4,
      fontFace: BODY, fontSize: 13, bold: ri === 0, color: ri === 0 ? CORAL : MUTED,
      isTextBox: true, margin: 0, valign: "middle",
    });
    for (let i = 0; i < count; i++) {
      s.addShape(pres.ShapeType.ellipse, {
        x: 2.35 + i * 0.46, y: y, w: 0.34, h: 0.34,
        fill: { color: GREEN }, line: { color: GREEN },
      });
    }
    s.addText(row.note, {
      x: 6.4, y: y - 0.02, w: 6.2, h: 0.4,
      fontFace: BODY, fontSize: 12.5, italic: true, color: MUTED,
      isTextBox: true, margin: 0, valign: "middle",
    });
    y += 0.78;
  });
  s.addNotes("Regrowth from survivors. The dots are illustrative, not to scale.");
}

// --- 7. the 2 percent result -------------------------------------------------
{
  const s = darkSlide();
  sectionHead(s, "The result the whole project rests on", 0.55, true);
  s.addText("100%", {
    x: M, y: 1.5, w: 4.6, h: 1.7,
    fontFace: HEAD, fontSize: 92, bold: true, color: GREEN,
    isTextBox: true, margin: 0, valign: "middle",
  });
  s.addText("of the message came back, from as few as 2 germs in every 100 surviving", {
    x: M, y: 3.15, w: 5.4, h: 1.0,
    fontFace: BODY, fontSize: 16, color: PAPER,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  });
  s.addText("The glowing colour was right too, not just the genes underneath it. Tested at every survival level from 2 percent up to no damage at all.", {
    x: M, y: 4.3, w: 5.4, h: 1.1,
    fontFace: BODY, fontSize: 13.5, color: PALE,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  });

  s.addShape(pres.ShapeType.roundRect, {
    x: 7.0, y: 1.5, w: 5.6, h: 3.9, rectRadius: 0.1,
    fill: { color: "1E2E24" }, line: { color: CORAL },
  });
  s.addText("Read this part twice", {
    x: 7.3, y: 1.75, w: 5.0, h: 0.4,
    fontFace: BODY, fontSize: 11, bold: true, color: CORAL,
    charSpacing: 1.4, isTextBox: true, margin: 0,
  });
  s.addText("This happened in a computer simulation, not in a laboratory. No living germ has ever been tested this way, by anyone.\n\n2 percent is simply the lowest amount the test tried. Everything from 2 percent upward worked perfectly, so the real breaking point is somewhere below 2 percent and nobody has found it.\n\nThe honest sentence is \"it survived every level we tested, down to 2 percent.\"", {
    x: 7.3, y: 2.2, w: 5.0, h: 3.0,
    fontFace: BODY, fontSize: 13, color: PAPER,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.12,
  });
  s.addNotes("Source: simulations/bsubtilis_07_colony_regrowth.py and bsubtilis_13_reporter_colony_regrowth.py, re-run 21 September 2026.");
}

// --- 8. why the organism is interchangeable ---------------------------------
{
  const s = lightSlide();
  sectionHead(s, "Why it does not matter which creature", 0.55, false);
  s.addText("Acheron is the idea, not the animal. Any living thing that regrows from a piece of itself could carry it, and the plan is to test more than one over time.", {
    x: M, y: 1.25, w: 11.9, h: 0.75,
    fontFace: BODY, fontSize: 15.5, color: INK,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  });

  const two = [
    ["Flatworms came first", "Cut one into pieces and every piece grows back into a whole worm, carrying its body plan with it. That is exactly the behaviour Acheron wants, already working in nature."],
    ["Germs are being tested first", "Not because they are better. Because they are cheap, fast and easy to rewire. A germ splits every half hour, so a test takes days instead of months."],
  ];
  two.forEach(function (t, i) {
    const x = M + i * 6.05;
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 2.15, w: 5.85, h: 1.95, rectRadius: 0.1,
      fill: { color: TINT }, line: { color: TINT },
    });
    s.addShape(pres.ShapeType.ellipse, {
      x: x + 0.3, y: 2.48, w: 0.16, h: 0.16,
      fill: { color: GREEN }, line: { color: GREEN },
    });
    s.addText(t[0], {
      x: x + 0.6, y: 2.38, w: 5.0, h: 0.38,
      fontFace: HEAD, fontSize: 16.5, bold: true, color: INK,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(t[1], {
      x: x + 0.6, y: 2.84, w: 5.0, h: 1.05,
      fontFace: BODY, fontSize: 13, color: MUTED,
      isTextBox: true, margin: 0, lineSpacingMultiple: 1.1,
    });
  });

  s.addText("Michael Levin", {
    x: M, y: 4.35, w: 11.9, h: 0.35,
    fontFace: BODY, fontSize: 11, bold: true, color: GREEN,
    charSpacing: 1.4, isTextBox: true, margin: 0,
  });
  s.addText("Dayana picked flatworms on her own reasoning, before she had heard of him, and found his lab afterwards. His lab at Tufts showed that a flatworm's body plan is partly stored as electricity across its cells: interfere with that electricity and the worm regrows with two heads, and keeps regrowing two-headed with no further interference. The instructions changed, not the genes.", {
    x: M, y: 4.72, w: 11.9, h: 1.1,
    fontFace: BODY, fontSize: 13.5, color: INK,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.12,
  });
  s.addText("What that proves is that a worm's own natural pattern really is stored this way and really does survive being cut apart. What it does not prove is that a made-up pattern, a file Dayana invents, behaves the same way. That gap is the whole experiment.", {
    x: M, y: 5.9, w: 11.9, h: 0.9,
    fontFace: BODY, fontSize: 13.5, italic: true, color: MUTED,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.12,
  });
  s.addNotes("Organism-agnostic framing, per the founder's own statement of the goal, 21 September 2026. Levin detail per docs/SCIENTIFIC_AUDIT_2026.md Parts 3 and 4.");
}

// --- 9. where it could be used ----------------------------------------------
{
  const s = lightSlide();
  sectionHead(s, "Where it could be used, if it works", 0.55, false);
  s.addText("Places people would plausibly want this. None of them is a customer, a deal, or a promise.", {
    x: M, y: 1.2, w: 11.9, h: 0.4,
    fontFace: BODY, fontSize: 14, italic: true, color: MUTED,
    isTextBox: true, margin: 0,
  });

  const uses = [
    ["Long-term archives", "Things meant to last centuries, where every storage format we have today dies first."],
    ["Space", "Radiation destroys electronics. A colony that regrows from survivors behaves differently."],
    ["Labelling living material", "Seeds, cultures and samples that carry their own identity and keep it as they grow."],
    ["Anti-counterfeiting", "A mark that is very hard to copy, because copying it means copying life."],
  ];
  uses.forEach(function (u, i) {
    const x = i % 2 === 0 ? M : M + 6.05;
    const y = i < 2 ? 1.85 : 4.0;
    s.addShape(pres.ShapeType.roundRect, {
      x, y, w: 5.85, h: 1.85, rectRadius: 0.1,
      fill: { color: TINT }, line: { color: TINT },
    });
    s.addShape(pres.ShapeType.ellipse, {
      x: x + 0.3, y: y + 0.32, w: 0.16, h: 0.16,
      fill: { color: GREEN }, line: { color: GREEN },
    });
    s.addText(u[0], {
      x: x + 0.6, y: y + 0.22, w: 5.0, h: 0.38,
      fontFace: HEAD, fontSize: 17, bold: true, color: INK,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(u[1], {
      x: x + 0.6, y: y + 0.68, w: 5.0, h: 0.95,
      fontFace: BODY, fontSize: 13.5, color: MUTED,
      isTextBox: true, margin: 0, lineSpacingMultiple: 1.1,
    });
  });
  s.addNotes("Illustrative application areas. No customer relationship exists.");
}

// --- 10. the money -----------------------------------------------------------
{
  const s = lightSlide();
  sectionHead(s, "How much this can actually make", 0.55, false);
  s.addText("Four real figures. None of them invented, all of them checkable.", {
    x: M, y: 1.2, w: 11.9, h: 0.4,
    fontFace: BODY, fontSize: 14, italic: true, color: MUTED,
    isTextBox: true, margin: 0,
  });

  const cards = [
    ["$305,000", "The most one US government grant gives for a first phase, over 6 to 18 months. Up to $1.25M more after that. This money does not cost you part of the company.", GREEN],
    ["$37,700", "Total raised so far by BioCompute, a company doing almost the same thing with bacteria. This is what this stage really looks like.", INK],
    ["$35 million", "Raised in one round by Catalog, a DNA storage company with real machines. Roughly the ceiling of this field, after years of work.", INK, 28],
    ["$0", "Sales in this field today, a decade after the first demonstrations. Anyone who quotes you revenue is selling you something.", CORAL],
  ];
  cards.forEach(function (c, i) {
    statCard(s, M + i * 3.05, 1.8, 2.85, 2.45, c[0], c[1], c[2], c[3]);
  });

  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 4.55, w: 11.9, h: 1.55, rectRadius: 0.1,
    fill: { color: INK }, line: { color: INK },
  });
  s.addText("The number to hold in your head", {
    x: M + 0.35, y: 4.75, w: 11.2, h: 0.35,
    fontFace: BODY, fontSize: 11, bold: true, color: GREEN,
    charSpacing: 1.4, isTextBox: true, margin: 0,
  });
  s.addText("Over the next two to three years, a good outcome is $300,000 to $2 million, almost all of it from grants, and nothing from sales. Millions in revenue is not on the table until the lab test comes back positive and somebody builds a real device.", {
    x: M + 0.35, y: 5.12, w: 11.2, h: 0.85,
    fontFace: BODY, fontSize: 14, color: PAPER,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.12,
  });
  s.addNotes("NSF SBIR figures from seedfund.nsf.gov. BioCompute total from Inc42. Catalog Series B from its own 2021 announcement.");
}

// --- 11. what to watch ------------------------------------------------------
{
  const s = darkSlide();
  sectionHead(s, "What to watch, on your side", 0.55, true);
  const items = [
    ["The first lab test", "Roughly $2,000 to $5,000. A planning estimate, not a quote from a lab yet."],
    ["Patent fees", "Ongoing, and the main real expense so far."],
    ["One deadline question", "Whether an early paper was ever posted publicly. That sets how long is left to file patents in some countries."],
  ];
  let y = 1.45;
  items.forEach(function (it) {
    s.addShape(pres.ShapeType.ellipse, {
      x: M, y: y + 0.12, w: 0.16, h: 0.16,
      fill: { color: GREEN }, line: { color: GREEN },
    });
    s.addText(it[0], {
      x: M + 0.35, y: y, w: 3.6, h: 0.4,
      fontFace: HEAD, fontSize: 16, bold: true, color: PAPER,
      isTextBox: true, margin: 0, valign: "middle",
    });
    s.addText(it[1], {
      x: M + 4.1, y: y, w: 7.8, h: 0.8,
      fontFace: BODY, fontSize: 14, color: PALE,
      isTextBox: true, margin: 0, lineSpacingMultiple: 1.1,
    });
    y += 1.05;
  });

  s.addText("And the part nobody likes saying out loud: most research companies at this stage never reach that ceiling. The whole point of being careful is that if it fails, it fails cheaply and early, on a $3,000 test instead of a $3,000,000 one.", {
    x: M, y: 4.85, w: 11.9, h: 1.0,
    fontFace: BODY, fontSize: 14, italic: true, color: PAPER,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  });
  s.addText("She is trying to store a file inside something alive, because living things copy and repair themselves and our machines do not. The one test that decides whether it is real has not been run yet.", {
    x: M, y: 6.1, w: 11.9, h: 0.9,
    fontFace: HEAD, fontSize: 15, color: GREEN,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.12,
  });
  s.addNotes("Closing slide.");
}

pres.writeFile({ fileName: path.join(__dirname, "Acheron_Plain_Explainer.pptx") })
  .then(function (f) { console.log("wrote " + f); });
