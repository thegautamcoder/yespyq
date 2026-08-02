#!/usr/bin/env python3
"""One-off: add Smart Mock + PYQ Pass nav links and the brand-mark logo to
every static page's header, so it matches the homepage/_gen_exams.py nav.
Skips index.html (homepage, hand-edited SPA header), pyq-pass/index.html
(hand-edited), resizer/index.html (separate standalone tool, own header),
and everything under exams/ (regenerated via _gen_exams.py instead).
Run from repo root: python3 _fix_header_nav.py
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP = {
    os.path.join(ROOT, "index.html"),
    os.path.join(ROOT, "pyq-pass", "index.html"),
    os.path.join(ROOT, "resizer", "index.html"),
}

PRACTICE_RE = re.compile(r'(<a href="/"(?: class="active")?>Practice</a>)')
BLOG_RE = re.compile(r'(<a href="/blog/"(?: class="active")?>Blog</a>)')

SMART_MOCK_LINK = '<a href="/">Smart Mock</a>'
PYQ_PASS_LINK = '<a href="/pyq-pass/">PYQ Pass</a>'


def fix(path):
    with open(path, encoding="utf-8") as f:
        html = f.read()
    orig = html

    if "site-header" not in html or ">Practice</a>" not in html:
        return False  # not a standard-header page (e.g. resizer's kin)

    if "Smart Mock" not in html:
        html, _ = PRACTICE_RE.subn(r"\1" + SMART_MOCK_LINK, html, count=1)

    if ">PYQ Pass</a>" not in html.split("main-nav", 1)[1].split("</nav>", 1)[0]:
        html, _ = BLOG_RE.subn(r"\1" + PYQ_PASS_LINK, html, count=1)

    if html != orig:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return True
    return False


def main():
    files = glob.glob(os.path.join(ROOT, "**", "index.html"), recursive=True)
    changed = 0
    skipped_no_match = []
    for f in files:
        if f in SKIP or "/exams/" in f:
            continue
        try:
            if fix(f):
                changed += 1
            else:
                skipped_no_match.append(f)
        except Exception as e:
            print("ERROR", f, e)
    print(f"Updated {changed} files.")
    if skipped_no_match:
        print(f"{len(skipped_no_match)} files had no header match (sampling first 10):")
        for f in skipped_no_match[:10]:
            print(" ", os.path.relpath(f, ROOT))


if __name__ == "__main__":
    main()
