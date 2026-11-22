"""Fetch citation stats from a public Google Scholar profile and write them as JSON.

Exits non-zero (and writes nothing) if the page cannot be fetched or parsed,
so a blocked request never overwrites the last good numbers.
"""
import datetime
import json
import re
import sys
import urllib.request

USER = "Qw0Fh0EAAAAJ"
URL = f"https://scholar.google.com/citations?user={USER}&hl=en"
OUT = sys.argv[1] if len(sys.argv) > 1 else "scholar.json"

req = urllib.request.Request(URL, headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
cells = [int(x) for x in re.findall(r'<td class="gsc_rsb_std">(\d+)</td>', html)]
if len(cells) < 6:
    sys.exit(f"could not find the stats table (got {len(cells)} cells)")

data = {
    "citations": cells[0],
    "h_index": cells[2],
    "i10_index": cells[4],
    "updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
}
with open(OUT, "w") as f:
    json.dump(data, f)
    f.write("\n")
print(data)
