# Verification: the weekly page

## Promise

Every file https://ttrng3.github.io/Omni-sitecheck/ serves (the page, `index.json`, every week file) is byte-identical to `main`. `main`'s data holds together: week labels and their slugs agree, `currentWeek` is the newest week, every claimed detail file exists, open counts never exceed raised counts, and a week whose detail rows differ from its summary says why in its note. The page renders every week and the rows of the weeks it is asked for, with no console error and no link to the source files. No private file, personal link or email address, and no word from another entity, is served. The Cowork preview carries either `main`'s data or the last weekly run's.

## Clean state

```bash
cd ~/Projects/Omni-sitecheck && git checkout main && git pull --ff-only
```
Run after a weekly run (the OMNI Sitecheck routine's cron, `45 15 * * 1` UTC = 22:45 Monday Hanoi, per pipeline-wiring's `collect_status.py` on 01/10) or after any merge. Wait for the merge's Pages run to go green first (`gh run list -w "Pages (allowlist)" -L1`).

## Steps

1. **Repo and live site.** `python3 tools/verify_live.py --forbid <other entity's name>` → exit 0 and `"pass": true`. The words come from the runner's own notes: the other entity's name, plus any person's account handle that has leaked before (one did, in three notes, until 01/10, #10). Names of people are never written into this repo. Without `--forbid` the entity verdict fails on purpose.
2. **Live page in Chrome.** Open https://ttrng3.github.io/Omni-sitecheck/. Run the script under Invariants. Expected: one row per `history` week once the table shows "All"; the current week's detail table holds as many rows as its week file; another detail week does the same when clicked; a week without detail (if any) renders no rows and the table counter reads "0 of 0 tasks"; no link to a storage host and no "View source" text.
3. **Console.** Reload, then read errors for `TypeError|ReferenceError|Uncaught|SyntaxError`. Expected: none.
4. **Preview.** Get the preview link from the OMNI Sitecheck routine's prompt (`RemoteTrigger get`). Never write it here. Find the last weekly run: `c=$(git log --format='%h %s' -- data/index.json | grep -v ' (#[0-9]*)$' | head -1 | cut -d' ' -f1)`, the last commit to `index.json` that is not a squash-merged PR (their titles end `(#N)`); routine runs commit directly. `Artifact list` the preview's files, then `Artifact read` `data/index.json` and the current week's file. Expected: the files are `index.html` (the page fragment the routine's mirror step publishes), `data/index.json`, and one `data/weeks/<slug>.json` per `detail` entry of either `main` or `$c`; nothing else. Each file read has the sha256 of either `main`'s copy (`shasum -a 256 <path>`) or `$c`'s (`git show $c:<path> | shasum -a 256`). Matching `$c` and not `main` means PRs changed data since the run: behind by design until the next run.

## Invariants

Step 1 prints these verdicts, all of which must be true: `has_weeks`, `served_equals_main`, `private_not_served`, `labels_well_formed`, `weeks_ordered_unique`, `current_week_is_newest`, `detail_slugs_match`, `detail_files_match`, `open_within_raised`, `row_counts_explained`, `heartbeat_fresh` (≤ 9 days, pipeline-wiring's watchdog for this pipeline), `data_fresh` (≤ 24 days, `freshness.py`'s `MAX_DATA_AGE_DAYS` default; its 10-day `RUN_MAX` is the run clock, which `heartbeat_fresh` covers more tightly), `no_personal_traces`, `no_forbidden_words`.

Step 2, in the page:
```js
window.confirm=()=>true; window.alert=()=>{};
await new Promise(r=>setTimeout(r,2500));
const d=await fetch('data/index.json?v='+Date.now()).then(r=>r.json());
const tb=document.getElementById('taskTbody'), stat=()=>document.getElementById('tableStat').innerText;
const fileLen=async w=>(await fetch(`data/weeks/${d.detail[w]}.json?v=`+Date.now()).then(r=>r.json())).length;
const cur=tb.querySelectorAll('tr').length, curLen=await fileLen(d.currentWeek);
document.querySelector('button[data-table-view="all"]').click(); await new Promise(r=>setTimeout(r,500));
const rows=[...document.querySelectorAll('#weeklyTbody tr.clickable')].map(r=>r.dataset.week);
const pick=async(w,wait)=>{tb.innerHTML='';document.querySelector(`#weeklyTbody tr[data-week="${w}"]`).click();for(let i=0;i<wait/200;i++){await new Promise(r=>setTimeout(r,200));if(tb.querySelectorAll('tr').length>0)break;}return tb.querySelectorAll('tr').length;};
const other=d.history.map(h=>h.week).filter(w=>w in d.detail && w!==d.currentWeek).pop();
const otherOk=other?(await pick(other,8000))===(await fileLen(other)):true;
const none=d.history.map(h=>h.week).filter(w=>!(w in d.detail)).pop();
const noneOk=none?((await pick(none,2000))===0&&/\b0 of 0 tasks/.test(stat())):true;
JSON.stringify({rows_match:rows.length===d.history.length&&new Set(rows).size===rows.length, current_rows_render:cur===curLen,
  other_rows_render:otherOk, no_detail_week_says_so:noneOk,
  no_source_links:!document.querySelector('a[href*="sharepoint"],a[href*="1drv"],a.src')&&!document.body.innerText.includes('View source')})
```
All of them must be true. `current_rows_render` reads the table as the page first loads it, before any click and with no filter set.

## Adversary

- **A stranger on the public page.** `private_not_served`: README, CLAUDE.md, REVIEW.md, the runbook, the heartbeat, the three `tools/` scripts, this protocol, one `work/` file found at run time, `.github/scripts/freshness.py` and `.pages-allow` all exist on `main` and answer 404 live. `no_personal_traces`: no OneDrive `/personal/` path, SharePoint or 1drv link, or email address in the page, `index.json` or any week file, live or on `main`. Until 01/10 every week carried a link into one person's storage (#10). Matches are reported by count and file, never by value. `no_source_links` checks the rendered page the same way.
- **The other entity's tree read by mistake** (identical file names, different numbers). `no_forbidden_words` keeps its name off the page. The numbers themselves cannot be told apart by a script: see Not covered.
- **A label and slug that disagree** (the curly apostrophe, 22/09). `labels_well_formed` and `detail_slugs_match`.
- **A run that appends a week but not its detail, or claims detail it never wrote.** `detail_files_match`, `current_week_is_newest`.
- **A source that repeats or recycles rows, or whose summary disagrees with its rows.** `row_counts_explained`: the week's `note` must speak about the rows (contain "dòng"), as Sep W3 ’26's does. Three older weeks (Jan W5, Apr W2, Jul W2 ’26) differ with no note; they are listed in `KNOWN_UNEXPLAINED` in the script because the source files are not reachable from here.
- **A routine that stopped running.** `heartbeat_fresh`. **A routine that runs but publishes nothing:** `data_fresh`.
- **A preview a generation behind.** Step 4.

## Sanctioned substitutes

- The forbidden word list is passed on the command line, so it can change without a PR; the docs may still name the other entity's label, which REVIEW.md allows. This proves the served files and the tracked data don't contain it. It does not prove the numbers came from the right tree.
- The preview cannot be fetched by a script (artifact links need the Artifact tool), so step 4 is done by the runner with `Artifact list` and `Artifact read`.

## Evidence

- The JSON from step 1 and the JSON from step 2.
- Screenshots (`save_to_disk: true`): the top of the page, the weekly table on "All", and the current week's detail table.
- For step 4: the preview's file count and the hashes read.

## Not covered

- The runbook's "If it stops running" section says the freshness issue opens after 10 days without a data update; `freshness.py` opens it after 10 days without a run or 24 days without data. The runbook wording is a follow-up, not changed here.

- Whether the numbers came from the OMNI tree and not the other entity's. Only the runbook's path rule guards this.
- Why the three `KNOWN_UNEXPLAINED` weeks differ. It needs the source workbooks.
- Personal data inside verbatim row text: a person's name, a phone or an ID number. The script catches only personal links and email addresses.
- Git history still holds the source links removed on 01/10 (#10).

## Traps

- Pages answers `cache-control: max-age=600` (10 minutes; response header seen with `curl -sI`, 01/10). A `served_equals_main` failure straight after a merge is the cache: wait for the Pages run, then re-run. Each request retries once on a network error or a 5xx.
- The weekly table opens on "Last 12w"; step 2 clicks "All" before counting.
- The week file loads after the click. `pick` empties the detail table, clicks, and waits until rows appear (max 8 s), so it never reads the previous week's rows. A week without detail never fills the table, so it waits only 2 s and then reads the table counter ("0 of 0 tasks"); the "No row-level data" chart messages are hidden elements and always in the page source.
- The browser tool stops a script after 45 s. The first draft waited 8 s on the empty week as well and hung once (01/10); keep the waits short.
- Clicking the current week again does nothing (the page ignores it), so `other` is never the current week.
- `no_forbidden_words` can fail inside verbatim row text (the runbook keeps rows as written). Do not edit the row. Report it to Ty: the source itself names the other entity, which may mean the wrong tree was read.
- Weekly-run commit titles vary, and the heartbeat is committed before the data, so step 4 takes the last `index.json` commit that is not a `(#N)` PR merge.
