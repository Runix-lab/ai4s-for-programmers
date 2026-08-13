#!/usr/bin/env python3
"""Push the sitemap's URLs to IndexNow (Bing, Yandex, Seznam, Naver).

No account and no ownership verification: the key file served from the site
root is the proof. Google does not participate in IndexNow and does not need
to — it finds the sitemap through the directive in robots.txt.

    python3 scripts/indexnow.py
"""
import json
import re
import sys
import urllib.error
import urllib.request

HOST = "ai4s.runixcloud.io"
KEY = "b86af4864246a2dcad2b67cb1cdca04c"
ENDPOINT = "https://api.indexnow.org/indexnow"
# Cloudflare rejects urllib's default agent, which is indistinguishable from a
# scraper; identify the script honestly instead of pretending to be a browser.
UA = {"User-Agent": f"ai4s-indexnow/1.0 (+https://{HOST})"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def main() -> int:
    urls = re.findall(r"<loc>([^<]+)</loc>", get(f"https://{HOST}/sitemap.xml"))
    if not urls:
        print("no URLs in sitemap", file=sys.stderr)
        return 1

    served = get(f"https://{HOST}/{KEY}.txt").strip()
    if served != KEY:
        print(f"key file mismatch: served {served!r}", file=sys.stderr)
        return 1

    body = json.dumps({
        "host": HOST, "key": KEY,
        "keyLocation": f"https://{HOST}/{KEY}.txt",
        "urlList": urls,
    }).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body,
        headers={**UA, "Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"submitted {len(urls)} URLs -> HTTP {r.status}")
            return 0 if r.status in (200, 202) else 1
    except urllib.error.HTTPError as e:
        # 422 usually means the key file could not be fetched from their side.
        print(f"HTTP {e.code}: {e.read().decode()[:200]}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
