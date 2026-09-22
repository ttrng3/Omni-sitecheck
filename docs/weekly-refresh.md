# Weekly refresh runbook

This replaces the old `omni-sitecheck-weekly-refresh` skill, which was written
for a Mac-bound pipeline that no longer exists. Read this file, not that one.

## What changed, and why the old runbook is wrong

The old skill was built around three assumptions that are all now false:

1. **"The SharePoint connector's flattened text is NOT reliable for detail."**
   It is now. `read_resource` on a `.xlsx` returns every sheet as tab-separated
   cell values, including the row-level detail sheets. `openpyxl` is not needed,
   so nothing has to be downloaded to a machine.
2. **"Clone the repo and apply surgical edits to `index.html` with Python."**
   `index.html` no longer contains data. Never edit it for a refresh.
3. **"Read the token from `/Users/tytr3/.../.github-token` with the Read tool."**
   That is a macOS path, readable only from the Mac. It is the reason the whole
   pipeline died when the Mac was asleep — and that token is now revoked (401).

## Runs where?

Anywhere with (a) the Microsoft 365 connector and (b) a GitHub token. Both are
account-level, not machine-level, so this runs in a cloud routine with the lid
shut. No step requires the Mac.

## Steps

### 1. Find the newest source file

`sharepoint_search` with `query: "Sitecheck"`, `fileType: "xlsx"`, and an
`afterDateTime` a few weeks back.

**Two folder trees hold files with identical names.** Use only the one whose
`webUrl` contains `OMNI - CÁC TÀI LIỆU/OMNI - SITECHECK/`. The
`ECOPM/ECOPM - SITECHECK/` tree is a different project and its numbers are
different — taking them would silently corrupt the series.

### 2. Stop if nothing is new

Read `data/index.json` from the repo. If its last `history` week is already the
newest source week, report "no new data" and stop. Do not write anything.

### 3. Read the workbook

`read_resource` on the file's `uri`. Three sheets:

- **`TH`** — the summary. Columns run `STT | BỘ PHẬN | Tổng số đầu việc tuần …`
  (one per week) `| SL chưa hoàn thành đến nay`. Rows `BQLVH LONG AN` and
  `BQLVH VINH`. The new week's raised counts are the **rightmost weekly
  column**; open counts are the `SL chưa hoàn thành` column.
- **Long An sheet** — named `Eco Retreat`, or `Tuần N tháng M`. Its row count
  should be close to Long An's raised count.
- **Vinh sheet** — named `Eco Central Park` / `ECO CENTRAL PARK`.

Sheet names are not stable between weeks. Match by content and by which row
count lines up with which site, not by name alone.

### 4. Write two files to GitHub

Both via the Contents API (`PUT /repos/ttrng3/Omni-sitecheck/contents/<path>`,
base64 content, with the current file's `sha`).

- `data/weeks/<YYYY-MM-Wn>.json` — a JSON array, one object per detail row:
  `{"site": "Long An"|"Vinh", "area", "issue", "dept", "action", "status"}`.
  Reproduce `area`, `issue`, `action`, `status` verbatim. Do not translate,
  tidy, or deduplicate — duplicates in the source are a finding, not noise.
- `data/index.json` — append the week to `history`, add it to `detail`, set
  `currentWeek`, set `generated` to now as `%Y-%m-%dT%H:%M:%SZ` UTC.

History entry shape:

```json
{"week":"Sep W3 ’26","src":"2026-09-W03_Sitecheck.xlsx","srcUrl":"https://…",
 "laR":54,"vnR":44,"laO":32,"vnO":1,"verified":true,"note":"…"}
```

`week` uses a curly apostrophe (`’26`), and the slug for `Sep W3 ’26` is
`2026-09-W3`. Both matter — the manifest maps one to the other.

### 5. Mirror the same two files to the artifact

The claude.ai artifact carries **its own copy** of `data/`, because an artifact
is not allowed to fetch across origins (verified: fetching github.io from an
artifact fails, and jsdelivr's `/gh/` path is blocked too). Publish the same two
files to `https://claude.ai/artifact/J5bcB2tayCH3B5ByZsz4xh` with `url` set and
`files` carrying only the changed paths — files left out are kept, so this stays
a small write.

**Do not republish the artifact's `index.html` unless the renderer changed.**
If you do, publish the **fragment** build, not the repo's `index.html`: the
artifact service wraps what you give it in its own `<html><head><body>`, so
publishing a complete document nests one document inside another, the inner
`<head>` is discarded, and the page renders blank. The fragment starts at
`<title>` with no doctype/html/head/body tags.

### 6. Report

Long An and Vinh raised/open, week-over-week delta, closure rate, one thing
that stands out, and the commit sha. If the detail row count disagrees with the
`TH` summary, say so and record it in that week's `note` — never quietly pick
one number.

## Credentials

The GitHub token must be reachable **from wherever this runs**. A path under
`/Users/tytr3/` is not, which is the failure this rebuild exists to fix.

Use a fine-grained PAT, Resource owner `ttrng3`, Only select repositories →
`ttrng3/Omni-sitecheck`, Contents: Read and write, and nothing else. Mint it at
https://github.com/settings/personal-access-tokens/new

Keep it in the private Drive `_secrets` folder this account already uses for
per-repo tokens, named for this repo, and read it through the Drive connector —
that connector is account-level, so it works from a cloud run. Never echo it,
never write it into this repo, never commit it (see `.gitignore`). On a 401 the
PAT has expired or been revoked: say so plainly and stop rather than retrying.

## Keeping the two copies in sync

The Pages site and the artifact each hold their own `data/`, because an artifact
cannot fetch across origins and must carry its own copy. **The repo is the
source of truth** — write there first, then mirror the same two files to the
artifact in the same run. Done that way they never diverge.

There is no outbound hook from an artifact: nothing tells GitHub when one is
republished. So if anyone edits the artifact's data directly, the web page will
not follow on its own. To check and repair:

1. Download the artifact's `data/` (Artifact read, `paths`).
2. `python3 tools/reconcile.py data <downloaded-dir>` — it names the
   authoritative copy by `generated`, lists exactly what differs, and exits
   non-zero on drift.
3. Copy the newer side over the older, and republish that side.

Prefer not to need this. Write to the repo, mirror to the artifact, never the
other way round.

## If it stops running

`.github/workflows/freshness-check.yml` opens an issue when `data/index.json`
goes more than 10 days without an update, and closes it when the data is fresh
again. That is the only thing standing between a missed run and another silent
two-week drift, so do not disable it.
