// Generator for Acheron_Hardware_Concept.pptx, a short standalone deck showing
// the cartridge-and-reader product concept on its own, separate from the full
// investor deck. Palette, fonts and helpers deliberately match build_deck.js so
// the two read as one family. Requires pptxgenjs. Run with
// `node build_hardware_deck.js`, it writes the .pptx to the current working
// directory, copy that over this folder's existing file.
//
// Before shipping a rebuild: run the pptx skill's scripts/office/validate.py
// against the output and read the full markitdown text dump end to end.
// LibreOffice PDF conversion, and therefore visual/pixel QA, is unreliable in
// this environment.
//
// EVERY CLAIM ON THESE SLIDES TRACES TO A SIMULATION RESULT OR A CITATION.
// Nothing here has been built. Keep the "Not built" framing on slide 6 intact.
const pptxgen = require("pptxgenjs");

const NAVY = "0B1F3A", NAVY2 = "132A4D", WHITE = "FFFFFF", OFFWHITE = "F4F6F7";
const INK = "16232F", MUTED = "5B6B77";
const TEAL = "2EC4B6", TEAL_DARK = "1C8F84", AMBER = "E8A33D", CORAL = "E8604C";
const SLATE = "6E7F91", PALE = "AEC2C8", MIST = "CFE0DD";

const HEAD_FONT = "Cambria", BODY_FONT = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
const PW = 13.33, PH = 7.5;

function bgSlide(dark) {
  const s = pres.addSlide();
  s.background = { color: dark ? NAVY : OFFWHITE };
  return s;
}
function pageNum(s, n, dark) {
  s.addText(String(n).padStart(2, "0"), {
    x: PW - 0.9, y: PH - 0.5, w: 0.6, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 10, color: dark ? SLATE : "9AA7AF", align: "right",
  });
}
function kicker(s, text, x, y, color) {
  s.addText(text.toUpperCase(), {
    x, y, w: 8, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 12, bold: true, color, charSpacing: 2,
  });
}

// ============================================================ 1, Title
{
  const s = bgSlide(true);
  s.addShape("ellipse", { x: 10.4, y: -1.4, w: 5.8, h: 5.8, fill: { color: TEAL, transparency: 90 }, line: { type: "none" } });
  s.addShape("ellipse", { x: 11.6, y: 3.9, w: 3.4, h: 3.4, fill: { color: TEAL, transparency: 88 }, line: { type: "none" } });
  s.addShape("ellipse", { x: -1.6, y: 4.6, w: 4.2, h: 4.2, fill: { color: TEAL, transparency: 92 }, line: { type: "none" } });

  kicker(s, "Hardware Concept, September 2026", 0.9, 1.05, TEAL);
  s.addText("What Acheron\nWould Look Like", {
    x: 0.85, y: 1.5, w: 10, h: 2.0, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 52, bold: true, color: WHITE, lineSpacingMultiple: 1.05,
  });
  s.addText("A sealed cartridge of living cells, and a reader that writes to them and reads them back.", {
    x: 0.9, y: 3.75, w: 9.4, h: 0.7, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 20, color: MIST,
  });
  s.addText("A concept sketch of the product the research points toward. No prototype exists.", {
    x: 0.9, y: 4.55, w: 9.4, h: 0.5, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 14, italic: true, color: "8FA6AE",
  });
  s.addText([
    { text: "Acheron", options: { color: WHITE, bold: true } },
    { text: "   Self-Healing Bioelectric Memory", options: { color: "8FA6AE" } },
  ], { x: 0.9, y: 6.3, w: 9, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 13 });
  pageNum(s, 1, true);
}

// ============================================================ 2, The two objects
{
  const s = bgSlide(false);
  kicker(s, "The Product", 0.7, 0.5, TEAL_DARK);
  s.addText("Two objects: a sealed, disposable cartridge and a reusable reader", {
    x: 0.7, y: 0.88, w: 11.9, h: 0.75, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 26, bold: true, color: INK,
  });
  s.addText("Illustrative, not an engineering drawing. Every labeled part traces to a simulation result or a published citation.", {
    x: 0.7, y: 1.58, w: 11.9, h: 0.4, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 11.5, italic: true, color: MUTED,
  });

  // ---- Cartridge panel ----
  s.addShape("roundRect", { x: 0.7, y: 2.15, w: 5.9, h: 4.5, rectRadius: 0.1, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("CARTRIDGE, sealed and bio-safe", {
    x: 1.0, y: 2.35, w: 5.3, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, bold: true, fontSize: 12, color: TEAL, charSpacing: 1,
  });

  const wells = [
    ["Resting", "dried spores, no power needed", SLATE],
    ["Reads 1", "colony glows green", TEAL],
    ["Reads 0", "colony glows red", CORAL],
  ];
  let wx = 1.0;
  const ww = 1.75;
  wells.forEach(function (row) {
    const t = row[0], d = row[1], c = row[2];
    s.addShape("roundRect", { x: wx, y: 2.85, w: ww, h: 1.68, rectRadius: 0.06, fill: { color: NAVY2 }, line: { color: "2A4463", width: 1 } });
    s.addShape("ellipse", { x: wx + ww / 2 - 0.32, y: 3.04, w: 0.64, h: 0.64, fill: { color: c, transparency: c === SLATE ? 60 : 25 }, line: { color: c, width: 1.5 } });
    s.addText(t, { x: wx + 0.08, y: 3.8, w: ww - 0.16, h: 0.3, isTextBox: true, margin: 0, align: "center", fontFace: BODY_FONT, bold: true, fontSize: 10.5, color: WHITE });
    s.addText(d, { x: wx + 0.08, y: 4.08, w: ww - 0.16, h: 0.45, isTextBox: true, margin: 0, align: "center", fontFace: BODY_FONT, fontSize: 8.5, color: PALE, lineSpacingMultiple: 1.1 });
    wx += ww + 0.15;
  });
  s.addText("Repeats to fill the array. An illustrative 64 wells would hold 64 bits.", {
    x: 1.0, y: 4.64, w: 5.3, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 9.5, italic: true, color: SLATE,
  });
  s.addShape("line", { x: 1.0, y: 5.12, w: 5.3, h: 0, line: { color: AMBER, width: 2 } });
  s.addText("Shared channel, carries nutrient and the write chemical to every well", {
    x: 1.0, y: 5.22, w: 5.3, h: 0.3, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 9.5, color: AMBER,
  });
  s.addText("No cable on the cartridge itself. It is a consumable, closer to a lab test strip than a memory chip.", {
    x: 1.0, y: 5.68, w: 5.3, h: 0.75, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 10.5, color: MIST, lineSpacingMultiple: 1.2,
  });

  // ---- Reader panel ----
  s.addShape("roundRect", { x: 6.85, y: 2.15, w: 5.78, h: 4.5, rectRadius: 0.1, fill: { color: WHITE }, line: { color: "DCE3E6", width: 1 } });
  s.addText("READER, reusable instrument", {
    x: 7.15, y: 2.35, w: 5.2, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, bold: true, fontSize: 12, color: TEAL_DARK, charSpacing: 1,
  });

  s.addShape("roundRect", { x: 8.35, y: 2.88, w: 2.0, h: 0.5, rectRadius: 0.06, fill: { color: OFFWHITE }, line: { color: "B9C3C7", width: 1 } });
  s.addText("cartridge slot", { x: 8.35, y: 2.88, w: 2.0, h: 0.5, isTextBox: true, margin: 0, align: "center", valign: "middle", fontFace: BODY_FONT, fontSize: 9, color: MUTED });

  s.addShape("roundRect", { x: 8.55, y: 3.58, w: 1.6, h: 0.95, rectRadius: 0.08, fill: { color: OFFWHITE }, line: { color: "B9C3C7", width: 1 } });
  s.addShape("ellipse", { x: 9.15, y: 3.76, w: 0.4, h: 0.4, fill: { color: TEAL, transparency: 30 }, line: { color: TEAL_DARK, width: 1.5 } });
  s.addText("fluorescence\nread head", { x: 8.4, y: 4.58, w: 1.9, h: 0.55, isTextBox: true, margin: 0, align: "center", fontFace: BODY_FONT, fontSize: 8.5, color: MUTED, lineSpacingMultiple: 1.1 });

  s.addShape("roundRect", { x: 7.15, y: 3.58, w: 1.15, h: 0.95, rectRadius: 0.08, fill: { color: OFFWHITE }, line: { color: "B9C3C7", width: 1 } });
  s.addText("nutrient and\nwrite reservoir", { x: 7.0, y: 4.58, w: 1.45, h: 0.6, isTextBox: true, margin: 0, align: "center", fontFace: BODY_FONT, fontSize: 8.5, color: MUTED, lineSpacingMultiple: 1.1 });

  s.addShape("roundRect", { x: 10.35, y: 3.58, w: 1.15, h: 0.95, rectRadius: 0.08, fill: { color: OFFWHITE }, line: { color: "B9C3C7", width: 1 } });
  s.addText("control board", { x: 10.2, y: 4.58, w: 1.45, h: 0.4, isTextBox: true, margin: 0, align: "center", fontFace: BODY_FONT, fontSize: 8.5, color: MUTED });
  s.addShape("line", { x: 11.5, y: 4.03, w: 0.45, h: 0, line: { color: INK, width: 2.5 } });
  s.addText("USB-C to a laptop", { x: 10.5, y: 5.18, w: 2.0, h: 0.3, isTextBox: true, margin: 0, align: "center", fontFace: BODY_FONT, fontSize: 9, bold: true, color: INK });

  s.addText("The reader is the only part with a cable. The cartridge never plugs into anything directly.", {
    x: 7.15, y: 5.68, w: 5.2, h: 0.75, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 10.5, color: MUTED, lineSpacingMultiple: 1.2,
  });
  pageNum(s, 2, false);
}

// ============================================================ 3, Cartridge detail
{
  const s = bgSlide(true);
  kicker(s, "The Cartridge", 0.7, 0.5, TEAL);
  s.addText("A consumable, not a chip", {
    x: 0.7, y: 0.88, w: 11.9, h: 0.75, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 30, bold: true, color: WHITE,
  });
  s.addText("Why the storage medium is disposable, sealed, and needs no power while it sits on a shelf.",
    { x: 0.7, y: 1.6, w: 11.5, h: 0.45, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 14, color: PALE });

  const rows = [
    ["Dormant at rest", TEAL,
     "The cells sit as dried spores. No power, no cooling, no maintenance. Spores are how this organism already survives hard conditions in nature."],
    ["Sealed, single organism", TEAL,
     "One well-characterised laboratory bacterium, held behind a physical barrier. Nothing goes in and nothing comes out during normal use."],
    ["Self-healing by design", AMBER,
     "If most of a well's colony is killed, the survivors regrow it and the stored bit comes back with them. In simulation this holds from as few as 2 percent of cells surviving."],
    ["Read by colour", CORAL,
     "Each well glows green for a 1 and red for a 0. Reading is taking a picture, so the cartridge is not consumed by being read."],
  ];
  let ry = 2.2;
  rows.forEach(function (row) {
    const title = row[0], accent = row[1], body = row[2];
    s.addShape("roundRect", { x: 0.7, y: ry, w: 11.93, h: 1.0, rectRadius: 0.08, fill: { color: NAVY2 }, line: { type: "none" } });
    s.addShape("ellipse", { x: 1.05, y: ry + 0.33, w: 0.34, h: 0.34, fill: { color: accent, transparency: 25 }, line: { color: accent, width: 1.5 } });
    s.addText(title, { x: 1.62, y: ry + 0.17, w: 3.3, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY_FONT, bold: true, fontSize: 14, color: WHITE });
    s.addText(body, { x: 4.95, y: ry + 0.15, w: 7.4, h: 0.72, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 11.5, color: PALE, lineSpacingMultiple: 1.18 });
    ry += 1.13;
  });

  s.addText("The 2 percent survival figure is a simulation result, not a measurement. See the project's scientific audit.", {
    x: 0.7, y: 6.85, w: 11.9, h: 0.4, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 10.5, italic: true, color: SLATE,
  });
  pageNum(s, 3, true);
}

// ============================================================ 4, Reader detail
{
  const s = bgSlide(false);
  kicker(s, "The Reader", 0.7, 0.5, TEAL_DARK);
  s.addText("Ordinary instrument parts, doing an ordinary job", {
    x: 0.7, y: 0.88, w: 11.9, h: 0.75, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 30, bold: true, color: INK,
  });
  s.addText("Nothing in the reader is exotic. The novelty is entirely in the cartridge. That is deliberate, because it keeps the engineering risk in one place.",
    { x: 0.7, y: 1.6, w: 11.6, h: 0.45, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 14, color: MUTED });

  const parts = [
    ["Fluorescence\nread head", "Shines light at the wells and photographs what glows back. The same idea as a plate reader already found in any biology lab.", TEAL_DARK],
    ["Nutrient and\nwrite reservoir", "Feeds the wells to wake them, and delivers a timed chemical pulse to set each bit.", AMBER],
    ["Control board\nand USB-C", "Runs the sequence, converts the image into bits, and hands them to a laptop.", INK],
  ];
  let px = 0.7;
  parts.forEach(function (row) {
    const title = row[0], body = row[1], accent = row[2];
    s.addShape("roundRect", { x: px, y: 2.25, w: 3.85, h: 3.15, rectRadius: 0.1, fill: { color: WHITE }, line: { color: "DCE3E6", width: 1 } });
    s.addShape("ellipse", { x: px + 0.35, y: 2.6, w: 0.48, h: 0.48, fill: { color: accent, transparency: 80 }, line: { color: accent, width: 2 } });
    s.addText(title, { x: px + 0.35, y: 3.25, w: 3.15, h: 0.75, isTextBox: true, margin: 0, fontFace: BODY_FONT, bold: true, fontSize: 15, color: INK, lineSpacingMultiple: 1.1 });
    s.addText(body, { x: px + 0.35, y: 4.05, w: 3.15, h: 1.2, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 11.5, color: MUTED, lineSpacingMultiple: 1.2 });
    px += 4.04;
  });

  s.addShape("roundRect", { x: 0.7, y: 5.65, w: 11.93, h: 1.05, rectRadius: 0.08, fill: { color: "E9F2F1" }, line: { type: "none" } });
  s.addText([
    { text: "Why this matters commercially:  ", options: { bold: true, color: TEAL_DARK } },
    { text: "the reader is built from parts that already exist and are already understood. If the biology in the cartridge works, the instrument around it is a known engineering problem, not a research one.", options: { color: INK } },
  ], { x: 1.05, y: 5.87, w: 11.2, h: 0.65, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, lineSpacingMultiple: 1.2 });
  pageNum(s, 4, false);
}

// ============================================================ 5, One full cycle
{
  const s = bgSlide(true);
  kicker(s, "How It Would Work", 0.7, 0.5, TEAL);
  s.addText("One full cycle, start to finish", {
    x: 0.7, y: 0.88, w: 11.9, h: 0.7, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 30, bold: true, color: WHITE,
  });

  const steps = [
    ["Load", "The cartridge slides into the reader. Until this moment it has been sitting dry on a shelf, using nothing.", TEAL],
    ["Wake", "Nutrient flows through the shared channel. The spores germinate into living colonies, one per well.", TEAL],
    ["Write", "A timed chemical pulse flips each well's genetic switch to a 1 or a 0. The pulse then washes out.", AMBER],
    ["Hold", "The switch holds its own state with no power and no refresh cycle. This is what makes it memory rather than a sensor.", AMBER],
    ["Read", "The read head photographs the array. Green is a 1, red is a 0. Nothing is destroyed, so it can be read again.", CORAL],
    ["Heal", "If a well is damaged, the surviving cells divide and rebuild the colony, carrying the stored bit into the new cells.", CORAL],
  ];
  let sx = 0.7, sy = 1.95, i = 0;
  steps.forEach(function (row) {
    const title = row[0], body = row[1], accent = row[2];
    const col = i % 3, rowN = Math.floor(i / 3);
    sx = 0.7 + col * 4.04;
    sy = 1.95 + rowN * 2.45;
    s.addShape("roundRect", { x: sx, y: sy, w: 3.85, h: 2.2, rectRadius: 0.1, fill: { color: NAVY2 }, line: { type: "none" } });
    s.addShape("ellipse", { x: sx + 0.32, y: sy + 0.28, w: 0.52, h: 0.52, fill: { color: accent, transparency: 75 }, line: { color: accent, width: 2 } });
    s.addText(String(i + 1), { x: sx + 0.32, y: sy + 0.28, w: 0.52, h: 0.52, isTextBox: true, margin: 0, align: "center", valign: "middle", fontFace: BODY_FONT, bold: true, fontSize: 14, color: WHITE });
    s.addText(title, { x: sx + 1.0, y: sy + 0.35, w: 2.6, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY_FONT, bold: true, fontSize: 16, color: WHITE });
    s.addText(body, { x: sx + 0.32, y: sy + 0.98, w: 3.2, h: 1.08, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 11, color: PALE, lineSpacingMultiple: 1.18 });
    i += 1;
  });

  s.addText("Steps 3 through 6 are what the funded laboratory work is designed to test, in that order, cheapest first.", {
    x: 0.7, y: 6.95, w: 11.9, h: 0.4, isTextBox: true, margin: 0,
    fontFace: BODY_FONT, fontSize: 11.5, italic: true, color: SLATE,
  });
  pageNum(s, 5, true);
}

// ============================================================ 6, What is real
{
  const s = bgSlide(false);
  kicker(s, "Being Straight About It", 0.7, 0.5, CORAL);
  s.addText("What is real today, and what is not", {
    x: 0.7, y: 0.88, w: 11.9, h: 0.75, isTextBox: true, margin: 0,
    fontFace: HEAD_FONT, fontSize: 30, bold: true, color: INK,
  });
  s.addText("If someone asks about this design, this is the honest answer to give them.",
    { x: 0.7, y: 1.6, w: 11.6, h: 0.4, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 14, color: MUTED });

  s.addShape("roundRect", { x: 0.7, y: 2.2, w: 5.9, h: 3.55, rectRadius: 0.1, fill: { color: WHITE }, line: { color: "DCE3E6", width: 1 } });
  s.addText("GROUNDED IN REAL WORK", { x: 1.05, y: 2.45, w: 5.2, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY_FONT, bold: true, fontSize: 12, color: TEAL_DARK, charSpacing: 1 });
  s.addText([
    { text: "The genetic switch is a real, published circuit built from real, off-the-shelf bacterial parts.", options: { bullet: true, breakLine: true } },
    { text: "The colour readout is the one our own testing favours, because it avoids an interference problem the electrical readout has.", options: { bullet: true, breakLine: true } },
    { text: "Storing a bit through damage and regrowth holds in simulation from as few as 2 percent of cells surviving.", options: { bullet: true, breakLine: true } },
    { text: "Spores of this organism have survived two years of direct exposure outside the International Space Station (Deshevaya et al. 2024).", options: { bullet: true } },
  ], { x: 1.05, y: 2.9, w: 5.2, h: 2.7, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 11.5, color: INK, lineSpacingMultiple: 1.15, paraSpaceAfter: 8 });

  s.addShape("roundRect", { x: 6.85, y: 2.2, w: 5.78, h: 3.55, rectRadius: 0.1, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("NOT BUILT, AND WE SAY SO", { x: 7.2, y: 2.45, w: 5.1, h: 0.35, isTextBox: true, margin: 0, fontFace: BODY_FONT, bold: true, fontSize: 12, color: AMBER, charSpacing: 1 });
  s.addText([
    { text: "No prototype of either object exists. This is a concept sketch, not an engineering drawing.", options: { bullet: true, breakLine: true } },
    { text: "Every result behind it is simulation. Nothing has been measured in living cells yet.", options: { bullet: true, breakLine: true } },
    { text: "The array size, the physical dimensions and the timings are all illustrative.", options: { bullet: true, breakLine: true } },
    { text: "Other groups have written a state into living bacteria and read it back. What nobody has shown is that state surviving cell division, which is the part we are chasing.", options: { bullet: true } },
  ], { x: 7.2, y: 2.9, w: 5.1, h: 2.7, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 11.5, color: MIST, lineSpacingMultiple: 1.15, paraSpaceAfter: 8 });

  s.addShape("roundRect", { x: 0.7, y: 6.0, w: 11.93, h: 0.95, rectRadius: 0.08, fill: { color: "FBF0DC" }, line: { type: "none" } });
  s.addText([
    { text: "The one sentence to lead with:  ", options: { bold: true, color: "8A5D14" } },
    { text: "this is the product the first laboratory experiment is designed to de-risk, and that experiment is the cheapest one on our roadmap.", options: { color: INK } },
  ], { x: 1.05, y: 6.24, w: 11.2, h: 0.55, isTextBox: true, margin: 0, fontFace: BODY_FONT, fontSize: 12.5, lineSpacingMultiple: 1.2 });
  pageNum(s, 6, false);
}

pres.writeFile({ fileName: "Acheron_Hardware_Concept.pptx" }).then(function () {
  console.log("wrote Acheron_Hardware_Concept.pptx");
});
