# Spec (awaiting Ty)

Status: awaits Ty's "approve" with the intent.

- `data/index.json`: drop the `srcUrl` key from all 41 `history` entries. Nothing else changes.
- `index.html`: the source cell shows the file name as escaped plain text (`esc(w.src)`); the two unused link styles become one cell style.
- `README.md` and `docs/weekly-refresh.md`: no `srcUrl` in the entry shape; the runbook says never to write a link to the source file, and why. The routine prompt itself does not mention `srcUrl` (checked 01/10).
- No person-free link exists: the files sit in one person's own storage. Git history keeps the old links; rewriting it is Ty's call.
- Promise: no `/personal/` path or storage-host link in any tracked file outside git history; after merge, none in the served page or `data/`; the weekly table renders every row with the file name and no link; no console error.
