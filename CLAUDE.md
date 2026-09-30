# CLAUDE.md — Omni-sitecheck

OMNI's weekly site-check dashboard (Long An · Vinh), entity **OMNI**. Live: https://ttrng3.github.io/Omni-sitecheck/

**If you are the scheduled routine:** follow the files your prompt names, `docs/weekly-refresh.md` and `README.md` ("Adding a week"). They outrank this file. This file adds no step to a run.

## Commands
- Check `currentWeek` is in `detail` (a quick check, not full validation): `python3 -c "import json;d=json.load(open('data/index.json'));assert d['currentWeek'] in d['detail']"`
- Build the Cowork preview page: `python3 tools/build-fragment.py` (writes `build/artifact.html`). When the routine refreshes the preview is set by its runbook, not here. Never send `index.html` itself to the preview; Pages does serve it.
- Compare two `data/` trees: `python3 tools/reconcile.py <dir-a> <dir-b>` (exit 0 = same)
- Freshness check, as the daily Action runs it: `python3 .github/scripts/freshness.py`

## Layout
- `index.html` is a renderer holding no data. A refresh never touches it or its stylesheet.
- Data: `data/index.json` (manifest, `history`, `detail`, `currentWeek`, `generated`), `data/weeks/<YYYY-MM-Wn>.json` (row detail), `data/.last-check` (heartbeat, not published).
- `.pages-allow` lists what Pages publishes; `.github/workflows/pages.yml` deploys only that. Every tracked file under a watched area needs a `.pages-allow` line (published, or `!` for known but not published); a new kind of file needs Ty's say-so and that line in its own PR first.
- `README.md` explains the data model; `REVIEW.md` holds the reviewer's rules.

## Rules
- Changes reach `main` through a PR and Ty's ship. The only direct writes are the ones a routine's prompt and runbook allow.
- The runbook and README win over this file and any memory note.
- Never write a Cowork preview URL or artifact id, a person's details or a secret into this public repo.
- Entity separation: this is OMNI. Never take figures from the other company's site-check tree, and never mix the two series.

## Known mistakes
- Two SharePoint trees hold identically named workbooks. Only `OMNI - CÁC TÀI LIỆU/OMNI - SITECHECK/` is this project; the other tree belongs to another company and silently corrupts the series (2026-09-22).
- Source workbooks can repeat or recycle rows (Aug W3 Vinh: the tab was byte-identical to Aug W2, per that week's `note` in `data/index.json`). The runbook's answer is the week's `note`, which renders on the page (2026-08).
- The week label uses a curly apostrophe (`Sep W3 ’26`) and its slug is `2026-09-W3`; if the two disagree, the manifest breaks (2026-09-22).
- An old runbook said the workbook had to be downloaded and parsed on the Mac; `read_resource` on the SharePoint file returns every sheet with row detail (2026-09-22).
- Publishing `index.html` as the preview nests one document inside another and renders blank; the runbook's fragment build exists for this (2026-09-23).
