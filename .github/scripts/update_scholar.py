"""Fetch citation stats from a public Google Scholar profile and write them as JSON.

Exits non-zero (and writes nothing) if the page cannot be fetched or parsed,
so a blocked request never overwrites the last good numbers.
"""
import datetime
import html as htmllib
import json
import re
import sys
import time
import urllib.request

USER = "Qw0Fh0EAAAAJ"
OUT = sys.argv[1] if len(sys.argv) > 1 else "scholar.json"
# Scholar often refuses requests from cloud servers, so try a few regional hosts.
HOSTS = ["scholar.google.com", "scholar.google.co.uk", "scholar.google.com.hk",
         "scholar.google.de", "scholar.google.com.sg", "scholar.google.ca"]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
html = ""
for host in HOSTS:
    url = f"https://{host}/citations?user={USER}&hl=en&pagesize=100"
    try:
        html = urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=30).read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        print(f"{host}: {e}")
        time.sleep(3)
        continue
    if 'gsc_rsb_std' in html:
        print(f"{host}: ok")
        break
    print(f"{host}: page without stats")
    time.sleep(3)
cells = [int(x) for x in re.findall(r'<td class="gsc_rsb_std">(\d+)</td>', html)]
if len(cells) < 6:
    sys.exit(f"could not find the stats table (got {len(cells)} cells)")

papers = []
for row in re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', html, re.S):
    title = re.search(r'class="gsc_a_at">(.*?)</a>', row, re.S)
    count = re.search(r'class="gsc_a_ac[^"]*">(\d*)</a>', row)
    if title:
        papers.append({
            "title": htmllib.unescape(re.sub(r"<[^>]+>", "", title.group(1))).strip(),
            "citations": int(count.group(1)) if count and count.group(1) else 0,
        })
if not papers:
    sys.exit("could not find the list of papers")

data = {
    "citations": cells[0],
    "h_index": cells[2],
    "i10_index": cells[4],
    "papers": papers,
    "updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
}
with open(OUT, "w") as f:
    json.dump(data, f)
    f.write("\n")
print({k: v for k, v in data.items() if k != "papers"}, len(papers), "papers")
