import os
import random
import time

import requests

LIST = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"
UA = "Mozilla/5.0 (help-ingest; +https://github.com)"


def _want(title):
    t = title.lower()
    n = 0
    if "youtube" in t:
        n += 80
    if "getting started" in t:
        n += 50
    if "pair" in t or "add your first screen" in t:
        n += 40
    if "playlist" in t:
        n += 25
    if "schedule" in t:
        n += 20
    if "split screen" in t:
        n += 15
    return n


def grab(limit=50):
    rows = []
    url = LIST
    params = {"per_page": 100}
    sess = requests.Session()
    sess.headers["User-Agent"] = UA
    while url:
        for attempt in range(4):
            r = sess.get(url, params=params, timeout=45)
            if r.status_code == 429:
                time.sleep(2 + attempt * 2)
                continue
            r.raise_for_status()
            break
        else:
            r.raise_for_status()
        params = None
        data = r.json()
        for a in data.get("articles") or []:
            if a.get("draft"):
                continue
            if (a.get("locale") or "en-us") != "en-us":
                continue
            body = a.get("body") or ""
            if len(body) < 80:
                continue
            rows.append(a)
        url = data.get("next_page")
        time.sleep(0.15 + random.random() * 0.1)

    rows.sort(key=lambda a: (_want(a.get("title") or ""), a.get("updated_at") or ""), reverse=True)
    cap = int(os.environ.get("LIMIT", limit))
    picked = rows[: max(cap, 30)]
    print("fetched %d published, keeping %d" % (len(rows), len(picked)))
    return picked
