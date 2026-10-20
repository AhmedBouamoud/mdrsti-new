#!/usr/bin/env node
// مولّد ملف Word «أكتب في دفتري» لدرس من «رحلة الأولى باك»: يجمع فقرات الدفتر حرفيًا وبالترتيب.
// الاستعمال: node scripts/build_docx.cjs <content.json> <out.docx> [logo.png]
const fs = require("fs");
const path = require("path");
let docx;
try { docx = require("docx"); } catch (e) { docx = require("/opt/node22/lib/node_modules/docx"); }
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  BorderStyle, ShadingType, ImageRun, Footer, Header, PageNumber, HeadingLevel } = docx;

const [src, out, logo] = process.argv.slice(2);
const d = JSON.parse(fs.readFileSync(src, "utf8"));
const m = d.meta;
const NAVY = "0B2242", GOLD = "C9A24A", FONT = "Sakkal Majalla";
const SZ = 32; // 16pt

const run = (t, o = {}) => new TextRun({ text: t, rightToLeft: true, font: { name: FONT, cs: FONT }, size: o.size || SZ, sizeComplexScript: o.size || SZ, bold: !!o.bold, boldComplexScript: !!o.bold, color: o.color });
// قاعدة RTL (وورد على الهاتف): Word يقرأ jc في الفقرة العربية كـ«بداية/نهاية»: jc="left" = بداية = اليمين. بلا jc تظهر العناوين والنقاط يسارًا. الوسط فقط للأسطر المتوسّطة.
const para = (children, o = {}) => new Paragraph({ bidirectional: true, alignment: o.align === AlignmentType.CENTER ? AlignmentType.CENTER : AlignmentType.LEFT, spacing: { after: o.after ?? 120, line: 360 }, children: Array.isArray(children) ? children : [children], ...(o.extra || {}) });

const border = { style: BorderStyle.SINGLE, size: 6, color: "8A9AAE" };
const borders = { top: border, bottom: border, left: border, right: border, insideHorizontal: border, insideVertical: border };

function table(t) {
  const n = t.head.length;
  const total = 9638; // عرض A4 بهوامش 2 سم (DXA)
  const ratios = n === 3 ? [0.22, 0.26, 0.52] : n === 2 ? [0.26, 0.74] : Array(n).fill(1 / n);
  const widths = ratios.map(r => Math.round(total * r));
  const cell = (txt, i, head, shade) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA },
    shading: head ? { type: ShadingType.CLEAR, color: "auto", fill: NAVY } : (shade ? { type: ShadingType.CLEAR, color: "auto", fill: "F6EED8" } : undefined),
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
    children: [para(run(txt, { bold: head || i === 0, color: head ? "FFFFFF" : (i === 0 ? NAVY : undefined), size: 30 }), { align: head ? AlignmentType.CENTER : undefined, after: 0 })],
  });
  return new Table({
    visuallyRightToLeft: true,
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    borders,
    rows: [new TableRow({ tableHeader: true, children: t.head.map((h, i) => cell(h, i, true)) }),
      ...t.rows.map((r, k) => new TableRow({ children: r.map((c, i) => cell(c, i, false, k % 2 === 1)) }))],
  });
}

function blocks(nb) {
  const outp = [];
  for (const b of nb.blocks) {
    if (b.h) outp.push(para(run(b.h, { bold: true, color: NAVY, size: 36 }), { after: 100 }));
    else if (b.p) outp.push(para(run(b.p)));
    else if (b.ul) b.ul.forEach(x => outp.push(para([run("• ", { bold: true, color: GOLD }), run(x)], { after: 80 })));
    else if (b.table) { outp.push(table(b.table)); outp.push(para(run(""), { after: 80 })); }
  }
  return outp;
}

const body = [];
// الرأس
const headCells = [];
if (logo && fs.existsSync(logo)) {
  body.push(new Paragraph({ bidirectional: true, alignment: AlignmentType.CENTER, children: [new ImageRun({ type: "png", data: fs.readFileSync(logo), transformation: { width: 70, height: 70 } })] }));
}
body.push(para(run("الأستاذ أحمد بوعمود — أستاذ التاريخ والجغرافيا", { bold: true, color: NAVY, size: 28 }), { align: AlignmentType.CENTER, after: 40 }));
body.push(para(run(`مادة ${m.subject} | المستوى: ${m.level} | الموسم الدراسي 2026-2027`, { size: 26, color: "555555" }), { align: AlignmentType.CENTER, after: 200 }));
body.push(new Paragraph({ bidirectional: true, alignment: AlignmentType.CENTER, spacing: { after: 120 },
  border: { top: { style: BorderStyle.SINGLE, size: 12, color: GOLD, space: 6 }, bottom: { style: BorderStyle.SINGLE, size: 12, color: GOLD, space: 6 } },
  children: [run(m.title, { bold: true, color: NAVY, size: 40 })] }));
body.push(para(run("✍️ أكتب في دفتري — ملخص الدرس", { bold: true, color: GOLD, size: 30 }), { align: AlignmentType.CENTER, after: 240 }));

const parts = [];
if (d.notebook_intro) parts.push(d.notebook_intro);
for (const s of d.sections) if (s.notebook) parts.push(s.notebook);
if (d.notebook_conclusion) parts.push(d.notebook_conclusion);
for (const nb of parts) body.push(...blocks(nb));

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: SZ, rightToLeft: true }, paragraph: { bidirectional: true, alignment: AlignmentType.LEFT } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1000, bottom: 1000, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [para([run("ذ. أحمد بوعمود — مؤسسة الحنان الخاصة | 2026-2027", { size: 22, color: "777777" })], { align: AlignmentType.CENTER, after: 0 })] }) },
    children: body,
  }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(out, b); console.log("✅", out); });
