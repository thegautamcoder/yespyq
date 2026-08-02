#!/usr/bin/env python3
"""One-off: strip the tick-mark <img class="brand-mark"> icon from every
visible logo (header + footer brand blocks) site-wide, per explicit
request to keep the tick only as the actual favicon (<link rel="icon">,
apple-touch-icon, manifest icons, schema.org logo — all untouched here).
Leaves the surrounding <a class="brand">...<span class="brand-name">...
wordmark exactly as it was, just without the icon <img>.

Run from repo root: python3 _remove_tick_logo.py
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

IMG_RE = re.compile(
    r'\s*<img\s+src="/assets/favicon\.svg"\s+alt=""\s+class="brand-mark"\s*/>\s*'
)


def fix(path):
    with open(path, encoding="utf-8") as f:
        html = f.read()
    new, n = IMG_RE.subn(" ", html)
    if n:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
    return n


def main():
    files = glob.glob(os.path.join(ROOT, "**", "index.html"), recursive=True)
    total_files = 0
    total_removed = 0
    for f in files:
        n = fix(f)
        if n:
            total_files += 1
            total_removed += n
    print(f"Removed {total_removed} brand-mark <img> tags across {total_files} files.")


if __name__ == "__main__":
    main()
