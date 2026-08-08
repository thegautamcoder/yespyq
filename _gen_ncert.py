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

# Original, hand-written blurbs — not summarising or quoting the textbooks
# themselves, just general context on why each subject matters and how to
# use the PDF. Keyed by subject name so the same blurb can be reused across
# classes with the class name substituted in.
SUBJECT_BLURBS = {
    "Physics": (
        "Physics builds from first principles — every later chapter leans on the ones before it, "
        "which is exactly why a PDF you can flip back through is more useful than scattered notes. "
        "Working through the chapters in order, and re-deriving the key formulas by hand rather than "
        "just memorising them, is what actually sticks come exam time.",
        "Keep a separate page for formulas as you go — Physics rewards recognising which law applies "
        "to a new problem, not just recalling it in isolation."
    ),
    "Chemistry": (
        "Chemistry splits into three quite different ways of thinking — physical (calculation-heavy), "
        "organic (structure and reaction-heavy) and inorganic (fact-heavy) — and each chapter tends to "
        "sit clearly in one of those buckets. Knowing which mode a chapter needs before you start "
        "reading saves a lot of wasted effort.",
        "For organic chapters especially, draw the reaction mechanisms out by hand at least once — "
        "recognising them, not reproducing them from memory, is the actual skill being tested."
    ),
    "Maths": (
        "Maths chapters build a toolkit you're expected to combine, not use one at a time — a single "
        "exam question often pulls in ideas from two or three different chapters at once. Working "
        "through problems chapter by chapter first, then mixed-review sets later, mirrors how the "
        "subject is actually tested.",
        "Redo problems you got wrong a few days later without looking at the solution first — that "
        "gap is where the method actually gets internalised."
    ),
    "Biology": (
        "Biology is the most content-dense of the science subjects, and the difference between a "
        "vague answer and a precise one usually comes down to terminology — the exact name of a "
        "process, structure or stage. Reading a chapter once for the big picture and once more for "
        "the specific terms is a more efficient split than trying to absorb both at the same time.",
        "Diagrams are worth the extra time — labelling one from memory tests whether you actually "
        "understood the structure, not just whether you recognise it."
    ),
    "Science": (
        "At this stage Science moves fast across physics, chemistry and biology within the same "
        "chapter list, so it's worth being deliberate about which of the three a given chapter is "
        "testing before you dive in — the right approach (calculation vs. concept vs. recall) differs "
        "for each.",
        "Short, frequent revision of earlier chapters works better here than one long pass — the "
        "three subjects don't reinforce each other the way sequential chapters in a single subject do."
    ),
    "English": (
        "English chapters at this level are less about memorising the text and more about being able "
        "to discuss its themes, characters and structure in your own words — the questions test "
        "comprehension and expression, not recall.",
        "Practise answering in full sentences under a time limit — English exams reward clarity and "
        "structure in the answer almost as much as the content itself."
    ),
    "Social Science": (
        "Social Science covers history, geography, political science and economics in one bank of "
        "chapters, and each rewards a different kind of preparation — dates and causes for history, "
        "maps and processes for geography, structures and institutions for political science.",
        "Timelines and simple sketch-maps, drawn yourself rather than just viewed, make history and "
        "geography chapters far easier to recall accurately under exam pressure."
    ),
}

CLASS_INTRO = {
    "9": "the first year of the secondary syllabus, where subjects widen out from the primary curriculum into distinct disciplines",
    "10": "the board exam year most students remember — the syllabus here sets the base for whichever stream you pick after",
    "11": "the first year of senior secondary, where subjects go noticeably deeper and start feeding directly into JEE/NEET as well as boards",
    "12": "the final board year, and for Physics, Chemistry and Maths the last full pass through the syllabus before competitive exams",
}

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
    .ncert-faq{margin:1rem 0 1.5rem}
    .ncert-faq-item{border:1.5px solid var(--line);border-radius:12px;padding:.9rem 1.1rem;margin-bottom:.6rem}
    .ncert-faq-item summary{cursor:pointer;font-weight:700;font-size:.96rem}
    .ncert-faq-item p{margin:.6rem 0 0;color:var(--muted);font-size:.92rem;line-height:1.6}
    [data-theme="dark"] .ncert-faq-item{border-color:var(--line)}
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


def class_list(rows):
    """Returns [(class_id, class_slug, class_name), ...], e.g. ("11", "class-11", "Class 11")."""
    order = sorted(set(r["class"] for r in rows), key=lambda c: int(c) if c.isdigit() else 99)
    return [(c, f"class-{c}", f"Class {c}") for c in order]


def ncert_card(r):
    return (f'<div class="ncert-card" data-subject="{r["subject_slug"]}">'
            f'<span class="nc-subject">{ge.esc(r["subject"])} · Class {ge.esc(r["class"])}</span>'
            f'<b>{ge.esc(r["chapter"])}</b>'
            f'<a class="btn btn-primary btn-sm" href="{r["pdf_url"]}" download>Download PDF →</a>'
            f'</div>')


def hub(rows):
    canonical = f"{BASE}/ncert-pdfs/"
    total = len(rows)
    classes = class_list(rows)
    class_range = f"{classes[0][0]}–{classes[-1][0]}" if len(classes) > 1 else classes[0][2]
    by_class = {}
    for r in rows:
        by_class.setdefault(r["class_slug"], []).append(r)
    all_subs = sorted(set(r["subject"] for r in rows))

    title = ge.attr(f"Free NCERT PDF Download {YEAR} — Class {class_range} | YESPYQ")
    desc = ge.attr(f"Free NCERT &amp; board-syllabus PDF download for Class {class_range} — {total} chapters across {', '.join(all_subs)}. No signup, no download limit, practice online or save the PDF instantly.")

    faqs = [
        ("Are these official NCERT textbook PDFs?",
         f"The Class 11 & 12 Physics, Chemistry and Maths chapters are the actual NCERT textbook PDFs. The rest follow the same {class_range} board syllabus (CBSE and most state boards) chapter by chapter."),
        ("Is the download really free?",
         f"Yes, every one of the {total} chapter PDFs on this page is free to download, with no signup, no login and no download limit."),
        ("Which classes and subjects are covered?",
         f"Class {class_range} across {', '.join(all_subs)} — every chapter, organised by class and subject so you can jump straight to the one you need."),
        ("Can I use these PDFs for JEE and NEET preparation, not just boards?",
         "Yes — NCERT is the base syllabus for JEE and NEET as well as boards, so the Physics, Chemistry and Maths chapters work for all three."),
        ("How do I download a chapter PDF?",
         "Open a class page, filter by subject if you like, and tap Download PDF on the chapter you want — the file opens or saves immediately, no extra steps."),
    ]
    faq_html = "".join(f'<details class="ncert-faq-item"><summary>{ge.esc(q)}</summary><p>{ge.esc(a)}</p></details>' for q, a in faqs)
    faq_ld = ",".join(
        f'{{"@type":"Question","name":"{ge.json_esc(q)}","acceptedAnswer":{{"@type":"Answer","text":"{ge.json_esc(a)}"}}}}'
        for q, a in faqs
    )

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"NCERT PDFs","item":"{canonical}"}}]}}
  </script>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{faq_ld}]}}
  </script>'''

    tiles = ""
    for cid, cslug, cname in classes:
        n = len(by_class.get(cslug, []))
        subs = sorted(set(r["subject"] for r in by_class.get(cslug, [])))
        tiles += (f'<a class="ncert-class-card" href="/ncert-pdfs/{cslug}/">'
                  f'<h3>NCERT {cname} PDFs</h3><p>{n} chapters — {", ".join(subs)}</p></a>')

    body = f'''{ge.HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › NCERT PDFs</nav>
      <h1>Free NCERT PDF Download {YEAR} — Class {class_range}</h1>
      <p>{total} NCERT chapter PDFs for Class {class_range} — {', '.join(all_subs)}. Every chapter is free to download, no signup or app required. Pick a class to browse chapters by subject.</p>
      <p>NCERT textbooks are the base syllabus for CBSE boards and most state boards, and the same chapters carry directly into JEE and NEET for the science subjects — which is why they're usually the first thing a teacher points to before any reference book. Reading straight from the source rather than a summarised guide also avoids the small but real risk of a rewritten explanation drifting from what's actually being tested.</p>
      <div class="ncert-classes">{tiles}</div>
      <h2>Frequently asked questions</h2>
      <div class="ncert-faq">{faq_html}</div>
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
    class_ctx = CLASS_INTRO.get(cslug, "")
    subject_summary = "".join(
        f'<li><strong>{ge.esc(sname)}</strong> — {ge.esc(SUBJECT_BLURBS[sname][0].split(".")[0])}.</li>'
        for sslug, sname in subs if sname in SUBJECT_BLURBS
    )

    body = f'''{ge.HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/ncert-pdfs/">NCERT PDFs</a> › {ge.esc(cname)}</nav>
      <h1>Free NCERT {ge.esc(cname)} PDF Download {YEAR}</h1>
      <p>{total} NCERT {ge.esc(cname)} chapter PDFs — {", ".join(s[1] for s in subs)}, free to download, no signup needed. {ge.esc(cname)} is {class_ctx}. {subject_links}</p>
      {f'<ul>{subject_summary}</ul>' if subject_summary else ''}
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
    seen_names = []
    for r in srows:
        if r["chapter"] not in seen_names:
            seen_names.append(r["chapter"])
    chapter_names = ", ".join(seen_names)
    class_ctx = CLASS_INTRO.get(cslug, "")
    blurb = SUBJECT_BLURBS.get(sname)
    blurb_html = ""
    if blurb:
        intro, tip = blurb
        blurb_html = (
            f'<p>{intro}</p>'
            f'<p><strong>Tip:</strong> {tip}</p>'
        )

    body = f'''{ge.HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/ncert-pdfs/">NCERT PDFs</a> › <a href="/ncert-pdfs/class-{cslug}/">{ge.esc(cname)}</a> › {ge.esc(sname)}</nav>
      <h1>Free NCERT {ge.esc(cname)} {ge.esc(sname)} PDF Download {YEAR}</h1>
      <p>All {total} NCERT {ge.esc(cname)} {ge.esc(sname)} chapter PDFs — free to download, no signup needed. {ge.esc(cname)} is {class_ctx}.</p>
      {blurb_html}
      <p>The {total} chapters covered here: {ge.esc(chapter_names)}.</p>
      <div class="ncert-list">{cards}</div>
    </article>
  </main>
{ge.FOOTER}
{EXTRA_CSS}
</body>
</html>'''
    return ge.head(title, desc, canonical, schema, "") + body


def chapter_page(cslug, cname, sslug, sname, row, srows):
    canonical = f"{BASE}/ncert-pdfs/class-{cslug}/{sslug}/{row['chapter_slug']}/"
    chapter = row["chapter"]
    idx = next(i for i, r in enumerate(srows) if r["chapter_slug"] == row["chapter_slug"])
    prev_r = srows[idx - 1] if idx > 0 else None
    next_r = srows[idx + 1] if idx + 1 < len(srows) else None

    title = ge.attr(f"NCERT {cname} {sname} {chapter} PDF Download {YEAR} | YESPYQ")
    desc = ge.attr(f"Free NCERT {cname} {sname} \"{chapter}\" chapter PDF — download instantly, no signup needed. Part of the full NCERT {cname} {sname} syllabus.")

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"NCERT PDFs","item":"{BASE}/ncert-pdfs/"}},{{"@type":"ListItem","position":3,"name":"{ge.json_esc(cname)}","item":"{BASE}/ncert-pdfs/class-{cslug}/"}},{{"@type":"ListItem","position":4,"name":"{ge.json_esc(sname)}","item":"{BASE}/ncert-pdfs/class-{cslug}/{sslug}/"}},{{"@type":"ListItem","position":5,"name":"{ge.json_esc(chapter)}","item":"{canonical}"}}]}}
  </script>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"DigitalDocument","name":"{ge.json_esc(f'NCERT {cname} {sname} — {chapter}')}","about":"{ge.json_esc(chapter)}","educationalLevel":"{ge.json_esc(cname)}","learningResourceType":"Textbook chapter","encodingFormat":"application/pdf","url":"{canonical}","isAccessibleForFree":true}}
  </script>'''

    nav_links = ""
    if prev_r:
        nav_links += f'<a class="btn btn-ghost" href="/ncert-pdfs/class-{cslug}/{sslug}/{prev_r["chapter_slug"]}/">← {ge.esc(prev_r["chapter"])}</a>'
    if next_r:
        nav_links += f'<a class="btn btn-ghost" href="/ncert-pdfs/class-{cslug}/{sslug}/{next_r["chapter_slug"]}/">{ge.esc(next_r["chapter"])} →</a>'

    other_chapters = "".join(
        f'<a href="/ncert-pdfs/class-{cslug}/{sslug}/{r["chapter_slug"]}/">{ge.esc(r["chapter"])}</a>'
        for r in srows if r["chapter_slug"] != row["chapter_slug"]
    )

    body = f'''{ge.HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/ncert-pdfs/">NCERT PDFs</a> › <a href="/ncert-pdfs/class-{cslug}/">{ge.esc(cname)}</a> › <a href="/ncert-pdfs/class-{cslug}/{sslug}/">{ge.esc(sname)}</a> › {ge.esc(chapter)}</nav>
      <h1>NCERT {ge.esc(cname)} {ge.esc(sname)}: {ge.esc(chapter)} — PDF Download</h1>
      <p>Download the NCERT {ge.esc(cname)} {ge.esc(sname)} chapter "{ge.esc(chapter)}" as a free PDF — no signup, no download limit. Part of the complete NCERT {ge.esc(cname)} {ge.esc(sname)} syllabus, all {len(srows)} chapters available on YESPYQ.</p>
      <div class="ncert-list">{ncert_card(row)}</div>
      <div class="q-nav" style="display:flex;gap:.7rem;flex-wrap:wrap;margin:1.4rem 0">{nav_links}</div>
      <div class="cta-box">
        <h2>More NCERT {ge.esc(cname)} {ge.esc(sname)} chapters</h2>
        <p>Browse every {ge.esc(sname)} chapter for {ge.esc(cname)}, or explore all NCERT PDFs.</p>
        <a href="/ncert-pdfs/class-{cslug}/{sslug}/" class="btn btn-primary">All {ge.esc(cname)} {ge.esc(sname)} chapters →</a>
      </div>
      <section class="related">
        <h2>Other NCERT {ge.esc(cname)} {ge.esc(sname)} chapters</h2>
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
    ge.write("ncert-pdfs", hub(rows))
    urls = [f"{BASE}/ncert-pdfs/"]

    for cid, cslug, cname in class_list(rows):
        crows = [r for r in rows if r["class_slug"] == cslug]
        ge.write(f"ncert-pdfs/{cslug}", class_page(cid, cname, rows))
        urls.append(f"{BASE}/ncert-pdfs/{cslug}/")
        subs = sorted(set((r["subject_slug"], r["subject"]) for r in crows))
        for sslug, sname in subs:
            ge.write(f"ncert-pdfs/{cslug}/{sslug}", subject_page(cid, cname, sslug, sname, rows))
            urls.append(f"{BASE}/ncert-pdfs/{cslug}/{sslug}/")
            srows = [r for r in crows if r["subject_slug"] == sslug]
            for row in srows:
                ge.write(f"ncert-pdfs/{cslug}/{sslug}/{row['chapter_slug']}", chapter_page(cid, cname, sslug, sname, row, srows))
                urls.append(f"{BASE}/ncert-pdfs/{cslug}/{sslug}/{row['chapter_slug']}/")

    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>")
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap-ncert.xml"), "w").write("\n".join(sm) + "\n")

    print(f"Wrote {len(urls)} NCERT PDF pages ({len(rows)} PDFs).")


if __name__ == "__main__":
    main()
