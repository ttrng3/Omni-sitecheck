# Spec (approved)

Status: approved by Ty 30/09 via claude-config `work/260930-claude-md-per-repo/spec.md`.

- Add `CLAUDE.md` (30 lines): header with entity and Pages address, a routine line deferring to `docs/weekly-refresh.md`, commands, layout, rules, known mistakes.
- Every command in it was run once on 30/09 against main and passed (the currentWeek-in-detail check, build-fragment, reconcile on two copies of data/, freshness.py).
- No routine step is added or changed. Known mistakes state what happened, never an order; each is dated, names its repo source where one exists, and carries no figure that exists only in session notes.
- Promise: the next scheduled run (Mon 5/10 15:45 UTC, cron `45 15 * * 1` in the routine config) takes the same steps and writes the same files as the 30/09 test run.
