#!/usr/bin/env python3
"""Machine half of verification/weekly-page.md: is the live page what main says, and is main sound?

Run from an up-to-date checkout of main:
  git pull --ff-only && python3 tools/verify_live.py --forbid WORD [WORD ...]

--forbid takes words that must not appear in anything served (the other entity's name or label).
The runner supplies them so the list can change without a PR; the docs may name the entity's label,
which REVIEW.md allows. Without them the entity check fails rather than passing unchecked.

Prints one JSON object of verdicts and exits 0 only when every verdict is true.
Matches of personal traces are reported by count and file, never by value.
"""
import argparse, collections, datetime as dt, glob, hashlib, json, pathlib, re, sys, time, unicodedata, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIVE = "https://ttrng3.github.io/Omni-sitecheck/"
# Tracked but never served (.pages-allow); each must exist on main and answer 404 live.
PRIVATE = ["README.md", "CLAUDE.md", "REVIEW.md", "docs/weekly-refresh.md", "data/.last-check",
           "tools/build-fragment.py", "tools/reconcile.py", "tools/verify_live.py",
           "verification/weekly-page.md",
           ".github/scripts/freshness.py", ".pages-allow"]
TRACES = re.compile(r"/personal/|sharepoint\.com|1drv\.ms|[\w.+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}", re.I)
HEARTBEAT_MAX = 9  # the watchdog pipeline-wiring's collect_status.py sets for this pipeline
DATA_MAX = 24      # MAX_DATA_AGE_DAYS default in .github/scripts/freshness.py (its run clock, RUN_MAX, is 10)
MONTHS = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
# Weeks whose detail rows differ from the summary sheet with no note, found 01/10/2026 when this
# protocol was written. The source files are not reachable from here, so they are listed, not fixed.
# Any other week whose rows differ must explain it in its `note`.
KNOWN_UNEXPLAINED = {"Jan W5 ’26", "Apr W2 ’26", "Jul W2 ’26"}


def get(path, tries=2):
    """One retry on a network error or a 5xx: a blip must not read as a mismatch."""
    url = f"{LIVE}{path}?v={int(time.time())}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "verify-live"}), timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return get(path, tries - 1) if e.code >= 500 and tries > 1 else (e.code, b"")
    except Exception as e:
        return get(path, tries - 1) if tries > 1 else (str(e), b"")


def age_days(stamp):
    """Days since an ISO stamp ('...Z', '+00:00', 3/6-digit fractions); None if unreadable."""
    try:
        t = dt.datetime.fromisoformat(stamp.strip().replace("Z", "+00:00"))
        t = t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)
        return round((dt.datetime.now(dt.timezone.utc) - t).total_seconds() / 86400, 1)
    except (ValueError, AttributeError):
        return None


def norm(t):
    return unicodedata.normalize("NFC", str(t or "")).casefold()


def slug(label):
    """'Sep W4 ’26' -> '2026-09-W4' (README: the manifest maps one to the other); None if malformed."""
    try:
        mon, w, yy = label.split()
        return f"20{yy[-2:]}-{MONTHS[mon]:02d}-{w}" if re.fullmatch(r"W[1-5]", w) and re.fullmatch(r"’\d\d", yy) else None
    except (ValueError, KeyError, AttributeError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--forbid", nargs="*", default=[])
    forbid = [norm(w) for w in ap.parse_args().forbid if w.strip()]

    d = json.loads((ROOT / "data/index.json").read_text(encoding="utf-8"))
    hist, detail = d.get("history", []), d.get("detail", {})
    files = sorted(pathlib.Path(f).stem for f in glob.glob(str(ROOT / "data/weeks/*.json")))
    weeks = {x: json.loads((ROOT / f"data/weeks/{x}.json").read_text(encoding="utf-8")) for x in files}

    v, info, live = {}, {}, {}
    v["has_weeks"] = bool(hist) and bool(files)
    served = ["index.html", "data/index.json"] + [f"data/weeks/{x}.json" for x in files]
    for p in served:
        st, body = get(p)
        live[p] = body
        info[p] = {"status": st, "live": hashlib.sha256(body).hexdigest()[:12],
                   "main": hashlib.sha256((ROOT / p).read_bytes()).hexdigest()[:12]}
    v["served_equals_main"] = all(info[p]["status"] == 200 and info[p]["live"] == info[p]["main"] for p in served)
    info["served_mismatch"] = [p for p in served if info[p]["status"] != 200 or info[p]["live"] != info[p]["main"]]
    for p in served:
        del info[p]

    work = sorted(glob.glob(str(ROOT / "work/*/intent.md")))[:1]  # any one work file, found at run time
    private = PRIVATE + [str(pathlib.Path(w).relative_to(ROOT)) for w in work]
    info["private_status"] = {p: get(p)[0] for p in private}
    info["private_missing_on_main"] = [p for p in private if not (ROOT / p).exists()] + ([] if work else ["work/*/intent.md"])
    v["private_not_served"] = all(s == 404 for s in info["private_status"].values()) and not info["private_missing_on_main"]

    labels = [h.get("week") for h in hist]
    slugs = [slug(l) for l in labels]
    v["labels_well_formed"] = all(slugs)
    v["weeks_ordered_unique"] = all(slugs) and slugs == sorted(slugs) and len(set(labels)) == len(labels) == len(set(slugs))
    v["current_week_is_newest"] = bool(labels) and d.get("currentWeek") == labels[-1] and d.get("currentWeek") in detail
    v["detail_slugs_match"] = all(detail[l] == slug(l) for l in detail) and set(detail) <= set(labels)
    v["detail_files_match"] = sorted(detail.values()) == files
    nums = lambda h, *k: all(isinstance(h.get(x), int) for x in k)
    v["open_within_raised"] = all(nums(h, "laO", "laR", "vnO", "vnR") and 0 <= h["laO"] <= h["laR"] and 0 <= h["vnO"] <= h["vnR"] for h in hist)

    # Rows per site must equal the summary sheet, or the week's note must say why (README: notes record
    # source discrepancies). KNOWN_UNEXPLAINED covers the three older weeks found on 01/10.
    differ = []
    for h in hist:
        rows = weeks.get(detail.get(h.get("week"), ""), None)
        if rows is None:
            continue
        c = collections.Counter(r.get("site") for r in rows)
        if c.get("Long An", 0) != h.get("laR") or c.get("Vinh", 0) != h.get("vnR"):
            differ.append(h.get("week"))
    # Any note counts: the runbook asks for a note, not for particular words.
    unexplained = [w for w in differ if w not in KNOWN_UNEXPLAINED and
                   not norm(next(h for h in hist if h.get("week") == w).get("note")).strip()]
    v["row_counts_explained"] = not unexplained
    info["weeks"] = {"count": len(hist), "newest": labels[-1] if labels else None,
                     "without_detail": [l for l in labels if l not in detail], "rows": sum(len(r) for r in weeks.values()),
                     "rows_differ_from_summary": differ, "unexplained": unexplained}

    beat = ((ROOT / "data/.last-check").read_text(encoding="utf-8").split() or [""])[0]
    info["heartbeat_age_days"], info["data_age_days"] = age_days(beat), age_days(str(d.get("generated", "")))
    # -1 allows clock skew; a stamp further in the future (a wrong year) would otherwise pass forever.
    v["heartbeat_fresh"] = info["heartbeat_age_days"] is not None and -1 <= info["heartbeat_age_days"] <= HEARTBEAT_MAX
    v["data_fresh"] = info["data_age_days"] is not None and -1 <= info["data_age_days"] <= DATA_MAX

    # Every served path, both as Pages serves it and as main holds it (main may not be deployed yet).
    texts = {f"live:{p}": b.decode("utf-8", "replace") for p, b in live.items()}
    texts.update({f"main:{p}": (ROOT / p).read_text(encoding="utf-8") for p in served})
    hits = {p: len(TRACES.findall(t)) for p, t in texts.items()}
    info["traces"] = {p: n for p, n in hits.items() if n}
    v["no_personal_traces"] = not info["traces"]
    info["forbid_checked"] = len(forbid)
    v["no_forbidden_words"] = bool(forbid) and not any(w in norm(t) for w in forbid for t in texts.values())

    print(json.dumps({"pass": all(v.values()), "verdicts": v, "info": info}, ensure_ascii=False, indent=1))
    sys.exit(0 if all(v.values()) else 1)


if __name__ == "__main__":
    main()
