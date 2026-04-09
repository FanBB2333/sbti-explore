"""Fetch the inline <script> block from sbti.unun.dev and save it locally."""

from __future__ import annotations

import re
import urllib.request

URL = "https://sbti.unun.dev/"
OUTPUT = "sbti_inline.js"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


def fetch_inline_js() -> str:
    req = urllib.request.Request(URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8")

    # Match the first large inline <script>...</script> (skip tiny or external ones)
    blocks = re.findall(r"<script>(.*?)</script>", html, re.DOTALL)
    if not blocks:
        raise RuntimeError("No inline <script> block found")

    # Pick the largest block (the business logic one)
    return max(blocks, key=len)


def main() -> None:
    js = fetch_inline_js()
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(js)
    print(f"Saved {len(js)} chars -> {OUTPUT}")


if __name__ == "__main__":
    main()
