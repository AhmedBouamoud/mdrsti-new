#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مولّد صفحات الدروس الثابتة لـ«رحلة الأولى باك».
يقرأ ملفات المحتوى المنظّمة من content/ ويولّد صفحات HTML كاملة في lessons/.
المبدأ (الميثاق، بند 9 و10): المحتوى منفصل عن الواجهة، والنص الأساسي مُدمج في
HTML النهائي فيعمل بلا JavaScript وبلا اعتماد على Notion/Drive وقت التصفح.
"""
import json, html, os, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(ROOT, "content")
OUT_DIR = os.path.join(ROOT, "lessons")

CREST = ('<svg class="crest" viewBox="0 0 100 100" role="img" aria-label="شعار مؤسسة الحنان">'
         '<rect x="6" y="6" width="88" height="88" rx="20" fill="#12294a" stroke="#e0a53a" stroke-width="4"/>'
         '<rect x="30" y="46" width="40" height="30" fill="#fff"/>'
         '<path d="M26 46l24-16 24 16z" fill="#e0a53a"/>'
         '<rect x="46" y="58" width="8" height="18" fill="#12294a"/>'
         '<rect x="34" y="52" width="7" height="7" fill="#2b6cb0"/>'
         '<rect x="59" y="52" width="7" height="7" fill="#2b6cb0"/></svg>')

def e(s):
    return html.escape(str(s), quote=True)

def render_note(kind, label, text, icon):
    return (f'<div class="note {kind}"><div class="ic">{icon}</div>'
            f'<div class="bd"><b>{e(label)}</b><p>{e(text)}</p></div></div>')

def render_table(sec):
    head = "".join(f"<th>{e(h)}</th>" for h in sec["head"])
    rows = ""
    for r in sec["rows"]:
        cells = f"<th>{e(r[0])}</th>" + "".join(f"<td>{e(c)}</td>" for c in r[1:])
        rows += f"<tr>{cells}</tr>"
    out = f'<div class="banner">{e(sec["title"])}</div>'
    if sec.get("lead"):
        out += f'<p class="lead">{e(sec["lead"])}</p>'
    out += (f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')
    if sec.get("note"):
        n = sec["note"]
        out += render_note(n.get("type", "method"), n["label"], n["text"], "🧭")
    return out

def render_cards(sec):
    out = f'<div class="banner">{e(sec["title"])}</div><div class="cards">'
    for c in sec["cards"]:
        emoji = f'<span class="e">{c["emoji"]}</span> ' if c.get("emoji") else ""
        out += (f'<div class="card c-{e(c["color"])}"><div class="cap">{emoji}{e(c["cap"])}</div>'
                f'<div class="bd">{e(c["body"])}</div></div>')
    return out + "</div>"

def render_questions(sec):
    items = "".join(f"<li>{e(q)}</li>" for q in sec["items"])
    return f'<div class="banner">{e(sec["title"])}</div><ul class="questions">{items}</ul>'

RENDERERS = {"table": render_table, "cards": render_cards, "questions": render_questions}

def build_lesson(data):
    m = data["meta"]
    body = [render_note("intro", "مقدمة", data["intro"], "📘"),
            render_note("problem", "الإشكالية المركزية", data["problematic"], "❓")]
    for sec in data["sections"]:
        body.append(RENDERERS[sec["kind"]](sec))
    body.append(render_note("conclusion", "خاتمة", data["conclusion"], "✍️"))
    page = f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(m["title"])} | رحلة الأولى باك</title>
<meta name="description" content="{e(m["title"])} — {e(m["subject"])} · {e(m["level"])}. درس كامل ضمن رحلة الأولى باك.">
<link rel="stylesheet" href="../assets/css/lesson.css">
</head>
<body data-lesson="{e(m["id"])}">
<nav class="topbar">
  <a class="back" href="../index.html">→ عودة إلى الدروس</a>
  <span>رحلة الأولى باك · {e(m["subject"])} · {e(m["lessonTag"])}</span>
  <button class="print-btn" type="button" onclick="window.print()">🖨️ طباعة / PDF</button>
</nav>
<div class="sheet-wrap"><article class="sheet">
  <header class="doc-head">
    <div class="brand">{CREST}<div class="brand-txt">
      <span class="inst">مؤسسة الحنان للتعليم الخاص</span>
      <span class="sub">مادة التاريخ والجغرافيا</span>
    </div></div>
    <div class="season">الموسم الدراسي<br>2025 / 2026</div>
  </header>
  <div class="title-band">
    <span class="lvl">مادة {e(m["subject"])} <span>|</span> المستوى: {e(m["level"])}</span>
    <h1>{e(m["title"])}</h1>
    <span class="lesson-tag">{e(m["lessonTag"])}</span>
  </div>
  {"".join(body)}
  <div class="doc-foot">
    <span>إعداد: الأستاذ أحمد بوعمود — أستاذ الاجتماعيات</span>
    <span>مؤسسة الحنان · ahmedbouamoud.com</span>
  </div>
</article></div>
</body>
</html>'''
    return page

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(CONTENT_DIR, "**", "*.json"), recursive=True))
    if not files:
        print("لا توجد ملفات محتوى في", CONTENT_DIR); return 1
    count = 0
    for f in files:
        data = json.load(open(f, encoding="utf-8"))
        m = data["meta"]
        out = os.path.join(OUT_DIR, f'{m["slug"]}.html')
        open(out, "w", encoding="utf-8").write(build_lesson(data))
        print(f'✅ {m["number"]:>2}. {m["title"][:45]}  →  lessons/{m["slug"]}.html  [{m["status"]}]')
        count += 1
    print(f"\nتم توليد {count} درس/دروس.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
