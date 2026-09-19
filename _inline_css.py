#!/usr/bin/env python3
"""Stamps the stylesheets into the pages, so nothing blocks the first paint.

A page carries an empty <style data-src="styles.css"></style> in its head and this fills
it with that file. The guide pages are filled by docs/_build.py as they are written, the
hand written pages by this script. Run it from the repository root after editing a
stylesheet:

    python3 _inline_css.py
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
STYLE = re.compile(r'(<style data-src="([^"]+)">).*?(</style>)', re.S)
_sheets: dict[str, str] = {}


def sheet(path: str) -> str:
    if path not in _sheets:
        with open(os.path.join(ROOT, path)) as source:
            _sheets[path] = source.read().strip()
    return _sheets[path]


def fill(page: str) -> str:
    """The page with every data-src style element carrying its stylesheet."""
    return STYLE.sub(lambda m: f"{m.group(1)}\n{sheet(m.group(2))}\n{m.group(3)}", page)


def main() -> int:
    filled = 0
    for folder, _, files in os.walk(ROOT):
        if ".git" in folder.split(os.sep):
            continue
        for name in sorted(files):
            if not name.endswith(".html") or name.startswith("_"):
                continue
            path = os.path.join(folder, name)
            with open(path) as page:
                before = page.read()
            after = fill(before)
            if after != before:
                with open(path, "w") as page:
                    page.write(after)
                filled += 1
    print(f"inlined {', '.join(sorted(_sheets)) or 'nothing'} into {filled} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
