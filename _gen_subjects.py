#!/usr/bin/env python3
"""Generate subject-wise SEO landing pages for YESPYQ.
Each page targets a high-intent keyword like "UPSC Polity Previous Year Questions".
Run from repo root: python3 _gen_subjects.py
"""
import os, html, datetime

TODAY = "2026-06-30"
BASE = "https://yespyq.com"

# Per-subject hand-written, unique content (no thin/duplicate text).
SUBJECTS = [
    {
        "slug": "polity",
        "name": "Polity & Governance",
        "short": "Polity",
        "icon": "⚖️",
        "weightage": "15–22 questions",
        "title": "UPSC Polity PYQs — Previous Year Questions with Answers & Explanations",
        "desc": "Practice UPSC CSE Prelims Polity & Governance previous year questions (PYQs) with instant answer keys and detailed explanations. Constitution, Fundamental Rights, Parliament, judiciary, federalism and more.",
        "keywords": "UPSC Polity PYQ, UPSC Polity previous year questions, Polity PYQ with answers, UPSC Prelims Polity questions, Indian Polity MCQ UPSC, Constitution PYQ UPSC",
        "intro": "Polity is the most scoring and most predictable subject in the UPSC Prelims. The Commission re-asks the same constitutional ideas year after year in fresh wrappers, which makes <strong>previous year questions (PYQs)</strong> the single most efficient way to prepare. On this page you can practise authentic UPSC CSE Prelims Polity PYQs with instant answers and crisp explanations.",
        "topics": [
            ("Constitution: framing, Preamble & amendments", "The nature of the Preamble, amending power under Article 368 and the basic structure doctrine are tested for precision almost every year."),
            ("Fundamental Rights, DPSP & Duties", "Which rights apply to citizens vs all persons, the FR–DPSP relationship, and the exact articles behind each right form one of the densest PYQ zones."),
            ("Parliament & state legislatures", "Money bills vs financial bills, types of majorities, the Speaker's role, parliamentary committees and the Anti-Defection Law recur constantly."),
            ("Executive, judiciary & constitutional bodies", "Presidential powers, the Governor's discretion, Supreme Court jurisdiction and the constitutional/statutory/executive body distinction are perennial favourites."),
            ("Federalism & centre–state relations", "Distribution of legislative powers, the Finance Commission, and emergency provisions — often probing whether a recommendation is binding or advisory."),
        ],
        "tip": "In Polity a single qualifier — \"binding,\" \"only,\" \"all,\" \"discretion\" — usually decides the answer. Train your eye on the exact wording.",
        "faq": [
            ("Is Polity the most scoring subject in UPSC Prelims?", "For most aspirants, yes. It is conceptual and highly repetitive, so disciplined PYQ-based preparation gives high, reliable returns."),
            ("How many Polity questions come in UPSC Prelims?", "Polity & Governance typically accounts for 15–22 of the 100 questions in the GS Paper-I, making it one of the highest-weightage subjects."),
            ("Can I prepare Polity from PYQs alone?", "PYQs should guide your reading and revision, but you still need one standard text for concept-building. Use PYQs to calibrate depth."),
        ],
        "related_blog": ("upsc-polity-pyq-important-topics", "Polity PYQs: Most Repeated Topics"),
    },
    {
        "slug": "history",
        "name": "History & Art-Culture",
        "short": "History",
        "icon": "🏛️",
        "weightage": "12–18 questions",
        "title": "UPSC History PYQs — Ancient, Medieval, Modern & Art-Culture Questions",
        "desc": "Practice UPSC CSE Prelims History previous year questions (PYQs) with answers and explanations — Ancient, Medieval, Modern India, the freedom struggle and Art & Culture.",
        "keywords": "UPSC History PYQ, UPSC History previous year questions, Modern History PYQ UPSC, Art and Culture PYQ UPSC, Ancient History UPSC questions, freedom struggle PYQ",
        "intro": "History spans Ancient, Medieval, Modern India and Art & Culture, and the Commission's choices here are best decoded through <strong>previous year questions</strong>. PYQs reveal exactly which themes — the national movement, cultural institutions, key reformers — the examiner returns to. Practise authentic UPSC History PYQs below with full explanations.",
        "topics": [
            ("Modern India & the freedom struggle", "The highest-yield zone: phases of the national movement, key sessions of the Congress, acts and reforms, and the contributions of leaders."),
            ("Art & Culture", "Temple architecture, classical dances, painting schools, music traditions and UNESCO heritage sites are tested with growing depth."),
            ("Ancient India", "The Indus Valley Civilisation, Vedic society, Mauryan and Gupta administration, and Buddhist/Jain traditions recur frequently."),
            ("Medieval India", "Delhi Sultanate and Mughal administration, the Bhakti and Sufi movements, and regional kingdoms feature regularly."),
            ("Personalities & institutions", "Reformers, revolutionaries and the institutions they founded are a favourite matching-and-statement format."),
        ],
        "tip": "Art & Culture questions reward visual familiarity — link each temple, dance and painting style to its region and dynasty.",
        "faq": [
            ("Which part of History is most important for UPSC Prelims?", "Modern India and the freedom struggle carry the most weight, followed by Art & Culture, which has grown sharply in recent years."),
            ("How many History questions appear in UPSC Prelims?", "History & Art-Culture together usually contribute 12–18 questions in the Prelims GS Paper-I."),
            ("Are NCERTs enough for History PYQs?", "NCERTs build the base, but solving PYQs alongside them shows where extra depth in Art & Culture and Modern History is needed."),
        ],
        "related_blog": ("upsc-prelims-pyq-strategy", "How to Solve UPSC Prelims PYQs"),
    },
    {
        "slug": "geography",
        "name": "Geography",
        "short": "Geography",
        "icon": "🌍",
        "weightage": "10–15 questions",
        "title": "UPSC Geography PYQs — Physical, Indian & World Geography Questions",
        "desc": "Practice UPSC CSE Prelims Geography previous year questions (PYQs) with answers and explanations — physical, Indian, world and economic geography, plus map-based questions.",
        "keywords": "UPSC Geography PYQ, Geography previous year questions UPSC, Indian Geography PYQ, physical geography UPSC, map based questions UPSC, world geography PYQ",
        "intro": "Geography blends static concepts with map-based reasoning, and <strong>previous year questions</strong> show exactly how the Commission mixes the two. From monsoon mechanics to mineral belts and river systems, PYQs map the recurring terrain. Practise authentic UPSC Geography PYQs here with clear explanations.",
        "topics": [
            ("Physical geography", "Geomorphology, climatology (monsoon, cyclones), oceanography and the atmosphere are conceptual cores that repeat in varied forms."),
            ("Indian geography", "Drainage systems, soils, vegetation, agriculture and mineral/industrial distribution are heavily tested, often map-linked."),
            ("World geography", "Major landforms, climatic regions, ocean currents and important straits/locations appear regularly."),
            ("Economic & human geography", "Resources, energy, transport and population distribution connect Geography to current affairs."),
            ("Map & location-based questions", "Rivers, mountain passes, tiger reserves and neighbouring-country borders demand atlas familiarity."),
        ],
        "tip": "Keep an atlas open while solving Geography PYQs — half the marks here come from knowing exactly where things are.",
        "faq": [
            ("Is Geography scoring for UPSC Prelims?", "Yes, the physical-geography portion is conceptual and stable, so it rewards consistent PYQ practice and map work."),
            ("How many Geography questions come in Prelims?", "Geography generally contributes 10–15 questions, and overlaps with Environment and current affairs."),
            ("How do I prepare map-based Geography PYQs?", "Solve location questions with an atlas beside you and revise a map of India's rivers, ranges and reserves repeatedly."),
        ],
        "related_blog": ("upsc-subject-wise-weightage", "Subject-Wise Weightage & Trends"),
    },
    {
        "slug": "economy",
        "name": "Economy",
        "short": "Economy",
        "icon": "📈",
        "weightage": "13–20 questions",
        "title": "UPSC Economy PYQs — Indian Economy & Current Affairs Questions",
        "desc": "Practice UPSC CSE Prelims Economy previous year questions (PYQs) with answers and explanations — banking, fiscal & monetary policy, budget, BoP and economic survey themes.",
        "keywords": "UPSC Economy PYQ, Indian Economy previous year questions, Economy PYQ with answers UPSC, banking PYQ UPSC, fiscal policy UPSC questions, economic survey PYQ",
        "intro": "Economy questions increasingly blend static concepts with the year's economic developments, so <strong>previous year questions</strong> are essential for seeing how theory meets current affairs. Banking, monetary policy and fiscal terms recur in statement-based formats. Practise authentic UPSC Economy PYQs below with explanations.",
        "topics": [
            ("Money, banking & monetary policy", "RBI tools (repo, CRR, SLR, OMO), types of money, and the banking structure are tested almost every year."),
            ("Fiscal policy, budget & taxation", "Deficits, the budget process, GST and direct/indirect taxes form a dense, conceptual PYQ zone."),
            ("Growth, inflation & national income", "GDP/GNP concepts, inflation measures (CPI/WPI) and indices recur in definition-checking questions."),
            ("External sector", "Balance of payments, exchange rates, FDI/FPI and trade terms connect strongly to current affairs."),
            ("Planning, schemes & institutions", "Government schemes, financial-sector regulators and economic institutions appear regularly."),
        ],
        "tip": "Economy PYQs test definitions precisely — be sure you can distinguish look-alike terms like fiscal vs revenue deficit, or CRR vs SLR.",
        "faq": [
            ("Is Economy hard to score in UPSC Prelims?", "Economy is conceptual and current-affairs-linked, but PYQs show a clear pattern of repeated terms that make it very learnable."),
            ("How many Economy questions appear in Prelims?", "Economy typically accounts for 13–20 questions, often overlapping with current affairs and government schemes."),
            ("Do I need to read the Economic Survey for PYQs?", "Read it selectively. PYQs show which themes matter; pair them with the Survey's key chapters rather than reading cover to cover."),
        ],
        "related_blog": ("upsc-current-affairs-pyq-approach", "Current Affairs PYQ Approach"),
    },
    {
        "slug": "environment",
        "name": "Environment & Ecology",
        "short": "Environment",
        "icon": "🌱",
        "weightage": "15–20 questions",
        "title": "UPSC Environment & Ecology PYQs — Biodiversity & Climate Questions",
        "desc": "Practice UPSC CSE Prelims Environment & Ecology previous year questions (PYQs) with answers and explanations — biodiversity, climate change, conservation, species and protected areas.",
        "keywords": "UPSC Environment PYQ, Environment and Ecology previous year questions, biodiversity PYQ UPSC, climate change UPSC questions, conservation PYQ, species in news UPSC",
        "intro": "Environment & Ecology has become one of the highest-weightage areas in the Prelims, fusing static ecology with species and conventions in the news. <strong>Previous year questions</strong> reveal the examiner's love of conservation status, protected areas and climate institutions. Practise authentic UPSC Environment PYQs here with explanations.",
        "topics": [
            ("Biodiversity & conservation", "IUCN status, flagship/keystone species, and recently-in-news flora and fauna are tested heavily."),
            ("Protected areas & institutions", "National parks, wildlife sanctuaries, biosphere reserves, Ramsar sites and the bodies that manage them recur."),
            ("Climate change & conventions", "UNFCCC, IPCC, COP outcomes, carbon markets and international environmental agreements appear regularly."),
            ("Ecology & ecosystems", "Food chains, biogeochemical cycles, ecological succession and the basics of ecosystems form the static core."),
            ("Pollution & environmental laws", "Acts, regulatory bodies, pollutants and standards connect Environment to governance and current affairs."),
        ],
        "tip": "Maintain a running list of \"species in news\" with their habitat and conservation status — PYQs reward exactly this kind of current linkage.",
        "faq": [
            ("Why is Environment so important for UPSC Prelims?", "It carries 15–20 questions and overlaps with Geography, science and current affairs, giving it an outsized effective weight."),
            ("Can I prepare Environment mainly from current affairs?", "Pair current affairs with static ecology. PYQs show that the examiner rewards both the news hook and the underlying concept."),
            ("How many Environment questions come in Prelims?", "Environment & Ecology typically contributes 15–20 questions, among the highest of any single area."),
        ],
        "related_blog": ("upsc-current-affairs-pyq-approach", "Current Affairs PYQ Approach"),
    },
    {
        "slug": "science-technology",
        "name": "Science & Technology",
        "short": "Science & Tech",
        "icon": "🔬",
        "weightage": "10–15 questions",
        "title": "UPSC Science & Technology PYQs — Sci-Tech & Current Developments",
        "desc": "Practice UPSC CSE Prelims Science & Technology previous year questions (PYQs) with answers and explanations — biotech, space, defence, IT, and science in the news.",
        "keywords": "UPSC Science and Technology PYQ, Science Tech previous year questions UPSC, biotechnology PYQ UPSC, space technology UPSC questions, defence technology PYQ",
        "intro": "Science & Technology in the Prelims is increasingly current-affairs-driven — missions, vaccines, chips and defence systems in the news. <strong>Previous year questions</strong> show that the examiner pairs each development with a basic scientific concept. Practise authentic UPSC Science & Tech PYQs below with clear explanations.",
        "topics": [
            ("Biotechnology & health", "Genetics, vaccines, diseases, and applications like CRISPR and recombinant DNA are recurring favourites."),
            ("Space technology", "ISRO missions, satellites, launch vehicles and space concepts feature almost every year."),
            ("Defence technology", "Missiles, indigenous platforms and defence developments in the news are regularly tested."),
            ("IT, computing & emerging tech", "AI, blockchain, semiconductors, 5G and quantum themes increasingly appear with a current hook."),
            ("Basic & applied science", "Physics, chemistry and biology fundamentals underpin many news-linked questions."),
        ],
        "tip": "For Sci-Tech, learn the concept behind each news item — the examiner tests why a technology matters, not just that it happened.",
        "faq": [
            ("How do I prepare Science & Technology for Prelims?", "Track science in the news and attach a basic concept to each item. PYQs show this concept-plus-current pattern clearly."),
            ("How many Sci-Tech questions appear in Prelims?", "Science & Technology generally contributes 10–15 questions, with a strong current-affairs flavour."),
            ("Do I need a science background for these PYQs?", "No. The questions test general scientific awareness, not specialist depth — PYQ practice is enough to calibrate the level."),
        ],
        "related_blog": ("upsc-current-affairs-pyq-approach", "Current Affairs PYQ Approach"),
    },
    {
        "slug": "current-affairs",
        "name": "Current Affairs",
        "short": "Current Affairs",
        "icon": "🗞️",
        "weightage": "15–25 questions",
        "title": "UPSC Current Affairs PYQs — News-based Prelims Questions",
        "desc": "Practice UPSC CSE Prelims Current Affairs previous year questions (PYQs) with answers and explanations — schemes, reports, indices, summits, and news that translated into questions.",
        "keywords": "UPSC Current Affairs PYQ, current affairs previous year questions UPSC, government schemes PYQ, reports and indices UPSC, summits PYQ UPSC, news based questions",
        "intro": "Current affairs is the connective tissue of the Prelims — it surfaces inside Polity, Economy, Environment and Science. <strong>Previous year questions</strong> teach the most valuable lesson here: how a news item becomes a static, conceptual question. Practise authentic UPSC current-affairs-linked PYQs below with explanations.",
        "topics": [
            ("Government schemes & programmes", "Flagship schemes, their ministries and objectives are tested in precise statement-based formats."),
            ("Reports, indices & rankings", "Global and national indices, their publishing bodies and India's standing recur frequently."),
            ("Summits, organisations & agreements", "International groupings, summits and conventions connect news to institutional knowledge."),
            ("Awards, persons & places in news", "People, places and events in the news are mapped back to static geography, history or polity."),
            ("Economy & environment in the news", "Much of current affairs lands inside Economy and Environment — making cross-linking essential."),
        ],
        "tip": "Don't memorise news as headlines — convert each item into the static concept the examiner is likely to test, exactly as PYQs do.",
        "faq": [
            ("How much of UPSC Prelims is current affairs?", "Directly and indirectly, 15–25 questions carry a current-affairs flavour, making it one of the most decisive areas."),
            ("How far back should current affairs go for Prelims?", "Roughly the 12–18 months before the exam, with PYQs showing how older themes still resurface."),
            ("Can PYQs help with current affairs?", "Yes — they teach the conversion from news to concept, which is the real skill the Prelims tests in current affairs."),
        ],
        "related_blog": ("upsc-current-affairs-pyq-approach", "Current Affairs PYQ Approach"),
    },
]

PAGE_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <!-- Google Analytics (GA4) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-G2DK8674FB"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-G2DK8674FB');
  </script>

  <title>{title} | YESPYQ</title>
  <meta name="description" content="{desc}" />
  <meta name="keywords" content="{keywords}" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <meta name="googlebot" content="index, follow" />
  <meta name="author" content="YESPYQ" />
  <meta name="theme-color" content="#2563eb" />
  <link rel="canonical" href="{base}/subjects/{slug}/" />

  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="YESPYQ" />
  <meta property="og:url" content="{base}/subjects/{slug}/" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{ogdesc}" />
  <meta property="og:image" content="{base}/assets/og-image.png" />
  <meta property="og:locale" content="en_IN" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="UPSC {short} PYQs — Practice with Answers" />
  <meta name="twitter:description" content="{ogdesc}" />
  <meta name="twitter:image" content="{base}/assets/og-image.png" />

  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg" />
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" />
  <link rel="manifest" href="/manifest.webmanifest" />
  <link rel="stylesheet" href="/styles.css?v=24" />
  <link rel="stylesheet" href="/blog.css?v=5" />

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{h1}",
    "description": "{desc}",
    "image": "{base}/assets/og-image.png",
    "datePublished": "{today}",
    "dateModified": "{today}",
    "inLanguage": "en-IN",
    "author": {{ "@type": "Organization", "name": "YESPYQ", "url": "{base}/" }},
    "publisher": {{ "@type": "EducationalOrganization", "name": "YESPYQ", "logo": {{ "@type": "ImageObject", "url": "{base}/assets/favicon.svg" }} }},
    "mainEntityOfPage": {{ "@type": "WebPage", "@id": "{base}/subjects/{slug}/" }}
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{ "@type": "ListItem", "position": 1, "name": "Home", "item": "{base}/" }},
      {{ "@type": "ListItem", "position": 2, "name": "Subjects", "item": "{base}/subjects/" }},
      {{ "@type": "ListItem", "position": 3, "name": "{short} PYQs", "item": "{base}/subjects/{slug}/" }}
    ]
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
{faq_ld}
    ]
  }}
  </script>
  <script src="/theme.js?v=1"></script>
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="/">
        <img src="/assets/favicon.svg" alt="" class="brand-mark" />
        <span class="brand-name">YES<span>PYQ</span></span>
      </a>
      <nav class="main-nav">
        <a href="/">Home</a>
        <a href="/">Practice</a>
        <a href="/subjects/" class="active">Subjects</a>
      </nav>
      <a href="/" class="btn btn-primary btn-sm">Start Practice</a>
    </div>
  </header>

  <main>
    <article class="article">
      <nav class="breadcrumb">
        <a href="/">Home</a> › <a href="/subjects/">Subjects</a> › {short} PYQs
      </nav>
      <h1>{icon} {h1}</h1>
      <div class="meta"><span>By YESPYQ</span> · <span>Updated June 2026</span> · <span>UPSC CSE Prelims</span> · <span>~{weightage} per paper</span></div>

      <div class="prose">
        <p>{intro}</p>

        <div class="cta-box">
          <h3>Practice {short} PYQs now</h3>
          <p>Attempt real UPSC CSE Prelims {name} questions with instant answers and detailed explanations — free, no login.</p>
          <a href="/" class="btn btn-primary">Start {short} Practice →</a>
        </div>

        <h2>High-yield {short} topics in UPSC PYQs</h2>
        <p>Across past papers, the same {short} themes resurface repeatedly. These are the areas to prioritise when you practise previous year questions:</p>
{topics_html}

        <blockquote>{tip}</blockquote>

        <h2>How to use {short} PYQs effectively</h2>
        <ul>
          <li><strong>Solve theme-wise, not just year-wise.</strong> Group questions by topic to see the repetition that PYQs reveal.</li>
          <li><strong>Read every explanation.</strong> The reasoning behind a wrong option is often the next year's question.</li>
          <li><strong>Revisit, don't just attempt.</strong> Re-solve {short} PYQs in timed sets to lock in accuracy and speed.</li>
          <li><strong>Link to the syllabus.</strong> Use PYQs as a map of what to study deeply versus what to skim.</li>
        </ul>

        <div class="faq">
          <h2>Frequently asked questions</h2>
{faq_html}
        </div>
      </div>

      <section class="related">
        <h2>Practice other subjects</h2>
        <div class="related-list">
{related_html}
        </div>
      </section>
    </article>
  </main>

  <footer class="site-footer">
    <div class="container footer-inner">
      <div class="footer-brand">
        <img src="/assets/favicon.svg" alt="" class="brand-mark" />
        <span class="brand-name">YES<span>PYQ</span></span>
        <p>Previous Year Questions, simplified.</p>
      </div>
      <div class="footer-col">
        <h4>Practice</h4>
        <a href="/">Home</a>
        <a href="/subjects/">Subjects</a>
      </div>
      <div class="footer-col">
        <h4>Company</h4>
        <a href="/about/">About</a>
        <a href="/contact/">Contact</a>
      </div>
      <div class="footer-col">
        <h4>Legal</h4>
        <a href="/privacy-policy/">Privacy Policy</a>
        <a href="/terms/">Terms &amp; Conditions</a>
        <a href="/disclaimer/">Disclaimer</a>
      </div>
    </div>
    <div class="footer-bottom">© <span id="year"></span> YESPYQ.com · Built for UPSC CSE aspirants · Not affiliated with UPSC</div>
  </footer>
  <script>document.getElementById("year").textContent = new Date().getFullYear();</script>
</body>
</html>
"""

def esc(s):
    return s.replace('"', '\\"')

def build_page(sub, all_subs):
    h1 = "UPSC " + sub["short"] + " Previous Year Questions (PYQs)"
    ogdesc = "Free UPSC CSE Prelims " + sub["short"] + " PYQ practice with answer keys and detailed explanations."
    # topics
    topics_html = ""
    for i, (t, d) in enumerate(sub["topics"], 1):
        topics_html += '        <h3>{}. {}</h3>\n        <p>{}</p>\n'.format(i, t, d)
    # faq html + ld
    faq_html = ""
    faq_ld_items = []
    for q, a in sub["faq"]:
        faq_html += '          <details>\n            <summary>{}</summary>\n            <p>{}</p>\n          </details>\n'.format(q, a)
        faq_ld_items.append('      {{ "@type": "Question", "name": "{}", "acceptedAnswer": {{ "@type": "Answer", "text": "{}" }} }}'.format(esc(q), esc(a)))
    faq_ld = ",\n".join(faq_ld_items)
    # related (other subjects)
    related_html = ""
    for o in all_subs:
        if o["slug"] == sub["slug"]:
            continue
        related_html += '          <a href="/subjects/{}/"><span class="tag">{}</span><b>UPSC {} PYQs</b></a>\n'.format(o["slug"], o["icon"], o["short"])
    # add blog related link
    bslug, btitle = sub["related_blog"]
    related_html += '          <a href="/blog/{}/"><span class="tag">📘 Blog</span><b>{}</b></a>\n'.format(bslug, btitle)

    return PAGE_TMPL.format(
        title=sub["title"], desc=sub["desc"], keywords=sub["keywords"],
        base=BASE, slug=sub["slug"], short=sub["short"], name=sub["name"],
        h1=h1, ogdesc=ogdesc, today=TODAY, icon=sub["icon"],
        weightage=sub["weightage"], intro=sub["intro"],
        topics_html=topics_html, tip=sub["tip"],
        faq_html=faq_html, faq_ld=faq_ld, related_html=related_html,
    )

# Hub index page
HUB_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-G2DK8674FB"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-G2DK8674FB');
  </script>

  <title>UPSC Subject-Wise PYQs — Practice Previous Year Questions by Subject | YESPYQ</title>
  <meta name="description" content="Practice UPSC CSE Prelims previous year questions (PYQs) subject-wise — Polity, History, Geography, Economy, Environment, Science & Technology and Current Affairs — with answers and explanations." />
  <meta name="keywords" content="UPSC subject wise PYQ, UPSC PYQ by subject, UPSC Prelims previous year questions, Polity History Geography Economy PYQ, UPSC question bank subject wise" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <meta name="author" content="YESPYQ" />
  <meta name="theme-color" content="#2563eb" />
  <link rel="canonical" href="{base}/subjects/" />

  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="YESPYQ" />
  <meta property="og:url" content="{base}/subjects/" />
  <meta property="og:title" content="UPSC Subject-Wise PYQs — Practice by Subject" />
  <meta property="og:description" content="Free UPSC CSE Prelims PYQ practice, organised subject-wise with answers and explanations." />
  <meta property="og:image" content="{base}/assets/og-image.png" />
  <meta property="og:locale" content="en_IN" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="UPSC Subject-Wise PYQs" />
  <meta name="twitter:description" content="Practice UPSC Prelims PYQs subject-wise — free, with explanations." />
  <meta name="twitter:image" content="{base}/assets/og-image.png" />

  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg" />
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" />
  <link rel="manifest" href="/manifest.webmanifest" />
  <link rel="stylesheet" href="/styles.css?v=24" />
  <link rel="stylesheet" href="/blog.css?v=5" />

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{ "@type": "ListItem", "position": 1, "name": "Home", "item": "{base}/" }},
      {{ "@type": "ListItem", "position": 2, "name": "Subjects", "item": "{base}/subjects/" }}
    ]
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "UPSC CSE Prelims Subjects",
    "itemListElement": [
{itemlist}
    ]
  }}
  </script>
  <script src="/theme.js?v=1"></script>
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="/">
        <img src="/assets/favicon.svg" alt="" class="brand-mark" />
        <span class="brand-name">YES<span>PYQ</span></span>
      </a>
      <nav class="main-nav">
        <a href="/">Home</a>
        <a href="/">Practice</a>
        <a href="/subjects/" class="active">Subjects</a>
      </nav>
      <a href="/" class="btn btn-primary btn-sm">Start Practice</a>
    </div>
  </header>

  <section class="blog-hero">
    <div class="container">
      <span class="pill">UPSC CSE Prelims</span>
      <h1>UPSC Subject-Wise Previous Year Questions (PYQs)</h1>
      <p>Practice authentic UPSC Civil Services Prelims PYQs organised subject-wise — with instant answer keys and detailed explanations. Pick a subject to dive into its most-tested themes.</p>
    </div>
  </section>

  <main>
    <div class="container">
      <div class="post-grid">
{cards}
      </div>

      <div class="prose" style="width:min(740px,92vw);margin:0 auto 3rem">
        <h2>Why practise UPSC PYQs subject-wise?</h2>
        <p>The UPSC Prelims rewards pattern recognition. When you solve previous year questions grouped by subject, the Commission's recurring themes — the same constitutional ideas, the same conservation-status traps, the same economic definitions — become impossible to miss. Each subject page below distils the high-yield topics and links straight into focused practice.</p>
        <p>New to PYQ-based preparation? Start with our guide on <a href="/blog/upsc-prelims-pyq-strategy/">how to solve UPSC Prelims PYQs</a>, see the full <a href="/blog/upsc-subject-wise-weightage/">subject-wise weightage and trends</a>, or read <a href="/blog/how-many-pyqs-to-solve-upsc/">how many PYQs you should solve</a>.</p>
      </div>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container footer-inner">
      <div class="footer-brand">
        <img src="/assets/favicon.svg" alt="" class="brand-mark" />
        <span class="brand-name">YES<span>PYQ</span></span>
        <p>Previous Year Questions, simplified.</p>
      </div>
      <div class="footer-col">
        <h4>Practice</h4>
        <a href="/">Home</a>
        <a href="/subjects/">Subjects</a>
      </div>
      <div class="footer-col">
        <h4>Company</h4>
        <a href="/about/">About</a>
        <a href="/contact/">Contact</a>
      </div>
      <div class="footer-col">
        <h4>Legal</h4>
        <a href="/privacy-policy/">Privacy Policy</a>
        <a href="/terms/">Terms &amp; Conditions</a>
        <a href="/disclaimer/">Disclaimer</a>
      </div>
    </div>
    <div class="footer-bottom">© <span id="year"></span> YESPYQ.com · Built for UPSC CSE aspirants · Not affiliated with UPSC</div>
  </footer>
  <script>document.getElementById("year").textContent = new Date().getFullYear();</script>
</body>
</html>
"""

def build_hub(all_subs):
    cards = ""
    items = []
    for i, s in enumerate(all_subs, 1):
        cards += (
            '        <a class="post-card" href="/subjects/{slug}/">\n'
            '          <span class="tag">{icon} {short}</span>\n'
            '          <h2>UPSC {short} PYQs</h2>\n'
            '          <p>{desc}</p>\n'
            '          <span class="read">Practice {short} →</span>\n'
            '        </a>\n'
        ).format(slug=s["slug"], icon=s["icon"], short=s["short"],
                 desc="High-yield " + s["name"] + " previous year questions with answers and explanations.")
        items.append('      {{ "@type": "ListItem", "position": {}, "name": "UPSC {} PYQs", "url": "{}/subjects/{}/" }}'.format(i, esc(s["short"]), BASE, s["slug"]))
    return HUB_TMPL.format(base=BASE, cards=cards, itemlist=",\n".join(items))

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    for s in SUBJECTS:
        d = os.path.join(root, "subjects", s["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(build_page(s, SUBJECTS))
        print("wrote", d)
    hubdir = os.path.join(root, "subjects")
    os.makedirs(hubdir, exist_ok=True)
    with open(os.path.join(hubdir, "index.html"), "w") as f:
        f.write(build_hub(SUBJECTS))
    print("wrote hub", hubdir)

if __name__ == "__main__":
    main()
