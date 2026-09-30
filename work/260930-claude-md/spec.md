# Spec (approved)

Status: approved by Ty 30/09 via claude-config `work/260930-claude-md-per-repo/spec.md`.

- Add `CLAUDE.md` (30 lines): header with entity and Pages address, a routine line deferring to `docs/weekly-refresh.md`, commands, layout, rules, known mistakes.
- Every command in it was run once on 30/09 against main and passed (validate, build-fragment, reconcile on two copies of data/, freshness.py).
- No routine step is added or changed; the known-mistake lines restate what `docs/weekly-refresh.md` and `README.md` already say, with dates.
- Promise: the next scheduled run (Mon 5/10 15:45 UTC) takes the same steps and writes the same files as the 30/09 test run.
