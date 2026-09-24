#!/usr/bin/env python3
"""Publish one verified, public-facing project update to the live hub."""

import argparse
import datetime as dt
import fcntl
import html
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "status.json"
PUBLIC_DATA = "https://codenolimits.github.io/dreamnova-suivi/status.json"
PUBLIC_ROOT = PUBLIC_DATA.rsplit('/', 1)[0] + '/'


def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)


def check_public_page(url):
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("A public HTTPS URL is required")
    req = urllib.request.Request(url, headers={"User-Agent": "DreamNova-Link-Check/1.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        body = response.read(4096).lower()
        if response.status != 200:
            raise ValueError(f"Link returned HTTP {response.status}: {url}")
        if b"authentication required" in body or b"_vercel_sso" in body:
            raise ValueError(f"Link shows an authentication wall: {url}")


def html_revision_matches(url, expected):
    with urllib.request.urlopen(url + '?v=' + str(time.time_ns()), timeout=10) as response:
        body = response.read().decode('utf-8')
    match = re.search(r'<meta name="portal-revision" content="([^"]+)"', body)
    return bool(match and html.unescape(match.group(1)) == expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True)
    parser.add_argument("--status", required=True, choices=("available", "review", "live", "working"))
    parser.add_argument("--url", default="")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--proof", required=True)
    parser.add_argument("--handover", default="")
    args = parser.parse_args()
    if args.status in ("live", "available") and not args.url:
        parser.error("--status available requires --url")
    if args.url:
        check_public_page(args.url)
    if args.handover:
        check_public_page(args.handover)

    with (ROOT / ".publish.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        run("git", "pull", "--rebase", "origin", "main")
        data = json.loads(DATA.read_text())
        project = next((p for p in data["projects"] if p["id"] == args.id), None)
        if project is None:
            parser.error("Unknown project id; use an id from status.json")
        status = {"live": "available", "working": "review"}.get(args.status, args.status)
        project.update(status=status, summary=args.summary, proof=args.proof)
        if args.url:
            project["url"] = args.url
        project["checkedAt"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")
        if args.handover:
            project["handover"] = args.handover
        data["updatedAt"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")
        DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        run(sys.executable, "build_portal.py")
        run("git", "add", "status.json", "index.html", "projets", "journal", "404.html")
        run("git", "-c", "user.name=DreamNova", "-c", "user.email=codenolimits@gmail.com", "commit", "-m", f"docs: update {args.id} project status")
        run("git", "push", "origin", "main")
        expected = data["updatedAt"]
        for _ in range(12):
            try:
                with urllib.request.urlopen(PUBLIC_DATA + "?v=" + str(time.time()), timeout=10) as response:
                    published = json.load(response)
                pages = (PUBLIC_ROOT, PUBLIC_ROOT + f'projets/{args.id}/', PUBLIC_ROOT + 'journal/')
                if published.get("updatedAt") == expected and all(html_revision_matches(page, expected) for page in pages):
                    print(f"PUBLISHED {args.id} {args.status} {args.url or '(no link yet)'}")
                    return
            except Exception:
                pass
            time.sleep(5)
        print("PUSHED: GitHub Pages is still building; check the public page before claiming it is visible.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
