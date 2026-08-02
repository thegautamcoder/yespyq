#!/usr/bin/env python3
"""Generate one dedicated SEO page per JEE/NEET/SSC-CGL/Defence/Board
question, mirroring what _gen_questions.py already does for UPSC's
/pyq/q/<slug>/ pages — one URL per question so each can rank on its own
exact-match search, instead of only existing inside a chapter page that
bundles dozens of questions together.

Reuses _gen_exams.py's gating (question_block), grouping and free/gated
determination so a question's paywall state is IDENTICAL whether it's
viewed on its chapter page or its own dedicated page — this does NOT
change the paywall: options are always free, the correct answer +
explanation stay gated for the ~90% non-preview questions, exactly like
the chapter pages.

- /exams/<exam>/q/<slug>/     one page per question
- sitemap-exam-questions.xml  all of the above
Run from repo root: python3 _gen_exam_questions.py (after _gen_exams.py)
"""
import os
from collections import defaultdict

import _gen_exams as ge

BASE = ge.BASE
TODAY = ge.TODAY
ROOT = ge.ROOT


def make_title(x, ecfg, sname, trunc_len=90):
    qplain = ge.plain(x["q"])
    short = qplain[:trunc_len].rsplit(" ", 1)[0] if len(qplain) > trunc_len else qplain
    year_bit = f" {x['y']}" if x.get("y") else ""
    # re-normalize: truncation can leave a run of whitespace that only
    # collapses to one space once attr()/plain() runs at output time —
    # normalize now so collision-detection matches the final HTML exactly
    return ge.plain(f"{short} — {ecfg['name']}{year_bit} {sname} PYQ | YESPYQ")


def make_desc(x, ecfg, sname, is_free, trunc_len=140):
    qplain = ge.plain(x["q"])
    short = qplain[:trunc_len]
    if is_free:
        d = f"{short} — see the correct answer and explanation, free. {ecfg['name']} {sname} previous year question on YESPYQ."
    else:
        d = f"{short} — {ecfg['name']} {sname} previous year question. Options free to see; unlock the answer & explanation with PYQ Pass."
    return ge.plain(d)


def question_page(x, ecfg, exam, subject, sname, sicon, chapter, gated, is_free, prev_slug, next_slug, title, desc):
    slug = ge.qslug(x)
    canonical = f"{BASE}/exams/{exam}/q/{slug}/"
    chapter_url = f"/exams/{exam}/{subject}/{ge.slugify(chapter)}/"

    qplain = ge.plain(x["q"])
    ans_letter = chr(97 + x["a"])
    if is_free:
        html_mode = x.get("fmt") == "html"
        ans_text = ge.plain(x["o"][x["a"]]) if not html_mode else ge.plain(x["o"][x["a"]])
        ans_summary = ge.json_esc(f"Correct answer: {ans_letter}) {ans_text}. {ge.plain(x['exp'])}"[:1100])
        answer_block = f'"acceptedAnswer":{{"@type":"Answer","text":"{ans_summary}","url":"{canonical}","author":{{"@type":"Organization","name":"YESPYQ","url":"{BASE}/"}},"datePublished":"{TODAY}"}}'
    else:
        teaser = ge.json_esc("Options are free to see. Unlock the correct answer and full explanation with PYQ Pass.")
        answer_block = f'"acceptedAnswer":{{"@type":"Answer","text":"{teaser}","url":"{canonical}","author":{{"@type":"Organization","name":"YESPYQ","url":"{BASE}/"}},"datePublished":"{TODAY}"}}'

    schema = f'''  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"QAPage","mainEntity":{{"@type":"Question","name":"{ge.json_esc(x['q'])}","text":"{ge.json_esc(x['q'])}","answerCount":1,"author":{{"@type":"Organization","name":"YESPYQ","url":"{BASE}/"}},"datePublished":"{TODAY}",{answer_block}}}}}
  </script>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{BASE}/"}},{{"@type":"ListItem","position":2,"name":"Exams","item":"{BASE}/exams/"}},{{"@type":"ListItem","position":3,"name":"{ge.json_esc(ecfg['name'])}","item":"{BASE}/exams/{exam}/"}},{{"@type":"ListItem","position":4,"name":"{ge.json_esc(sname)}","item":"{BASE}/exams/{exam}/{subject}/"}},{{"@type":"ListItem","position":5,"name":"{ge.json_esc(chapter)}","item":"{BASE}{chapter_url}"}},{{"@type":"ListItem","position":6,"name":"Question","item":"{canonical}"}}]}}
  </script>'''

    qs_html = ge.question_block(x, 1, gated, free=is_free)

    nav_links = ""
    if prev_slug:
        nav_links += f'<a class="btn btn-ghost" href="/exams/{exam}/q/{prev_slug}/">← Previous question</a>'
    if next_slug:
        nav_links += f'<a class="btn btn-ghost" href="/exams/{exam}/q/{next_slug}/">Next question →</a>'

    body = f'''{ge.HEADER}
  <main>
    <article class="article">
      <nav class="breadcrumb"><a href="/">Home</a> › <a href="/exams/">Exams</a> › <a href="/exams/{exam}/">{ge.esc(ecfg['name'])}</a> › <a href="/exams/{exam}/{subject}/">{ge.esc(sname)}</a> › <a href="{chapter_url}">{ge.esc(chapter)}</a></nav>
      <div class="qtags"><span class="qtag">{ecfg['icon']} {ge.esc(ecfg['name'])}</span><span class="qtag">{sicon} {ge.esc(sname)}</span>{f'<span class="qtag">{x["y"]}</span>' if x.get("y") else ""}</div>
      <h1>{ge.esc(qplain[:120])}{"…" if len(qplain) > 120 else ""}</h1>
{qs_html}
      <div class="q-nav" style="display:flex;gap:.7rem;flex-wrap:wrap;margin:1.2rem 0">{nav_links}</div>
      <div class="cta-box">
        <h3>Practice more {ge.esc(ecfg['name'])} {ge.esc(sname)} PYQs</h3>
        <p>See every question on {ge.esc(chapter)}, or browse the full {ge.esc(ecfg['name'])} question bank.</p>
        <a href="{chapter_url}" class="btn btn-primary">See all questions on {ge.esc(chapter)} →</a>
      </div>
    </article>
  </main>
{ge.FOOTER}
{ge.KATEX_SCRIPTS}
</body>
</html>'''
    extra_head = ge.KATEX_HEAD
    return ge.head(ge.attr(title), ge.attr(desc), canonical, schema, extra_head) + body


def main():
    sitemap_urls = []
    total_written = 0

    for exam, ecfg in ge.EXAMS.items():
        if not ecfg.get("gated"):
            continue  # only gated exams need per-question paywall-consistent pages
        items = ge.load_bank(exam)
        by_subject = defaultdict(list)
        for x in items:
            by_subject[x["subject"]].append(x)
        subjects = ge.resolve_subjects(ecfg, by_subject)
        original_subjects = ecfg["subjects"]
        ecfg["subjects"] = subjects

        # Precompute title/description with collision-avoidance, same
        # pattern as _gen_questions.py: extend truncation, then guarantee
        # uniqueness with a question-ID suffix for any leftover collision.
        all_rows = []  # (x, sname, sicon, chapter, gated, is_free)
        for subject in subjects:
            sname, sicon = ecfg["subjects"][subject]
            sitems = by_subject.get(subject, [])
            by_chapter = defaultdict(list)
            for x in sitems:
                by_chapter[x.get("chapter") or "General"].append(x)
            for chapter, qs in by_chapter.items():
                free_n = ge.free_preview_count(len(qs))
                for i, x in enumerate(qs):
                    all_rows.append((x, subject, sname, sicon, chapter, i < free_n))

        seen_titles, seen_descs = {}, {}
        titles, descs = {}, {}
        for x, subject, sname, sicon, chapter, is_free in all_rows:
            t = make_title(x, ecfg, sname)
            if t in seen_titles:
                t = f"{t} (Q{x['i'].split('-')[-1]})"
            seen_titles[t] = x["i"]
            titles[x["i"]] = t

            d = make_desc(x, ecfg, sname, is_free)
            if d in seen_descs:
                d = f"{d} [{x['i'].split('-')[-1]}]"
            seen_descs[d] = x["i"]
            descs[x["i"]] = d

        # Group by chapter again (in the same order) to wire prev/next links.
        by_chapter_slugs = defaultdict(list)
        for x, subject, sname, sicon, chapter, is_free in all_rows:
            by_chapter_slugs[(subject, chapter)].append(ge.qslug(x))

        chapter_pos = defaultdict(int)
        for x, subject, sname, sicon, chapter, is_free in all_rows:
            key = (subject, chapter)
            slugs = by_chapter_slugs[key]
            pos = chapter_pos[key]
            chapter_pos[key] += 1
            prev_slug = slugs[pos - 1] if pos > 0 else None
            next_slug = slugs[pos + 1] if pos + 1 < len(slugs) else None

            slug = ge.qslug(x)
            page = question_page(
                x, ecfg, exam, subject, sname, sicon, chapter,
                gated=True, is_free=is_free,
                prev_slug=prev_slug, next_slug=next_slug,
                title=titles[x["i"]], desc=descs[x["i"]],
            )
            ge.write(f"exams/{exam}/q/{slug}", page)
            sitemap_urls.append(f"{BASE}/exams/{exam}/q/{slug}/")
            total_written += 1

        ecfg["subjects"] = original_subjects
        print(f"{exam}: wrote {len([r for r in all_rows])} question pages")

    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in sitemap_urls:
        sm.append(f"  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>0.5</priority></url>")
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap-exam-questions.xml"), "w").write("\n".join(sm))

    print(f"TOTAL: wrote {total_written} question pages. sitemap-exam-questions.xml: {len(sitemap_urls)} URLs")


if __name__ == "__main__":
    main()
