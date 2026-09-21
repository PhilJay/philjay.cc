#!/usr/bin/env python3
"""Renders the guide sources in docs/src into static pages under mpandroidchart/docs.

Run from the repository root: python3 docs/_build.py
"""

import html
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs", "src")
OUT = os.path.join(ROOT, "mpandroidchart", "docs")
TEMPLATE = os.path.join(ROOT, "docs", "_template.html")

sys.path.insert(0, ROOT)
import _inline_css  # noqa: E402

KOTLIN_KEYWORDS = {
    "val", "var", "fun", "class", "object", "interface", "override", "private", "internal", "protected",
    "return", "if", "else", "when", "for", "while", "in", "is", "as", "true", "false", "null", "this",
    "super", "import", "package", "data", "sealed", "enum", "open", "abstract", "companion", "init",
    "by", "lazy", "constructor", "operator", "suspend", "typealias", "vararg", "out", "reified", "inline",
}
XML_LIKE = {"xml", "html"}
LANGUAGE_LABELS = {"kotlin": "Kotlin", "xml": "XML", "groovy": "Groovy", "bash": "Shell",
                   "proguard": "ProGuard", "text": "Text"}
KOTLIN_LIKE = {"kotlin", "kt", "java"}

SECTIONS = [
    ("Basics", ["getting-started"]),
    ("The axes", ["axis", "xaxis", "yaxis"]),
    ("Data", ["setting-data", "colors", "formatters", "highlighting"]),
    ("Styling", ["general-styling", "chart-styling", "legend", "description", "theming"]),
    ("Motion and viewport", ["interaction", "dynamic-data", "viewport", "animations", "markers"]),
    ("Classes in depth", ["chartdata", "chartdata-subclasses", "dataset", "dataset-subclasses",
                          "viewporthandler", "fillformatter", "custom-datasets", "custom-renderers"]),
    ("Integration", ["compose", "java-interop", "lists-and-scrolling", "proguard"]),
    ("In practice", ["performance", "accessibility", "troubleshooting", "migration", "miscellaneous"]),
]


def encode(index: int) -> str:
    """Index as uppercase letters, so the keyword and number rules never match a placeholder."""
    text = ""
    while True:
        text = chr(ord("A") + index % 26) + text
        index //= 26
        if index == 0:
            return text


def decode(text: str) -> int:
    value = 0
    for char in text:
        value = value * 26 + (ord(char) - ord("A"))
    return value


def highlight(code: str, language: str) -> str:
    """Wraps strings, comments, numbers and keywords in spans. Escapes the rest."""
    if language in XML_LIKE:
        return highlight_xml(code)
    if language not in KOTLIN_LIKE:
        return html.escape(code)
    tokens = []

    def store(kind: str, text: str) -> str:
        tokens.append((kind, text))
        return "\x00" + encode(len(tokens) - 1) + "\x00"

    pattern = re.compile(r'"""[\s\S]*?"""|"(?:[^"\\\n]|\\.)*"|//[^\n]*|/\*[\s\S]*?\*/')
    code = pattern.sub(lambda m: store("c" if m.group(0).startswith("/") else "s", m.group(0)), code)
    code = html.escape(code)
    # Keywords first: the number rule would otherwise wrap digits that the keyword rule then walks into.
    code = re.sub(
        r"\b(" + "|".join(sorted(KOTLIN_KEYWORDS, key=len, reverse=True)) + r")\b",
        r'<span class="k">\1</span>',
        code,
    )
    # Placeholders are uppercase letters between null bytes, so the type rule must not step into one.
    code = re.sub(r'(?<![\w\x00"])([A-Z][A-Za-z0-9_]*)\b(?!\x00)', r'<span class="t">\1</span>', code)
    code = re.sub(r"(?<![\w\"=])(\d+\.?\d*[fLdD]?)\b", r'<span class="n">\1</span>', code)

    def restore(match: re.Match) -> str:
        kind, text = tokens[decode(match.group(1))]
        return f'<span class="{kind}">{html.escape(text)}</span>'

    return re.sub(r"\x00([A-Z]+)\x00", restore, code)


def highlight_xml(code: str) -> str:
    code = html.escape(code)
    code = re.sub(r"(&lt;!--[\s\S]*?--&gt;)", r'<span class="c">\1</span>', code)
    code = re.sub(r"(&quot;[^&]*?&quot;)", r'<span class="s">\1</span>', code)
    code = re.sub(r"(&lt;/?)([\w.:]+)", r'\1<span class="k">\2</span>', code)
    return code


def inline(text: str) -> str:
    """Inline markdown: code, images, links, bold, italic."""
    spans = []

    def store(content: str) -> str:
        spans.append(content)
        return f"\x01{len(spans) - 1}\x01"

    text = re.sub(r"`([^`]+)`", lambda m: store(f"<code>{html.escape(m.group(1))}</code>"), text)
    text = html.escape(text)
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda m: store(f'<img src="{m.group(2)}" alt="{m.group(1)}" loading="lazy">'),
        text,
    )
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: store(f'<a href="{m.group(2)}">{m.group(1)}</a>'),
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", text)
    return re.sub(r"\x01(\d+)\x01", lambda m: spans[int(m.group(1))], text)


def slugify(text: str) -> str:
    plain = re.sub(r"&\w+;", " ", re.sub(r"<[^>]+>", "", text))
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")


def plain_text(markdown: str) -> str:
    """Markdown reduced to the words a reader would search for, code included."""
    text = re.sub(r"^\s*[-:| ]+$", " ", markdown, flags=re.M)
    text = re.sub(r"```\w*", " ", text)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[#>*`|]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def unique(anchor: str, used: set) -> str:
    """Keeps one id per heading even when two headings on a page share a title."""
    candidate, n = anchor, 2
    while candidate in used:
        candidate, n = f"{anchor}-{n}", n + 1
    used.add(candidate)
    return candidate


def render(markdown: str):
    """Returns (html, [(id, heading text)]) for the level two headings."""
    out, headings, used_anchors = [], [], set()
    lines = markdown.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("```"):
            language = line[3:].strip() or "text"
            i += 1
            block = []
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1
            if language == "figure":
                out.append(chr(10).join(block))
                continue

            label = LANGUAGE_LABELS.get(language, language.title())
            copy = '<button class="copy" type="button" aria-label="Copy code">Copy</button>'
            out.append(f'<pre data-lang="{html.escape(label)}">{copy}'
                       f'<code>{highlight(chr(10).join(block), language)}</code></pre>')
            continue

        if re.match(r"^#{1,4} ", line):
            level = len(line) - len(line.lstrip("#"))
            text = inline(line[level:].strip())
            if level in (2, 3):
                anchor = unique(slugify(text), used_anchors)
                if level == 2:
                    headings.append((anchor, re.sub(r"<[^>]+>", "", text)))
                link = f'<a class="anchor" href="#{anchor}" aria-label="Link to this section">#</a>'
                out.append(f'<h{level} id="{anchor}">{text}{link}</h{level}>')
            else:
                out.append(f"<h{level}>{text}</h{level}>")
            i += 1
            continue

        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1]):
            header = [c.strip() for c in line.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                i += 1
            body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            head = ""
            if any(c for c in header):
                head = "<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in header) + "</tr></thead>"
            out.append(f"<div class='table-wrap'><table>{head}<tbody>{body}</tbody></table></div>")
            continue

        if re.match(r"^[-*] |^\d+\. ", line):
            ordered = bool(re.match(r"^\d+\. ", line))
            items = []
            while i < len(lines) and re.match(r"^[-*] |^\d+\. ", lines[i]):
                items.append(re.sub(r"^([-*] |\d+\. )", "", lines[i]))
                i += 1
                while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                    items[-1] += " " + lines[i].strip()
                    i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(item)}</li>" for item in items) + f"</{tag}>")
            continue

        if line.startswith("> "):
            block = []
            while i < len(lines) and lines[i].startswith("> "):
                block.append(lines[i][2:])
                i += 1
            out.append(f"<blockquote>{inline(' '.join(block))}</blockquote>")
            continue

        if line.strip() == "---":
            out.append("<hr>")
            i += 1
            continue

        if line.strip():
            block = []
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,4} |```|\||[-*] |\d+\. |> )", lines[i]):
                block.append(lines[i])
                i += 1
            out.append(f"<p>{inline(' '.join(block))}</p>")
            continue

        i += 1
    return "\n".join(out), headings


def main() -> int:
    sources = sorted(f for f in os.listdir(SRC) if f.endswith(".md"))
    if not sources:
        print("no sources in docs/src", file=sys.stderr)
        return 1

    chapters = []
    for name in sources:
        text = open(os.path.join(SRC, name)).read()
        title = text.split("\n", 1)[0].lstrip("# ").strip()
        body = text.split("\n", 1)[1] if "\n" in text else ""
        summary = ""
        for line in body.split("\n"):
            if line.strip() and not line.startswith(("#", "`", ">", "-", "|")):
                summary = re.sub(r"[\[\]`*]|\([^)]*\)", "", line).strip()
                break
        chapters.append({"slug": name[3:-3], "title": title, "body": body, "summary": summary})

    template = open(TEMPLATE).read()
    position = {c["slug"]: i for i, c in enumerate(chapters)}
    grouped = [slug for _, slugs in SECTIONS for slug in slugs]
    unplaced = [s for s in position if s not in grouped]
    if unplaced:
        print(f"every chapter needs a section, unplaced: {unplaced}", file=sys.stderr)
        return 1
    # Sections may name a chapter that is still being written; it joins the site once its file exists.
    sections = [(title, [s for s in slugs if s in position]) for title, slugs in SECTIONS]
    sections = [(title, slugs) for title, slugs in sections if slugs]
    section_of = {slug: title for title, slugs in sections for slug in slugs}

    def navigation() -> str:
        blocks = []
        for title, slugs in sections:
            items = "".join(
                f'<li><a href="/mpandroidchart/docs/{slug}/" data-slug="{slug}">'
                f'<span class="num">{position[slug] + 1}</span>'
                f'{html.escape(chapters[position[slug]]["title"])}</a></li>'
                for slug in slugs
            )
            blocks.append(f'<div class="nav-section"><span class="nav-section-title">{html.escape(title)}</span><ol>{items}</ol></div>')
        return "".join(blocks)

    nav = navigation()

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    for index, chapter in enumerate(chapters):
        content, headings = render(chapter["body"])
        toc = ""
        if len(headings) >= 3:
            items = "".join(f'<a href="#{a}">{html.escape(t)}</a>' for a, t in headings)
            toc = f'<nav class="onthispage"><span>On this page</span>{items}</nav>'
        previous = chapters[index - 1] if index else None
        following = chapters[index + 1] if index + 1 < len(chapters) else None
        links = []
        if previous:
            links.append(f'<a class="prev" href="/mpandroidchart/docs/{previous["slug"]}/"><span>Previous</span>{html.escape(previous["title"])}</a>')
        if following:
            links.append(f'<a class="next" href="/mpandroidchart/docs/{following["slug"]}/"><span>Next</span>{html.escape(following["title"])}</a>')
        page = (template
                .replace("{{title}}", html.escape(chapter["title"]))
                .replace("{{description}}", html.escape(chapter["summary"])[:180])
                .replace("{{nav}}", nav.replace(f'data-slug="{chapter["slug"]}"', f'data-slug="{chapter["slug"]}" class="active"'))
                .replace("{{toc}}", toc)
                .replace("{{content}}", content)
                .replace("{{pager}}", f'<div class="pager">{"".join(links)}</div>')
                .replace("{{canonical}}", f'https://philjay.cc/mpandroidchart/docs/{chapter["slug"]}/')
                .replace("{{root}}", "../../../")
                .replace("{{chapter}}", f'{html.escape(section_of[chapter["slug"]])} <span>Chapter {index + 1} of {len(chapters)}</span>'))
        folder = os.path.join(OUT, chapter["slug"])
        os.makedirs(folder, exist_ok=True)
        open(os.path.join(folder, "index.html"), "w").write(_inline_css.fill(page))

    def card(slug: str) -> str:
        c = chapters[position[slug]]
        return (f'<a class="card link" href="/mpandroidchart/docs/{slug}/">'
                f'<h3><span class="num">{position[slug] + 1}</span>{html.escape(c["title"])}</h3>'
                f'<p>{html.escape(c["summary"])}</p></a>')

    cards = "".join(
        f'<h2 class="section-heading">{html.escape(title)}</h2>'
        f'<div class="cards docs-cards">{"".join(card(slug) for slug in slugs)}</div>'
        for title, slugs in sections
    )
    overview = (template
                .replace("{{title}}", "Guides")
                .replace("{{description}}", "Every chapter of the MPAndroidChart documentation, from getting started to custom data sets.")
                .replace("{{nav}}", nav)
                .replace("{{toc}}", "")
                .replace("{{content}}", f'<h1>Guides</h1><p class="lead-in">Every part of the library in {len(chapters)} chapters, with Kotlin examples checked against the current source. Start at the top or jump to what you need.</p>{cards}')
                .replace("{{pager}}", "")
                .replace("{{canonical}}", "https://philjay.cc/mpandroidchart/docs/")
                .replace("{{root}}", "../../")
                .replace("{{chapter}}", f'Documentation <span>{len(chapters)} chapters in {len(sections)} parts</span>'))
    open(os.path.join(OUT, "index.html"), "w").write(_inline_css.fill(overview))

    records = []
    for chapter in chapters:
        _, headings = render(chapter["body"])
        parts = re.split(r"^## ", chapter["body"], flags=re.M)
        records.append({"s": chapter["slug"], "c": chapter["title"], "h": "", "a": "",
                        "x": plain_text(parts[0])[:900]})
        for anchor_text, part in zip(headings, parts[1:]):
            anchor, heading = anchor_text
            records.append({"s": chapter["slug"], "c": chapter["title"], "h": heading, "a": anchor,
                            "x": plain_text(part.partition(chr(10))[2])[:900]})
    with open(os.path.join(OUT, "search.json"), "w") as index:
        json.dump(records, index, separators=(",", ":"))

    size = os.path.getsize(os.path.join(OUT, "search.json")) // 1024
    print(f"built {len(chapters)} chapters into {os.path.relpath(OUT, ROOT)}, "
          f"search index {len(records)} entries, {size} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
