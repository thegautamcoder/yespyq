#!/usr/bin/env python3
"""Generate JEE/NEET exam pages for YESPYQ.
- /exams/                         hub (all exams, incl. link back to UPSC's /pyq/)
- /exams/<exam>/                  exam hub (subject tiles)
- /exams/<exam>/<subject>/        subject index (chapter list)
- /exams/<exam>/<subject>/<ch>/   chapter page — all clean questions, grouped
- sitemap-exams.xml               all of the above
Run from repo root: python3 _gen_exams.py
"""
import json, os, re
from collections import defaultdict

BASE = "https://yespyq.com"
TODAY = "2026-07-15"
ROOT = os.path.dirname(os.path.abspath(__file__))

EXAMS = {
    "jee": {
        "name": "JEE",
        "full": "JEE (Main & Advanced)",
        "desc": "engineering entrance",
        "icon": "🛠️",
        "subjects": {
            "physics": ("Physics", "🧲"),
            "chemistry": ("Chemistry", "🧪"),
        },
    },
    "neet": {
        "name": "NEET",
        "full": "NEET-UG",
        "desc": "medical entrance",
        "icon": "🩺",
        "subjects": {
            "physics": ("Physics", "🧲"),
            "chemistry": ("Chemistry", "🧪"),
            "biology": ("Biology", "🧬"),
        },
    },
}


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def plain(s):
    s = re.sub(r"<[^>]+>", " ", str(s))
    return re.sub(r"\s+", " ", s).strip()


def attr(s):
    return plain(s).replace('"', "&quot;").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", plain(s).lower()).strip("-")
    return s or "general"


ABBR = set("Dr Mr Mrs Ms Smt Shri Sh Prof Rev Hon St Lt Col Gen Capt Sgt Ex No Art Sec Fig Vol Rs vs etc Pvt Ltd Co viz Mt Govt Deptt".split())


def break_sentences(t):
    def repl(m):
        if m.group(1) == ".":
            before = t[: m.start()]
            wm = re.search(r"(\S+)$", before)
            core = wm.group(1) if wm else ""
            if re.match(r"^(?:[A-Za-z]\.)*[A-Za-z]$", core):
                return m.group(0)
            if re.match(r"^\d+$", core):
                return m.group(0)
            if re.sub(r"[^A-Za-z]", "", core) in ABBR:
                return m.group(0)
        return m.group(1) + "\n"
    return re.sub(r"([.?!])\s+(?=[A-Z0-9\"(])", repl, t)


def format_body(raw, is_q):
    t = re.sub(r"[\x80-\x9F•‣▪●·]+", " \n ", str(raw))
    t = esc(t)
    t = re.sub(r"[^\S\n]+", " ", t)
    if is_q:
        t = re.sub(r"(^|\s)([A-E])\.\s+(?=[A-Z])", r"\1\n\2. ", t)
        t = re.sub(r"[^\S\n]*(\d{1,2})\.\s+", r"\n\1. ", t)
        t = re.sub(r"\s*(Codes?\s*:)", r"\n\1", t)
    else:
        t = re.sub(r"\s*(Statement\s+\d+\b)", r"\n\1", t)
        t = re.sub(r"[^\S\n]*(\d{1,2})\.\s+", r"\n\1. ", t)
        t = break_sentences(t)
    out = []
    for ln in [s.strip() for s in t.split("\n") if s.strip()]:
        stmt = " stmt" if re.match(r"^(?:\d{1,2}|[A-E])\.\s", ln) else ""
        out.append(f'<span class="bline{stmt}">{ln}</span>')
    return "".join(out)


HEADER = '''  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="/"><img src="/assets/favicon.svg" alt="" class="brand-mark" /><span class="brand-name">YES<span>PYQ</span></span></a>
      <nav class="main-nav">
        <a href="/">Home</a>
        <a href="/pyq/">UPSC PYQs</a>
        <a href="/exams/" class="active">Exams</a>
        <a href="/subjects/">Subjects</a>
        <a href="/blog/">Blog</a>
      </nav>
      <a href="/exams/" class="btn btn-primary btn-sm">Browse Exams</a>
    </div>
  </header>'''

FOOTER = '''  <footer class="site-footer">
    <div class="container footer-inner">
      <div class="footer-brand"><img src="/assets/favicon.svg" alt="" class="brand-mark" /><span class="brand-name">YES<span>PYQ</span></span><p>India's previous year questions hub — free practice with answers &amp; explanations.</p></div>
      <div class="footer-col"><h4>Exams</h4><a href="/exams/">All Exams</a><a href="/exams/jee/">JEE PYQs</a><a href="/exams/neet/">NEET PYQs</a><a href="/pyq/">UPSC PYQs</a></div>
      <div class="footer-col"><h4>Practice</h4><a href="/">Home</a><a href="/subjects/">Subjects</a><a href="/blog/">Blog</a><a href="/tools/">Tools</a></div>
      <div class="footer-col"><h4>Company</h4><a href="/about/">About</a><a href="/contact/">Contact</a><a href="/privacy-policy/">Privacy Policy</a><a href="/terms/">Terms &amp; Conditions</a><a href="/disclaimer/">Disclaimer</a></div>
    </div>
    <div class="footer-bottom">© <span id="year"></span> YESPYQ.com · Not affiliated with UPSC, NTA, JEE or NEET</div>
  </footer>
  <script>document.getElementById("year").textContent = new Date().getFullYear();</script>'''

EXTRA_CSS = '''  <style>
    .exam-tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:1rem;margin:1.6rem 0}
    .exam-tile{border:1.5px solid var(--line);border-radius:14px;padding:1.3rem;text-decoration:none;color:inherit;display:block;transition:border-color .15s,transform .15s}
    .exam-tile:hover{border-color:var(--blue-500,#2563eb);transform:translateY(-2px)}
    .exam-tile .et-icon{font-size:1.8rem}
    .exam-tile h3{margin:.5rem 0 .2rem;font-size:1.15rem}
    .exam-tile p{margin:0;color:var(--muted);font-size:.9rem}
    .chapter-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:.7rem;margin:1.4rem 0}
    .chapter-card{border:1.5px solid var(--line);border-radius:12px;padding:.9rem 1rem;text-decoration:none;color:inherit;display:flex;justify-content:space-between;align-items:center;gap:.5rem}
    .chapter-card:hover{border-color:var(--blue-500,#2563eb)}
    .chapter-card b{font-size:.92rem;line-height:1.3}
    .chapter-card span{font-size:.78rem;color:var(--muted);white-space:nowrap}
    .qblock{border:1.5px solid var(--line);border-radius:14px;padding:1.2rem;margin:1.1rem 0}
    .qblock .qnum{font-size:.78rem;font-weight:700;color:var(--muted);margin-bottom:.4rem}
    .qblock .qtext{font-weight:600;margin-bottom:.8rem;line-height:1.55}
    [data-theme="dark"] .exam-tile,[data-theme="dark"] .chapter-card,[data-theme="dark"] .qblock{border-color:var(--line)}
  </style>'''


def head(title, desc, canonical, schema_blocks):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-G2DK8674FB"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-G2DK8674FB');</script>
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <meta name="theme-color" content="#2563eb" />
  <link rel="canonical" href="{canonical}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="YESPYQ" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:image" content="{BASE}/assets/og-image.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg" />
  <link rel="manifest" href="/manifest.webmanifest" />
  <link rel="stylesheet" href="/styles.css?v=25" />
  <link rel="stylesheet" href="/blog.css?v=5" />
{schema_blocks}
{EXTRA_CSS}
  <script src="/theme.js?v=1"></script>
</head>
<body>'''


def load_bank(exam):
    return json.load(open(os.path.join(ROOT, "exam-data", f"{exam}.json")))


def qslug(x):
    return (x["i"].lower() + "-" + slugify(x["q"]))[:80].rstrip("-")


def question_block(x, n):
    opts = ""
    for i, o in enumerate(x["o"]):
        cls = "option" + (" correct" if i == x["a"] else "")
        opts += f'<div class="{cls}"><span class="key">{chr(97+i)}</span><span>{esc(o)}</span></div>'
    ans_letter = chr(97 + x["a"])
    ans_text = x["o"][x["a"]]
    year_tag = f'<span class="qtag">{x["y"]}</span>' if x.get("y") else ""
    return f'''    <div class="qblock" id="q{n}">
      <div class="qnum">Q{n}{year_tag and " · " + str(x["y"]) or ""}</div>
      <div class="qtext">{format_body(x["q"], True)}</div>
      <div class="options qpage-options">{opts}</div>
      <div class="explain">
        <div class="verdict ok">✓ Correct answer: {ans_letter}) {esc(ans_text)}</div>
        <div class="exp-body"><span class="lbl">Explanation</span>{format_body(x["exp"], False)}</div>
      </div>
    </div>'''


def chapter_page(exam, subject, chapter, items):
    ecfg = EXAMS[exam]
    sname, sicon = ecfg["subjects"][subject]
    slug = slugify(chapter)
    canonical = f"{BASE}/exams/{exam}/{subject}/{slug}/"
    title = attr(f"{chapter} — {ecfg['name']} {sname} PYQs with Answers | YESPYQ")
    desc = attr(f"{len(items)} solved {ecfg['name']} {sname} previous year questions on {chapter}, each with the correct answer and explanation. Free practice on YESPYQ.")

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"Exams","item":"{BASE}/exams/"}},{{"@type":"ListItem","position":3,"name":"{esc(ecfg['name'])}","item":"{BASE}/exams/{exam}/"}},{{"@type":"ListItem","position":4,"name":"{esc(sname)}","item":"{BASE}/exams/{exam}/{subject}/"}},{{"@type":"ListItem","position":5,"name":"{esc(chapter)}","item":"{canonical}"}}]}}
  </script>'''

    qs_html = "\n".join(question_block(x, i + 1) for i, x in enumerate(items))

    body = f'''{HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/exams/">Exams</a> › <a href="/exams/{exam}/">{esc(ecfg['name'])}</a> › <a href="/exams/{exam}/{subject}/">{esc(sname)}</a> › {esc(chapter)}</nav>
      <div class="qtags"><span class="qtag">{ecfg['icon']} {esc(ecfg['name'])}</span><span class="qtag">{sicon} {esc(sname)}</span></div>
      <h1>{esc(chapter)}</h1>
      <p>{len(items)} solved {esc(ecfg['name'])} {esc(sname)} previous year questions on <b>{esc(chapter)}</b>, each with the correct answer and a full explanation.</p>
{qs_html}
      <div class="cta-box">
        <h3>Practice more {esc(ecfg['name'])} {esc(sname)} PYQs</h3>
        <p>Browse every {esc(sname)} chapter, or explore the full {esc(ecfg['name'])} question bank.</p>
        <a href="/exams/{exam}/{subject}/" class="btn btn-primary">{sicon} All {esc(sname)} chapters →</a>
      </div>
    </article>
  </main>
{FOOTER}
</body>
</html>'''
    return head(title, desc, canonical, schema) + body


def subject_index(exam, subject, by_chapter):
    ecfg = EXAMS[exam]
    sname, sicon = ecfg["subjects"][subject]
    canonical = f"{BASE}/exams/{exam}/{subject}/"
    total = sum(len(v) for v in by_chapter.values())
    title = attr(f"{ecfg['name']} {sname} PYQs — {total} Solved Previous Year Questions | YESPYQ")
    desc = attr(f"Browse {len(by_chapter)} {ecfg['name']} {sname} chapters with {total} solved previous year questions, each with the correct answer and a detailed explanation. Free on YESPYQ.")

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"Exams","item":"{BASE}/exams/"}},{{"@type":"ListItem","position":3,"name":"{esc(ecfg['name'])}","item":"{BASE}/exams/{exam}/"}},{{"@type":"ListItem","position":4,"name":"{esc(sname)}","item":"{canonical}"}}]}}
  </script>'''

    cards = ""
    for ch in sorted(by_chapter, key=lambda c: -len(by_chapter[c])):
        n = len(by_chapter[ch])
        cslug = slugify(ch)
        cards += f'<a class="chapter-card" href="/exams/{exam}/{subject}/{cslug}/"><b>{esc(ch)}</b><span>{n} Q</span></a>'

    body = f'''{HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/exams/">Exams</a> › <a href="/exams/{exam}/">{esc(ecfg['name'])}</a> › {esc(sname)}</nav>
      <div class="qtags"><span class="qtag">{ecfg['icon']} {esc(ecfg['name'])}</span></div>
      <h1>{sicon} {esc(ecfg['name'])} {esc(sname)} PYQs</h1>
      <p>{total} solved {esc(ecfg['name'])} {esc(sname)} previous year questions across {len(by_chapter)} chapters. Pick a chapter to practice.</p>
      <div class="chapter-list">{cards}</div>
    </article>
  </main>
{FOOTER}
</body>
</html>'''
    return head(title, desc, canonical, schema) + body


def exam_hub(exam, by_subject):
    ecfg = EXAMS[exam]
    canonical = f"{BASE}/exams/{exam}/"
    total = sum(len(v) for v in by_subject.values())
    title = attr(f"{ecfg['full']} PYQs — {total} Solved Previous Year Questions | YESPYQ")
    desc = attr(f"Free {ecfg['full']} previous year questions ({ecfg['desc']}), subject-wise, each with the correct answer and a detailed explanation. Practice on YESPYQ.")

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"Exams","item":"{BASE}/exams/"}},{{"@type":"ListItem","position":3,"name":"{esc(ecfg['name'])}","item":"{canonical}"}}]}}
  </script>'''

    tiles = ""
    for sid, (sname, sicon) in ecfg["subjects"].items():
        n = len(by_subject.get(sid, []))
        tiles += f'<a class="exam-tile" href="/exams/{exam}/{sid}/"><div class="et-icon">{sicon}</div><h3>{esc(sname)}</h3><p>{n} solved PYQs</p></a>'

    body = f'''{HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/exams/">Exams</a> › {esc(ecfg['name'])}</nav>
      <h1>{ecfg['icon']} {esc(ecfg['full'])} PYQs</h1>
      <p>{total} solved previous year questions for {esc(ecfg['full'])} ({esc(ecfg['desc'])}), organised by subject — each with the correct answer and a full explanation.</p>
      <div class="exam-tiles">{tiles}</div>
    </article>
  </main>
{FOOTER}
</body>
</html>'''
    return head(title, desc, canonical, schema) + body


def exams_hub(counts):
    canonical = f"{BASE}/exams/"
    total = sum(counts.values())
    title = attr(f"India's PYQ Hub — UPSC, JEE, NEET Previous Year Questions | YESPYQ")
    desc = attr(f"Free previous year questions for UPSC, JEE and NEET — {total}+ solved questions with answers and explanations. Pick your exam to start practicing.")

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"Exams","item":"{canonical}"}}]}}
  </script>'''

    tiles = f'<a class="exam-tile" href="/pyq/"><div class="et-icon">🏛️</div><h3>UPSC (CSE Prelims)</h3><p>2,200+ solved PYQs</p></a>'
    for exam, ecfg in EXAMS.items():
        tiles += f'<a class="exam-tile" href="/exams/{exam}/"><div class="et-icon">{ecfg["icon"]}</div><h3>{esc(ecfg["full"])}</h3><p>{counts.get(exam,0)} solved PYQs</p></a>'

    body = f'''{HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › Exams</nav>
      <h1>India's Previous Year Questions Hub</h1>
      <p>YESPYQ is expanding beyond UPSC — solved previous year questions for every major Indian exam, all free, all with answers and explanations. Pick your exam below.</p>
      <div class="exam-tiles">{tiles}</div>
      <p style="margin-top:2rem;color:var(--muted);font-size:.9rem">More exams (SSC, Banking, TET, Defence and others) are on the way.</p>
    </article>
  </main>
{FOOTER}
</body>
</html>'''
    return head(title, desc, canonical, schema) + body


def write(path, content):
    full = os.path.join(ROOT, path, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(content)


def main():
    sitemap_urls = []
    exam_totals = {}

    for exam, ecfg in EXAMS.items():
        items = load_bank(exam)
        by_subject = defaultdict(list)
        for x in items:
            by_subject[x["subject"]].append(x)
        exam_totals[exam] = len(items)

        for subject in ecfg["subjects"]:
            sitems = by_subject.get(subject, [])
            by_chapter = defaultdict(list)
            for x in sitems:
                by_chapter[x["chapter"]].append(x)

            for chapter, qs in by_chapter.items():
                write(f"exams/{exam}/{subject}/{slugify(chapter)}", chapter_page(exam, subject, chapter, qs))
                sitemap_urls.append((f"{BASE}/exams/{exam}/{subject}/{slugify(chapter)}/", "0.6"))

            write(f"exams/{exam}/{subject}", subject_index(exam, subject, by_chapter))
            sitemap_urls.append((f"{BASE}/exams/{exam}/{subject}/", "0.7"))

        write(f"exams/{exam}", exam_hub(exam, by_subject))
        sitemap_urls.append((f"{BASE}/exams/{exam}/", "0.8"))

    write("exams", exams_hub(exam_totals))
    sitemap_urls.append((f"{BASE}/exams/", "0.9"))

    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, pr in sitemap_urls:
        sm.append(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>{pr}</priority></url>")
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap-exams.xml"), "w").write("\n".join(sm))

    print(f"Wrote exam pages. Totals: {exam_totals}. Sitemap URLs: {len(sitemap_urls)}")


if __name__ == "__main__":
    main()
