# Spec

Status: approved by Ty 01/10 (same words as the intent).

- `verification/weekly-page.md`: promise, clean state, 4 steps (script, live page in Chrome, console, preview), invariants, adversary, sanctioned substitutes, evidence, not covered, traps.
- `tools/verify_live.py` (stdlib only, not served): 14 verdicts as JSON, exit 0 only when all pass. Words that must not be served come in on `--forbid` and are never written into the repo; without them that verdict fails. Personal traces are reported by count and file. Three older weeks whose rows differ from the summary with no note are listed as known exceptions (`KNOWN_UNEXPLAINED`); any other such week must carry a note.
- No change to the page, the data, `.pages-allow` or the runbook.
- Promise: after #10 is live and this is merged, step 1 prints `"pass": true` and step 2 prints five trues. Before #10, `no_personal_traces` (step 1) and `no_source_links` (step 2) fail on the source links and nothing else does.
