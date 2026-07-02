#!/usr/bin/env python3
"""Generate how-to UPSC blog posts for YESPYQ.
Run from repo root: python3 _gen_blog.py
Each post: unique content + Article + BreadcrumbList + FAQPage JSON-LD.
"""
import os

BASE = "https://yespyq.com"
TODAY = "2026-06-30"

POSTS = [
    {
        "slug": "how-to-start-upsc-preparation",
        "tag": "Beginner",
        "read": "11 min read",
        "title": "How to Start UPSC Preparation from Zero: A Beginner's Guide",
        "h1": "How to Start UPSC Preparation from Zero",
        "desc": "A clear, beginner-friendly roadmap to start UPSC CSE preparation from scratch — understand the exam, build an NCERT foundation, pick the right sources, and use PYQs from day one.",
        "keywords": "how to start UPSC preparation, UPSC preparation for beginners, how to prepare for IAS from zero, UPSC strategy for beginners, IAS preparation guide, UPSC roadmap",
        "ogdesc": "A beginner's roadmap to start UPSC CSE preparation from scratch — the right order, sources, and the role of PYQs.",
        "body": """
        <p>Starting UPSC preparation with zero background feels overwhelming because the syllabus looks endless. It is not. The Civil Services Examination rewards a small set of well-chosen sources read many times, anchored to <strong>previous year questions (PYQs)</strong>. This guide gives you a calm, sequential way to begin.</p>

        <h2>Step 1: Understand the exam before you study</h2>
        <p>Spend your first few days understanding what you are preparing for. The exam has three stages — Prelims, Mains and the Personality Test (interview). Read the official syllabus once, end to end, and skim a few past papers. You are not trying to solve them; you are calibrating what "depth" the examiner expects.</p>
        <p>For the full structure, read our breakdown of <a href="/blog/upsc-prelims-mains-interview-pattern/">UPSC Prelims vs Mains vs Interview</a>.</p>

        <h2>Step 2: Build the NCERT foundation</h2>
        <p>NCERT textbooks (classes 6–12) are the universal starting point because they are simple, accurate, and exactly the level the Prelims begins at. Cover History, Geography, Polity, Economy, and basic Science. Do not over-note at this stage — read for understanding and clarity.</p>

        <h2>Step 3: One standard source per subject</h2>
        <p>After NCERTs, add one standard reference per subject and stick with it. The single biggest beginner mistake is collecting many books and finishing none. <strong>One source, many revisions</strong> beats many sources read once.</p>
        <ul>
          <li><strong>Polity</strong> — one standard text, revised repeatedly. See <a href="/subjects/polity/">Polity PYQs</a>.</li>
          <li><strong>Geography &amp; Environment</strong> — NCERTs plus an atlas. See <a href="/subjects/environment/">Environment PYQs</a>.</li>
          <li><strong>Economy</strong> — one conceptual text linked to current affairs. See <a href="/subjects/economy/">Economy PYQs</a>.</li>
          <li><strong>History &amp; Culture</strong> — NCERTs plus one modern-history reference. See <a href="/subjects/history/">History PYQs</a>.</li>
        </ul>

        <h2>Step 4: Make PYQs your compass</h2>
        <p>Begin solving previous year questions early — not at the end. PYQs tell you which themes repeat and how deep to go, so you read with the examiner's priorities in mind. Before starting any chapter, skim its past questions first.</p>

        <blockquote>The goal of your first months is not to "finish the syllabus." It is to finish the NCERTs, choose your sources, and learn to read through the lens of PYQs.</blockquote>

        <div class="cta-box">
          <h3>Start with real PYQs</h3>
          <p>Practise authentic UPSC CSE Prelims previous year questions, subject-wise, with instant answers and explanations — free.</p>
          <a href="/subjects/" class="btn btn-primary">Browse subjects →</a>
        </div>

        <h2>A simple first-90-days plan</h2>
        <ul>
          <li><strong>Weeks 1–2:</strong> Read the syllabus, understand the exam, skim past papers.</li>
          <li><strong>Weeks 3–8:</strong> Finish core NCERTs subject by subject.</li>
          <li><strong>Weeks 9–12:</strong> Add one standard source per subject; start theme-wise PYQs; begin a daily newspaper habit.</li>
        </ul>

        <h2>Common beginner mistakes to avoid</h2>
        <ul>
          <li>Hoarding books and coaching material instead of revising one source.</li>
          <li>Postponing PYQs to the "last phase."</li>
          <li>Making long, decorative notes you never revise.</li>
          <li>Ignoring current affairs in the early months.</li>
        </ul>
        """,
        "faq": [
            ("Can I start UPSC preparation without coaching?", "Yes. A disciplined self-study plan built on NCERTs, one standard source per subject, daily current affairs, and consistent PYQ practice is enough for many successful candidates."),
            ("How long does UPSC preparation take?", "Most aspirants need roughly 12–18 months of consistent preparation for a serious first attempt, though this varies with your starting point and daily study hours."),
            ("Should beginners start with PYQs?", "Yes — start early. PYQs show which topics matter and how deeply they are tested, so you study efficiently from day one rather than reading blindly."),
        ],
        "related": [
            ("how-to-prepare-current-affairs-upsc", "Current Affairs", "How to Prepare Current Affairs"),
            ("upsc-prelims-mains-interview-pattern", "Exam Pattern", "Prelims vs Mains vs Interview"),
            ("upsc-prelims-pyq-strategy", "Strategy", "How to Solve UPSC Prelims PYQs"),
        ],
    },
    {
        "slug": "upsc-prelims-mains-interview-pattern",
        "tag": "Exam Pattern",
        "read": "10 min read",
        "title": "UPSC Prelims vs Mains vs Interview: Exam Pattern Explained",
        "h1": "UPSC Prelims vs Mains vs Interview: The Exam Pattern Explained",
        "desc": "Understand the three stages of the UPSC Civil Services Examination — Prelims, Mains and the Personality Test — including papers, marks, negative marking and how the final rank is decided.",
        "keywords": "UPSC exam pattern, UPSC Prelims vs Mains, UPSC stages, UPSC Mains pattern, CSAT qualifying, UPSC interview marks, civil services exam pattern",
        "ogdesc": "The three stages of the UPSC CSE — Prelims, Mains and Interview — with papers, marks and how the final rank works.",
        "body": """
        <p>The UPSC Civil Services Examination is conducted in three successive stages. Each filters candidates to the next, but only the last two decide your rank. Understanding the structure early helps you study with the right end in mind.</p>

        <h2>The three stages at a glance</h2>
        <ul>
          <li><strong>Stage 1 — Preliminary Examination (Prelims):</strong> a screening test. Objective, MCQ-based. Marks do not count toward the final rank.</li>
          <li><strong>Stage 2 — Main Examination (Mains):</strong> descriptive, written papers. The core of your final score.</li>
          <li><strong>Stage 3 — Personality Test (Interview):</strong> a structured interview before a board.</li>
        </ul>

        <h2>Stage 1: The Preliminary Examination</h2>
        <p>Prelims has two papers, each of 200 marks:</p>
        <ul>
          <li><strong>GS Paper-I (General Studies):</strong> 100 questions covering history, geography, polity, economy, environment, science and current affairs. This paper decides whether you clear the cut-off.</li>
          <li><strong>GS Paper-II (CSAT):</strong> a qualifying paper. You need to score 33% to pass; beyond that, it does not add to your merit.</li>
        </ul>
        <p>Both papers carry a <strong>negative marking</strong> of one-third of the marks for each wrong answer, so intelligent question selection matters. The best preparation for GS Paper-I is sustained <a href="/subjects/">subject-wise PYQ practice</a>.</p>

        <h2>Stage 2: The Main Examination</h2>
        <p>Mains is a set of nine descriptive papers. Two are qualifying language papers; the remaining seven count toward your merit:</p>
        <ul>
          <li><strong>Essay paper</strong></li>
          <li><strong>General Studies I–IV</strong> — covering heritage and society; governance and international relations; economy, environment and security; and ethics, integrity and aptitude.</li>
          <li><strong>Optional Subject</strong> — two papers in a subject you choose.</li>
        </ul>
        <p>Mains rewards structured, analytical writing within tight time limits — a very different skill from Prelims' recognition-based MCQs.</p>

        <blockquote>Prelims tests recognition; Mains tests articulation; the Interview tests personality. The same knowledge has to be expressed three different ways.</blockquote>

        <h2>Stage 3: The Personality Test</h2>
        <p>The interview, conducted by a UPSC board, assesses your clarity of thought, balance of judgement, and suitability for public service. It carries a substantial number of marks and can move ranks significantly.</p>

        <h2>How the final rank is decided</h2>
        <p>Your final merit is the sum of your <strong>Mains</strong> written marks and your <strong>Interview</strong> marks. Prelims marks are not added — Prelims only qualifies you for Mains. This is why serious preparation is always built around Mains and reinforced by Prelims practice.</p>

        <div class="cta-box">
          <h3>Build your Prelims base</h3>
          <p>Clearing Prelims is the first filter. Practise real PYQs subject-wise with answers and explanations — free, no login.</p>
          <a href="/subjects/" class="btn btn-primary">Practice Prelims PYQs →</a>
        </div>
        """,
        "faq": [
            ("Do Prelims marks count in the final UPSC rank?", "No. Prelims is only a screening stage. The final rank is calculated from Mains written marks plus the Personality Test (interview) marks."),
            ("Is CSAT counted for merit in UPSC Prelims?", "No. CSAT (GS Paper-II) is qualifying — you need 33% to pass it. Your Prelims cut-off is decided by GS Paper-I only."),
            ("How many papers are there in UPSC Mains?", "Mains has nine papers: two qualifying language papers, the essay, four General Studies papers, and two optional-subject papers. Seven of these count toward merit."),
        ],
        "related": [
            ("how-to-start-upsc-preparation", "Beginner", "How to Start UPSC from Zero"),
            ("upsc-eligibility-age-limit-attempts", "Eligibility", "Eligibility, Age & Attempts"),
            ("upsc-prelims-pyq-strategy", "Strategy", "How to Solve UPSC Prelims PYQs"),
        ],
    },
    {
        "slug": "how-many-hours-study-upsc",
        "tag": "Planning",
        "read": "8 min read",
        "title": "How Many Hours Should You Study for UPSC?",
        "h1": "How Many Hours Should You Study for UPSC?",
        "desc": "How many hours a day you really need to prepare for UPSC — realistic ranges for full-time and working aspirants, why consistency beats marathon sessions, and how to structure a productive study day.",
        "keywords": "how many hours to study for UPSC, UPSC study hours, UPSC daily timetable, study schedule for IAS, UPSC preparation hours, working professional UPSC",
        "ogdesc": "How many hours you really need for UPSC — realistic ranges, why consistency wins, and how to structure your day.",
        "body": """
        <p>"How many hours should I study?" is the most common question beginners ask — and the least useful one to obsess over. The honest answer: <strong>consistent, focused hours beat long, distracted ones</strong>. Here is a realistic way to think about it.</p>

        <h2>There is no magic number</h2>
        <p>Toppers have cleared the exam studying anywhere from 6 to 12 hours a day. What they share is not a number of hours but <strong>focus, revision, and consistency over months</strong>. Five deeply focused hours can outperform ten distracted ones.</p>

        <h2>Realistic ranges</h2>
        <ul>
          <li><strong>Full-time aspirants:</strong> roughly 8–10 productive hours a day, broken into focused blocks with real breaks.</li>
          <li><strong>Working professionals:</strong> 4–6 focused hours on weekdays, with longer sessions on weekends, can be enough when sustained.</li>
          <li><strong>College students:</strong> 2–4 consistent hours alongside coursework builds a strong base over a year or two.</li>
        </ul>

        <h2>Structure beats raw hours</h2>
        <p>A productive UPSC day usually mixes:</p>
        <ul>
          <li><strong>New learning</strong> — one or two subjects, read for understanding.</li>
          <li><strong>Current affairs</strong> — newspaper plus notes, ideally at a fixed time.</li>
          <li><strong>Revision</strong> — revisiting what you studied earlier in the week.</li>
          <li><strong>PYQ practice</strong> — solving previous year questions to test retention.</li>
        </ul>
        <p>Use PYQs as your feedback loop — they reveal whether your hours are translating into recall. Start with <a href="/subjects/">subject-wise practice sets</a>.</p>

        <blockquote>Don't measure your day in hours studied. Measure it in pages revised, questions solved, and concepts you can now explain from memory.</blockquote>

        <h2>Why consistency wins</h2>
        <p>UPSC preparation is a months-long endurance effort. A sustainable 6 hours every single day will take you far further than bursts of 14 hours followed by burnout. Protect your sleep, schedule breaks, and treat consistency as the real metric.</p>

        <div class="cta-box">
          <h3>Make your hours count</h3>
          <p>End each study block with a short PYQ set to lock in what you learned. Free, instant answers and explanations.</p>
          <a href="/subjects/" class="btn btn-primary">Solve PYQs now →</a>
        </div>

        <h2>A simple daily template</h2>
        <ul>
          <li><strong>Morning:</strong> hardest new subject, when focus is highest.</li>
          <li><strong>Midday:</strong> current affairs + note-making.</li>
          <li><strong>Afternoon:</strong> second subject or optional.</li>
          <li><strong>Evening:</strong> revision + a timed PYQ set.</li>
        </ul>
        """,
        "faq": [
            ("Is 6 hours a day enough for UPSC?", "Yes, if those hours are focused and consistent over many months, and include revision and PYQ practice. Quality and consistency matter far more than a high hour count."),
            ("Can a working professional crack UPSC?", "Yes. Many working aspirants succeed with 4–6 focused hours on weekdays and longer weekend sessions, sustained with disciplined revision and PYQs."),
            ("How many hours do UPSC toppers study?", "It varies widely, from about 6 to 12 hours. There is no single number — what toppers share is focus, regular revision, and consistency rather than a fixed hour count."),
        ],
        "related": [
            ("how-to-start-upsc-preparation", "Beginner", "How to Start UPSC from Zero"),
            ("how-many-pyqs-to-solve-upsc", "Planning", "How Many PYQs Should You Solve?"),
            ("how-to-prepare-current-affairs-upsc", "Current Affairs", "How to Prepare Current Affairs"),
        ],
    },
    {
        "slug": "upsc-eligibility-age-limit-attempts",
        "tag": "Eligibility",
        "read": "8 min read",
        "title": "UPSC Eligibility, Age Limit & Number of Attempts",
        "h1": "UPSC Eligibility, Age Limit & Number of Attempts",
        "desc": "A clear summary of UPSC Civil Services eligibility — nationality, educational qualification, age limits and the number of attempts allowed for each category. Always verify with the official UPSC notification.",
        "keywords": "UPSC eligibility, UPSC age limit, UPSC number of attempts, IAS eligibility criteria, UPSC age limit for OBC SC ST, civil services eligibility, UPSC attempts limit",
        "ogdesc": "UPSC CSE eligibility made simple — nationality, qualification, age limits and attempts by category.",
        "body": """
        <p>Before you invest months in preparation, confirm that you meet the UPSC Civil Services eligibility criteria. The essentials — nationality, educational qualification, age and attempts — are summarised below.</p>

        <p><strong>Important:</strong> rules and relaxations can change from year to year. Always cross-check the exact figures in the <strong>official UPSC notification</strong> for the year you intend to apply.</p>

        <h2>1. Nationality</h2>
        <p>For the Indian Administrative Service (IAS) and Indian Police Service (IPS), a candidate must be a <strong>citizen of India</strong>. For some other services, certain other categories (such as specified persons of Indian origin) may also be eligible, subject to the notification's conditions.</p>

        <h2>2. Educational qualification</h2>
        <p>You need a <strong>degree from a recognised university</strong> — a graduate in any discipline is eligible. Final-year students can typically appear for the Prelims and must produce proof of passing before the Mains stage, as specified in the notification.</p>

        <h2>3. Age limit</h2>
        <p>The general age window is <strong>21 to 32 years</strong> as on the cut-off date specified in the notification, with category-based relaxation on the upper limit:</p>
        <table>
          <tr><th>Category</th><th>Upper age relaxation</th></tr>
          <tr><td>General / EWS</td><td>No relaxation (up to 32)</td></tr>
          <tr><td>OBC</td><td>+3 years</td></tr>
          <tr><td>SC / ST</td><td>+5 years</td></tr>
          <tr><td>PwBD</td><td>Additional relaxation as per rules</td></tr>
        </table>
        <p>Defence service personnel and certain other categories may receive further relaxation under the notification's provisions.</p>

        <h2>4. Number of attempts</h2>
        <p>The number of permitted attempts also depends on category:</p>
        <table>
          <tr><th>Category</th><th>Attempts allowed</th></tr>
          <tr><td>General / EWS</td><td>6</td></tr>
          <tr><td>OBC</td><td>9</td></tr>
          <tr><td>SC / ST</td><td>Up to the upper age limit</td></tr>
          <tr><td>PwBD (Gen/EWS/OBC)</td><td>9</td></tr>
        </table>
        <p>Appearing in the Prelims of a given year counts as one attempt; merely applying does not.</p>

        <blockquote>These figures reflect the long-standing pattern, but the official notification is the only authoritative source — verify before you apply.</blockquote>

        <div class="cta-box">
          <h3>Eligible? Start practising</h3>
          <p>If you meet the criteria, begin with real UPSC Prelims PYQs — free, subject-wise, with explanations.</p>
          <a href="/subjects/" class="btn btn-primary">Start practising →</a>
        </div>
        """,
        "faq": [
            ("What is the age limit for UPSC?", "The general age limit is 21 to 32 years as on the notification's cut-off date, with upper-age relaxation of three years for OBC, five years for SC/ST, and further relaxation for PwBD and certain other categories. Always confirm with the official notification."),
            ("How many attempts are allowed in UPSC?", "General and EWS candidates get 6 attempts, OBC candidates get 9, and SC/ST candidates may attempt until the upper age limit. Appearing in a Prelims counts as one attempt."),
            ("Can final-year students apply for UPSC?", "Yes. Final-year graduates can usually appear for the Preliminary Examination and must submit proof of passing their degree before the Main Examination, as specified in the notification."),
        ],
        "related": [
            ("upsc-prelims-mains-interview-pattern", "Exam Pattern", "Prelims vs Mains vs Interview"),
            ("how-to-start-upsc-preparation", "Beginner", "How to Start UPSC from Zero"),
            ("how-many-hours-study-upsc", "Planning", "How Many Hours to Study?"),
        ],
    },
    {
        "slug": "how-to-prepare-current-affairs-upsc",
        "tag": "Current Affairs",
        "read": "9 min read",
        "title": "How to Prepare Current Affairs for UPSC CSE",
        "h1": "How to Prepare Current Affairs for UPSC CSE",
        "desc": "A practical method to prepare current affairs for UPSC — what to read, the right time window, how to link news to the static syllabus, and how PYQs reveal what UPSC actually tests.",
        "keywords": "UPSC current affairs preparation, how to prepare current affairs for UPSC, current affairs strategy UPSC, newspaper for UPSC, current affairs notes UPSC, UPSC current affairs sources",
        "ogdesc": "A practical method for UPSC current affairs — what to read, the right window, and how to link news to the static syllabus.",
        "body": """
        <p>Current affairs intimidates aspirants because it feels infinite. It is not. UPSC does not test whether you remember every headline — it tests whether you can connect a news item to the <strong>static syllabus</strong>. Master that conversion and current affairs becomes manageable.</p>

        <h2>What "current affairs" really means for UPSC</h2>
        <p>The examiner rarely asks "what happened on a date." Instead, a news item becomes a doorway to a concept — a scheme to its ministry and objective, a summit to the organisation behind it, a species to its habitat and conservation status. Your job is to read news and immediately ask: <em>what static topic does this connect to?</em></p>

        <h2>Keep your sources lean</h2>
        <ul>
          <li><strong>One newspaper</strong> read daily — for understanding, not clipping everything.</li>
          <li><strong>One monthly compilation</strong> — to consolidate and fill gaps.</li>
          <li><strong>Your own concise notes</strong> — organised by syllabus theme, not by date.</li>
        </ul>
        <p>Resist the urge to follow ten sources. Depth and consistency beat breadth here just as they do everywhere in UPSC.</p>

        <h2>Mind the time window</h2>
        <p>For Prelims, roughly the <strong>12–18 months</strong> before the exam matter most. But older themes resurface, which is exactly what <a href="/subjects/current-affairs/">current-affairs PYQs</a> reveal — they show which kinds of developments the examiner keeps returning to.</p>

        <h2>Link news to the static syllabus</h2>
        <p>Every current item should be filed under a static head:</p>
        <ul>
          <li>A new policy → <a href="/subjects/polity/">Polity &amp; Governance</a></li>
          <li>An index or fiscal measure → <a href="/subjects/economy/">Economy</a></li>
          <li>A species or climate summit → <a href="/subjects/environment/">Environment &amp; Ecology</a></li>
          <li>A mission or technology → <a href="/subjects/science-technology/">Science &amp; Technology</a></li>
        </ul>

        <blockquote>Don't memorise the news. Translate each item into the concept the examiner is likely to test — that single habit is the whole skill.</blockquote>

        <h2>Make notes you will actually revise</h2>
        <p>Keep notes short, thematic, and revisable. A bullet linking the news hook to its static concept is worth more than a paragraph copied from an article. Revisit them weekly.</p>

        <div class="cta-box">
          <h3>See how news becomes questions</h3>
          <p>Practise current-affairs-linked PYQs and watch how UPSC converts the news into static concepts. Free, with explanations.</p>
          <a href="/subjects/current-affairs/" class="btn btn-primary">Practice Current Affairs PYQs →</a>
        </div>
        """,
        "faq": [
            ("How many months of current affairs are needed for UPSC Prelims?", "Roughly the 12–18 months before the exam are most important, though older recurring themes can still appear. PYQs help you see which developments matter most."),
            ("Which newspaper is best for UPSC current affairs?", "Any one standard national daily read consistently is enough. The source matters less than the habit of reading daily and linking news to the static syllabus."),
            ("How do I make current affairs notes for UPSC?", "Organise notes by syllabus theme rather than by date, keep them short, link each item to its static concept, and revise them weekly."),
        ],
        "related": [
            ("upsc-current-affairs-pyq-approach", "Current Affairs", "What Past Papers Reveal"),
            ("how-to-start-upsc-preparation", "Beginner", "How to Start UPSC from Zero"),
            ("how-many-hours-study-upsc", "Planning", "How Many Hours to Study?"),
        ],
    },
]

TMPL = """<!DOCTYPE html>
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
  <link rel="canonical" href="{base}/blog/{slug}/" />

  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="YESPYQ" />
  <meta property="og:url" content="{base}/blog/{slug}/" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{ogdesc}" />
  <meta property="og:image" content="{base}/assets/og-image.png" />
  <meta property="og:locale" content="en_IN" />
  <meta property="article:published_time" content="{today}" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{h1}" />
  <meta name="twitter:description" content="{ogdesc}" />
  <meta name="twitter:image" content="{base}/assets/og-image.png" />

  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg" />
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" />
  <link rel="manifest" href="/manifest.webmanifest" />
  <link rel="stylesheet" href="/styles.css?v=19" />
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
    "mainEntityOfPage": {{ "@type": "WebPage", "@id": "{base}/blog/{slug}/" }}
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{ "@type": "ListItem", "position": 1, "name": "Home", "item": "{base}/" }},
      {{ "@type": "ListItem", "position": 2, "name": "Blog", "item": "{base}/blog/" }},
      {{ "@type": "ListItem", "position": 3, "name": "{tag}", "item": "{base}/blog/{slug}/" }}
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
        <a href="/subjects/">Subjects</a>
      </nav>
      <a href="/" class="btn btn-primary btn-sm">Start Practice</a>
    </div>
  </header>

  <main>
    <article class="article">
      <nav class="breadcrumb">
      </nav>
      <h1>{h1}</h1>
      <div class="meta"><span>By YESPYQ</span> · <span>Updated June 2026</span> · <span>{read}</span></div>

      <div class="prose">
{body}
        <div class="faq">
          <h2>Frequently asked questions</h2>
{faq_html}
        </div>
      </div>

      <section class="related">
        <h2>Keep reading</h2>
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

def build(p):
    faq_html = ""
    faq_ld = []
    for q, a in p["faq"]:
        faq_html += '          <details>\n            <summary>{}</summary>\n            <p>{}</p>\n          </details>\n'.format(q, a)
        faq_ld.append('      {{ "@type": "Question", "name": "{}", "acceptedAnswer": {{ "@type": "Answer", "text": "{}" }} }}'.format(esc(q), esc(a)))
    related_html = ""
    for slug, tag, title in p["related"]:
        related_html += '          <a href="/blog/{}/"><span class="tag">{}</span><b>{}</b></a>\n'.format(slug, tag, title)
    return TMPL.format(
        title=p["title"], desc=p["desc"], keywords=p["keywords"], ogdesc=p["ogdesc"],
        base=BASE, slug=p["slug"], today=TODAY, h1=p["h1"], tag=p["tag"], read=p["read"],
        body=p["body"], faq_ld=",\n".join(faq_ld), faq_html=faq_html, related_html=related_html,
    )

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    for p in POSTS:
        d = os.path.join(root, "blog", p["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(build(p))
        print("wrote", d)

if __name__ == "__main__":
    main()
