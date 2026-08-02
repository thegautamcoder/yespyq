#!/usr/bin/env python3
"""ETL: import high-confidence JEE/NEET/Board PYQs from yessss.xlsx.

Reads: /Users/pw/Downloads/yessss.xlsx
Writes: exam-data/_staging/{neet,board,jee}_new.json  (net-new only)

Excludes:
  - any row with <img>
  - bad / missing answers or empty options
  - garbled / low-confidence HTML
  - Devanagari-only / non-STEM board subjects we don't surface yet
  - duplicates of live exam-data

Run: python3 _import_exam_xlsx.py
"""
import json
import os
import re
from collections import Counter

import openpyxl
from bs4 import BeautifulSoup, NavigableString

ROOT = os.path.dirname(os.path.abspath(__file__))
XLSX_PATH = "/Users/pw/Downloads/yessss.xlsx"
STAGING_DIR = os.path.join(ROOT, "exam-data", "_staging")

JEE_EXAMS = {"JEE Mains", "JEE Advanced", "JEE", "BITSAT", "VITEEE", "MHT CET"}
NEET_EXAMS = {"NEET", "AIIMS"}

# Only subjects we already ship UI + SEO pages for
ALLOWED_SUBJECTS = {
    "jee": {"physics", "chemistry", "maths"},
    "neet": {"physics", "chemistry", "biology"},
    "board": {"physics", "chemistry", "maths"},
}

ALLOWED_ATTRLESS_TAGS = {
    "p", "br", "ul", "ol", "li", "strong", "b", "em", "i", "sub", "sup",
    "table", "thead", "tbody", "tr", "td", "th",
}

SUBJECT_MAP = {
    "zoology": "biology",
    "botany": "biology",
    "biology": "biology",
    "physics": "physics",
    "chemistry": "chemistry",
    "maths": "maths",
    "mathematics": "maths",
    "core maths": "maths",
}

DEVANAGARI = re.compile(r"[\u0900-\u097F]")
GARBLED = re.compile(r"spantrebuchet|data-sheets-root|font-weight:normal|mso-|<!--", re.I)
BAD_OPT = re.compile(
    r"consider the following|incorrect\s*:|correct\s*:|\([a-d]\)\s|"
    r"select the correct answer|explanation\s*:|hence\s+(the\s+)?(correct|answer)",
    re.I,
)


def plain(s):
    t = BeautifulSoup(str(s or ""), "html.parser").get_text(" ", strip=True)
    return re.sub(r"\s+", " ", t).strip()


def bucket_exam(exam_raw, cat_raw=None, subj_raw=None, q_raw=None):
    e = (exam_raw or "").strip()
    if e in JEE_EXAMS:
        return "jee"
    if e in NEET_EXAMS:
        return "neet"
    if e:
        return "board"

    c = (cat_raw or "").strip()
    if c == "JEE":
        return "jee"
    if c == "NEET":
        return "neet"
    if c == "NEET-JEE":
        s = (subj_raw or "").strip().lower()
        if s in ("botany", "zoology", "biology"):
            return "neet"
        if s in ("physics", "chemistry", "maths", "mathematics"):
            return "jee"

    qt = plain(q_raw)
    if re.search(r"\bJEE\b", qt, re.I):
        return "jee"
    if re.search(r"\bNEET\b|\bAIIMS\b", qt, re.I):
        return "neet"
    # empty exam + vernacular/arts without clear tag → low confidence
    if c in ("Vernacular", "Arts", "Nursing", "Xylem", ""):
        return None
    return "board"


def bucket_subject(subject_raw):
    s = (subject_raw or "").strip().lower()
    return SUBJECT_MAP.get(s)


def has_img(*cells):
    return any("<img" in str(c or "").lower() for c in cells)


def fingerprint(q):
    return plain(q).lower()[:500]


def _math_to_latex(math_tag):
    ann = math_tag.find("annotation", attrs={"encoding": re.compile("latex", re.I)})
    if ann and ann.get_text(strip=True):
        return ann.get_text()
    return None


def clean_html(raw):
    if raw is None:
        return ""
    soup = BeautifulSoup(str(raw), "html.parser")

    for el in soup.find_all(attrs={"data-math": True}):
        latex = el["data-math"]
        classes = el.get("class") or []
        display = "math-block" in classes
        wrapped = f"\\[{latex}\\]" if display else f"\\({latex}\\)"
        el.replace_with(NavigableString(wrapped))

    for el in soup.find_all("math"):
        latex = _math_to_latex(el)
        if latex:
            el.replace_with(NavigableString(f"\\({latex}\\)"))

    for el in soup.find_all(True):
        if el.name == "math" or el.find_parent("math"):
            continue
        if el.name in ALLOWED_ATTRLESS_TAGS:
            el.attrs = {}
        else:
            el.unwrap()

    for node in soup.find_all(string=True):
        if node.find_parent("math"):
            continue
        node.replace_with(re.sub(r"\s+", " ", str(node)))

    return str(soup).strip()


def parse_answer(corr):
    try:
        a = int(str(corr).strip()) - 1
    except (TypeError, ValueError):
        return None
    if a not in (0, 1, 2, 3):
        return None
    return a


def confident(q, opts, sol, subject, exam_bucket):
    """Strict quality gate — skip anything we are not confident about."""
    if exam_bucket not in ALLOWED_SUBJECTS:
        return False, "bucket"
    if subject not in ALLOWED_SUBJECTS[exam_bucket]:
        return False, "subject"

    qp = plain(q)
    if len(qp) < 24:
        return False, "short_q"
    if DEVANAGARI.search(qp) and len(re.sub(DEVANAGARI, "", qp)) < 20:
        return False, "non_english"
    if GARBLED.search(str(q or "")):
        return False, "garbled"
    if re.search(r"\bOptions?\s*$", qp):
        return False, "truncated"

    plains = [plain(o) for o in opts]
    if any(len(p) < 1 for p in plains):
        return False, "empty_opt"
    if any(len(p) > 400 for p in plains):
        return False, "long_opt"
    if any(len(p) <= 2 and not re.match(r"^[a-z0-9]+$", p, re.I) for p in plains):
        return False, "punct_opt"
    if any(BAD_OPT.search(p) for p in plains):
        return False, "bad_opt"
    if any(GARBLED.search(str(o or "")) for o in opts):
        return False, "garbled_opt"
    # options should be distinct
    if len(set(p.lower() for p in plains)) < 4:
        return False, "dup_opts"

    sp = plain(sol)
    if len(sp) < 30:
        return False, "thin_sol"
    if GARBLED.search(str(sol or "")):
        return False, "garbled_sol"

    return True, "ok"


def load_live_fingerprints():
    fps = set()
    starts = {}
    for eb in ("jee", "neet", "board"):
        data = json.load(open(os.path.join(ROOT, "exam-data", f"{eb}.json")))
        starts[eb] = len(data) + 1
        for item in data:
            fps.add(fingerprint(item.get("q")))
    return fps, starts


def main():
    live_fps, start = load_live_fingerprints()
    wb = openpyxl.load_workbook(XLSX_PATH, read_only=True, data_only=True)
    ws = wb["Query result"]

    buckets = {"neet": [], "board": [], "jee": []}
    seen_batch = set()
    stats = Counter()

    for row in ws.iter_rows(min_row=2, values_only=True):
        (q, o1, o2, o3, o4, o5, corr, sol, typ, diff, klass, subj, chap, cat, exam) = row[:15]
        stats["rows"] += 1

        if has_img(q, o1, o2, o3, o4, sol):
            stats["img"] += 1
            continue

        ans = parse_answer(corr)
        if ans is None:
            stats["bad_answer"] += 1
            continue

        eb = bucket_exam(exam, cat, subj, q)
        if not eb:
            stats["low_conf_bucket"] += 1
            continue

        subject = bucket_subject(subj)
        if subject not in ALLOWED_SUBJECTS.get(eb, set()):
            stats["skip_subject"] += 1
            continue

        # Clean first — spreadsheet junk (spantrebuchet, data-sheets-*) unwraps away.
        q_c = clean_html(q)
        o_c = [clean_html(o1), clean_html(o2), clean_html(o3), clean_html(o4)]
        sol_c = clean_html(sol)

        ok, reason = confident(q_c, o_c, sol_c, subject, eb)
        if not ok:
            stats[f"skip_{reason}"] += 1
            continue

        fp = fingerprint(q_c)
        if not fp or fp in live_fps or fp in seen_batch:
            stats["dup"] += 1
            continue

        entry = {
            "q": q_c,
            "o": o_c,
            "a": ans,
            "subject": subject,
            "chapter": str(chap or "").strip() or "General",
            "y": None,
            "exp": sol_c,
            "fmt": "html",
        }
        if eb == "board":
            entry["cls"] = str(klass or "").strip()

        buckets[eb].append(entry)
        seen_batch.add(fp)
        stats[f"new_{eb}"] += 1

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
        with open(os.path.join(STAGING_DIR, f"{eb}_progress.json"), "w") as f:
            json.dump({"offset": 0}, f)
        if ided:
            print(f"{eb}: {len(ided)} NEW -> {out_path} ({ided[0]['i']}..{ided[-1]['i']})")
        else:
            print(f"{eb}: 0 NEW -> {out_path}")

    print("stats:", dict(stats))


if __name__ == "__main__":
    main()
