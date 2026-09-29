# REVIEW.md

What the reviewer agent (`agents/reviewer.md` in claude-config) checks on every PR to this repo. The three passes run in order, each in full. The last section holds this repo's own rules.

This file is never served: it is not in `.pages-allow`.

## Severity
- **Critical:** it will break something live or publish something it must not. A secret or token, personal data by value in a public repo, a newly served path that shouldn't be, a broken deploy, data loss, a gate bypass.
- **High:** wrong behaviour that will show up. A bug on a path that runs, a broken reference, a diff that does something other than what the PR says, a house rule broken in a way Ty would have to undo.
- **Medium:** it's wrong but contained. An edge case that isn't hit yet, a doc that disagrees with the code, a missing test for a changed behaviour.
- **Low:** clarity, naming, a stale comment.

When unsure between two levels, pick the higher one and say why.

## Pass 1: Bugs
- [ ] Logic: off-by-one, inverted condition, wrong variable, an unreachable branch, loop bounds.
- [ ] Edge cases: empty input, a missing file, a first run, a name with spaces or accents, a timezone (Hanoi is UTC+7; cron is UTC).
- [ ] References resolve: every path, heading anchor, script flag, workflow job name and file named in the diff exists in `files/` or in the base.
- [ ] Shell: quoting, `set -e` interactions, `$?` after a pipe, BSD vs GNU flags (the Mac runs BSD tools).
- [ ] Syntax: YAML, JSON, Python (3.9 on the Mac: no `match`, no `X | Y` types), HTML.
- [ ] The diff does what the PR description says, and nothing it doesn't say.

## Pass 2: Security
- [ ] Secrets by pattern: `ghp_`, `github_pat_`, `sk-`, `sk-ant-`, `AKIA`, `xox[bp]-`, private-key headers, `eyJ…` JWTs (a Supabase **service_role** JWT is always Critical), passwords in URLs, `?token=`/`?key=` in a link.
- [ ] Personal data **by value** in a public repo: a name with money, a phone number, an email address, an account number, an ID number. Referring to where the value lives is fine; the value itself isn't.
- [ ] Anything newly published: a path added to `.pages-allow`, or any new file in a repo still on legacy Pages.
- [ ] Workflow permissions widened (`permissions:`, `pull_request_target`, `secrets: inherit`), or a new third-party action not pinned to a sha.
- [ ] Test fixtures build fake secrets at run time; a token-shaped string typed into a file is a finding even if it's fake.

## Pass 3: House rules
- [ ] **Never by value:** a sensitive value is referenced, not quoted, in any file of a public repo, including `work/` docs.
- [ ] **Artifact mirror contract:** no Cowork preview URL and no artifact id in anything public or anything Ty is shown. (A registry row that records an id on the private Drive mount is the exception.)
- [ ] **Entity separation:** OMNI and ECOPM data, names and numbers never cross into each other's repo or page.
- [ ] **One change per `work/` folder:** the PR names its `work/<yymmdd>-<slug>/`; `intent.md` says accepted; `spec.md` says approved; the diff matches the spec's promise, with nothing extra.
- [ ] **`gate/` untouched** while it is frozen (until 2026-10-05).
- [ ] **One PR per merge command:** nothing in the diff merges or batches PRs (`gh pr merge` in a loop, the merge API).
- [ ] **Verify before you assert:** every number in a doc or page has a source named beside it or in its section.

## Repo-specific rules
Rules specific to Omni-sitecheck. **Every standing ruling in the README (visual standard, one address one preview, the data layout) applies as well; a PR that breaks one is High.** The lines below are the ones most often at risk.

- **The README is what the routine follows.** The routine prompt says this repo's files win over anything else. A change to what the routine does ("Adding a week", sources, files written, checks) must change the README in the same PR; a README that disagrees with the diff is High.
- **The renderer holds no data.** `index.html` fetches `data/` at load. A number, a row or a week typed into `index.html` is High: the old 300 KB self-contained page is why the site once sat two weeks behind.
- **A refresh writes `data/` only.** A change to either `<style>` block in `index.html` (the base sheet or `apple-layer`) needs its own PR and Ty's say-so; mixed into a data change it is High.
- **`data/index.json` shape.** A new week is appended to `history[]` (never an old entry rewritten), added to `detail{}` with a file that exists, and `generated` is UTC in `%Y-%m-%dT%H:%M:%SZ`. Breaking any of the three is High.
- **Discrepancies are recorded, not smoothed.** When detail rows disagree with the `TH` summary, the real rows are used and the difference goes in that week's `note`. A diff that adjusts counts to match without a note is High.
- **Light only, ruled 2026-09-24 by Ty.** No dark theme, no webfont link, no raw hex on screen outside the token blocks. A status pill has a dot and a word; identity pills (site, department) have no dot. Stacked chart segments keep `borderWidth: 2` with the `--chart-sep` border; setting it to 0 is High.
- **Print is load-bearing.** The `@media print` block and the `beforeprint` hook that expands every `<details>` must survive every renderer change; the page gets photocopied.
- **One address, one preview.** `https://ttrng3.github.io/Omni-sitecheck/` is the only link. A Cowork preview URL or artifact id anywhere in the repo is Critical (the repo is public).
- **Don't widen what is published.** A new path in `.pages-allow`, or a new kind of data in `data/`, is High and needs Ty.
- **Entity separation.** This is an OMNI repo. Any ECOPM data (a person's or a client's name, a number, or a file from the ECOPM side) is **Critical**. The entity label itself isn't.
