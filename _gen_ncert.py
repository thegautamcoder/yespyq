#!/usr/bin/env python3
"""Generate the NCERT PDFs section:
- /ncert-pdfs/                          hub (by class)
- /ncert-pdfs/<class>/                  all chapters for a class, subject filter chips
- /ncert-pdfs/<class>/<subject>/        one subject's chapters (deepest SEO target)
PDFs themselves already live under /downloads/ncert/<class>/<subject>/<chapter>.pdf
(downloaded separately — this script only builds the browsing/SEO pages around them).
Run from repo root: python3 _gen_ncert.py
"""
import json, os, re
import _gen_exams as ge

BASE = ge.BASE
TODAY = ge.TODAY
YEAR = ge.YEAR
ROOT = ge.ROOT

MANIFEST = os.path.join(ROOT, "downloads", "ncert", "manifest.json")

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

CLASSES = [("11", "Class 11"), ("12", "Class 12")]
SUBJECTS = [("physics", "Physics"), ("chemistry", "Chemistry"), ("maths", "Maths")]


def load_rows():
    rows = json.load(open(MANIFEST, encoding="utf-8"))
    for r in rows:
        r["pdf_url"] = f"/{r['local_path']}"
    return rows


def ncert_card(r):
    return (f'<div class="ncert-card" data-subject="{r["subject_slug"]}">'
            f'<span class="nc-subject">{ge.esc(r["subject"])} · Class {ge.esc(r["class"])}</span>'
            f'<b>{ge.esc(r["chapter"])}</b>'
            f'<a class="btn btn-primary btn-sm" href="{r["pdf_url"]}" download>Download PDF →</a>'
            f'</div>')


def hub(rows):
    canonical = f"{BASE}/ncert-pdfs/"
    total = len(rows)
    by_class = {}
    for r in rows:
        by_class.setdefault(r["class"], []).append(r)

    title = ge.attr(f"Free NCERT PDF Download {YEAR} — Class 11 & 12 Physics, Chemistry, Maths | YESPYQ")
    desc = ge.attr(f"Free NCERT PDF download for Class 11 & 12 — {total} chapters across Physics, Chemistry and Maths. No signup, no download limit, practice online or save the PDF instantly.")

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"NCERT PDFs","item":"{canonical}"}}]}}
  </script>'''

    tiles = ""
    for cslug, cname in CLASSES:
        n = len(by_class.get(cslug, []))
        subs = sorted(set(r["subject"] for r in by_class.get(cslug, [])))
        tiles += (f'<a class="ncert-class-card" href="/ncert-pdfs/class-{cslug}/">'
                  f'<h3>NCERT {cname} PDFs</h3><p>{n} chapters — {", ".join(subs)}</p></a>')

    body = f'''{ge.HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › NCERT PDFs</nav>
      <h1>Free NCERT PDF Download {YEAR} — Class 11 &amp; 12</h1>
      <p>{total} NCERT chapter PDFs for Class 11 and Class 12 — Physics, Chemistry and Maths. Every chapter is free to download, no signup or app required. Pick a class to browse chapters by subject.</p>
      <div class="ncert-classes">{tiles}</div>
    </article>
  </main>
{ge.FOOTER}
{EXTRA_CSS}
</body>
</html>'''
    return ge.head(title, desc, canonical, schema, "") + body


def class_page(cslug, cname, rows):
    canonical = f"{BASE}/ncert-pdfs/class-{cslug}/"
    crows = [r for r in rows if r["class"] == cslug]
    total = len(crows)
    subs = sorted(set((r["subject_slug"], r["subject"]) for r in crows))

    title = ge.attr(f"Free NCERT {cname} PDF Download {YEAR} — Physics, Chemistry, Maths | YESPYQ")
    desc = ge.attr(f"Free NCERT {cname} PDF download — {total} chapters across {', '.join(s[1] for s in subs)}. No signup, practice online or save the PDF instantly.")

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"NCERT PDFs","item":"{BASE}/ncert-pdfs/"}},{{"@type":"ListItem","position":3,"name":"{ge.json_esc(cname)}","item":"{canonical}"}}]}}
  </script>'''

    chips = '<button class="ncert-chip active" data-filter="all">All subjects</button>'
    for sslug, sname in subs:
        chips += f'<button class="ncert-chip" data-filter="{sslug}">{ge.esc(sname)}</button>'

    subject_links = "".join(f'<a href="/ncert-pdfs/class-{cslug}/{sslug}/">{ge.esc(sname)} PDFs →</a> ' for sslug, sname in subs)

    cards = "".join(ncert_card(r) for r in crows)

    body = f'''{ge.HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/ncert-pdfs/">NCERT PDFs</a> › {ge.esc(cname)}</nav>
      <h1>Free NCERT {ge.esc(cname)} PDF Download {YEAR}</h1>
      <p>{total} NCERT {ge.esc(cname)} chapter PDFs — {", ".join(s[1] for s in subs)}, free to download, no signup needed. {subject_links}</p>
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
    canonical = f"{BASE}/ncert-pdfs/class-{cslug}/{sslug}/"
    srows = [r for r in rows if r["class"] == cslug and r["subject_slug"] == sslug]
    total = len(srows)

    title = ge.attr(f"Free NCERT {cname} {sname} PDF Download {YEAR} — All Chapters | YESPYQ")
    desc = ge.attr(f"Free NCERT {cname} {sname} PDF download — all {total} chapters, no signup. Practice online or save the PDF instantly.")

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"NCERT PDFs","item":"{BASE}/ncert-pdfs/"}},{{"@type":"ListItem","position":3,"name":"{ge.json_esc(cname)}","item":"{BASE}/ncert-pdfs/class-{cslug}/"}},{{"@type":"ListItem","position":4,"name":"{ge.json_esc(sname)}","item":"{canonical}"}}]}}
  </script>'''

    cards = "".join(ncert_card(r) for r in srows)

    body = f'''{ge.HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/ncert-pdfs/">NCERT PDFs</a> › <a href="/ncert-pdfs/class-{cslug}/">{ge.esc(cname)}</a> › {ge.esc(sname)}</nav>
      <h1>Free NCERT {ge.esc(cname)} {ge.esc(sname)} PDF Download {YEAR}</h1>
      <p>All {total} NCERT {ge.esc(cname)} {ge.esc(sname)} chapter PDFs — free to download, no signup needed.</p>
      <div class="ncert-list">{cards}</div>
    </article>
  </main>
{ge.FOOTER}
{EXTRA_CSS}
</body>
</html>'''
    return ge.head(title, desc, canonical, schema, "") + body


def main():
    rows = load_rows()
    ge.write("ncert-pdfs", hub(rows))
    urls = [f"{BASE}/ncert-pdfs/"]

    for cslug, cname in CLASSES:
        ge.write(f"ncert-pdfs/class-{cslug}", class_page(cslug, cname, rows))
        urls.append(f"{BASE}/ncert-pdfs/class-{cslug}/")
        subs = sorted(set((r["subject_slug"], r["subject"]) for r in rows if r["class"] == cslug))
        for sslug, sname in subs:
            ge.write(f"ncert-pdfs/class-{cslug}/{sslug}", subject_page(cslug, cname, sslug, sname, rows))
            urls.append(f"{BASE}/ncert-pdfs/class-{cslug}/{sslug}/")

    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>")
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap-ncert.xml"), "w").write("\n".join(sm) + "\n")

    print(f"Wrote {len(urls)} NCERT PDF pages ({len(rows)} PDFs).")


if __name__ == "__main__":
    main()
