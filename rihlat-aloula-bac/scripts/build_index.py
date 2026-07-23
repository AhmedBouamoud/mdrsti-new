#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""يولّد الصفحة الرئيسية (index.html) من ملفات المحتوى، بالهوية المعتمدة."""
import json, glob, html, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
OUT = os.path.join(ROOT, "index.html")
e = lambda s: html.escape(str(s), quote=True)

def load():
    groups = {}
    for f in sorted(glob.glob(os.path.join(CONTENT, "**", "*.json"), recursive=True)):
        m = json.load(open(f, encoding="utf-8"))["meta"]
        groups.setdefault(m["subject"], []).append(m)
    for g in groups:
        groups[g].sort(key=lambda m: m["number"])
    return groups

def card(m):
    badge = "إنفوغرافيا + تمارين" if m.get("hasInfographic") else "درس كامل"
    return (f'<a class="card" href="lessons/{e(m["slug"])}.html">'
            f'<span class="c-num">الدرس {m["number"]}</span>'
            f'<span class="c-title">{e(m["title"])}</span>'
            f'<span class="c-foot"><span class="c-badge">{badge}</span>'
            f'<span class="c-open">افتح الدرس ←</span></span></a>')

def track(icon, name, subject, items):
    cards = "\n".join("        " + card(m) for m in items)
    return (f'''    <section class="track" id="{subject}">
      <div class="track-head">
        <span class="t-ic">{icon}</span>
        <div><h2>{name}</h2><p>{len(items)} دروس كاملة · قابلة للقراءة والطباعة</p></div>
      </div>
      <div class="grid">
{cards}
      </div>
    </section>''')

def build():
    g = load()
    hist = g.get("التاريخ", [])
    geo = g.get("الجغرافيا", [])
    total = len(hist) + len(geo)
    page = f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>رحلة الأولى باك | الاجتماعيات — التاريخ والجغرافيا</title>
<meta name="description" content="رحلة الأولى باك: دروس الاجتماعيات الكاملة (التاريخ والجغرافيا) للسنة الأولى بكالوريا — إعداد الأستاذ أحمد بوعمود، مؤسسة الحنان.">
<meta name="theme-color" content="#0f2438">
<style>
:root{{--navy:#0f2438;--navy-2:#173f5f;--ink:#22364d;--muted:#5d6f83;--orange:#e8820e;--gold:#e0a53a;
--desk:#eef1f5;--card:#fff;--line:#dce4ee;--shadow:0 18px 45px rgba(15,36,56,.14);--card-sh:0 6px 18px rgba(15,36,56,.08);--max:1120px;}}
@media (prefers-color-scheme:dark){{:root{{--desk:#0c1219;--ink:#e6edf5;--muted:#9fb0c2;--card:#141d28;--line:#243447;--shadow:0 18px 45px rgba(0,0,0,.5);}}}}
:root[data-theme="dark"]{{--desk:#0c1219;--ink:#e6edf5;--muted:#9fb0c2;--card:#141d28;--line:#243447;}}
:root[data-theme="light"]{{--desk:#eef1f5;--ink:#22364d;--muted:#5d6f83;--card:#fff;--line:#dce4ee;}}
*{{box-sizing:border-box;}}
body{{margin:0;background:var(--desk);color:var(--ink);direction:rtl;
font-family:"Noto Naskh Arabic","Amiri","Segoe UI",Tahoma,Arial,sans-serif;line-height:1.8;-webkit-text-size-adjust:100%;}}
h1,h2,h3{{font-family:"Cairo","Tajawal","Segoe UI",Tahoma,sans-serif;margin:0;}}
a{{color:inherit;}}

/* ===== الترويسة العلوية ===== */
.topnav{{position:sticky;top:0;z-index:30;background:rgba(15,36,56,.92);backdrop-filter:blur(10px);
color:#fff;display:flex;align-items:center;justify-content:space-between;gap:12px;
padding:10px clamp(16px,4vw,40px);}}
.brand{{display:flex;align-items:center;gap:11px;}}
.brand .crest{{width:40px;height:40px;}}
.brand b{{font-size:1rem;}}
.brand small{{display:block;color:#c9d6e3;font-family:Tahoma,sans-serif;font-size:.7rem;font-weight:400;}}
.topnav .links{{display:flex;gap:8px;font-family:Tahoma,sans-serif;font-size:.85rem;}}
.topnav .links a{{color:#cdd9e6;text-decoration:none;padding:6px 12px;border-radius:8px;}}
.topnav .links a:hover{{background:rgba(255,255,255,.1);color:#fff;}}

/* ===== الواجهة (Hero) ===== */
.hero{{position:relative;overflow:hidden;background:linear-gradient(135deg,#0f2438,#173f5f 60%,#1d5c86);
color:#fff;padding:clamp(48px,9vw,96px) clamp(20px,5vw,40px);text-align:center;}}
.hero::before,.hero::after{{content:"";position:absolute;border-radius:50%;filter:blur(8px);opacity:.55;pointer-events:none;}}
.hero::before{{width:340px;height:340px;background:radial-gradient(circle,#f5a623,#e8820e 40%,transparent 70%);top:-120px;left:-90px;}}
.hero::after{{width:300px;height:300px;background:radial-gradient(circle,#2f80c4,#173f5f 45%,transparent 72%);bottom:-130px;right:-80px;}}
.hero-in{{position:relative;z-index:2;max-width:820px;margin:auto;}}
.eyebrow{{display:inline-block;font-family:Tahoma,sans-serif;color:var(--gold);font-weight:800;font-size:.82rem;letter-spacing:.5px;
border:1px solid rgba(224,165,58,.4);padding:5px 16px;border-radius:999px;margin-bottom:20px;}}
.hero h1{{font-size:clamp(2.4rem,7vw,4.4rem);line-height:1.15;font-weight:800;margin:0 0 6px;}}
.hero h1 em{{font-style:normal;color:var(--gold);}}
.hero .lead{{font-size:clamp(1rem,2.4vw,1.2rem);color:#dbe7f2;max-width:620px;margin:14px auto 26px;}}
.pills{{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-bottom:30px;}}
.pill{{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.16);border-radius:999px;
padding:7px 16px;font-family:Tahoma,sans-serif;font-size:.83rem;}}
.pill b{{color:var(--gold);}}
.cta{{display:inline-flex;gap:10px;flex-wrap:wrap;justify-content:center;}}
.btn{{text-decoration:none;font-family:Tahoma,sans-serif;font-weight:800;font-size:.95rem;padding:13px 26px;border-radius:12px;transition:.18s;}}
.btn.primary{{background:var(--orange);color:#fff;box-shadow:0 10px 24px rgba(232,130,14,.35);}}
.btn.primary:hover{{background:#f5a623;transform:translateY(-2px);}}
.btn.ghost{{border:1px solid rgba(255,255,255,.35);color:#fff;}}
.btn.ghost:hover{{background:rgba(255,255,255,.12);}}
.stats{{display:flex;flex-wrap:wrap;gap:14px;justify-content:center;margin-top:38px;}}
.stat{{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.13);border-radius:14px;padding:14px 24px;min-width:120px;}}
.stat b{{display:block;font-size:1.7rem;color:var(--gold);font-family:Tahoma,sans-serif;}}
.stat span{{font-family:Tahoma,sans-serif;font-size:.78rem;color:#cdd9e6;}}

/* ===== المحاور ===== */
main{{max-width:var(--max);margin:auto;padding:clamp(30px,6vw,64px) clamp(16px,4vw,32px) 20px;}}
.track{{margin-bottom:clamp(34px,6vw,58px);}}
.track-head{{display:flex;align-items:center;gap:14px;margin-bottom:20px;}}
.track-head .t-ic{{width:52px;height:52px;flex:0 0 auto;display:grid;place-items:center;font-size:1.7rem;
background:linear-gradient(135deg,var(--navy),var(--navy-2));color:#fff;border-radius:14px;box-shadow:var(--card-sh);}}
.track-head h2{{font-size:clamp(1.4rem,3.4vw,1.9rem);color:var(--ink);}}
.track-head p{{margin:2px 0 0;color:var(--muted);font-family:Tahoma,sans-serif;font-size:.82rem;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(268px,1fr));gap:16px;}}
.card{{display:flex;flex-direction:column;gap:12px;text-decoration:none;background:var(--card);
border:1px solid var(--line);border-radius:16px;padding:18px 20px;box-shadow:var(--card-sh);
position:relative;overflow:hidden;transition:.2s;}}
.card::before{{content:"";position:absolute;top:0;right:0;width:6px;height:100%;background:var(--navy);transition:.2s;}}
.card:hover{{transform:translateY(-4px);box-shadow:var(--shadow);border-color:#c3d0df;}}
.card:hover::before{{background:var(--orange);}}
.c-num{{font-family:Tahoma,sans-serif;font-size:.74rem;font-weight:800;color:var(--orange);}}
.c-title{{color:var(--ink);font-weight:800;font-size:1.05rem;line-height:1.6;flex:1;}}
.c-foot{{display:flex;justify-content:space-between;align-items:center;border-top:1px solid var(--line);padding-top:12px;}}
.c-badge{{font-family:Tahoma,sans-serif;font-size:.72rem;color:var(--muted);}}
.c-open{{font-family:Tahoma,sans-serif;font-weight:800;color:var(--orange);font-size:.84rem;}}

/* ===== التذييل ===== */
footer{{background:var(--navy);color:#cdd9e6;margin-top:20px;padding:34px clamp(20px,5vw,40px);}}
.foot-in{{max-width:var(--max);margin:auto;display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;}}
.foot-in .fb{{display:flex;align-items:center;gap:12px;}}
.foot-in .crest{{width:44px;height:44px;}}
.foot-in b{{color:#fff;}}
.foot-in small{{font-family:Tahoma,sans-serif;font-size:.78rem;}}
.foot-site{{font-family:Tahoma,sans-serif;font-size:.82rem;color:var(--gold);}}

@media (max-width:520px){{.topnav .links{{display:none;}} .stat{{flex:1;min-width:0;}}}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important;}}}}
</style>
</head>
<body>
{CREST_NAV}
<header class="hero">
  <div class="hero-in">
    <span class="eyebrow">مؤسسة الحنان للتعليم الخاص</span>
    <h1>رحلة <em>الأولى باك</em></h1>
    <p class="lead">دروس الاجتماعيات الكاملة — التاريخ والجغرافيا — للسنة الأولى بكالوريا، منظّمة ومراجَعة وقابلة للقراءة والطباعة على الهاتف والحاسوب.</p>
    <div class="pills">
      <span class="pill">📜 <b>التاريخ</b></span>
      <span class="pill">🌍 <b>الجغرافيا</b></span>
      <span class="pill">السنة الأولى بكالوريا</span>
    </div>
    <div class="cta">
      <a class="btn primary" href="#التاريخ">ابدأ بدروس التاريخ</a>
      <a class="btn ghost" href="#الجغرافيا">دروس الجغرافيا</a>
    </div>
    <div class="stats">
      <div class="stat"><b>{total}</b><span>درسًا كاملًا</span></div>
      <div class="stat"><b>{len(hist)}</b><span>محور التاريخ</span></div>
      <div class="stat"><b>{len(geo)}</b><span>محور الجغرافيا</span></div>
    </div>
  </div>
</header>
<main>
{track("📜","محور التاريخ","التاريخ",hist)}
{track("🌍","محور الجغرافيا","الجغرافيا",geo)}
</main>
<footer>
  <div class="foot-in">
    <div class="fb">{CREST}<div><b>الأستاذ أحمد بوعمود</b><br><small>أستاذ الاجتماعيات — مؤسسة الحنان</small></div></div>
    <div class="foot-site">ahmedbouamoud.com · aloula.hanane.today</div>
  </div>
</footer>
</body>
</html>'''
    open(OUT, "w", encoding="utf-8").write(page)
    print(f"✅ index.html: {len(hist)} تاريخ + {len(geo)} جغرافيا = {total} درسًا")

CREST = ('<svg class="crest" viewBox="0 0 100 100" role="img" aria-label="شعار مؤسسة الحنان">'
         '<rect x="6" y="6" width="88" height="88" rx="20" fill="#12294a" stroke="#e0a53a" stroke-width="4"/>'
         '<rect x="30" y="46" width="40" height="30" fill="#fff"/>'
         '<path d="M26 46l24-16 24 16z" fill="#e0a53a"/>'
         '<rect x="46" y="58" width="8" height="18" fill="#12294a"/>'
         '<rect x="34" y="52" width="7" height="7" fill="#2b6cb0"/>'
         '<rect x="59" y="52" width="7" height="7" fill="#2b6cb0"/></svg>')

CREST_NAV = (f'<nav class="topnav"><div class="brand">{CREST}'
             f'<div><b>رحلة الأولى باك</b><small>الاجتماعيات · مؤسسة الحنان</small></div></div>'
             f'<div class="links"><a href="#التاريخ">التاريخ</a><a href="#الجغرافيا">الجغرافيا</a></div></nav>')

if __name__ == "__main__":
    build()
