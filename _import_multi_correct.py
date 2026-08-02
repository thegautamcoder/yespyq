#!/usr/bin/env python3
"""Import multi-correct PYQs (correctoptions like 1,2,4) from finalyes + yessss.

Skips images / empty options / dups. Appends into exam-data/{jee,neet,board}.json
with a = [0-based indices] and kind = "multi".
"""
import json, os, re
from collections import Counter
import openpyxl
from bs4 import BeautifulSoup, NavigableString

ROOT = os.path.dirname(os.path.abspath(__file__))
PATHS = ["/Users/pw/Downloads/finalyes.xlsx", "/Users/pw/Downloads/yessss.xlsx"]

JEE_EXAMS = {"JEE Mains", "JEE Advanced", "JEE", "BITSAT", "VITEEE", "MHT CET"}
NEET_EXAMS = {"NEET", "AIIMS"}
ALLOWED = {
    "p", "br", "ul", "ol", "li", "strong", "b", "em", "i", "sub", "sup",
    "table", "thead", "tbody", "tr", "td", "th",
}
SUBJECT_MAP = {
    "zoology": "biology", "botany": "biology", "biology": "biology",
    "physics": "physics", "chemistry": "chemistry",
    "maths": "maths", "mathematics": "maths", "core maths": "maths",
}


def plain(s):
    t = BeautifulSoup(str(s or ""), "html.parser").get_text(" ", strip=True)
    return re.sub(r"\s+", " ", t).strip()


def fingerprint(q):
    return plain(q).lower()[:500]


def has_img(*cells):
    return any("<img" in str(c or "").lower() for c in cells)


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
    qt = plain(q_raw)
    if re.search(r"\bJEE\b", qt, re.I):
        return "jee"
    if re.search(r"\bNEET\b|\bAIIMS\b", qt, re.I):
        return "neet"
    return "board"


def bucket_subject(subject_raw, eb):
    s = (subject_raw or "").strip().lower()
    if s in SUBJECT_MAP:
        return SUBJECT_MAP[s]
    slug = re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "general"
    return slug


def clean_html(raw):
    if raw is None:
        return ""
    soup = BeautifulSoup(str(raw), "html.parser")
    for el in soup.find_all(attrs={"data-math": True}):
        latex = el["data-math"]
        display = "math-block" in (el.get("class") or [])
        el.replace_with(NavigableString(f"\\[{latex}\\]" if display else f"\\({latex}\\)"))
    for el in soup.find_all("math"):
        ann = el.find("annotation", attrs={"encoding": re.compile("latex", re.I)})
        if ann and ann.get_text(strip=True):
            el.replace_with(NavigableString(f"\\({ann.get_text()}\\)"))
    for el in soup.find_all(True):
        if el.name == "math" or el.find_parent("math"):
            continue
        if el.name in ALLOWED:
            el.attrs = {}
        else:
            el.unwrap()
    for node in soup.find_all(string=True):
        if node.find_parent("math"):
            continue
        node.replace_with(re.sub(r"\s+", " ", str(node)))
    return str(soup).strip()


def parse_multi(corr):
    s = str(corr or "").strip()
    if "," not in s:
        return None
    out = []
    for p in s.split(","):
        try:
            a = int(p.strip()) - 1
        except ValueError:
            return None
        if a not in (0, 1, 2, 3):
            return None
        out.append(a)
    out = sorted(set(out))
    return out if len(out) >= 2 else None


def main():
    live_fps = set()
    starts = {}
    for eb in ("jee", "neet", "board"):
        data = json.load(open(os.path.join(ROOT, "exam-data", f"{eb}.json")))
        starts[eb] = len(data) + 1
        for item in data:
            live_fps.add(fingerprint(item.get("q")))

    buckets = {"jee": [], "neet": [], "board": []}
    seen = set()
    stats = Counter()

    for path in PATHS:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        for row in wb["Query result"].iter_rows(min_row=2, values_only=True):
            q, o1, o2, o3, o4, o5, corr, sol, typ, diff, klass, subj, chap, cat, exam = row[:15]
            stats["rows"] += 1
            ans = parse_multi(corr)
            if not ans:
                continue
            stats["multi_rows"] += 1
            if has_img(q, o1, o2, o3, o4, sol):
                stats["img"] += 1
                continue
            q_c, o_c, sol_c = clean_html(q), [clean_html(x) for x in (o1, o2, o3, o4)], clean_html(sol)
            if len(plain(q_c)) < 8 or any(len(plain(o)) < 1 for o in o_c):
                stats["empty"] += 1
                continue
            fp = fingerprint(q_c)
            if fp in live_fps or fp in seen:
                stats["dup"] += 1
                continue
            eb = bucket_exam(exam, cat, subj, q_c)
            entry = {
                "q": q_c, "o": o_c, "a": ans, "kind": "multi",
                "subject": bucket_subject(subj, eb),
                "chapter": str(chap or "").strip() or "General",
                "y": None, "exp": sol_c, "fmt": "html",
            }
            if eb == "board":
                entry["cls"] = str(klass or "").strip()
            buckets[eb].append(entry)
            seen.add(fp)
            stats[f"new_{eb}"] += 1
        wb.close()

    prefix = {"neet": "NEET", "jee": "JEE", "board": "BOARD"}
    for eb, items in buckets.items():
        if not items:
            print(eb, "0 multi")
            continue
        live = json.load(open(os.path.join(ROOT, "exam-data", f"{eb}.json")))
        n = starts[eb]
        for entry in items:
            live.append({"i": f"{prefix[eb]}-{n:05d}", **entry})
            n += 1
        json.dump(live, open(os.path.join(ROOT, "exam-data", f"{eb}.json"), "w"), ensure_ascii=False, indent=1)
        print(f"{eb}: +{len(items)} multi -> {len(live)} ({items[0] and 'ok'})")
    print("stats", dict(stats))


if __name__ == "__main__":
    main()
