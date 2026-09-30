# Spec

Status: approved by Ty 30/09 ("approve for all four", in chat).

- `docs/weekly-refresh.md` step 2: `newest-source=<week or filename>` becomes `newest-source=<week slug>` (the newest file's `YYYY-MM-Wnn` with the leading zero dropped, as in step 4; `none` if no file is found), plus one sentence: the note is the week only, never a file name, person's name, Drive id or figure.
- No other file documents the note (grep of the repo for `newest-source` outside `work/`, 30/09). `.github/scripts/freshness.py` reads only the timestamp, so nothing that parses the file changes.
- Doc text only. Promise: `grep -rn "week or filename" --exclude-dir=work .` prints nothing, and the next weekly run writes a week-only note.
