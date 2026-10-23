// Generator for Acheron_Selection_Day_Deck.pptx, the 6-slide deck for a 3 minute
// Selection Day talk. Requires `npm install pptxgenjs` (run from a scratch
// directory). Run with `node build_selection_deck.js`, it writes the .pptx to the
// current working directory, copy it over docs/pitch/. The speaker notes on each
// slide are the script, mirrored in docs/ACHERON_SELECTION_DAY.docx, keep both in
// step. Every claim is a simulation result, a citation, or labelled unknown.
const pptxgen = require("pptxgenjs");

const NAVY = "0B1F3A", NAVY2 = "132A4D", WHITE = "FFFFFF", OFFWHITE = "F4F6F7";
const INK = "16232F", MUTED = "5B6B77", TEAL = "2EC4B6", TEAL_DARK = "1C8F84";
const AMBER = "E8A33D", CORAL = "E8604C", PALE = "C9D6E2";
const HEAD = "Cambria", BODY = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "Acheron, Selection Day";
pres.author = "Dayana Sanchez";
const PW = 13.33, PH = 7.5;

function bg(dark) { const s = pres.addSlide(); s.background = { color: dark ? NAVY : OFFWHITE }; return s; }
function num(s, n, dark) {
  s.addText(String(n).padStart(2, "0"), { x: PW - 0.9, y: PH - 0.5, w: 0.6, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10, color: dark ? "6E7F91" : "9AA7AF", align: "right" });
}
function kicker(s, t, color) {
  s.addText(t.toUpperCase(), { x: 0.7, y: 0.45, w: 8, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12, bold: true, color, charSpacing: 2 });
}
function title(s, t, color) {
  s.addText(t, { x: 0.7, y: 0.8, w: 11.9, h: 0.85, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 36, bold: true, color });
}
function caption(s, t, color) {
  s.addText(t, { x: 0.7, y: 6.85, w: 11.5, h: 0.4, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, italic: true, color });
}

// ---- 1. Title and the four steps
{
  const s = bg(true);
  s.addShape("ellipse", { x: 10.6, y: -1.2, w: 5.5, h: 5.5, fill: { color: TEAL, transparency: 90 }, line: { type: "none" } });
  s.addShape("ellipse", { x: -1.5, y: 4.8, w: 4, h: 4, fill: { color: TEAL, transparency: 92 }, line: { type: "none" } });
  kicker(s, "YES!Delft Selection Day", TEAL);
  s.addText("Acheron", { x: 0.7, y: 1.1, w: 11, h: 1.3, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 66, bold: true, color: WHITE });
  s.addText("Memory that survives damage", { x: 0.7, y: 2.4, w: 11, h: 0.7, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 26, color: PALE });
  const steps = [["1", "Write", "a 0 or 1 into living cells"], ["2", "Damage", "kill most of them"], ["3", "Notice", "the organism senses it"], ["4", "Regrow", "and the bit is still there"]];
  let x = 0.7;
  steps.forEach(function (st) {
    s.addShape("roundRect", { x, y: 3.75, w: 2.85, h: 1.9, rectRadius: 0.1, fill: { color: NAVY2 }, line: { color: TEAL, width: 1 } });
    s.addShape("ellipse", { x: x + 0.25, y: 3.98, w: 0.5, h: 0.5, fill: { color: TEAL }, line: { type: "none" } });
    s.addText(st[0], { x: x + 0.25, y: 3.98, w: 0.5, h: 0.5, isTextBox: true, margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 16, bold: true, color: NAVY });
    s.addText(st[1], { x: x + 0.25, y: 4.6, w: 2.4, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 24, bold: true, color: WHITE });
    s.addText(st[2], { x: x + 0.25, y: 5.1, w: 2.4, h: 0.5, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, color: PALE });
    x += 3.08;
  });
  s.addText("Simulation-backed. Not yet tested at a bench.", { x: 0.7, y: 6.1, w: 11, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 16, bold: true, color: AMBER });
  s.addText("Dayana Sanchez and Jacqueline Solano", { x: 0.7, y: 6.7, w: 8, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12, color: "8EA0B3" });
  s.addNotes("Hi, I'm Dayana, with my co-founder Jacqueline. Acheron asks one question: can you write a bit of data into living cells, damage them badly, and have the bit come back when they regrow? Write, damage, the organism notices, it regrows. Nobody has tested that whole loop. We have simulated it, and we want help testing it.");
  num(s, 1, true);
}

// ---- 2. How a bit lives in a cell
{
  const s = bg(false);
  kicker(s, "The mechanism", TEAL_DARK);
  title(s, "How a bit lives in a bacterium", INK);
  // left: toggle diagram card
  s.addShape("roundRect", { x: 0.7, y: 1.9, w: 6.3, h: 4.7, rectRadius: 0.1, fill: { color: WHITE }, line: { color: "DCE3E6", width: 1 } });
  s.addText("Genetic toggle switch", { x: 1.0, y: 2.05, w: 5.7, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, bold: true, color: MUTED });
  s.addShape("roundRect", { x: 1.0, y: 2.8, w: 2.3, h: 1.1, rectRadius: 0.1, fill: { color: TEAL_DARK }, line: { type: "none" } });
  s.addText("Gene A", { x: 1.0, y: 2.8, w: 2.3, h: 1.1, isTextBox: true, margin: 0, align: "center", valign: "middle", fontFace: HEAD, fontSize: 22, bold: true, color: WHITE });
  s.addShape("roundRect", { x: 4.7, y: 2.8, w: 2.0, h: 1.1, rectRadius: 0.1, fill: { color: AMBER }, line: { type: "none" } });
  s.addText("Gene B", { x: 4.7, y: 2.8, w: 2.0, h: 1.1, isTextBox: true, margin: 0, align: "center", valign: "middle", fontFace: HEAD, fontSize: 22, bold: true, color: INK });
  s.addShape("line", { x: 3.3, y: 3.1, w: 1.4, h: 0, line: { color: CORAL, width: 3, endArrowType: "triangle" } });
  s.addShape("line", { x: 4.7, y: 3.6, w: -1.4, h: 0, line: { color: CORAL, width: 3, endArrowType: "triangle" } });
  s.addText("each mutes the other", { x: 2.9, y: 3.95, w: 2.2, h: 0.35, isTextBox: true, margin: 0, align: "center", fontFace: BODY, fontSize: 12, italic: true, color: CORAL });
  s.addShape("roundRect", { x: 1.0, y: 4.65, w: 2.7, h: 0.9, rectRadius: 0.08, fill: { color: "E3F3F1" }, line: { type: "none" } });
  s.addText("A wins = 0", { x: 1.0, y: 4.65, w: 2.7, h: 0.9, isTextBox: true, margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 18, bold: true, color: TEAL_DARK });
  s.addShape("roundRect", { x: 4.0, y: 4.65, w: 2.7, h: 0.9, rectRadius: 0.08, fill: { color: "FBEFD9" }, line: { type: "none" } });
  s.addText("B wins = 1", { x: 4.0, y: 4.65, w: 2.7, h: 0.9, isTextBox: true, margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 18, bold: true, color: "9A6414" });
  s.addText("Rests in one of two stable states, like a light switch, not a dimmer.", { x: 1.0, y: 5.75, w: 5.7, h: 0.6, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, color: MUTED });
  // right: three points
  const pts = [
    ["Division copies the state", "The proteins that hold the state pass into both daughter cells, so it is copied into the regrowth."],
    ["Read by colour", "Two fluorescent reporters, one per state, read one cell at a time by flow cytometry."],
    ["One design rule", "The two promoters must be matched in strength, or the switch collapses to a single setting."],
  ];
  let y = 1.9;
  pts.forEach(function (p, i) {
    s.addShape("ellipse", { x: 7.4, y: y + 0.05, w: 0.5, h: 0.5, fill: { color: TEAL_DARK }, line: { type: "none" } });
    s.addText(String(i + 1), { x: 7.4, y: y + 0.05, w: 0.5, h: 0.5, isTextBox: true, margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 16, bold: true, color: WHITE });
    s.addText(p[0], { x: 8.1, y: y, w: 4.5, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 18, bold: true, color: INK });
    s.addText(p[1], { x: 8.1, y: y + 0.45, w: 4.5, h: 1.0, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, color: MUTED });
    y += 1.6;
  });
  caption(s, "Organism: Bacillus subtilis. Toggle design: Gardner, Cantor and Collins 2000.", MUTED);
  s.addNotes("We use B. subtilis, a harmless, well-studied soil bacterium. We wire two genes so each one's protein shuts off the other: a genetic toggle switch, first built by Gardner and Collins in 2000. It rests in one of two states, like a light switch. A winning is a 0, B winning is a 1. When a cell divides, those proteins pass into both daughters, so the state is copied into the regrowth. We read it by colour. One rule from our model: the two promoters must be matched in strength, or the switch collapses to one setting.");
  num(s, 2, false);
}

// ---- 3. What the simulations say
{
  const s = bg(true);
  kicker(s, "What the simulations say", TEAL);
  title(s, "Three results, all simulated", WHITE);
  const cards = [
    ["50%", CORAL, "Our first idea failed", "A voltage held passively in flatworm tissue fell to a coin flip once we added realistic noise. We retired it."],
    ["2%", TEAL, "Survivors still regrow the bit", "From 2% of a colony, 98 to 100% of the regrown colony kept the bit, at 25 to 200 molecules per cell, if the survivors hold the right bit."],
    ["3", AMBER, "Kinds of math checked it", "They agree on the promoter rule and disagree on how much noise the switch can take. That depends on measurements we do not have."],
  ];
  let x = 0.7;
  cards.forEach(function (c) {
    s.addShape("roundRect", { x, y: 2.0, w: 3.85, h: 4.5, rectRadius: 0.1, fill: { color: NAVY2 }, line: { type: "none" } });
    s.addText(c[0], { x: x + 0.3, y: 2.2, w: 3.3, h: 1.3, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 66, bold: true, color: c[1] });
    s.addText(c[2], { x: x + 0.3, y: 3.65, w: 3.3, h: 0.8, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 20, bold: true, color: WHITE });
    s.addText(c[3], { x: x + 0.3, y: 4.5, w: 3.3, h: 1.9, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, color: PALE });
    x += 4.04;
  });
  caption(s, "Python models of published equations (Gardner 2000, Huh and Paulsson 2011, BBB 2.0 promoter strengths). Noise sizes are assumed. No cell has been tested.", "8EA0B3");
  s.addNotes("Our simulations are Python models of published equations. First, our own first idea, a voltage held in flatworm tissue, fell to a coin flip once we added realistic noise, so we retired it. Second, when only two percent of a colony survives, the regrown colony still holds the bit, as long as the survivors hold the right one. Third, three kinds of math agree on the promoter rule and disagree on how much noise the switch can take, so that needs real measurements. All of this is simulation.");
  num(s, 3, true);
}

// ---- 4. Where Acheron sits
{
  const s = bg(false);
  kicker(s, "Prior work", TEAL_DARK);
  title(s, "We are not first, and we say so", INK);
  const cols = [
    ["Gardner 2000", "Nature", "Built the toggle switch in E. coli. Proved genetic memory of this kind works.", TEAL_DARK],
    ["Yang 2020", "Cell Systems, Suel lab", "Wrote voltage patterns into B. subtilis with light. Their memory is lost when cells divide.", AMBER],
    ["Bonnet 2012", "PNAS, Endy lab", "Rewritable DNA memory in living cells that lasts over 100 divisions.", CORAL],
  ];
  let x = 0.7;
  cols.forEach(function (c) {
    s.addShape("roundRect", { x, y: 1.95, w: 3.85, h: 2.9, rectRadius: 0.1, fill: { color: WHITE }, line: { color: "DCE3E6", width: 1 } });
    s.addShape("ellipse", { x: x + 0.3, y: 2.2, w: 0.45, h: 0.45, fill: { color: c[3], transparency: 20 }, line: { color: c[3], width: 2 } });
    s.addText(c[0], { x: x + 0.3, y: 2.8, w: 3.3, h: 0.45, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 22, bold: true, color: INK });
    s.addText(c[1], { x: x + 0.3, y: 3.25, w: 3.3, h: 0.3, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 12, color: MUTED });
    s.addText(c[2], { x: x + 0.3, y: 3.6, w: 3.3, h: 1.2, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, color: INK });
    x += 4.04;
  });
  s.addShape("roundRect", { x: 0.7, y: 5.1, w: 11.93, h: 1.5, rectRadius: 0.1, fill: { color: "E3F3F1" }, line: { type: "none" } });
  s.addText("What we are testing: the whole loop", { x: 1.0, y: 5.2, w: 11.3, h: 0.45, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 18, bold: true, color: TEAL_DARK });
  s.addText("Write, damage, the organism notices and reinforces its own state, regrows, and keeps the bit. We claim no advantage over a DNA latch yet. That is what the experiments are for.", { x: 1.0, y: 5.7, w: 11.3, h: 0.85, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 15, color: INK });
  s.addNotes("We are not first. Gardner proved genetic memory works. Yang's lab wrote voltage patterns into this bacterium in 2020, but their memory fades when cells divide. Bonnet's lab built rewritable DNA memory that survives over a hundred divisions. We claim no advantage over a DNA latch yet. We are testing the whole loop: damage, self-detection, regrowth.");
  num(s, 4, false);
}

// ---- 5. The first test
{
  const s = bg(true);
  kicker(s, "The first test", TEAL);
  title(s, "Small, staged, each step a go or no-go", WHITE);
  const gates = [
    ["Pilot P0", "Can this experiment run at all? Build one matched switch. Measure how fast it settles.", TEAL],
    ["Stage 1a", "Does it switch? A real switch remembers its history. A mismatched control should not.", TEAL],
    ["Stage 1b", "Does it hold? 72 hour run, growth race against plain cells, spore check.", AMBER],
    ["Experiment 3", "Damage and regrowth. The real test of the idea.", CORAL],
  ];
  let x = 0.7;
  gates.forEach(function (g, i) {
    s.addShape("roundRect", { x, y: 1.95, w: 2.85, h: 2.7, rectRadius: 0.1, fill: { color: NAVY2 }, line: { color: g[2], width: 1.5 } });
    s.addText(g[0], { x: x + 0.25, y: 2.15, w: 2.4, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 22, bold: true, color: g[2] });
    s.addText(g[1], { x: x + 0.25, y: 2.75, w: 2.4, h: 1.8, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, color: PALE });
    if (i < 3) s.addShape("line", { x: x + 2.85, y: 3.3, w: 0.23, h: 0, line: { color: PALE, width: 2, endArrowType: "triangle" } });
    x += 3.08;
  });
  const facts = [
    ["Read", "Flow cytometry, single cells, two colours"],
    ["Pass rule", "Written before any data is seen"],
    ["Cost", "Planning estimate $2K to $5K, now a floor. No lab has quoted it."],
  ];
  let fx = 0.7;
  facts.forEach(function (f) {
    s.addText([{ text: f[0] + "  ", options: { bold: true, color: TEAL } }, { text: f[1], options: { color: PALE } }],
      { x: fx, y: 5.0, w: 3.85, h: 1.2, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, valign: "top" });
    fx += 4.04;
  });
  caption(s, "Fail early and cheaply. If P0 or 1a fails, we stop before the expensive stages.", "8EA0B3");
  s.addNotes("The first test is small and staged. A pilot: can the experiment run at all. Then Stage 1a: a matched switch and a deliberately mismatched control. A real switch remembers its history, the control should not. We read single cells by flow cytometry, with pass rules fixed before the data. If it fails, we stop having spent little. If it passes, damage and regrowth is next.");
  num(s, 5, true);
}

// ---- 6. The ask
{
  const s = bg(false);
  kicker(s, "What we need", TEAL_DARK);
  title(s, "Help running the test that replaces our simulations", INK);
  const asks = [
    ["A lab partner", "to run the pilot and Stage 1a. We cannot run it ourselves."],
    ["A synthetic biologist", "to review our protocol and tell us where it is naive."],
    ["Grant help", "with the first grant. This is too early for investors, and we know it."],
  ];
  let x = 0.7;
  asks.forEach(function (a, i) {
    s.addShape("roundRect", { x, y: 2.2, w: 3.85, h: 2.5, rectRadius: 0.1, fill: { color: WHITE }, line: { color: "DCE3E6", width: 1 } });
    s.addShape("ellipse", { x: x + 0.3, y: 2.45, w: 0.55, h: 0.55, fill: { color: TEAL_DARK }, line: { type: "none" } });
    s.addText(String(i + 1), { x: x + 0.3, y: 2.45, w: 0.55, h: 0.55, isTextBox: true, margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 18, bold: true, color: WHITE });
    s.addText(a[0], { x: x + 0.3, y: 3.2, w: 3.3, h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 22, bold: true, color: INK });
    s.addText(a[1], { x: x + 0.3, y: 3.75, w: 3.3, h: 0.9, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, color: MUTED });
    x += 4.04;
  });
  s.addShape("roundRect", { x: 0.7, y: 5.1, w: 11.93, h: 1.4, rectRadius: 0.1, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("Do not trust our simulations. Help us run the test that replaces them.", { x: 1.0, y: 5.1, w: 11.3, h: 1.4, isTextBox: true, margin: 0, valign: "middle", fontFace: HEAD, fontSize: 24, bold: true, color: WHITE });
  s.addNotes("We need a partner lab to run the first experiment, a synthetic biologist to review our protocol, and help with the first grant. We don't ask you to trust our simulations. We ask for help running the test that replaces them. Thank you.");
  num(s, 6, false);
}

pres.writeFile({ fileName: "Acheron_Selection_Day_Deck.pptx" }).then(function (f) { console.log("wrote " + f); });
