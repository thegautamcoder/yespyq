#!/usr/bin/env python3
"""Generate broad informational/aspirational SEO pages for YESPYQ under /guides/.
Run from repo root: python3 _gen_guides.py
Each page: unique content + Article + BreadcrumbList + FAQPage JSON-LD.
"""
import os

BASE = "https://yespyq.com"
TODAY = "2026-07-01"
ROOT = os.path.dirname(os.path.abspath(__file__))

GUIDES = [
    {
        "slug": "how-to-become-an-ias-officer",
        "tag": "Career Guide",
        "read": "12 min read",
        "title": "How to Become an IAS Officer: Step-by-Step Roadmap",
        "h1": "How to Become an IAS Officer",
        "desc": "A complete step-by-step roadmap to become an IAS officer in India — eligibility, the UPSC Civil Services Examination, the three stages, preparation, and the path from aspirant to officer.",
        "keywords": "how to become an IAS officer, how to become IAS, IAS officer kaise bane, become IAS after graduation, UPSC IAS roadmap, IAS preparation steps",
        "ogdesc": "The full roadmap to becoming an IAS officer — eligibility, the UPSC exam stages, and how to prepare.",
        "body": """
        <p>Becoming an IAS (Indian Administrative Service) officer is one of the most respected career goals in India. There is only one route: clearing the <strong>UPSC Civil Services Examination (CSE)</strong> and earning a rank high enough to be allotted the IAS. This guide lays out the entire path, step by step.</p>

        <h2>Step 1: Check your eligibility</h2>
        <ul>
          <li><strong>Nationality:</strong> an Indian citizen (for IAS/IPS).</li>
          <li><strong>Qualification:</strong> a graduate degree in any discipline from a recognised university. Final-year students can appear for the Prelims.</li>
          <li><strong>Age:</strong> generally 21–32 years, with relaxation for OBC (+3), SC/ST (+5) and PwBD categories.</li>
        </ul>
        <p>Confirm the exact figures in our guide to <a href="/blog/upsc-eligibility-age-limit-attempts/">UPSC eligibility, age limit and attempts</a>, and always cross-check the official notification.</p>

        <h2>Step 2: Understand the exam</h2>
        <p>The Civil Services Examination has three stages — Preliminary, Main and the Personality Test (interview). Only the last two decide your rank. Read the full breakdown in <a href="/blog/upsc-prelims-mains-interview-pattern/">Prelims vs Mains vs Interview</a>.</p>

        <h2>Step 3: Build the foundation</h2>
        <p>Start with NCERT textbooks across History, Geography, Polity, Economy and Science. Then pick one standard reference per subject and revise it repeatedly. Our <a href="/blog/how-to-start-upsc-preparation/">beginner's roadmap</a> shows the exact order.</p>

        <div class="cta-box">
          <h3>Start with real Prelims PYQs</h3>
          <p>The fastest way to understand the exam is to solve it. Practise authentic UPSC Prelims previous year questions, free.</p>
          <a href="/pyq/" class="btn btn-primary">Practise PYQs →</a>
        </div>

        <h2>Step 4: Make PYQs your compass</h2>
        <p>Previous year questions reveal exactly what the examiner tests and how deep to go. Solve them subject-wise from early on — see <a href="/subjects/">subject-wise PYQs</a> and <a href="/blog/upsc-prelims-pyq-strategy/">how to solve them</a>.</p>

        <h2>Step 5: Add current affairs and answer writing</h2>
        <p>Read one newspaper daily and link news to the static syllabus (our <a href="/blog/how-to-prepare-current-affairs-upsc/">current-affairs method</a>). For Mains, practise structured answer writing under time pressure.</p>

        <h2>Step 6: Clear all three stages, then training</h2>
        <p>Qualify Prelims, score well in Mains, perform in the interview, and earn a rank that gets you the IAS. Selected candidates train at the LBSNAA academy in Mussoorie before their first postings.</p>

        <blockquote>There is no shortcut, but there is a system: NCERTs → one source per subject → PYQs → current affairs → answer writing → revision. Repeat until exam day.</blockquote>
        """,
        "faq": [
            ("What is the qualification to become an IAS officer?", "You need a graduate degree in any discipline from a recognised university, and you must clear the UPSC Civil Services Examination with a rank high enough for the IAS."),
            ("Can I become an IAS officer after any graduation?", "Yes. A degree in any stream — arts, science, commerce or engineering — makes you eligible. The subject of your degree does not matter for eligibility."),
            ("How many attempts are allowed to become an IAS officer?", "General/EWS candidates get 6 attempts, OBC get 9, and SC/ST can attempt until the upper age limit. Appearing in a Prelims counts as one attempt."),
        ],
        "related": [
            ("upsc-full-form-and-services", "UPSC 101", "UPSC Full Form & Services"),
            ("ias-ips-ifs-difference", "Services", "IAS vs IPS vs IFS"),
            ("why-become-an-ias-officer", "Motivation", "Why Become an IAS Officer?"),
        ],
    },
    {
        "slug": "government-jobs-after-graduation",
        "tag": "Careers",
        "read": "10 min read",
        "title": "Best Government Jobs After Graduation in India",
        "h1": "Best Government Jobs After Graduation in India",
        "desc": "A guide to the best government jobs after graduation in India — UPSC Civil Services, banking, SSC, railways, state PSCs and defence — with what they offer and how to start preparing.",
        "keywords": "government jobs after graduation, best govt jobs in India, sarkari naukri after graduation, UPSC SSC banking jobs, government job options graduates",
        "ogdesc": "The top government job options after graduation in India and how to start preparing for them.",
        "body": """
        <p>Government jobs remain among the most sought-after careers in India for their stability, respect and social impact. After graduation, several strong options open up — here are the most popular, and where UPSC fits in.</p>

        <h2>1. UPSC Civil Services (IAS, IPS, IFS &amp; more)</h2>
        <p>The most prestigious route. A single exam — the Civil Services Examination — leads to the IAS, IPS, IFS and other central services. It offers unmatched responsibility and impact. Learn <a href="/guides/how-to-become-an-ias-officer/">how to become an IAS officer</a>.</p>

        <h2>2. Banking (IBPS, SBI, RBI)</h2>
        <p>Probationary Officer (PO) and clerk roles in public-sector banks, plus RBI Grade B, are popular for their pay and work-life balance. Selection is via objective exams and interviews.</p>

        <h2>3. SSC (Staff Selection Commission)</h2>
        <p>SSC CGL and CHSL fill a wide range of central-government posts — from inspectors to assistants — and are a favourite among graduates seeking stable clerical and officer roles.</p>

        <h2>4. Railways (RRB)</h2>
        <p>The Railway Recruitment Boards hire for numerous technical and non-technical posts, making Indian Railways one of the largest employers in the country.</p>

        <h2>5. State PSC exams</h2>
        <p>Each state's Public Service Commission conducts exams for state administrative and police services (e.g., Deputy Collector, DSP), mirroring the UPSC pattern at the state level.</p>

        <h2>6. Defence &amp; others</h2>
        <p>CDS, AFCAT and CAPF exams lead to careers in the armed and paramilitary forces. Teaching (via NET), PSUs and insurance sectors add further options.</p>

        <div class="cta-box">
          <h3>Aiming for UPSC? Start now</h3>
          <p>Whatever exam you target, previous year questions are the smartest starting point. Practise UPSC Prelims PYQs free.</p>
          <a href="/pyq/" class="btn btn-primary">Practise PYQs →</a>
        </div>

        <h2>How to choose and start</h2>
        <p>Pick based on your interests, the role's responsibilities and the exam pattern. Many exams share a common base — general studies, aptitude and current affairs — so a strong foundation helps across all of them. If administration and leadership appeal to you, the Civil Services is the pinnacle.</p>
        """,
        "faq": [
            ("Which is the best government job after graduation?", "The UPSC Civil Services (IAS/IPS/IFS) is considered the most prestigious, but banking, SSC CGL, railways and state PSC jobs are all strong options depending on your interests."),
            ("Can I prepare for UPSC and other exams together?", "Yes, to an extent. Many exams share a general-studies and current-affairs base, so a strong foundation helps — but each exam still needs targeted practice."),
            ("Do government jobs require a specific graduation stream?", "Most, including UPSC Civil Services, accept a degree in any discipline. Some technical posts require specific qualifications, so always check the notification."),
        ],
        "related": [
            ("how-to-become-an-ias-officer", "Career Guide", "How to Become an IAS Officer"),
            ("upsc-full-form-and-services", "UPSC 101", "UPSC Full Form & Services"),
            ("why-become-an-ias-officer", "Motivation", "Why Become an IAS Officer?"),
        ],
    },
    {
        "slug": "ias-ips-ifs-difference",
        "tag": "Services",
        "read": "9 min read",
        "title": "IAS vs IPS vs IFS: Roles, Powers and Differences",
        "h1": "IAS vs IPS vs IFS: What's the Difference?",
        "desc": "Understand the difference between IAS, IPS and IFS — their roles, powers, training, uniforms and responsibilities — all selected through the same UPSC Civil Services Examination.",
        "keywords": "IAS vs IPS vs IFS, difference between IAS and IPS, IFS officer role, civil services difference, IAS IPS IFS roles powers",
        "ogdesc": "IAS vs IPS vs IFS — roles, powers and differences, all through one UPSC exam.",
        "body": """
        <p>The IAS, IPS and IFS are three of the most prestigious All-India and central services — and all three are filled through the <strong>same UPSC Civil Services Examination</strong>. Your rank and preferences decide which service you get. Here is how they differ.</p>

        <h2>IAS — Indian Administrative Service</h2>
        <p>IAS officers form the administrative backbone of the country. They handle policy implementation, district administration (as Collector/DM), and hold key posts in state and central governments. The IAS is generally the top preference for its breadth of responsibility.</p>

        <h2>IPS — Indian Police Service</h2>
        <p>IPS officers lead the police and law-enforcement machinery — maintaining order, preventing crime, and heading forces at district (SP), state (DGP) and central levels (CBI, intelligence, paramilitary). The role is operational and leadership-intensive.</p>

        <h2>IFS — Indian Foreign Service</h2>
        <p>IFS officers represent India abroad. They work in embassies and missions, handle diplomacy, trade and international relations, and shape the country's foreign policy. Postings are global, unlike the India-based IAS and IPS.</p>

        <h2>Key differences at a glance</h2>
        <table>
          <tr><th>Aspect</th><th>IAS</th><th>IPS</th><th>IFS</th></tr>
          <tr><td>Domain</td><td>Administration</td><td>Police &amp; order</td><td>Diplomacy</td></tr>
          <tr><td>Typical posting</td><td>District/State/Centre</td><td>District/State/Centre</td><td>Embassies abroad</td></tr>
          <tr><td>Top post</td><td>Cabinet Secretary</td><td>Director-General</td><td>Foreign Secretary</td></tr>
        </table>

        <blockquote>Same exam, different worlds: the IAS runs administration, the IPS commands the police, and the IFS represents India abroad.</blockquote>

        <div class="cta-box">
          <h3>One exam opens all three</h3>
          <p>Clearing the UPSC CSE is the common gateway. Start with real Prelims PYQs, free.</p>
          <a href="/pyq/" class="btn btn-primary">Practise PYQs →</a>
        </div>
        """,
        "faq": [
            ("Are IAS, IPS and IFS selected through the same exam?", "Yes. All three are filled through the UPSC Civil Services Examination. Your final rank and service preference determine which service you are allotted."),
            ("Which is more powerful, IAS or IPS?", "They are different domains rather than a hierarchy. The IAS leads administration and the IPS leads the police; both are senior, powerful services with distinct responsibilities."),
            ("What does an IFS officer do?", "An IFS (Indian Foreign Service) officer represents India abroad — handling diplomacy, trade and international relations in embassies and missions worldwide."),
        ],
        "related": [
            ("how-to-become-an-ias-officer", "Career Guide", "How to Become an IAS Officer"),
            ("upsc-full-form-and-services", "UPSC 101", "UPSC Full Form & Services"),
            ("government-jobs-after-graduation", "Careers", "Govt Jobs After Graduation"),
        ],
    },
    {
        "slug": "why-become-an-ias-officer",
        "tag": "Motivation",
        "read": "7 min read",
        "title": "Why Become an IAS Officer? The Real Rewards",
        "h1": "Why Become an IAS Officer?",
        "desc": "Why do millions aspire to the IAS? The real reasons to become an IAS officer — impact, leadership, service, variety and the chance to change lives at scale.",
        "keywords": "why become an IAS officer, why UPSC, reasons to become IAS, importance of IAS, why civil services",
        "ogdesc": "The real reasons to become an IAS officer — impact, service and leadership at scale.",
        "body": """
        <p>Every year, millions of Indians prepare for the UPSC Civil Services Examination. Beyond the prestige, what makes the IAS so compelling? Here are the real reasons — worth remembering on the hard days of preparation.</p>

        <h2>1. Impact at scale</h2>
        <p>Few careers let you affect the lives of lakhs of people directly. As a District Magistrate, an IAS officer shapes health, education, welfare and disaster response across an entire district.</p>

        <h2>2. Leadership and responsibility</h2>
        <p>From an early stage, IAS officers lead teams, manage crises and take decisions that matter. The responsibility is immense — and so is the growth.</p>

        <h2>3. Variety like no other job</h2>
        <p>An IAS career spans revenue, development, policy, and postings across departments and levels. No two phases look the same, which keeps the work endlessly engaging.</p>

        <h2>4. Service and purpose</h2>
        <p>At its core, the civil service is about public service — using authority to solve real problems for real people. That sense of purpose is what sustains many officers through demanding years.</p>

        <h2>5. A level playing field</h2>
        <p>The UPSC exam is famously merit-based. A graduate from any background, any stream, any corner of India can earn the top rank through disciplined preparation.</p>

        <div class="cta-box">
          <h3>Turn the dream into a plan</h3>
          <p>Motivation starts the journey; PYQs finish it. Practise real UPSC Prelims questions, free.</p>
          <a href="/pyq/" class="btn btn-primary">Practise PYQs →</a>
        </div>

        <blockquote>The IAS is not just a job — it is a platform to serve, to lead, and to change lives at a scale few careers can match.</blockquote>
        """,
        "faq": [
            ("Why is the IAS so respected in India?", "Because IAS officers hold significant responsibility for administration and public welfare, affecting the lives of large populations directly, with authority to drive real change."),
            ("Is becoming an IAS officer worth it?", "For those motivated by public service, leadership and large-scale impact, yes. It is demanding but offers purpose, variety and influence that few careers match."),
            ("Do I need a special background to aim for the IAS?", "No. The UPSC exam is merit-based and open to graduates of any stream and background. Disciplined preparation matters far more than your starting point."),
        ],
        "related": [
            ("how-to-become-an-ias-officer", "Career Guide", "How to Become an IAS Officer"),
            ("importance-of-education", "Perspective", "The Importance of Education"),
            ("government-jobs-after-graduation", "Careers", "Govt Jobs After Graduation"),
        ],
    },
    {
        "slug": "upsc-full-form-and-services",
        "tag": "UPSC 101",
        "read": "8 min read",
        "title": "UPSC Full Form, Services and Posts Explained",
        "h1": "UPSC Full Form, Services and Posts",
        "desc": "What is the full form of UPSC, what does it do, and which services and posts does the Civil Services Examination lead to — IAS, IPS, IFS, IRS and more, explained simply.",
        "keywords": "UPSC full form, what is UPSC, UPSC services list, UPSC posts, civil services list, IAS IPS IRS full form",
        "ogdesc": "UPSC full form, what it does, and the services and posts the Civil Services Exam leads to.",
        "body": """
        <p><strong>UPSC stands for the Union Public Service Commission.</strong> It is India's central recruiting agency, constituted under Article 315 of the Constitution, responsible for conducting exams for the country's premier civil services.</p>

        <h2>What does UPSC do?</h2>
        <p>The UPSC conducts several examinations, the most famous being the <strong>Civil Services Examination (CSE)</strong>, which recruits officers for the All-India and central services. It also conducts exams like the Engineering Services, CDS, CMS and others.</p>

        <h2>Services the CSE leads to</h2>
        <ul>
          <li><strong>IAS</strong> — Indian Administrative Service (administration)</li>
          <li><strong>IPS</strong> — Indian Police Service (law &amp; order)</li>
          <li><strong>IFS</strong> — Indian Foreign Service (diplomacy)</li>
          <li><strong>IRS</strong> — Indian Revenue Service (taxation)</li>
          <li><strong>IAAS, IRTS, IPoS</strong> and other Group A &amp; B central services</li>
        </ul>
        <p>For how these differ, read <a href="/guides/ias-ips-ifs-difference/">IAS vs IPS vs IFS</a>.</p>

        <h2>How officers are allotted</h2>
        <p>Based on your final rank and the preferences you fill, you are allotted a service. Higher ranks typically get the IAS, IPS or IFS. The final rank is decided by Mains + interview marks.</p>

        <div class="cta-box">
          <h3>Begin at the beginning — PYQs</h3>
          <p>Understand the exam by solving it. Practise UPSC Prelims previous year questions, free.</p>
          <a href="/pyq/" class="btn btn-primary">Practise PYQs →</a>
        </div>

        <h2>Is UPSC only for the IAS?</h2>
        <p>No. While the IAS is the best-known outcome, the CSE fills more than 20 services. Even a rank outside the IAS opens the door to influential, rewarding careers in taxation, railways, audit, foreign affairs and more.</p>
        """,
        "faq": [
            ("What is the full form of UPSC?", "UPSC stands for the Union Public Service Commission, India's central agency for recruiting officers to the civil services through examinations like the Civil Services Examination."),
            ("Which services does the UPSC Civil Services Exam fill?", "It fills over 20 services including the IAS, IPS, IFS and IRS, along with other Group A and Group B central services, based on rank and preference."),
            ("Is UPSC only for becoming an IAS officer?", "No. The IAS is the most sought-after, but the same exam recruits for the IPS, IFS, IRS and many other services — all influential careers."),
        ],
        "related": [
            ("how-to-become-an-ias-officer", "Career Guide", "How to Become an IAS Officer"),
            ("ias-ips-ifs-difference", "Services", "IAS vs IPS vs IFS"),
            ("government-jobs-after-graduation", "Careers", "Govt Jobs After Graduation"),
        ],
    },
    {
        "slug": "importance-of-education",
        "tag": "Perspective",
        "read": "6 min read",
        "title": "The Importance of Education: Why It Changes Lives",
        "h1": "The Importance of Education",
        "desc": "Why education matters — how it builds opportunity, critical thinking, confidence and social mobility, and why disciplined learning is the foundation of every career, including the civil services.",
        "keywords": "importance of education, why education is important, value of education, education and success, benefits of education",
        "ogdesc": "Why education matters — opportunity, thinking, confidence and mobility.",
        "body": """
        <p>Education is the single most powerful lever for changing a life. It is not merely about degrees or exams — it is about the ability to think, to choose, and to shape one's own future. Here is why it matters so deeply.</p>

        <h2>1. Opportunity and mobility</h2>
        <p>Education opens doors that would otherwise stay shut. It is the most reliable path out of disadvantage — allowing a person from any background to compete on merit, whether in a competitive exam or a career.</p>

        <h2>2. Critical thinking</h2>
        <p>A good education teaches you not just facts but how to reason — to weigh evidence, spot flawed arguments and make better decisions. This is exactly the skill tested by exams like the UPSC Civil Services.</p>

        <h2>3. Confidence and voice</h2>
        <p>Knowledge builds confidence. An educated person can articulate ideas, question authority respectfully, and participate fully in society and democracy.</p>

        <h2>4. A foundation for service</h2>
        <p>The most impactful public servants are lifelong learners. Education is what allows an administrator to understand complex problems and craft solutions that genuinely help people.</p>

        <div class="cta-box">
          <h3>Learning, made engaging</h3>
          <p>Turn study into daily progress. Practise UPSC PYQs one question at a time — free, with XP and streaks.</p>
          <a href="/pyq/" class="btn btn-primary">Start learning →</a>
        </div>

        <blockquote>Education is not the filling of a pail, but the lighting of a fire — the discipline of learning is what carries you through any goal, including the civil services.</blockquote>
        """,
        "faq": [
            ("Why is education important?", "Education builds opportunity, critical thinking, confidence and social mobility. It equips people to make better decisions, compete on merit and contribute meaningfully to society."),
            ("How does education help in competitive exams?", "Beyond knowledge, education develops reasoning, discipline and the ability to learn efficiently — the exact skills that competitive exams like the UPSC Civil Services reward."),
            ("Is self-education enough to succeed?", "Disciplined self-study can take you very far, especially with the right resources and consistent practice. Many successful aspirants prepare largely on their own."),
        ],
        "related": [
            ("why-become-an-ias-officer", "Motivation", "Why Become an IAS Officer?"),
            ("how-to-become-an-ias-officer", "Career Guide", "How to Become an IAS Officer"),
            ("government-jobs-after-graduation", "Careers", "Govt Jobs After Graduation"),
        ],
    },
]

TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-G2DK8674FB"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-G2DK8674FB');</script>
  <title>{title} | YESPYQ</title>
  <meta name="description" content="{desc}" />
  <meta name="keywords" content="{keywords}" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <meta name="googlebot" content="index, follow" />
  <meta name="author" content="YESPYQ" />
  <meta name="theme-color" content="#2563eb" />
  <link rel="canonical" href="{base}/guides/{slug}/" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="YESPYQ" />
  <meta property="og:url" content="{base}/guides/{slug}/" />
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
  <link rel="stylesheet" href="/styles.css?v=17" />
  <link rel="stylesheet" href="/blog.css?v=5" />
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"Article","headline":"{h1}","description":"{desc}","image":"{base}/assets/og-image.png","datePublished":"{today}","dateModified":"{today}","inLanguage":"en-IN","author":{{"@type":"Organization","name":"YESPYQ","url":"{base}/"}},"publisher":{{"@type":"EducationalOrganization","name":"YESPYQ","logo":{{"@type":"ImageObject","url":"{base}/assets/favicon.svg"}}}},"mainEntityOfPage":{{"@type":"WebPage","@id":"{base}/guides/{slug}/"}}}}
  </script>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{base}/"}},{{"@type":"ListItem","position":2,"name":"Guides","item":"{base}/guides/"}},{{"@type":"ListItem","position":3,"name":"{tag}","item":"{base}/guides/{slug}/"}}]}}
  </script>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{faq_ld}]}}
  </script>
  <script src="/theme.js?v=1"></script>
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="/"><img src="/assets/favicon.svg" alt="" class="brand-mark" /><span class="brand-name">YES<span>PYQ</span></span></a>
      <nav class="main-nav">
        <a href="/">Home</a>
        <a href="/">Practice</a>
        <a href="/subjects/">Subjects</a>
      </nav>
      <a href="/" class="btn btn-primary btn-sm">Start Practice</a>
    </div>
  </header>
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/guides/">Guides</a> › {tag}</nav>
      <h1>{h1}</h1>
      <div class="meta"><span>By YESPYQ</span> · <span>Updated {monthyear}</span> · <span>{read}</span></div>
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
      <div class="footer-brand"><img src="/assets/favicon.svg" alt="" class="brand-mark" /><span class="brand-name">YES<span>PYQ</span></span><p>Previous Year Questions, simplified.</p></div>
      <div class="footer-col"><h4>Practice</h4><a href="/">Home</a><a href="/subjects/">Subjects</a><a href="/pyq/">All PYQs</a><a href="/guides/">Guides</a><a href="/blog/">Blog</a></div>
      <div class="footer-col"><h4>Company</h4><a href="/about/">About</a><a href="/contact/">Contact</a></div>
      <div class="footer-col"><h4>Legal</h4><a href="/privacy-policy/">Privacy Policy</a><a href="/terms/">Terms &amp; Conditions</a><a href="/disclaimer/">Disclaimer</a></div>
    </div>
    <div class="footer-bottom">© <span id="year"></span> YESPYQ.com · Built for UPSC CSE aspirants · Not affiliated with UPSC</div>
  </footer>
  <script>document.getElementById("year").textContent = new Date().getFullYear();</script>
</body>
</html>
"""

HUB_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-G2DK8674FB"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-G2DK8674FB');</script>
  <title>UPSC &amp; Career Guides — How to Become an IAS Officer &amp; More | YESPYQ</title>
  <meta name="description" content="Free UPSC and career guides — how to become an IAS officer, government jobs after graduation, IAS vs IPS vs IFS, UPSC full form and services, and why civil services matter." />
  <meta name="keywords" content="UPSC guides, how to become IAS, government jobs after graduation, IAS IPS IFS, UPSC full form, civil services guide" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <meta name="author" content="YESPYQ" />
  <meta name="theme-color" content="#2563eb" />
  <link rel="canonical" href="{base}/guides/" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="YESPYQ" />
  <meta property="og:url" content="{base}/guides/" />
  <meta property="og:title" content="UPSC &amp; Career Guides | YESPYQ" />
  <meta property="og:description" content="How to become an IAS officer, government jobs after graduation, IAS vs IPS vs IFS, and more — free." />
  <meta property="og:image" content="{base}/assets/og-image.png" />
  <meta property="og:locale" content="en_IN" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="UPSC & Career Guides | YESPYQ" />
  <meta name="twitter:description" content="How to become an IAS officer, govt jobs, IAS vs IPS vs IFS, and more." />
  <meta name="twitter:image" content="{base}/assets/og-image.png" />
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg" />
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" />
  <link rel="manifest" href="/manifest.webmanifest" />
  <link rel="stylesheet" href="/styles.css?v=17" />
  <link rel="stylesheet" href="/blog.css?v=5" />
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{base}/"}},{{"@type":"ListItem","position":2,"name":"Guides","item":"{base}/guides/"}}]}}
  </script>
  <script src="/theme.js?v=1"></script>
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="/"><img src="/assets/favicon.svg" alt="" class="brand-mark" /><span class="brand-name">YES<span>PYQ</span></span></a>
      <nav class="main-nav">
        <a href="/">Home</a>
        <a href="/">Practice</a>
        <a href="/subjects/">Subjects</a>
      </nav>
      <a href="/" class="btn btn-primary btn-sm">Start Practice</a>
    </div>
  </header>
  <main>
    <section class="blog-hero"><div class="container"><span class="pill">UPSC &amp; Career Guides</span>
      <h1>Guides for UPSC Aspirants</h1>
      <p>Clear, honest answers to the big questions — how to become an IAS officer, which government jobs to target, and what the civil services really involve.</p></div></section>
    <div class="container"><div class="post-grid">
{cards}
    </div></div>
  </main>
  <footer class="site-footer">
    <div class="container footer-inner">
      <div class="footer-brand"><img src="/assets/favicon.svg" alt="" class="brand-mark" /><span class="brand-name">YES<span>PYQ</span></span><p>Previous Year Questions, simplified.</p></div>
      <div class="footer-col"><h4>Practice</h4><a href="/">Home</a><a href="/subjects/">Subjects</a><a href="/pyq/">All PYQs</a><a href="/guides/">Guides</a><a href="/blog/">Blog</a></div>
      <div class="footer-col"><h4>Company</h4><a href="/about/">About</a><a href="/contact/">Contact</a></div>
      <div class="footer-col"><h4>Legal</h4><a href="/privacy-policy/">Privacy Policy</a><a href="/terms/">Terms &amp; Conditions</a><a href="/disclaimer/">Disclaimer</a></div>
    </div>
    <div class="footer-bottom">© <span id="year"></span> YESPYQ.com · Built for UPSC CSE aspirants · Not affiliated with UPSC</div>
  </footer>
  <script>document.getElementById("year").textContent = new Date().getFullYear();</script>
</body>
</html>
"""

def esc(s):
    return s.replace('"', '\\"')

def build(g):
    faq_html = ""
    faq_ld = []
    for q, a in g["faq"]:
        faq_html += '          <details>\n            <summary>{}</summary>\n            <p>{}</p>\n          </details>\n'.format(q, a)
        faq_ld.append('{{"@type":"Question","name":"{}","acceptedAnswer":{{"@type":"Answer","text":"{}"}}}}'.format(esc(q), esc(a)))
    related_html = ""
    for slug, tag, title in g["related"]:
        related_html += '          <a href="/guides/{}/"><span class="tag">{}</span><b>{}</b></a>\n'.format(slug, tag, title)
    return TMPL.format(
        title=g["title"], desc=g["desc"], keywords=g["keywords"], ogdesc=g["ogdesc"],
        base=BASE, slug=g["slug"], today=TODAY, monthyear="July 2026", h1=g["h1"], tag=g["tag"], read=g["read"],
        body=g["body"], faq_ld=",".join(faq_ld), faq_html=faq_html, related_html=related_html,
    )

def build_hub():
    cards = ""
    for g in GUIDES:
        cards += ('        <a class="post-card" href="/guides/{slug}/"><span class="tag">{tag}</span>'
                  '<h2>{h1}</h2><p>{ogdesc}</p><div class="meta"><span>{read}</span></div>'
                  '<span class="read">Read guide →</span></a>\n').format(
            slug=g["slug"], tag=g["tag"], h1=g["h1"], ogdesc=g["ogdesc"], read=g["read"])
    return HUB_TMPL.format(base=BASE, cards=cards)

def main():
    for g in GUIDES:
        d = os.path.join(ROOT, "guides", g["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(build(g))
    os.makedirs(os.path.join(ROOT, "guides"), exist_ok=True)
    with open(os.path.join(ROOT, "guides", "index.html"), "w") as f:
        f.write(build_hub())
    print("wrote {} guides + hub".format(len(GUIDES)))

if __name__ == "__main__":
    main()
