#!/usr/bin/env python3
"""Compare two copies of a dashboard's data and say which one is authoritative.

GitHub Pages and the claude.ai artifact each hold their own copy of `data/`,
because an artifact cannot fetch across origins. Two copies can drift. This
says whether they have, and which way to sync.

Handles both dashboard schemas: OMNI keys its weeks `history[].week` with an
ISO `generated`; ECOPM keys them `wk[].id` with a display `generated` plus an
ISO `generatedUtc`. The comparison is the same either way.

Usage:
    python3 tools/reconcile.py <dir-a> <dir-b>

Each directory is a `data/` tree. Exits 0 when they agree, 1 when they differ.
"""
import json
import pathlib
import sys


def load(root):
    root = pathlib.Path(root)
    idx = json.loads((root / "index.json").read_text(encoding="utf-8"))
    weeks = {p.stem: p.read_text(encoding="utf-8")
             for p in (root / "weeks").glob("*.json")}
    return idx, weeks


def stamp(idx):
    """The machine-comparable generation time, whichever schema this is."""
    return idx.get("generatedUtc") or idx.get("generated", "")


def week_map(idx):
    """week-key -> the whole entry, for either schema."""
    if "history" in idx:
        return {w["week"]: w for w in idx["history"]}
    return {w["id"]: w for w in idx.get("wk", [])}


def main(a_dir, b_dir):
    (a_idx, a_weeks), (b_idx, b_weeks) = load(a_dir), load(b_dir)
    diffs = []

    a_gen, b_gen = stamp(a_idx), stamp(b_idx)
    if a_gen != b_gen:
        newer = a_dir if a_gen > b_gen else b_dir
        diffs.append(f"generated differs: {a_dir}={a_gen}  {b_dir}={b_gen}"
                     f"  -> newer: {newer}")

    a_hist, b_hist = week_map(a_idx), week_map(b_idx)
    for wk in sorted(set(a_hist) ^ set(b_hist)):
        diffs.append(f"week only in {a_dir if wk in a_hist else b_dir}: {wk}")
    for wk in sorted(set(a_hist) & set(b_hist)):
        if a_hist[wk] != b_hist[wk]:
            fields = [k for k in set(a_hist[wk]) | set(b_hist[wk])
                      if a_hist[wk].get(k) != b_hist[wk].get(k)]
            diffs.append(f"week {wk} differs on: {', '.join(sorted(fields))}")

    for slug in sorted(set(a_weeks) ^ set(b_weeks)):
        diffs.append(f"detail file only in "
                     f"{a_dir if slug in a_weeks else b_dir}: {slug}.json")
    for slug in sorted(set(a_weeks) & set(b_weeks)):
        if a_weeks[slug] != b_weeks[slug]:
            na = len(json.loads(a_weeks[slug]))
            nb = len(json.loads(b_weeks[slug]))
            diffs.append(f"detail file {slug}.json differs ({na} vs {nb} rows)")

    if not diffs:
        print(f"IN SYNC — {len(a_hist)} weeks, {len(a_weeks)} detail files, "
              f"generated {a_gen}")
        return 0
    print(f"DRIFT — {len(diffs)} difference(s):")
    for d in diffs:
        print("  -", d)
    print("\nThe copy with the newer generation stamp is authoritative. Copy "
          "its files over the other, then republish that side.")
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2]))
