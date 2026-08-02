#!/usr/bin/env python3
"""Build the public, paywall-safe question pool that powers the Smart PYQ
Mock generator and Real Exam Mode for JEE/NEET/Board/Defence/SSC-CGL.

Mirrors _gen_exams.py's free-preview selection EXACTLY (same grouping,
same free_preview_count formula) so this file only ever contains
questions that are already fully free on the static exam pages. Never
add anything here that isn't independently free — this file is public.

UPSC isn't included: it's already public in pyq.js, loaded separately
client-side and merged in by the mock-builder UI.

Run from repo root: python3 _gen_mock_pool.py
Output: mock-pool.json (repo root, deployed as a public static asset)
"""
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
EXAMS = ["jee", "neet", "board", "defence", "ssc-cgl"]


def free_preview_count(n):
    return max(1, round(n * 0.10))


def main():
    pool = []
    counts = {}
    for exam in EXAMS:
        items = json.load(open(os.path.join(ROOT, "exam-data", f"{exam}.json")))
        by_group = defaultdict(list)
        for x in items:
            key = (x.get("subject") or "general", x.get("chapter") or "General")
            by_group[key].append(x)

        exam_pool = []
        for (subject, chapter), group in by_group.items():
            n = free_preview_count(len(group))
            for x in group[:n]:
                exam_pool.append({
                    "i": x["i"],
                    "exam": exam,
                    "subject": subject,
                    "chapter": chapter,
                    "y": x.get("y"),
                    "q": x["q"],
                    "o": x["o"],
                    "a": x["a"],
                    "exp": x["exp"],
                    "fmt": x.get("fmt") or "",
                })
        pool.extend(exam_pool)
        counts[exam] = len(exam_pool)

    out_path = os.path.join(ROOT, "mock-pool.json")
    with open(out_path, "w") as f:
        json.dump(pool, f, ensure_ascii=False, separators=(",", ":"))

    print(f"Wrote {out_path}: {len(pool)} questions. Per exam: {counts}")


if __name__ == "__main__":
    main()
