#!/usr/bin/env python3
"""Generate the Study Material PDFs section (Class 9-12, board-syllabus
chapters across Maths/Science/English/Social Science/Physics/Chemistry/
Biology) — same pattern as _gen_ncert.py, kept as a separate section
because these chapter titles aren't standard NCERT-only naming (board
curriculum material spanning multiple subjects/classes).
- /study-material/                          hub (by class)
- /study-material/<class>/                  all chapters, subject filter chips
- /study-material/<class>/<subject>/        one subject's chapters
- /study-material/<class>/<subject>/<ch>/   one chapter — deepest SEO target
PDFs already live under /downloads/study-material/<class>/<subject>/<chapter>.pdf
Run from repo root: python3 _gen_study.py
"""
import json, os
import _gen_exams as ge

BASE = ge.BASE
TODAY = ge.TODAY
YEAR = ge.YEAR
ROOT = ge.ROOT

MANIFEST = os.path.join(ROOT, "downloads", "study-material", "manifest.json")

EXTRA_CSS = '''  <style>
    .ncert-classes{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:1rem;margin:1.6rem 0}
    .ncert-class-card{border:1.5px solid var(--line);border-radius:14px;padding:1.5rem;text-decoration:none;color:inherit;display:block;transition:border-color .15s,transform .15s}
    .ncert-class-card:hover{border-color:var(--blue-500,#2563eb);transform:translateY(-2px)}
    .ncert-class-card h3{margin:0 0 .3rem;font-size:1.3rem}
    .ncert-class-card p{margin:0;color:var(--muted);font-size:.9rem}
    .ncert-filters{display:flex;gap:.5rem;flex-wrap:wrap;margin:1.4rem 0}
    .ncert-chip{border:1.5px solid var(--line);border-radius:999px;padding:.5rem 1.1rem;font-size:.88rem;
      font-weight:600;background:var(--card);color:inherit;cursor:pointer;transition:.15s}
    .ncert-chip:hover{border-color:var(--blue-500,#2563eb)}
    .ncert-chip.active{background:var(--accent,#2563eb);border-color:var(--accent,#2563eb);color:#fff}
    .ncert-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:.8rem;margin:1rem 0}
    .ncert-card{border:1.5px solid var(--line);border-radius:12px;padding:1rem 1.1rem;display:flex;
      flex-direction:column;gap:.6rem}
    .ncert-card .nc-subject{font-size:.72rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;
      color:var(--accent,#2563eb)}
    .ncert-card b{font-size:.95rem;line-height:1.35}
    .ncert-card .btn{align-self:flex-start;margin-top:auto}
    [data-theme="dark"] .ncert-class-card,[data-theme="dark"] .ncert-card,[data-theme="dark"] .ncert-chip{border-color:var(--line)}
  </style>'''

FILTER_JS = '''  <script>
  (function(){
    var chips = document.querySelectorAll('.ncert-chip[data-filter]');
    var cards = document.querySelectorAll('.ncert-card[data-subject]');
    chips.forEach(function(c){
      c.addEventListener('click', function(){
        chips.forEach(function(x){ x.classList.remove('active'); });
        c.classList.add('active');
        var f = c.dataset.filter;
        cards.forEach(function(card){
          card.style.display = (f === 'all' || card.dataset.subject === f) ? '' : 'none';
        });
      });
    });
  })();
  </script>'''


def load_rows():
    rows = json.load(open(MANIFEST, encoding="utf-8"))
    for r in rows:
        r["pdf_url"] = f"/{r['local_path']}"
    return rows


def study_card(r):
    return (f'<div class="ncert-card" data-subject="{r["subject_slug"]}">'
            f'<span class="nc-subject">{ge.esc(r["subject"])} · Class {ge.esc(r["class"])}</span>'
            f'<b>{ge.esc(r["chapter"])}</b>'
            f'<a class="btn btn-primary btn-sm" href="{r["pdf_url"]}" download>Download PDF →</a>'
            f'</div>')


def hub(rows, classes):
    canonical = f"{BASE}/study-material/"
    total = len(rows)
    by_class = {}
    for r in rows:
        by_class.setdefault(r["class_slug"], []).append(r)

    title = ge.attr(f"Free Class 9-12 Study Material PDF Download {YEAR} | YESPYQ")
    desc = ge.attr(f"Free study material PDFs for Class 9, 10, 11 & 12 — {total} chapters across Maths, Science, English, Social Science, Physics, Chemistry and Biology. No signup needed.")

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"Study Material PDFs","item":"{canonical}"}}]}}
  </script>'''

    tiles = ""
    for cslug, cname in classes:
        crows = by_class.get(cslug, [])
        subs = sorted(set(r["subject"] for r in crows))
        tiles += (f'<a class="ncert-class-card" href="/study-material/{cslug}/">'
                  f'<h3>{ge.esc(cname)} Study PDFs</h3><p>{len(crows)} chapters — {", ".join(subs)}</p></a>')

    body = f'''{ge.HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › Study Material PDFs</nav>
      <h1>Free Class 9-12 Study Material PDF Download {YEAR}</h1>
      <p>{total} board-syllabus chapter PDFs for Class 9 to 12 — Maths, Science, English, Social Science, Physics, Chemistry and Biology. Every chapter is free to download, no signup or app required. Pick a class to browse chapters by subject.</p>
      <div class="ncert-classes">{tiles}</div>
    </article>
  </main>
{ge.FOOTER}
{EXTRA_CSS}
</body>
</html>'''
    return ge.head(title, desc, canonical, schema, "") + body


def class_page(cslug, cname, rows):
    canonical = f"{BASE}/study-material/{cslug}/"
    crows = [r for r in rows if r["class_slug"] == cslug]
    total = len(crows)
    subs = sorted(set((r["subject_slug"], r["subject"]) for r in crows))

    title = ge.attr(f"Free {cname} Study Material PDF Download {YEAR} | YESPYQ")
    desc = ge.attr(f"Free {cname} study material PDF download — {total} chapters across {', '.join(s[1] for s in subs)}. No signup needed.")

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"Study Material PDFs","item":"{BASE}/study-material/"}},{{"@type":"ListItem","position":3,"name":"{ge.json_esc(cname)}","item":"{canonical}"}}]}}
  </script>'''

    chips = '<button class="ncert-chip active" data-filter="all">All subjects</button>'
    for sslug, sname in subs:
        chips += f'<button class="ncert-chip" data-filter="{sslug}">{ge.esc(sname)}</button>'

    subject_links = "".join(f'<a href="/study-material/{cslug}/{sslug}/">{ge.esc(sname)} PDFs →</a> ' for sslug, sname in subs)
    cards = "".join(study_card(r) for r in crows)

    body = f'''{ge.HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/study-material/">Study Material PDFs</a> › {ge.esc(cname)}</nav>
      <h1>Free {ge.esc(cname)} Study Material PDF Download {YEAR}</h1>
      <p>{total} {ge.esc(cname)} chapter PDFs — {", ".join(s[1] for s in subs)}, free to download, no signup needed. {subject_links}</p>
      <div class="ncert-filters">{chips}</div>
      <div class="ncert-list">{cards}</div>
    </article>
  </main>
{ge.FOOTER}
{EXTRA_CSS}
{FILTER_JS}
</body>
</html>'''
    return ge.head(title, desc, canonical, schema, "") + body


def subject_page(cslug, cname, sslug, sname, rows):
    canonical = f"{BASE}/study-material/{cslug}/{sslug}/"
    srows = [r for r in rows if r["class_slug"] == cslug and r["subject_slug"] == sslug]
    total = len(srows)

    title = ge.attr(f"Free {cname} {sname} PDF Download {YEAR} — All Chapters | YESPYQ")
    desc = ge.attr(f"Free {cname} {sname} study material PDF download — all {total} chapters, no signup.")

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"Study Material PDFs","item":"{BASE}/study-material/"}},{{"@type":"ListItem","position":3,"name":"{ge.json_esc(cname)}","item":"{BASE}/study-material/{cslug}/"}},{{"@type":"ListItem","position":4,"name":"{ge.json_esc(sname)}","item":"{canonical}"}}]}}
  </script>'''

    cards = "".join(study_card(r) for r in srows)

    body = f'''{ge.HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/study-material/">Study Material PDFs</a> › <a href="/study-material/{cslug}/">{ge.esc(cname)}</a> › {ge.esc(sname)}</nav>
      <h1>Free {ge.esc(cname)} {ge.esc(sname)} PDF Download {YEAR}</h1>
      <p>All {total} {ge.esc(cname)} {ge.esc(sname)} chapter PDFs — free to download, no signup needed.</p>
      <div class="ncert-list">{cards}</div>
    </article>
  </main>
{ge.FOOTER}
{EXTRA_CSS}
</body>
</html>'''
    return ge.head(title, desc, canonical, schema, "") + body


def chapter_page(cslug, cname, sslug, sname, row, srows):
    canonical = f"{BASE}/study-material/{cslug}/{sslug}/{row['chapter_slug']}/"
    chapter = row["chapter"]
    idx = next(i for i, r in enumerate(srows) if r["chapter_slug"] == row["chapter_slug"])
    prev_r = srows[idx - 1] if idx > 0 else None
    next_r = srows[idx + 1] if idx + 1 < len(srows) else None

    title = ge.attr(f"{cname} {sname} {chapter} PDF Download {YEAR} | YESPYQ")
    desc = ge.attr(f"Free {cname} {sname} \"{chapter}\" chapter PDF — download instantly, no signup needed.")

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"Study Material PDFs","item":"{BASE}/study-material/"}},{{"@type":"ListItem","position":3,"name":"{ge.json_esc(cname)}","item":"{BASE}/study-material/{cslug}/"}},{{"@type":"ListItem","position":4,"name":"{ge.json_esc(sname)}","item":"{BASE}/study-material/{cslug}/{sslug}/"}},{{"@type":"ListItem","position":5,"name":"{ge.json_esc(chapter)}","item":"{canonical}"}}]}}
  </script>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"DigitalDocument","name":"{ge.json_esc(f'{cname} {sname} — {chapter}')}","about":"{ge.json_esc(chapter)}","educationalLevel":"{ge.json_esc(cname)}","learningResourceType":"Textbook chapter","encodingFormat":"application/pdf","url":"{canonical}","isAccessibleForFree":true}}
  </script>'''

    nav_links = ""
    if prev_r:
        nav_links += f'<a class="btn btn-ghost" href="/study-material/{cslug}/{sslug}/{prev_r["chapter_slug"]}/">← {ge.esc(prev_r["chapter"])}</a>'
    if next_r:
        nav_links += f'<a class="btn btn-ghost" href="/study-material/{cslug}/{sslug}/{next_r["chapter_slug"]}/">{ge.esc(next_r["chapter"])} →</a>'

    other_chapters = "".join(
        f'<a href="/study-material/{cslug}/{sslug}/{r["chapter_slug"]}/">{ge.esc(r["chapter"])}</a>'
        for r in srows if r["chapter_slug"] != row["chapter_slug"]
    )

    body = f'''{ge.HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/study-material/">Study Material PDFs</a> › <a href="/study-material/{cslug}/">{ge.esc(cname)}</a> › <a href="/study-material/{cslug}/{sslug}/">{ge.esc(sname)}</a> › {ge.esc(chapter)}</nav>
      <h1>{ge.esc(cname)} {ge.esc(sname)}: {ge.esc(chapter)} — PDF Download</h1>
      <p>Download the {ge.esc(cname)} {ge.esc(sname)} chapter "{ge.esc(chapter)}" as a free PDF — no signup, no download limit. Part of the complete {ge.esc(cname)} {ge.esc(sname)} syllabus, all {len(srows)} chapters available on YESPYQ.</p>
      <div class="ncert-list">{study_card(row)}</div>
      <div class="q-nav" style="display:flex;gap:.7rem;flex-wrap:wrap;margin:1.4rem 0">{nav_links}</div>
      <div class="cta-box">
        <h2>More {ge.esc(cname)} {ge.esc(sname)} chapters</h2>
        <p>Browse every {ge.esc(sname)} chapter for {ge.esc(cname)}, or explore all study material PDFs.</p>
        <a href="/study-material/{cslug}/{sslug}/" class="btn btn-primary">All {ge.esc(cname)} {ge.esc(sname)} chapters →</a>
      </div>
      <section class="related">
        <h2>Other {ge.esc(cname)} {ge.esc(sname)} chapters</h2>
        <div class="related-list">{other_chapters}</div>
      </section>
    </article>
  </main>
{ge.FOOTER}
{EXTRA_CSS}
</body>
</html>'''
    return ge.head(title, desc, canonical, schema, "") + body


def main():
    rows = load_rows()
    class_order = sorted(set(r["class"] for r in rows), key=lambda c: int(c) if c.isdigit() else 99)
    classes = [(f"class-{c}", f"Class {c}") for c in class_order]

    ge.write("study-material", hub(rows, classes))
    urls = [f"{BASE}/study-material/"]

    for cslug, cname in classes:
        ge.write(f"study-material/{cslug}", class_page(cslug, cname, rows))
        urls.append(f"{BASE}/study-material/{cslug}/")
        subs = sorted(set((r["subject_slug"], r["subject"]) for r in rows if r["class_slug"] == cslug))
        for sslug, sname in subs:
            ge.write(f"study-material/{cslug}/{sslug}", subject_page(cslug, cname, sslug, sname, rows))
            urls.append(f"{BASE}/study-material/{cslug}/{sslug}/")
            srows = [r for r in rows if r["class_slug"] == cslug and r["subject_slug"] == sslug]
            for row in srows:
                ge.write(f"study-material/{cslug}/{sslug}/{row['chapter_slug']}", chapter_page(cslug, cname, sslug, sname, row, srows))
                urls.append(f"{BASE}/study-material/{cslug}/{sslug}/{row['chapter_slug']}/")

    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>")
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap-study-material.xml"), "w").write("\n".join(sm) + "\n")

    print(f"Wrote {len(urls)} Study Material pages ({len(rows)} PDFs).")


if __name__ == "__main__":
    main()
