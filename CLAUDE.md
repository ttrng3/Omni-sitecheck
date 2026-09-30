# CLAUDE.md — Omni-sitecheck

OMNI's weekly site-check dashboard (Long An · Vinh), entity **OMNI**. Live: https://ttrng3.github.io/Omni-sitecheck/

**If you are the scheduled routine:** follow the files your prompt names, `docs/weekly-refresh.md` and `README.md` ("Adding a week"). They outrank this file. This file adds no step to a run.

## Commands
- Check `currentWeek` is in `detail` (a quick check, not full validation): `python3 -c "import json;d=json.load(open('data/index.json'));assert d['currentWeek'] in d['detail']"`
- Build the Cowork preview page, only when `index.html` changed: `python3 tools/build-fragment.py` (writes `build/artifact.html`; never publish `index.html` itself)
- Compare two `data/` trees: `python3 tools/reconcile.py <dir-a> <dir-b>` (exit 0 = same)
- Freshness check, as the daily Action runs it: `python3 .github/scripts/freshness.py`

## Layout
- `index.html` is a renderer holding no data. A refresh never touches it or its stylesheet.
- Data: `data/index.json` (manifest, `history`, `detail`, `currentWeek`, `generated`), `data/weeks/<YYYY-MM-Wn>.json` (row detail), `data/.last-check` (heartbeat, not published).
- `.pages-allow` lists what Pages publishes; `.github/workflows/pages.yml` deploys only that. A new kind of file under `data/` needs Ty's say-so and its own `.pages-allow` line in its own PR first.
- `README.md` explains the data model; `REVIEW.md` holds the reviewer's rules.

## Rules
- Changes reach `main` through a PR and Ty's ship. The routine's data writes are the only direct writes.
- The runbook and README win over this file and any memory note.
- Never write a Cowork preview URL or artifact id, a person's details or a secret into this public repo.
- Entity separation: this is OMNI. Never take figures from the other company's site-check tree, and never mix the two series.

## Known mistakes
- Two SharePoint trees hold identically named workbooks. Only `OMNI - CÁC TÀI LIỆU/OMNI - SITECHECK/` is this project; the other tree belongs to another company and silently corrupts the series (22/09).
- Source workbooks can repeat or recycle rows (Aug W3 Vinh: the tab was byte-identical to Aug W2, per that week's `note` in `data/index.json`). Record the gap in the week's `note`, which renders on the page; never quietly pick one number.
- The week label uses a curly apostrophe (`Sep W3 ’26`) and its slug is `2026-09-W3`; if the two disagree, the manifest breaks (22/09).
- `read_resource` on the SharePoint file returns every sheet with row detail. Do not download the workbook or reach for openpyxl, and no step needs the Mac (22/09).
- Publishing `index.html` as the preview nests one document inside another and renders blank. When the renderer changes, build the fragment, and send data files and the page in separate calls (23/09).
