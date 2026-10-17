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

CREST = '<img class="crest" src="../assets/img/ab-icon.png" alt="شعار الأستاذ أحمد بوعمود" width="160" height="160">'

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
    out = f'<div class="banner">{e(sec["title"])}</div>'
    if sec.get("lead"):
        out += f'<p class="lead">{e(sec["lead"])}</p>'
    out += '<div class="cards">'
    for c in sec["cards"]:
        emoji = f'<span class="e">{c["emoji"]}</span> ' if c.get("emoji") else ""
        if c.get("bullets"):
            body = "<ul>" + "".join(f"<li>{e(b)}</li>" for b in c["bullets"]) + "</ul>"
        else:
            body = e(c.get("body", ""))
        out += (f'<div class="card c-{e(c["color"])}"><div class="cap">{emoji}{e(c["cap"])}</div>'
                f'<div class="bd">{body}</div></div>')
    return out + "</div>"

def render_questions(sec):
    items = "".join(f"<li>{e(q)}</li>" for q in sec["items"])
    return f'<div class="banner">{e(sec["title"])}</div><ul class="questions">{items}</ul>'

def render_text(sec):
    out = f'<div class="banner">{e(sec["title"])}</div>'
    for p in sec.get("paragraphs", []):
        out += f'<p class="lead">{e(p)}</p>'
    if sec.get("note"):
        n = sec["note"]
        out += render_note(n.get("type", "method"), n["label"], n["text"], n.get("icon", "🧭"))
    return out

def render_application(sec):
    return (f'<div class="banner">{e(sec["title"])}</div>'
            + render_note("problem", sec.get("label", "تطبيق منهجي"), sec["task"], "📝"))

def render_infographic(sec):
    out = f'<div class="banner">{e(sec["title"])}</div>'
    if sec.get("lead"):
        out += f'<p class="lead">{e(sec["lead"])}</p>'
    out += '<div class="infographics">'
    for img in sec["images"]:
        out += (f'<figure class="info-fig"><img src="{e(img["src"])}" alt="{e(img["alt"])}" loading="lazy">'
                f'<figcaption>{e(img["caption"])} · '
                f'<a href="{e(img["src"])}" download>تحميل الصورة ⤓</a></figcaption></figure>')
    return out + "</div>"

def render_resources(sec):
    out = f'<div class="banner">{e(sec["title"])}</div>'
    if sec.get("lead"):
        out += f'<p class="lead">{e(sec["lead"])}</p>'
    out += '<div class="resources">'
    for r in sec["items"]:
        icon = e(r.get("icon", "🔗"))
        kind = e(r.get("kind", "مورد"))
        target = ' download' if r["url"].startswith("../") else ' target="_blank" rel="noopener"'
        out += (f'<a class="res" href="{e(r["url"])}"{target}>'
                f'<span class="res-ic" aria-hidden="true">{icon}</span>'
                f'<span class="res-tx"><b>{e(r["title"])}</b><small>{kind}</small></span>'
                f'<span class="res-go">{"تحميل ⤓" if r["url"].startswith("../") else "فتح ⤴"}</span></a>')
    out += '</div>'
    if sec.get("note"):
        n = sec["note"]
        out += render_note(n.get("type", "method"), n["label"], n["text"], n.get("icon", "📂"))
    return out

def render_notebook(nb):
    """«أكتب في دفتري»: فقرة تُنقل حرفيًا من ملف الدرس إلى الدفتر."""
    if not nb:
        return ""
    out = '<div class="notebook"><div class="nb-head"><span class="nb-ic" aria-hidden="true">✍️</span>أكتب في دفتري'
    out += '</div><div class="nb-body">'
    for b in nb["blocks"]:
        if "h" in b:
            out += f'<h4>{e(b["h"])}</h4>'
        elif "p" in b:
            out += f'<p>{e(b["p"])}</p>'
        elif "ul" in b:
            out += "<ul>" + "".join(f"<li>{e(x)}</li>" for x in b["ul"]) + "</ul>"
        elif "table" in b:
            t = b["table"]
            head = "".join(f"<th>{e(h)}</th>" for h in t["head"])
            rows = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in t["rows"])
            out += f'<table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>'
    return out + "</div></div>"

RENDERERS = {"table": render_table, "cards": render_cards, "questions": render_questions,
             "text": render_text, "application": render_application,
             "infographic": render_infographic, "resources": render_resources}

def build_lesson(data):
    m = data["meta"]
    body = [render_note("intro", "مقدمة", data["intro"], "📘"),
            render_note("problem", "الإشكالية المركزية", data["problematic"], "❓"),
            render_notebook(data.get("notebook_intro"))]
    for sec in data["sections"]:
        body.append(RENDERERS[sec["kind"]](sec))
        body.append(render_notebook(sec.get("notebook")))
    body.append(render_note("conclusion", "خاتمة", data["conclusion"], "✍️"))
    body.append(render_notebook(data.get("notebook_conclusion")))
    page = f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(m["title"])} | رحلة الأولى باك</title>
<meta name="description" content="{e(m["title"])} — {e(m["subject"])} · {e(m["level"])}. درس كامل ضمن رحلة الأولى باك.">
<link rel="icon" href="../assets/img/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="../assets/img/apple-touch-icon.png">
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
      <span class="inst">الأستاذ أحمد بوعمود</span>
      <span class="sub">أستاذ التاريخ والجغرافيا</span>
    </div></div>
    <div class="season">الموسم الدراسي<br><bdi dir="ltr">2026 / 2027</bdi></div>
  </header>
  <div class="title-band">
    <span class="lvl">مادة {e(m["subject"])} <span>|</span> المستوى: {e(m["level"])}</span>
    <h1>{e(m["title"])}</h1>
    <span class="lesson-tag">{e(m["lessonTag"])}</span>
  </div>
  {"".join(body)}
  <div class="doc-foot">
    <span>إعداد: الأستاذ أحمد بوعمود — أستاذ الاجتماعيات</span>
    <span>ذ. أحمد بوعمود — مؤسسة الحنان الخاصة | <bdi dir="ltr">2026-2027</bdi></span>
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
