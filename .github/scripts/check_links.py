"""Report the reachability of external links in the skill packages. Reachability is not proof of current content."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[2]
LINK = re.compile(r"\]\((https?://[^)\s]+)\)")


def collect(root):
    links = {}
    for language in ("en", "tr"):
        for path in sorted((root / language).rglob("*.md")):
            if "archived" in path.parts:
                continue
            for url in LINK.findall(path.read_text(encoding="utf-8")):
                links.setdefault(url.split("#", 1)[0], []).append(path.relative_to(root).as_posix())
    return links


def probe(url, timeout):
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": "public-skills-link-check"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.status
        except urllib.error.HTTPError as error:
            if method == "GET" or error.code not in (403, 405, 501):
                return error.code
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            if method == "GET":
                return str(getattr(error, "reason", error))
    return "unreachable"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--strict", action="store_true", help="Exit 1 when a link answers 404 or 410.")
    args = parser.parse_args()
    links = collect(ROOT)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = dict(zip(links, pool.map(lambda url: probe(url, args.timeout), links)))
    gone = [url for url, status in results.items() if status in (404, 410)]
    for url, status in sorted(results.items(), key=lambda item: str(item[1])):
        if status != 200:
            print(f"{status}\t{url}\t{', '.join(sorted(set(links[url])))}")
    print(f"Checked {len(results)} links; {sum(status == 200 for status in results.values())} answered 200; {len(gone)} gone.")
    return 1 if args.strict and gone else 0


if __name__ == "__main__":
    raise SystemExit(main())
