# OMNI Sitecheck — Điều hành

Live dashboard: **https://ttrng3.github.io/Omni-sitecheck/**

## How this repo is the source of truth

This repo is the single place the sitecheck numbers live. Everything else —
the GitHub Pages site, the claude.ai artifact, any Drive copy — **reads** from
here. Nothing writes to the dashboard by copying HTML around.

```
SharePoint (OMNI - CÁC TÀI LIỆU / OMNI - SITECHECK)
        │   weekly .xlsx dropped by BQLVH
        ▼
weekly refresh job  ──writes──▶  data/index.json + data/weeks/<week>.json
                                          │
                        ┌─────────────────┼─────────────────┐
                        ▼                 ▼                 ▼
                 GitHub Pages     claude.ai artifact    any other viewer
                 (index.html)     (same index.html)
```

`index.html` is a **renderer with no data baked in**. It fetches `data/` at
load time — relative first, then falling back to the published
`https://ttrng3.github.io/Omni-sitecheck/data/`. That fallback is why the same
file works unchanged as a GitHub Pages site, as a claude.ai artifact, and from
a local copy. Update the data and every surface is current on next load; no
artifact needs republishing.

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
