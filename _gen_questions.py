#!/usr/bin/env python3
"""Generate per-question SEO pages (question + solution) for YESPYQ.
- /pyq/                      hub
- /pyq/<subject>/            per-subject question index
- /pyq/q/<slug>/             one page per question (QAPage schema)
- sitemap-questions.xml      all of the above
Run from repo root: python3 _gen_questions.py
"""
import re, json, os, html
from collections import defaultdict

BASE = "https://yespyq.com"
TODAY = "2026-06-30"
ROOT = os.path.dirname(os.path.abspath(__file__))

SUB = {
    "polity": ("Polity & Governance", "⚖️", "polity"),
    "history": ("History & Art-Culture", "🏛️", "history"),
    "geography": ("Geography", "🌍", "geography"),
    "economy": ("Economy", "📈", "economy"),
    "environment": ("Environment & Ecology", "🌱", "environment"),
    "science": ("Science & Technology", "🔬", "science-technology"),
    "currentaff": ("Current Affairs", "🗞️", "current-affairs"),
}

# ---------- load + clean (mirrors app.js isCleanQ) ----------
Q = json.loads(re.search(r'QUESTIONS\.push\(\.\.\.(\[.*\])\);', open(os.path.join(ROOT, 'pyq.js')).read(), re.S).group(1))
EXP = json.loads(re.search(r'window\.EXP\s*=\s*(\{.*\})\s*;?\s*$', open(os.path.join(ROOT, 'pyq-exp.js')).read(), re.S).group(1))
BAD = re.compile(r'consider the following|incorrect\s*:|correct\s*:|\([a-d]\)\s|\(20\d\d\)|select the correct answer', re.I)

def is_clean(x):
    qq = (x.get('q') or '').strip(); o = x.get('o') or []; a = x.get('a')
    if len(o) != 4 or len(qq) < 12: return False
    if not isinstance(a, int) or a < 0 or a >= len(o): return False
    if re.search(r'\bOptions?\s*$', qq): return False
    for t in o:
        t = (t or '').strip()
        if len(t) < 1 or len(t) > 180: return False
        if len(t) <= 2 and not t.isalnum(): return False
        if BAD.search(t): return False
    return True

ITEMS = [x for x in Q if is_clean(x) and len((EXP.get(x['i']) or '').strip()) >= 120]

# ---------- formatter (port of app.js formatBody) ----------
ABBR = set("Dr Mr Mrs Ms Smt Shri Sh Prof Rev Hon St Lt Col Gen Capt Sgt Ex No Art Sec Fig Vol Rs vs etc Pvt Ltd Co viz Mt Govt Deptt".split())
def esc(s): return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def break_sentences(t):
    def repl(m):
        if m.group(1) == ".":
            before = t[:m.start()]
            wm = re.search(r'(\S+)$', before)
            core = wm.group(1) if wm else ""
            if re.match(r'^(?:[A-Za-z]\.)*[A-Za-z]$', core): return m.group(0)
            if re.match(r'^\d+$', core): return m.group(0)
            if re.sub(r'[^A-Za-z]', '', core) in ABBR: return m.group(0)
        return m.group(1) + "\n"
    return re.sub(r'([.?!])\s+(?=[A-Z0-9"(])', repl, t)

def format_body(raw, is_q):
    t = re.sub(r'[\x80-\x9F•‣▪●·]+', ' \n ', str(raw))
    t = esc(t)
    t = re.sub(r'[^\S\n]+', ' ', t)
    if is_q:
        t = re.sub(r'(^|\s)([A-E])\.\s+(?=[A-Z])', r'\1\n\2. ', t)
        t = re.sub(r'[^\S\n]*(\d{1,2})\.\s+', r'\n\1. ', t)
        t = re.sub(r'\s*(Codes?\s*:)', r'\n\1', t)
        t = re.sub(r'\s*(How many of the |Which of the statements |Which of the above |Which one of the following |Select the correct answer |Consider the following codes )', r'\n\1', t)
    else:
        t = re.sub(r'\s*(Statement\s+\d+\b)', r'\n\1', t)
        t = re.sub(r'[^\S\n]*(\d{1,2})\.\s+', r'\n\1. ', t)
        t = break_sentences(t)
    out = []
    for ln in [s.strip() for s in t.split("\n") if s.strip()]:
        stmt = " stmt" if re.match(r'^(?:\d{1,2}|[A-E])\.\s', ln) else ""
        out.append(f'<span class="bline{stmt}">{ln}</span>')
    return "".join(out)

def plain(s):
    s = re.sub(r'<[^>]+>', ' ', str(s))
    return re.sub(r'\s+', ' ', s).strip()

def slugify(s):
    s = re.sub(r'[^a-z0-9]+', '-', plain(s).lower()).strip('-')
    return s

def qslug(x):
    return (x['i'].lower() + "-" + slugify(x['q']))[:80].rstrip('-')

def attr(s):  # safe for HTML attribute (title/meta content)
    return plain(s).replace('"', '&quot;').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# precompute slugs + groupings
SLUG = {x['i']: qslug(x) for x in ITEMS}
BY_SUB = defaultdict(list)
for x in ITEMS:
    BY_SUB[x['s']].append(x)

HEADER = '''  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="/"><img src="/assets/favicon.svg" alt="" class="brand-mark" /><span class="brand-name">YES<span>PYQ</span></span></a>
      <nav class="main-nav">
        <a href="/">Home</a>
        <a href="/">Practice</a>
        <a href="/subjects/">Subjects</a>
      </nav>
      <a href="/" class="btn btn-primary btn-sm">Start Practice</a>
    </div>
  </header>'''

FOOTER = '''  <footer class="site-footer">
    <div class="container footer-inner">
      <div class="footer-brand"><img src="/assets/favicon.svg" alt="" class="brand-mark" /><span class="brand-name">YES<span>PYQ</span></span><p>Previous Year Questions, simplified.</p></div>
      <div class="footer-col"><h4>Practice</h4><a href="/">Home</a><a href="/subjects/">Subjects</a><a href="/pyq/">All PYQs</a><a href="/guides/">Guides</a><a href="/blog/">Blog</a></div>
      <div class="footer-col"><h4>Company</h4><a href="/about/">About</a><a href="/contact/">Contact</a></div>
      <div class="footer-col"><h4>Legal</h4><a href="/privacy-policy/">Privacy Policy</a><a href="/terms/">Terms &amp; Conditions</a><a href="/disclaimer/">Disclaimer</a></div>
    </div>
    <div class="footer-bottom">© <span id="year"></span> YESPYQ.com · Built for UPSC CSE aspirants · Not affiliated with UPSC</div>
  </footer>
  <script>document.getElementById("year").textContent = new Date().getFullYear();</script>'''

def head(title, desc, canonical, schema_blocks, og_type="article"):
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
  <meta name="googlebot" content="index, follow" />
  <meta name="author" content="YESPYQ" />
  <meta name="theme-color" content="#2563eb" />
  <link rel="canonical" href="{canonical}" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:site_name" content="YESPYQ" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:image" content="{BASE}/assets/og-image.png" />
  <meta property="og:locale" content="en_IN" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{desc}" />
  <meta name="twitter:image" content="{BASE}/assets/og-image.png" />
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg" />
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" />
  <link rel="manifest" href="/manifest.webmanifest" />
  <link rel="stylesheet" href="/styles.css?v=22" />
  <link rel="stylesheet" href="/blog.css?v=5" />
{schema_blocks}
  <script src="/theme.js?v=1"></script>
</head>
<body>'''

def question_page(x):
    sname, sicon, shub = SUB[x['s']]
    slug = SLUG[x['i']]
    canonical = f"{BASE}/pyq/q/{slug}/"
    year = x.get('y') or ""
    qplain = plain(x['q'])
    short = qplain[:64].rsplit(' ', 1)[0] if len(qplain) > 64 else qplain
    title = attr(f"{short} — UPSC {year} {sname.split(' ')[0]} PYQ | YESPYQ")
    desc = attr(f"{qplain[:150]} — see the correct answer and a detailed explanation. Free UPSC CSE Prelims PYQ practice on YESPYQ.")
    expl = EXP.get(x['i'], "")
    ans_letter = chr(97 + x['a'])
    ans_text = x['o'][x['a']]

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"QAPage","mainEntity":{{"@type":"Question","name":"{attr(x['q'])}","text":"{attr(x['q'])}","answerCount":1,"acceptedAnswer":{{"@type":"Answer","text":"{attr('Correct answer: ' + ans_text + '. ' + plain(expl))[:1100]}"}}}}}}
  </script>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"PYQs","item":"{BASE}/pyq/"}},{{"@type":"ListItem","position":3,"name":"{attr(sname)}","item":"{BASE}/pyq/{x['s']}/"}},{{"@type":"ListItem","position":4,"name":"Question","item":"{canonical}"}}]}}
  </script>'''

    opts = ""
    for i, o in enumerate(x['o']):
        cls = "option" + (" correct" if i == x['a'] else "")
        opts += f'<div class="{cls}"><span class="key">{chr(97 + i)}</span><span>{esc(o)}</span></div>'

    # related: same chapter first, then same subject
    pool = [r for r in BY_SUB[x['s']] if r['i'] != x['i']]
    pool.sort(key=lambda r: (r.get('c') != x.get('c')))
    rel = pool[:6]
    rel_html = "".join(
        f'<a href="/pyq/q/{SLUG[r["i"]]}/"><span class="tag">{sicon} {sname.split(" ")[0]}{(" · " + str(r["y"])) if r.get("y") else ""}</span><b>{esc(plain(r["q"])[:90])}…</b></a>'
        for r in rel)

    body = f'''{HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/pyq/">PYQs</a> › <a href="/pyq/{x['s']}/">{esc(sname)}</a> › Question</nav>
      <div class="qmeta-tags"><span class="qtag">{sicon} {esc(sname)}</span>{f'<span class="qtag">UPSC {year}</span>' if year else ''}{f'<span class="qtag">{esc(x.get("c",""))}</span>' if x.get("c") else ''}</div>
      <h1 class="qpage-h1 qtext">{format_body(x['q'], True)}</h1>
      <div class="options qpage-options">{opts}</div>
      <div class="explain">
        <div class="verdict ok">✓ Correct answer: {ans_letter}) {esc(ans_text)}</div>
        <div class="exp-body"><span class="lbl">Explanation</span>{format_body(expl, False)}</div>
      </div>
      <div class="cta-box">
        <h3>Practice more {esc(sname.split(' ')[0])} PYQs</h3>
        <p>Attempt a free 10-question quiz or browse the full {esc(sname)} previous-year-question bank with instant answers and explanations.</p>
        <a href="/subjects/{shub}/" class="btn btn-primary">{sicon} {esc(sname.split(' ')[0])} PYQs →</a>
      </div>
      <section class="related">
        <h2>More UPSC {esc(sname.split(' ')[0])} PYQs</h2>
        <div class="related-list">{rel_html}</div>
      </section>
    </article>
  </main>
{FOOTER}
</body>
</html>'''
    return head(title, desc, canonical, schema) + body

def subject_index(sid):
    sname, sicon, shub = SUB[sid]
    items = BY_SUB[sid]
    canonical = f"{BASE}/pyq/{sid}/"
    title = attr(f"UPSC {sname} PYQs — {len(items)} Solved Previous Year Questions | YESPYQ")
    desc = attr(f"Browse {len(items)} solved UPSC CSE Prelims {sname} previous year questions with correct answers and detailed explanations. Free PYQ practice on YESPYQ.")
    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"PYQs","item":"{BASE}/pyq/"}},{{"@type":"ListItem","position":3,"name":"{attr(sname)}","item":"{canonical}"}}]}}
  </script>'''
    # group by year desc
    by_year = defaultdict(list)
    for x in items: by_year[x.get('y') or 0].append(x)
    listing = ""
    for y in sorted(by_year, reverse=True):
        ylabel = f"UPSC {y}" if y else "Other"
        listing += f'<h2 class="pyq-year">{ylabel}</h2><ul class="pyq-list">'
        for x in by_year[y]:
            listing += f'<li><a href="/pyq/q/{SLUG[x["i"]]}/">{esc(plain(x["q"])[:110])}{"…" if len(plain(x["q"]))>110 else ""}</a></li>'
        listing += '</ul>'
    body = f'''{HEADER}
  <main>
    <section class="blog-hero"><div class="container"><span class="pill">UPSC CSE Prelims</span>
      <h1>UPSC {esc(sname)} — Solved Previous Year Questions</h1>
      <p>{len(items)} authentic {esc(sname)} PYQs with correct answers and detailed explanations. Click any question to see its full solution.</p></div></section>
    <div class="container">
      <p class="pyq-cross"><a href="/subjects/{shub}/">About {esc(sname.split(' ')[0])} PYQs &amp; strategy →</a> · <a href="/pyq/">All subjects</a></p>
      {listing}
    </div>
  </main>
{FOOTER}
</body>
</html>'''
    return head(title, desc, canonical, schema, "website") + body

def hub():
    canonical = f"{BASE}/pyq/"
    total = len(ITEMS)
    title = attr(f"UPSC PYQs with Answers — {total} Solved Previous Year Questions | YESPYQ")
    desc = attr(f"Browse {total} solved UPSC CSE Prelims previous year questions (PYQs) with correct answers and detailed explanations, organised by subject. Free practice on YESPYQ.")
    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"PYQs","item":"{canonical}"}}]}}
  </script>'''
    cards = ""
    for sid, (sname, sicon, shub) in SUB.items():
        n = len(BY_SUB[sid])
        if not n: continue
        cards += f'<a class="post-card" href="/pyq/{sid}/"><span class="tag">{sicon} {esc(sname.split(" ")[0])}</span><h2>{esc(sname)} PYQs</h2><p>{n} solved previous year questions with answers &amp; explanations.</p><span class="read">Browse {n} questions →</span></a>'
    body = f'''{HEADER}
  <main>
    <section class="blog-hero"><div class="container"><span class="pill">UPSC CSE Prelims</span>
      <h1>UPSC Previous Year Questions with Answers &amp; Explanations</h1>
      <p>{total} solved UPSC CSE Prelims PYQs — every question with its correct answer and a detailed explanation. Pick a subject to start.</p></div></section>
    <div class="container"><div class="post-grid">{cards}</div>
      <div class="prose" style="width:min(740px,92vw);margin:0 auto 3rem">
        <h2>Solved UPSC PYQs, free and searchable</h2>
        <p>Every previous-year question here is on its own page with the four options, the correct answer and a full explanation — so you can revise a single concept or search for an exact question and land straight on its solution. For focused practice, take a <a href="/">10-question quiz</a> or explore <a href="/subjects/">subject-wise PYQs and strategy</a>.</p>
      </div>
    </div>
  </main>
{FOOTER}
</body>
</html>'''
    return head(title, desc, canonical, schema, "website") + body

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

def main():
    write(os.path.join(ROOT, "pyq", "index.html"), hub())
    for sid in SUB:
        if BY_SUB[sid]:
            write(os.path.join(ROOT, "pyq", sid, "index.html"), subject_index(sid))
    for x in ITEMS:
        write(os.path.join(ROOT, "pyq", "q", SLUG[x['i']], "index.html"), question_page(x))

    # sitemap-questions.xml
    urls = [f"{BASE}/pyq/"]
    urls += [f"{BASE}/pyq/{sid}/" for sid in SUB if BY_SUB[sid]]
    urls += [f"{BASE}/pyq/q/{SLUG[x['i']]}/" for x in ITEMS]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        pr = "0.8" if u.endswith("/pyq/") or u.count("/") == 4 else "0.6"
        sm.append(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>{pr}</priority></url>")
    sm.append("</urlset>")
    write(os.path.join(ROOT, "sitemap-questions.xml"), "\n".join(sm) + "\n")
    print(f"wrote {len(ITEMS)} question pages + {sum(1 for s in SUB if BY_SUB[s])} subject indexes + hub")
    print(f"sitemap-questions.xml: {len(urls)} URLs")

if __name__ == "__main__":
    main()
