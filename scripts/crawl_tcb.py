#!/usr/bin/env python3
"""Crawl Tokyo Comedy Bar pages and extract performer names from show pages."""
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from html import unescape
from pathlib import Path
from urllib.parse import urljoin

BASE = "https://www.tokyocomedybar.com"
PAGES = ["/comedians", "/shows", "/festival"]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "standupcomedian-db/0.1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore")


def links(html: str, base: str) -> set[str]:
    found = set()
    for href in re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.I):
        u = urljoin(base, unescape(href))
        if "tokyocomedybar.com" in u and ("/show/" in u or "/event/" in u):
            found.add(u.split("#")[0])
    return found


def text(html: str) -> str:
    html = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.I | re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", unescape(html))).strip()


def extract_candidates(page_text: str) -> list[str]:
    # TCB show pages frequently expose an explicit 出演者/MC block.
    m = re.search(r"(?:出演者|出演|Featuring|Featuring:|MC[:：])(.{0,1000})", page_text, re.I)
    if not m:
        return []
    chunk = m.group(1)
    chunk = re.split(r"(?:Buy Ticket|ADDRESS|INFO|HOURS)", chunk, maxsplit=1)[0]
    raw = re.split(r"[,、/|・\\n]", chunk)
    out = []
    for name in raw:
        name = name.strip(" .:：()[]{}\"")
        if 1 < len(name) <= 40 and not re.search(r"(?:ticket|comedy|show|image|http)", name, re.I):
            out.append(name)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="data/tcb-candidates.jsonl")
    args = ap.parse_args()

    discovered = set()
    for path in PAGES:
        try:
            html = fetch(BASE + path)
            discovered |= links(html, BASE + path)
        except Exception as exc:
            print(f"WARN {path}: {exc}")

    rows = []
    for url in sorted(discovered):
        try:
            names = extract_candidates(text(fetch(url)))
            for name in names:
                rows.append({"name": name, "type": "standup_comedian", "source_url": url, "source_type": "tokyo_comedy_bar_crawl", "seed": False})
        except Exception as exc:
            print(f"WARN {url}: {exc}")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} candidates from {len(discovered)} TCB pages")


if __name__ == "__main__":
    main()
