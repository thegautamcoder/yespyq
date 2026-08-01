#!/usr/bin/env python3
"""One-off ETL: import NEET/JEE/Board PYQs from an xlsx export into YESPYQ's
exam-data schema, cleaned + bucketed + ID-assigned.

Reads: /Users/pw/Downloads/yes..xlsx (sheet "Query result")
Writes: exam-data/_staging/{neet,board,jee}_new.json

Rows with <img> tags (in question/options/solution) are excluded from this
pass. IDs continue the existing jee.json/neet.json sequences; board.json is
a brand-new bucket. Re-running reproduces identical output (pure function of
the source xlsx + the current exam-data/{jee,neet}.json counts).

Run from repo root: python3 _import_exam_xlsx.py
"""
import json
import os
import re

import openpyxl
from bs4 import BeautifulSoup, NavigableString

ROOT = os.path.dirname(os.path.abspath(__file__))
XLSX_PATH = "/Users/pw/Downloads/yes..xlsx"
STAGING_DIR = os.path.join(ROOT, "exam-data", "_staging")

EXPECTED_COUNTS = {"neet": 747, "board": 1348, "jee": 3908}

JEE_EXAMS = {"JEE Mains", "JEE Advanced", "JEE", "BITSAT", "VITEEE", "MHT CET"}
NEET_EXAMS = {"NEET", "AIIMS"}

ALLOWED_ATTRLESS_TAGS = {
    "p", "br", "ul", "ol", "li", "strong", "b", "em", "i", "sub", "sup",
    "table", "thead", "tbody", "tr", "td", "th",
}


def bucket_exam(exam_raw):
    e = (exam_raw or "").strip()
    if e in JEE_EXAMS:
        return "jee"
    if e in NEET_EXAMS:
        return "neet"
    return "board"


def bucket_subject(subject_raw):
    s = (subject_raw or "").strip()
    if s in ("Zoology", "Botany"):
        return "biology"
    return s.lower()


def has_img(*cells):
    return any("<img" in str(c or "") for c in cells)


def _math_to_latex(math_tag):
    ann = math_tag.find("annotation", attrs={"encoding": re.compile("latex", re.I)})
    if ann and ann.get_text(strip=True):
        return ann.get_text()
    return None


def clean_html(raw):
    """Sanitize an HTML cell: strip to a small allowlist, replace LaTeX-sourced
    math (data-math attrs, or <math><semantics><annotation encoding=LaTeX>) with
    literal \\( \\)/\\[ \\] spans for KaTeX, and leave bare MathML (no LaTeX
    source) untouched so it renders natively in the browser."""
    if raw is None:
        return ""
    soup = BeautifulSoup(str(raw), "html.parser")

    # 1. elements carrying a data-math attribute -> replace whole element
    for el in soup.find_all(attrs={"data-math": True}):
        latex = el["data-math"]
        classes = el.get("class") or []
        display = "math-block" in classes
        wrapped = f"\\[{latex}\\]" if display else f"\\({latex}\\)"
        el.replace_with(NavigableString(wrapped))

    # 2. remaining <math> blocks with a LaTeX annotation -> replace inline
    for el in soup.find_all("math"):
        latex = _math_to_latex(el)
        if latex:
            el.replace_with(NavigableString(f"\\({latex}\\)"))
        # else: leave <math>...</math> verbatim (native MathML rendering)

    # 3. allowlist pass over everything NOT inside a surviving <math> block
    for el in soup.find_all(True):
        if el.name == "math" or el.find_parent("math"):
            continue
        if el.name in ALLOWED_ATTRLESS_TAGS:
            el.attrs = {}
        else:
            el.unwrap()

    # 4. collapse whitespace in text nodes outside <math>
    for node in soup.find_all(string=True):
        if node.find_parent("math"):
            continue
        node.replace_with(re.sub(r"\s+", " ", str(node)))

    return str(soup).strip()


def load_rows():
    wb = openpyxl.load_workbook(XLSX_PATH, read_only=True, data_only=True)
    ws = wb["Query result"]
    return list(ws.iter_rows(min_row=2, values_only=True))


def main():
    rows = load_rows()
    buckets = {"neet": [], "board": [], "jee": []}

    for row in rows:
        (q, o1, o2, o3, o4, o5, corr, sol, typ, diff, klass, subj, chap, cat, exam) = row
        if has_img(q, o1, o2, o3, o4, sol):
            continue
        eb = bucket_exam(exam)
        entry = {
            "q": clean_html(q),
            "o": [clean_html(o1), clean_html(o2), clean_html(o3), clean_html(o4)],
            "a": int(str(corr).strip()) - 1,
            "subject": bucket_subject(subj),
            "chapter": str(chap).strip(),
            "y": None,
            "exp": clean_html(sol),
            "fmt": "html",
        }
        if eb == "board":
            entry["cls"] = str(klass).strip()
        buckets[eb].append(entry)

    for eb, expected in EXPECTED_COUNTS.items():
        actual = len(buckets[eb])
        assert actual == expected, f"{eb}: expected {expected} rows, got {actual}"

    # assign IDs, continuing existing sequences
    start = {
        "neet": len(json.load(open(os.path.join(ROOT, "exam-data", "neet.json")))) + 1,
        "jee": len(json.load(open(os.path.join(ROOT, "exam-data", "jee.json")))) + 1,
        "board": 1,
    }
    prefix = {"neet": "NEET", "jee": "JEE", "board": "BOARD"}

    os.makedirs(STAGING_DIR, exist_ok=True)
    for eb, items in buckets.items():
        n = start[eb]
        ided = []
        for entry in items:
            ided.append({"i": f"{prefix[eb]}-{n:05d}", **entry})
            n += 1
        out_path = os.path.join(STAGING_DIR, f"{eb}_new.json")
        with open(out_path, "w") as f:
            json.dump(ided, f, ensure_ascii=False, indent=1)
        print(f"{eb}: {len(ided)} rows -> {out_path} (IDs {ided[0]['i']}..{ided[-1]['i']})")


if __name__ == "__main__":
    main()
