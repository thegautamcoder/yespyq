#!/usr/bin/env python3
"""Generate JEE/NEET exam pages for YESPYQ.
- /exams/                         hub (all exams, incl. link back to UPSC's /pyq/)
- /exams/<exam>/                  exam hub (subject tiles)
- /exams/<exam>/<subject>/        subject index (chapter list)
- /exams/<exam>/<subject>/<ch>/   chapter page — all clean questions, grouped
- sitemap-exams.xml               all of the above
Run from repo root: python3 _gen_exams.py
"""
import datetime, json, os, re
from collections import defaultdict

BASE = "https://yespyq.com"
TODAY = datetime.date.today().isoformat()
ROOT = os.path.dirname(os.path.abspath(__file__))

SUBJECT_LABELS = {
    "physics": ("Physics", "🧲"),
    "chemistry": ("Chemistry", "🧪"),
    "maths": ("Maths", "➗"),
    "biology": ("Biology", "🧬"),
    "english": ("English", "🔤"),
    "hindi": ("Hindi", "🪔"),
    "sanskrit": ("Sanskrit", "📜"),
    "history": ("History", "🏛️"),
    "geography": ("Geography", "🌍"),
    "polity": ("Political Science", "⚖️"),
    "economics": ("Economics", "📈"),
    "accountancy": ("Accountancy", "📒"),
    "business-studies": ("Business Studies", "💼"),
    "social-studies": ("Social Studies", "🌏"),
    "psychology": ("Psychology", "🧠"),
    "sociology": ("Sociology", "👥"),
    "general": ("General", "📘"),
}


def subject_meta(sid):
    if sid in SUBJECT_LABELS:
        return SUBJECT_LABELS[sid]
    name = sid.replace("-", " ").title()
    return (name, "📘")


def resolve_subjects(ecfg, by_subject):
    """Prefer configured subjects, then any extra subjects present in the bank."""
    ordered = {}
    for sid, meta in ecfg["subjects"].items():
        if sid in by_subject and by_subject[sid]:
            ordered[sid] = meta
    for sid in sorted(by_subject, key=lambda s: (-len(by_subject[s]), s)):
        if sid not in ordered and by_subject[sid]:
            ordered[sid] = subject_meta(sid)
    return ordered


EXAMS = {
    "jee": {
        "name": "JEE",
        "full": "JEE (Main & Advanced)",
        "desc": "engineering entrance",
        "icon": "🛠️",
        "gated": True,
        "subjects": {
            "physics": ("Physics", "🧲"),
            "chemistry": ("Chemistry", "🧪"),
            "maths": ("Maths", "➗"),
        },
    },
    "neet": {
        "name": "NEET",
        "full": "NEET-UG",
        "desc": "medical entrance",
        "icon": "🩺",
        "gated": True,
        "subjects": {
            "physics": ("Physics", "🧲"),
            "chemistry": ("Chemistry", "🧪"),
            "biology": ("Biology", "🧬"),
        },
    },
    "board": {
        "name": "Board",
        "full": "Board Exams (Class 11 & 12)",
        "desc": "school board exams",
        "icon": "🏫",
        "gated": True,
        "subjects": {
            "physics": ("Physics", "🧲"),
            "chemistry": ("Chemistry", "🧪"),
            "maths": ("Maths", "➗"),
            "english": ("English", "🔤"),
            "hindi": ("Hindi", "🪔"),
            "biology": ("Biology", "🧬"),
            "history": ("History", "🏛️"),
            "geography": ("Geography", "🌍"),
            "polity": ("Political Science", "⚖️"),
            "economics": ("Economics", "📈"),
            "accountancy": ("Accountancy", "📒"),
            "business-studies": ("Business Studies", "💼"),
        },
    },
    "defence": {
        "name": "Defence",
        "full": "Defence Exams (Agniveer, AFCAT, Coast Guard & more)",
        "desc": "armed forces recruitment",
        "icon": "🎖️",
        "gated": True,
        "subjects": {
            "staticgk": ("Static GK", "🌐"),
            "currentaff": ("Current Affairs", "🗞️"),
            "economy": ("Economics", "📈"),
            "history": ("History", "🏛️"),
            "polity": ("Polity", "⚖️"),
            "english": ("English", "🔤"),
            "geography": ("Geography", "🌍"),
        },
    },
    "ssc-cgl": {
        "name": "SSC CGL",
        "full": "SSC CGL (Combined Graduate Level)",
        "desc": "staff selection commission",
        "icon": "📝",
        "gated": True,
        "subjects": {
            "english": ("English", "🔤"),
            "history": ("History", "🏛️"),
            "economy": ("Economy", "📈"),
            "aptitude": ("Quantitative Aptitude", "🔢"),
            "reasoning": ("Reasoning", "🧩"),
            "computer": ("Computer Awareness", "💻"),
            "geography": ("Geography", "🌍"),
            "science": ("Science", "🔬"),
            "gk": ("General Knowledge", "🌐"),
            "polity": ("Polity", "⚖️"),
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
      <a class="brand" href="/"><span class="brand-name">YES<span>PYQ</span></span></a>
      <nav class="main-nav">
        <a href="/">Home</a>
        <a href="/">Practice</a>
        <a href="/">Smart Mock</a>
        <a href="/exams/" class="active">Exams</a>
        <a href="/blog/">Blog</a>
        <a href="/pyq-pass/">PYQ Pass</a>
      </nav>
      <a href="/" class="btn btn-ghost btn-sm">Start Practice</a>
    </div>
  </header>'''

FOOTER = '''  <footer class="site-footer">
    <div class="container footer-inner">
      <div class="footer-brand"><span class="brand-name">YES<span>PYQ</span></span><p>India's previous year questions hub, simplified — free practice with answers &amp; explanations.</p><a class="footer-social" href="https://www.youtube.com/@YesPYQ.Official" target="_blank" rel="noopener">▶ YouTube</a></div>
      <div class="footer-col"><h4>Practice</h4><a href="/">Home</a><a href="/exams/">All Exams</a><a href="/pyq/">UPSC PYQs</a><a href="/subjects/">Subjects</a><a href="/guides/">Guides</a><a href="/blog/">Blog</a><a href="/tools/">Tools</a></div>
      <div class="footer-col"><h4>Exams</h4><a href="/pyq/">UPSC PYQs</a><a href="/exams/jee/">JEE PYQs</a><a href="/exams/neet/">NEET PYQs</a><a href="/exams/board/">Board Exam PYQs</a><a href="/exams/defence/">Defence PYQs</a><a href="/exams/ssc-cgl/">SSC CGL PYQs</a></div>
      <div class="footer-col"><h4>UPSC Subjects</h4><a href="/subjects/polity/">Polity PYQs</a><a href="/subjects/history/">History PYQs</a><a href="/subjects/geography/">Geography PYQs</a><a href="/subjects/economy/">Economy PYQs</a><a href="/subjects/environment/">Environment PYQs</a><a href="/subjects/science-technology/">Science &amp; Tech PYQs</a><a href="/subjects/current-affairs/">Current Affairs PYQs</a></div>
      <div class="footer-col"><h4>UPSC PYQs by Year</h4><a href="/pyq/year/2024/">UPSC 2024</a><a href="/pyq/year/2023/">UPSC 2023</a><a href="/pyq/year/2022/">UPSC 2022</a><a href="/pyq/year/2021/">UPSC 2021</a><a href="/pyq/year/2020/">UPSC 2020</a><a href="/pyq/">All Years</a></div>
      <div class="footer-col"><h4>Popular Explainers</h4><a href="/blog/goods-and-services-tax-gst/">GST Explained</a><a href="/blog/fundamental-rights-explained/">Fundamental Rights</a><a href="/blog/monetary-policy-repo-rate/">Monetary Policy</a><a href="/blog/niti-aayog-explained/">NITI Aayog</a><a href="/blog/inflation-cpi-wpi-explained/">Inflation: CPI vs WPI</a><a href="/blog/fiscal-deficit-explained/">Fiscal Deficit</a></div>
      <div class="footer-col"><h4>Company</h4><a href="/about/">About</a><a href="/pyq-pass/">PYQ Pass</a><a href="/contact/">Contact</a><a href="/privacy-policy/">Privacy Policy</a><a href="/terms/">Terms &amp; Conditions</a><a href="/disclaimer/">Disclaimer</a></div>
    </div>
    <div class="footer-bottom">© <span id="year"></span> YESPYQ.com · India's previous year questions hub · Not affiliated with UPSC, NTA, SSC, IBPS or any government body</div>
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
    .answer-gate{display:flex;align-items:center;gap:.8rem;border:1.5px dashed rgba(37,99,235,.4);border-radius:12px;padding:.9rem 1rem;margin:1rem 0;background:var(--card);cursor:pointer}
    .answer-gate .ag-lock{font-size:1.4rem;flex:none}
    .answer-gate div{flex:1;min-width:0}
    .answer-gate b{display:block;font-size:.92rem}
    .answer-gate p{margin:.15rem 0 0;font-size:.82rem;color:var(--muted)}
    .answer-gate .btn{flex:none}
    .free-tag{background:var(--good-bg,#dcfce7);color:var(--good,#16a34a);border-radius:6px;
      padding:.1rem .5rem;font-size:.68rem;font-weight:800;letter-spacing:.04em;margin-left:.4rem}
  </style>'''

KATEX_HEAD = '  <link rel="stylesheet" href="/assets/katex/katex.min.css" />'
KATEX_SCRIPTS = '''  <script defer src="/assets/katex/katex.min.js"></script>
  <script defer src="/assets/katex/auto-render.min.js"></script>
  <script defer src="/exam-gate.js?v=4"></script>
  <script>
  document.addEventListener("DOMContentLoaded", function () {
    if (window.renderMathInElement) {
      renderMathInElement(document.body, {
        delimiters: [
          {left: "$$", right: "$$", display: true},
          {left: "\\\\[", right: "\\\\]", display: true},
          {left: "\\\\(", right: "\\\\)", display: false}
        ],
        throwOnError: false
      });
    }
  });
  </script>'''


def head(title, desc, canonical, schema_blocks, extra_head=""):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="google-adsense-account" content="ca-pub-9837613085159910" />
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
  <link rel="stylesheet" href="/styles.css?v=71" />
  <link rel="stylesheet" href="/blog.css?v=5" />
{schema_blocks}
{EXTRA_CSS}
{extra_head}
  <script src="/theme.js?v=30"></script>
</head>
<body>'''


def load_bank(exam):
    return json.load(open(os.path.join(ROOT, "exam-data", f"{exam}.json")))


def qslug(x):
    return (x["i"].lower() + "-" + slugify(x["q"]))[:80].rstrip("-")


def question_block(x, n, gated, free=False):
    html_mode = x.get("fmt") == "html"
    q_html = x["q"] if html_mode else format_body(x["q"], True)
    year_suffix = f' · {x["y"]}' if x.get("y") else ""

    # Options are always public — only the correct answer + explanation are
    # Pass-gated for the ~90% non-preview questions.
    opts_plain = ""
    for i, o in enumerate(x["o"]):
        o_html = o if html_mode else esc(o)
        opts_plain += f'<div class="option"><span class="key">{chr(97+i)}</span><span>{o_html}</span></div>'

    if gated and not free:
        payload = json.dumps(
            {"a": x["a"], "exp": x["exp"], "fmt": x.get("fmt") or ""},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        payload = payload.replace("<", "\\u003c")
        return f'''    <div class="qblock" id="q{n}" data-gated="1">
      <div class="qnum">Q{n}{year_suffix}</div>
      <div class="qtext">{q_html}</div>
      <div class="options qpage-options">{opts_plain}</div>
      <div class="answer-gate" data-unlock="exam-answer">
        <span class="ag-lock">🔒</span>
        <div><b>Answer &amp; explanation — PYQ Pass</b><p>Options are free to see. Unlock the correct answer and full explanation with Pass.</p></div>
        <span class="btn btn-primary btn-sm" data-unlock="exam-answer">Unlock · ₹149</span>
      </div>
      <div class="explain hidden" data-exp></div>
      <script type="application/json" class="q-payload">{payload}</script>
    </div>'''

    opts = ""
    for i, o in enumerate(x["o"]):
        o_html = o if html_mode else esc(o)
        cls = "option" + (" correct" if i == x["a"] else "")
        opts += f'<div class="{cls}"><span class="key">{chr(97+i)}</span><span>{o_html}</span></div>'
    ans_letter = chr(97 + x["a"])
    ans_html = x["o"][x["a"]] if html_mode else esc(x["o"][x["a"]])
    exp_html = x["exp"] if html_mode else format_body(x["exp"], False)
    free_tag = ' <span class="free-tag">FREE PREVIEW</span>' if (gated and free) else ""
    return f'''    <div class="qblock" id="q{n}">
      <div class="qnum">Q{n}{year_suffix}{free_tag}</div>
      <div class="qtext">{q_html}</div>
      <div class="options qpage-options">{opts}</div>
      <div class="explain" data-exp>
        <div class="verdict ok">✓ Correct answer: {ans_letter}) {ans_html}</div>
        <div class="exp-body"><span class="lbl">Explanation</span>{exp_html}</div>
      </div>
    </div>'''


FREE_PREVIEW_PCT = 0.10


def free_preview_count(n):
    """At least 1 question free per chapter, ~10% of the rest, deterministic."""
    return max(1, round(n * FREE_PREVIEW_PCT))


def chapter_page(exam, subject, chapter, items):
    ecfg = EXAMS[exam]
    gated = ecfg.get("gated", False)
    free_n = free_preview_count(len(items)) if gated else len(items)
    sname, sicon = ecfg["subjects"][subject]
    slug = slugify(chapter)
    canonical = f"{BASE}/exams/{exam}/{subject}/{slug}/"
    title = attr(f"{chapter} — {ecfg['name']} {sname} PYQs with Answers | YESPYQ")
    if gated:
        desc = attr(f"{len(items)} {ecfg['name']} {sname} previous year questions on {chapter} — options free on every question, {free_n} with the answer & explanation free too, the rest unlock with PYQ Pass.")
    else:
        desc = attr(f"{len(items)} solved {ecfg['name']} {sname} previous year questions on {chapter}, each with the correct answer and explanation. Free practice on YESPYQ.")

    # Question stems listed for SEO; answers stay behind Pass on gated exams.
    item_els = []
    for i, x in enumerate(items[:40], 1):
        name = attr(plain(x["q"])[:140])
        item_els.append(
            f'{{"@type":"ListItem","position":{i},"name":"{name}","url":"{canonical}#q{i}"}}'
        )
    item_list = ",".join(item_els)
    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"Exams","item":"{BASE}/exams/"}},{{"@type":"ListItem","position":3,"name":"{esc(ecfg['name'])}","item":"{BASE}/exams/{exam}/"}},{{"@type":"ListItem","position":4,"name":"{esc(sname)}","item":"{BASE}/exams/{exam}/{subject}/"}},{{"@type":"ListItem","position":5,"name":"{esc(chapter)}","item":"{canonical}"}}]}}
  </script>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"ItemList","name":"{attr(chapter)} {ecfg['name']} {sname} PYQs","numberOfItems":{len(items)},"itemListElement":[{item_list}]}}
  </script>'''

    qs_html = "\n".join(
        question_block(x, i + 1, gated, free=(i < free_n)) for i, x in enumerate(items)
    )

    intro = (f"{len(items)} {esc(ecfg['name'])} {esc(sname)} previous year questions on <b>{esc(chapter)}</b> — options free on every question; <b>{free_n} include the answer &amp; explanation free</b>, the rest unlock with PYQ Pass."
              if gated else
              f"{len(items)} solved {esc(ecfg['name'])} {esc(sname)} previous year questions on <b>{esc(chapter)}</b>, each with the correct answer and a full explanation.")

    end_scripts = KATEX_SCRIPTS if gated else ""
    body = f'''{HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/exams/">Exams</a> › <a href="/exams/{exam}/">{esc(ecfg['name'])}</a> › <a href="/exams/{exam}/{subject}/">{esc(sname)}</a> › {esc(chapter)}</nav>
      <div class="qtags"><span class="qtag">{ecfg['icon']} {esc(ecfg['name'])}</span><span class="qtag">{sicon} {esc(sname)}</span></div>
      <h1>{esc(chapter)}</h1>
      <p>{intro}</p>
{qs_html}
      <div class="cta-box">
        <h3>Practice more {esc(ecfg['name'])} {esc(sname)} PYQs</h3>
        <p>Browse every {esc(sname)} chapter, or explore the full {esc(ecfg['name'])} question bank.</p>
        <a href="/exams/{exam}/{subject}/" class="btn btn-primary">{sicon} All {esc(sname)} chapters →</a>
      </div>
    </article>
  </main>
{FOOTER}
{end_scripts}
</body>
</html>'''
    extra_head = KATEX_HEAD if gated else ""
    return head(title, desc, canonical, schema, extra_head) + body


def subject_index(exam, subject, by_chapter):
    ecfg = EXAMS[exam]
    gated = ecfg.get("gated", False)
    sname, sicon = ecfg["subjects"][subject]
    canonical = f"{BASE}/exams/{exam}/{subject}/"
    total = sum(len(v) for v in by_chapter.values())
    title = attr(f"{ecfg['name']} {sname} PYQs — {total} Solved Previous Year Questions | YESPYQ")
    if gated:
        desc = attr(f"Browse {len(by_chapter)} {ecfg['name']} {sname} chapters with {total} previous year questions — free to practice, answers & explanations unlocked with PYQ Pass.")
    else:
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
    gated = ecfg.get("gated", False)
    canonical = f"{BASE}/exams/{exam}/"
    total = sum(len(v) for v in by_subject.values())
    title = attr(f"{ecfg['full']} PYQs — {total} Solved Previous Year Questions | YESPYQ")
    if gated:
        desc = attr(f"{ecfg['full']} previous year questions ({ecfg['desc']}), subject-wise. Every question and its options are free — ~10% also include the free answer & explanation, the rest unlock with PYQ Pass.")
    else:
        desc = attr(f"Free {ecfg['full']} previous year questions ({ecfg['desc']}), subject-wise, each with the correct answer and a detailed explanation. Practice on YESPYQ.")

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"Exams","item":"{BASE}/exams/"}},{{"@type":"ListItem","position":3,"name":"{esc(ecfg['name'])}","item":"{canonical}"}}]}}
  </script>'''

    tiles = ""
    for sid, (sname, sicon) in ecfg["subjects"].items():
        n = len(by_subject.get(sid, []))
        label = "PYQs" if gated else "solved PYQs"
        tiles += f'<a class="exam-tile" href="/exams/{exam}/{sid}/"><div class="et-icon">{sicon}</div><h3>{esc(sname)}</h3><p>{n} {label}</p></a>'

    intro = (f"{total} previous year questions for {esc(ecfg['full'])} ({esc(ecfg['desc'])}), organised by subject. Every question and its options are free — ~10% also include the free answer &amp; explanation, unlock the rest with PYQ Pass."
              if gated else
              f"{total} solved previous year questions for {esc(ecfg['full'])} ({esc(ecfg['desc'])}), organised by subject — each with the correct answer and a full explanation.")

    body = f'''{HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/exams/">Exams</a> › {esc(ecfg['name'])}</nav>
      <h1>{ecfg['icon']} {esc(ecfg['full'])} PYQs</h1>
      <p>{intro}</p>
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
    title = attr(f"India's PYQ Hub — UPSC, JEE, NEET, Board, Defence, SSC CGL PYQs | YESPYQ")
    desc = attr(f"Previous year questions for UPSC, JEE, NEET, Board exams, Defence and SSC CGL — {total}+ questions to practice. Pick your exam to start.")

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"Exams","item":"{canonical}"}}]}}
  </script>'''

    tiles = f'<a class="exam-tile" href="/pyq/"><div class="et-icon">🏛️</div><h3>UPSC (CSE Prelims)</h3><p>2,200+ solved PYQs</p></a>'
    for exam, ecfg in EXAMS.items():
        label = "PYQs" if ecfg.get("gated") else "solved PYQs"
        tiles += f'<a class="exam-tile" href="/exams/{exam}/"><div class="et-icon">{ecfg["icon"]}</div><h3>{esc(ecfg["full"])}</h3><p>{counts.get(exam,0)} {label}</p></a>'

    body = f'''{HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › Exams</nav>
      <h1>India's Previous Year Questions Hub</h1>
      <p>YESPYQ is expanding beyond UPSC — previous year questions for every major Indian exam, free to practice, with answers &amp; explanations unlocked with PYQ Pass. Pick your exam below.</p>
      <div class="exam-tiles">{tiles}</div>
      <p style="margin-top:2rem;color:var(--muted);font-size:.9rem">More exams (Banking, TET and others) are on the way.</p>
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
        subjects = resolve_subjects(ecfg, by_subject)
        # page helpers read ecfg["subjects"]
        original_subjects = ecfg["subjects"]
        ecfg["subjects"] = subjects

        for subject in subjects:
            sitems = by_subject.get(subject, [])
            by_chapter = defaultdict(list)
            for x in sitems:
                by_chapter[x.get("chapter") or "General"].append(x)

            for chapter, qs in by_chapter.items():
                write(f"exams/{exam}/{subject}/{slugify(chapter)}", chapter_page(exam, subject, chapter, qs))
                sitemap_urls.append((f"{BASE}/exams/{exam}/{subject}/{slugify(chapter)}/", "0.6"))

            write(f"exams/{exam}/{subject}", subject_index(exam, subject, by_chapter))
            sitemap_urls.append((f"{BASE}/exams/{exam}/{subject}/", "0.7"))

        write(f"exams/{exam}", exam_hub(exam, by_subject))
        sitemap_urls.append((f"{BASE}/exams/{exam}/", "0.8"))
        ecfg["subjects"] = original_subjects

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
