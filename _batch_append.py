#!/usr/bin/env python3
"""Append the next N rows from a staging file to the live exam-data file.
Usage: python3 _batch_append.py <exam> <count>
Tracks progress via exam-data/_staging/<exam>_progress.json (row offset).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    exam, count = sys.argv[1], int(sys.argv[2])
    staging_path = os.path.join(ROOT, "exam-data", "_staging", f"{exam}_new.json")
    live_path = os.path.join(ROOT, "exam-data", f"{exam}.json")
    progress_path = os.path.join(ROOT, "exam-data", "_staging", f"{exam}_progress.json")

    staged = json.load(open(staging_path))
    live = json.load(open(live_path))
    offset = json.load(open(progress_path))["offset"] if os.path.exists(progress_path) else 0

    batch = staged[offset:offset + count]
    if not batch:
        print(f"{exam}: nothing left to append (offset {offset}/{len(staged)})")
        return

    live.extend(batch)
    with open(live_path, "w") as f:
        json.dump(live, f, ensure_ascii=False, indent=1)

    new_offset = offset + len(batch)
    with open(progress_path, "w") as f:
        json.dump({"offset": new_offset}, f)

    print(f"{exam}: appended {len(batch)} rows ({batch[0]['i']}..{batch[-1]['i']}) — "
          f"progress {new_offset}/{len(staged)}, live total now {len(live)}")


if __name__ == "__main__":
    main()
