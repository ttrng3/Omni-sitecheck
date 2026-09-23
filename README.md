# OMNI Sitecheck — Điều hành

Live dashboard: **https://ttrng3.github.io/Omni-sitecheck/**

## How this repo is the source of truth

This repo is the single place the sitecheck numbers live. Everything else —
the GitHub Pages site, any Drive copy — **reads** from here. Nothing writes to the dashboard by copying HTML around.

```
SharePoint (OMNI - CÁC TÀI LIỆU / OMNI - SITECHECK)
        │   weekly .xlsx dropped by BQLVH
        ▼
weekly refresh job  ──writes──▶  data/index.json + data/weeks/<week>.json
                                          │
                                ┌─────────┴─────────┐
                                ▼                   ▼
                         GitHub Pages        any other viewer
                         (index.html)
```

`index.html` is a **renderer with no data baked in**. It fetches `data/` at
load time — relative first, then falling back to the published
`https://ttrng3.github.io/Omni-sitecheck/data/`. That fallback is why the same
file works unchanged as a GitHub Pages site and from a local copy. Update the
data and every surface is current on next load.

## Layout

| Path | What it is |
| --- | --- |
| `index.html` | Renderer only (~36 KB). Charts, tables, filters. No data. |
| `data/index.json` | Manifest: `generated`, `currentWeek`, `history[]` (per-week totals), `detail{}` (week → slug). |
| `data/weeks/<YYYY-MM-Wn>.json` | One week's row-level tasks: `{site, area, issue, dept, action, status}`. |
| `.github/workflows/freshness-check.yml` | Opens an issue if the data stops being refreshed. |

## Why data is split per week

The dashboard used to be one self-contained 300 KB HTML file. Updating it meant
*reproducing all 300 KB* through whichever surface was doing the update, and
any surface that could not emit 300 KB byte-exactly (see the reverted "mirror
sync part 000/011" commits) simply could not update it. That is what pinned the
whole pipeline to one machine with the file on disk, and why the site sat two
weeks behind.

Now a weekly update writes **two small files**: one new
`data/weeks/<week>.json` (~10–20 KB) and the rewritten `data/index.json`
(~17 KB). Both are small enough to write reliably over the GitHub Contents API
from anywhere.

## Adding a week

1. Read the new `YYYY-MM-Wnn_Sitecheck.xlsx` from SharePoint.
   - `TH` sheet → that week's raised counts per site and `SL chưa hoàn thành đến nay` → open counts.
   - The Long An sheet (Eco Retreat) and Vinh sheet (Eco Central Park) → one object per detail row.
2. Write `data/weeks/<slug>.json` — a JSON array of
   `{site: "Long An"|"Vinh", area, issue, dept, action, status}`.
3. In `data/index.json`: append the week to `history`, add it to `detail`,
   set `currentWeek`, and set `generated` to now (UTC, `%Y-%m-%dT%H:%M:%SZ`).

`history` entries carry `laR`/`vnR` (raised) and `laO`/`vnO` (open) plus `src`,
`srcUrl`, `verified`, and an optional `note` — notes surface on the page, so
use them to record source discrepancies rather than silently smoothing them.

## Data caveats

- Open counts are the point-in-time `SL chưa hoàn thành đến nay` column of each
  weekly file, not a cumulative backlog.
- Detail row counts occasionally differ from the `TH` summary by a few rows
  (duplicated or renumbered rows in the source workbook). The real rows are
  used and the discrepancy is recorded in that week's `note`.

## Visual standard

Since 2026-09-23 the renderer follows the **Ty Artifact Standard** — the house
Apple-HIG treatment that governs every page Ty builds, not just this one. The
skill `ty-artifact-standard` holds the full rules, and is the only place they
live. It replaced the warm-paper / Playfair treatment.

- Page ground `#F2F2F7`, cards `#FFFFFF` at 12 px radius, hairlines
  `1px solid #E5E5EA`, no drop shadows.
- System font stack only. **Do not add a webfont link back.**
- Ink in three tiers: `#1C1C1E` primary, `#3C3C43` body, `#8E8E93` muted.
- Semantic accents: blue `#007AFF` active/info, green `#34C759` done, amber
  `#FF9500` outstanding, red `#FF3B30` critical. Pill text uses a darkened ink
  of the same hue on a tint, because the raw hexes fail contrast at 12 px.
- **A status pill carries a dot and a word.** Identity pills (site, department)
  carry no dot, so a dot always means "this is a state".
- Chart.js: `c_LA_done` green, `c_LA_open` amber, `c_VN_done` blue,
  `c_VN_open` red, with `borderWidth: 2` and a white `borderColor` between
  stacked segments. That border is the second cue green and amber need under
  protanopia — **do not set it back to 0.**
- The `@media print` block and the `beforeprint` hook that expands every
  `<details>` are load-bearing; this page gets photocopied.

A refresh writes `data/`, never the stylesheet. If a refresh finds itself
editing CSS, something has gone wrong — stop and ask.

## Artifact mirror

The chain is **repo-first**, the same shape KSNB has always used:

    schedule → cloud routine → source → GitHub → Pages → artifact mirrored after

**The repo is the source of truth and Pages is the live surface.** The artifact
at https://claude.ai/artifact/Y8shYuiKTK9gXM82QE5Lvu is a **mirror**, published *after* the repo
is correct, and it is never authoritative. If the two ever disagree, the repo
wins and the artifact is what gets corrected.

How a refresh mirrors it, in this order:

1. Write and verify the repo first. Do not touch the artifact until `main` has
   moved and you have read the commit back.
2. Publish the changed data paths — data/index.json and the new data/weeks/<slug>.json — with the artifact's `url` set.
   Files you omit are kept, so a refresh is a small write.
3. Republish the page only when the **renderer** changed, and then publish the
   `tools/build-fragment.py` output, never `index.html` itself. The artifact
   service wraps what you give it, so a complete document nests inside another,
   the inner `<head>` is discarded, and the page renders **blank with no
   console error**. To tell that apart from the other blank cause, read the
   artifact's `index.html` back and count `<html>` tags: two means it nested,
   one means the markup is fine and it is the same-call publish problem.
4. **A failed mirror must never make you undo or retry the repo write.** Report
   it and stop; the site is already correct.

`tools/reconcile.py` diffs this repo's `data/` against the artifact's copy and
says which side is newer.

**Why the ordering is stated this bluntly.** On 2026-09-23 the TMDV artifact was
found *ahead* of its repo, carrying four fixes that had never been committed,
and the ECOPM artifact was found a whole renderer generation *behind*. Neither
was caught by the freshness guards, because both read data timestamps and the
drift was in the page. Repo-first is what keeps that from recurring.
