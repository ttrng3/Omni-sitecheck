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

Since 2026-09-24 the renderer follows the **apple-design** skill (it replaced
the retired `ty-artifact-standard`). The page is **light and dark**, not
light-only: a base sheet carries the Apple-HIG light tokens, and a second
`<style id="apple-layer">` block after it adds dark mode, materials, press
feedback and the accessibility media queries. The layer only overrides.

- Light: ground `#F2F2F7`, cards `#FFFFFF` at 12 px radius, hairlines
  `#E5E5EA`. Dark: ground `#000`, cards `#1C1C1E`, hairlines `#38383A`,
  iOS dark accents (`#0A84FF` / `#30D158` / `#FF9F0A` / `#FF453A`).
- Dark mode is **screen-only**. Print always gets the light sheet, and the
  charts are repainted light on `beforeprint` (the page pins
  `data-theme="light"` for the duration of the print).
- **No raw hex on screen outside the token blocks.** Chart.js reads every
  colour from CSS tokens at runtime (`tok()` / `themeCharts()` in the page
  script) and repaints when the OS scheme flips. Add a colour as a token with
  both a light and a dark value, never inline.
- System font stack only. **Do not add a webfont link back.**
- Semantic accents: blue active/info, green done, amber outstanding, red
  critical. Pill text uses the `*-ink` token of the same hue on a tint.
- **A status pill carries a dot and a word.** Identity pills (site, department)
  carry no dot, so a dot always means "this is a state".
- Chart.js: `c_LA_done` green, `c_LA_open` amber, `c_VN_done` blue,
  `c_VN_open` red, with `borderWidth: 2` and a `--chart-sep` border (white in
  light, card colour in dark) between stacked segments. That border is the
  second cue green and amber need under protanopia — **do not set it back to 0.**
- Force a theme for testing with `<html data-theme="light|dark">`.
- The `@media print` block and the `beforeprint` hook that expands every
  `<details>` are load-bearing; this page gets photocopied.

A refresh writes `data/`, never the stylesheet. If a refresh finds itself
editing CSS, something has gone wrong — stop and ask.

## One surface, on purpose

    schedule → cloud routine → source → GitHub → Pages

**GitHub Pages is the only published surface.** Ty ruled on 2026-09-23 that he
wants control over what exists of his work, so there is no claude.ai artifact
copy of this dashboard: the Pages URL above is the address, full stop.

A mirror artifact existed for a few hours that day and was deleted. Do not
recreate one, and do not add an artifact URL to this repo. `tools/build-fragment.py`
is kept only because it is the one thing that can derive a standalone fragment
of this page if it is ever needed; nothing in the refresh calls it.
