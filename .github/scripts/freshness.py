"""Report how old data/index.json is, for the freshness-check workflow."""
import datetime as dt
import json
import os
import pathlib

MAX_AGE = int(os.environ.get("MAX_AGE_DAYS", "10"))
data = json.loads(pathlib.Path("data/index.json").read_text(encoding="utf-8"))
generated = data["generated"]
age = (dt.datetime.now(dt.timezone.utc)
       - dt.datetime.strptime(generated, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)).days

print(f"generated={generated}")
print(f"week={data['currentWeek']}")
print(f"days={age}")
print(f"stale={'true' if age > MAX_AGE else 'false'}")
