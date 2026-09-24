// Converts a prep markdown file in this folder into a printable US Letter .docx.
// Generic: it handles headings, paragraphs, blockquotes, bullet and numbered
// lists, horizontal rules and inline **bold**, which is everything the prep docs
// use. Run it as `node build_prep_docx.js <input.md> <output.docx>`, needs the
// `docx` npm package, which is not committed.
//
// Used for docs/pitch/YESDELFT_Intake_Prep.docx. Edit the markdown and rerun,
// do not hand-edit the .docx. LibreOffice PDF conversion fails on any input in
// this sandbox, so visual QA is not available, check with the docx skill's
// scripts/office/validate.py and a read of the extracted text instead.

const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  BorderStyle, LevelFormat, convertInchesToTwip, PageOrientation,
} = require("docx");

const SRC = process.argv[2];
const OUT = process.argv[3];

const INK = "1A1A1A", MUTED = "555555", ACCENT = "0B3C5D", RULE = "BBBBBB";
const BODY = "Calibri", HEAD = "Cambria";

// ---- split markdown into blocks -------------------------------------------
const raw = fs.readFileSync(SRC, "utf8").split(/\r?\n/);
const blocks = [];
let i = 0;
while (i < raw.length) {
  const line = raw[i];
  if (!line.trim()) { i++; continue; }
  if (/^#{1,6}\s/.test(line)) {
    blocks.push({ t: "h", level: line.match(/^#+/)[0].length, text: line.replace(/^#+\s*/, "") });
    i++; continue;
  }
  if (/^---+$/.test(line.trim())) { blocks.push({ t: "hr" }); i++; continue; }
  if (/^>\s?/.test(line)) {
    const buf = [];
    while (i < raw.length && /^>\s?/.test(raw[i])) { buf.push(raw[i].replace(/^>\s?/, "")); i++; }
    blocks.push({ t: "quote", text: buf.join(" ").replace(/\s+/g, " ").trim() });
    continue;
  }
  if (/^\d+\.\s/.test(line)) {
    const buf = [line.replace(/^\d+\.\s*/, "")];
    i++;
    while (i < raw.length && raw[i].trim() && !/^\d+\.\s/.test(raw[i]) && !/^[-*]\s/.test(raw[i]) && !/^#{1,6}\s/.test(raw[i]) && !/^>/.test(raw[i])) { buf.push(raw[i].trim()); i++; }
    blocks.push({ t: "ol", text: buf.join(" ").replace(/\s+/g, " ").trim() });
    continue;
  }
  if (/^[-*]\s/.test(line)) {
    const buf = [line.replace(/^[-*]\s*/, "")];
    i++;
    while (i < raw.length && raw[i].trim() && !/^[-*]\s/.test(raw[i]) && !/^\d+\.\s/.test(raw[i]) && !/^#{1,6}\s/.test(raw[i]) && !/^>/.test(raw[i])) { buf.push(raw[i].trim()); i++; }
    blocks.push({ t: "ul", text: buf.join(" ").replace(/\s+/g, " ").trim() });
    continue;
  }
  const buf = [line.trim()];
  i++;
  while (i < raw.length && raw[i].trim() && !/^#{1,6}\s/.test(raw[i]) && !/^>/.test(raw[i]) && !/^[-*]\s/.test(raw[i]) && !/^\d+\.\s/.test(raw[i]) && !/^---+$/.test(raw[i].trim())) { buf.push(raw[i].trim()); i++; }
  blocks.push({ t: "p", text: buf.join(" ").replace(/\s+/g, " ").trim() });
}

// ---- inline **bold** ------------------------------------------------------
function runs(text, opts) {
  const o = opts || {};
  const out = [];
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  parts.forEach(function (p) {
    if (!p) return;
    const b = /^\*\*([\s\S]+)\*\*$/.exec(p);
    out.push(new TextRun({
      text: b ? b[1] : p,
      bold: b ? true : !!o.bold,
      italics: !!o.italics,
      font: o.font || BODY,
      size: o.size || 22,
      color: o.color || INK,
    }));
  });
  return out.length ? out : [new TextRun({ text: "", font: BODY, size: 22 })];
}

const children = [];

blocks.forEach(function (b) {
  if (b.t === "h" && b.level === 1) {
    children.push(new Paragraph({
      children: runs(b.text, { font: HEAD, size: 40, bold: true, color: ACCENT }),
      spacing: { after: 80 },
    }));
    children.push(new Paragraph({
      children: [new TextRun({ text: "Acheron, founder briefing. Not for distribution.", font: BODY, size: 18, color: MUTED, italics: true })],
      spacing: { after: 320 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE, space: 8 } },
    }));
    return;
  }
  if (b.t === "h") {
    children.push(new Paragraph({
      children: runs(b.text, { font: HEAD, size: b.level === 2 ? 28 : 24, bold: true, color: ACCENT }),
      heading: b.level === 2 ? HeadingLevel.HEADING_1 : HeadingLevel.HEADING_2,
      spacing: { before: 360, after: 140 },
      keepNext: true,
    }));
    return;
  }
  if (b.t === "hr") {
    children.push(new Paragraph({
      children: [new TextRun({ text: "", size: 2 })],
      spacing: { before: 200, after: 200 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: RULE, space: 6 } },
    }));
    return;
  }
  if (b.t === "quote") {
    children.push(new Paragraph({
      children: runs(b.text, { italics: true, size: 22, color: "24343F" }),
      indent: { left: convertInchesToTwip(0.35) },
      spacing: { before: 100, after: 160, line: 300 },
      border: { left: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 10 } },
    }));
    return;
  }
  if (b.t === "ul" || b.t === "ol") {
    children.push(new Paragraph({
      children: runs(b.text),
      numbering: { reference: b.t === "ul" ? "acheron-bullets" : "acheron-numbers", level: 0 },
      spacing: { after: 100, line: 280 },
    }));
    return;
  }
  children.push(new Paragraph({
    children: runs(b.text),
    spacing: { after: 160, line: 290 },
  }));
});

const doc = new Document({
  numbering: {
    config: [
      { reference: "acheron-bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: convertInchesToTwip(0.3), hanging: convertInchesToTwip(0.2) } } } }] },
      { reference: "acheron-numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: convertInchesToTwip(0.35), hanging: convertInchesToTwip(0.25) } } } }] },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840, orientation: PageOrientation.PORTRAIT },
        margin: { top: convertInchesToTwip(0.85), bottom: convertInchesToTwip(0.85), left: convertInchesToTwip(0.9), right: convertInchesToTwip(0.9) },
      },
    },
    children: children,
  }],
});

Packer.toBuffer(doc).then(function (buf) {
  fs.writeFileSync(OUT, buf);
  console.log("wrote " + OUT + " (" + blocks.length + " blocks)");
});
