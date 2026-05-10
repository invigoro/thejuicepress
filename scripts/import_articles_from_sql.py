#!/usr/bin/env python3
"""
One-off import: parse PostgreSQL pg_dump COPY block for public.Articles,
convert HTML body to minimal Markdown, write Jekyll pages under articles/.
"""

from __future__ import annotations

import html
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None  # type: ignore


ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / "juice-press-backup-7-3-22.sql"
OUT_DIR = ROOT / "articles"


def find_articles_copy(lines: list[str]) -> tuple[int, int]:
    start = None
    for i, line in enumerate(lines):
        if (
            line.startswith('COPY public."Articles"')
            or 'COPY public."Articles"' in line[:80]
        ):
            start = i
            break
    if start is None:
        raise SystemExit("Could not find COPY public.\"Articles\" block in SQL dump.")
    end = None
    for j in range(start + 1, len(lines)):
        if lines[j].strip() == r"\.":  # pg_dump end marker
            end = j
            break
    if end is None:
        raise SystemExit("Could not find end of Articles COPY block.")
    return start, end


def split_article_row(line: str) -> list[str]:
    """Tab-separated row; pg_dump typically escapes tabs inside fields — assume none."""
    line = line.rstrip("\n\r")
    return line.split("\t")


def slug_from_short_code(short_code: str, title: str, article_id: str) -> str:
    """Filename slug: prefer short code (already URL-safe), fallback to id."""
    code = (short_code or "").strip()
    if re.match(r"^[A-Za-z0-9_-]+$", code):
        return code.lower()
    # Fallback: simple slug from title
    base = title.lower() if title else f"article-{article_id}"
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base or f"article-{article_id}"


def strip_noise_tags(soup: BeautifulSoup) -> None:
    for tag in soup.find_all(["script", "style", "iframe", "noscript"]):
        tag.decompose()


def element_to_markdown(el, heading_level: int = 0) -> str:
    """Turn a BeautifulSoup node tree into minimal Markdown."""
    parts: list[str] = []

    for child in getattr(el, "children", []):
        if isinstance(child, str):
            t = str(child)
            if t:
                parts.append(t)
            continue
        if child.name is None:
            continue

        name = child.name.lower()

        if name in ("br",):
            parts.append("\n")
        elif name == "p":
            inner = element_to_markdown(child).strip()
            if inner:
                parts.append(inner + "\n\n")
        elif name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(name[1])
            inner = element_to_markdown(child).strip()
            if inner:
                parts.append("#" * level + " " + inner + "\n\n")
        elif name in ("strong", "b"):
            inner = element_to_markdown(child).strip()
            if inner:
                parts.append(f"**{inner}**")
        elif name in ("em", "i"):
            inner = element_to_markdown(child).strip()
            if inner:
                parts.append(f"*{inner}*")
        elif name == "a":
            href = (child.get("href") or "").strip()
            inner = element_to_markdown(child).strip()
            if href and inner:
                parts.append(f"[{inner}]({href})")
            elif inner:
                parts.append(inner)
        elif name in ("ul", "ol"):
            for li in child.find_all("li", recursive=False):
                bullet = element_to_markdown(li).strip()
                if bullet:
                    parts.append(f"- {bullet}\n")
            parts.append("\n")
        elif name == "li":
            parts.append(element_to_markdown(child))
        elif name in ("blockquote",):
            inner = element_to_markdown(child).strip()
            if inner:
                for ln in inner.splitlines():
                    parts.append("> " + ln + "\n")
                parts.append("\n")
        elif name in ("div", "span", "section", "article", "main"):
            parts.append(element_to_markdown(child))
        elif name == "img":
            alt = (child.get("alt") or "").strip()
            src = (child.get("src") or "").strip()
            if src:
                parts.append(f"![{alt}]({src})\n\n")
        elif name in ("code",):
            inner = child.get_text()
            parts.append(f"`{inner}`")
        elif name in ("pre",):
            inner = child.get_text().rstrip()
            parts.append("```\n" + inner + "\n```\n\n")
        else:
            parts.append(element_to_markdown(child))

    return "".join(parts)


def html_to_markdown(html_fragment: str) -> str:
    if not html_fragment or not html_fragment.strip():
        return ""

    if BeautifulSoup is None:
        raise SystemExit("Install beautifulsoup4: pip install beautifulsoup4")

    fragment = html_fragment.strip()
    soup = BeautifulSoup(fragment, "html.parser")
    strip_noise_tags(soup)

    # Prefer body-like roots; otherwise whole soup
    root = soup.body if soup.body else soup
    md = element_to_markdown(root).strip()
    # Decode HTML entities leftover in text nodes
    md = html.unescape(md)
    # Collapse excessive blank lines
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    # Google Docs / DB artifacts (literal \\t in HTML text; real tabs)
    md = md.replace("\xa0", " ")
    md = re.sub(r"\\t", "", md)
    md = md.replace("\t", "")
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    md = "\n".join(ln.rstrip() for ln in md.splitlines()).strip()
    return md


def parse_iso_datetime(s: str) -> datetime | None:
    s = (s or "").strip()
    if not s or s == r"\N":
        return None
    # "2020-09-27 23:33:25.371128"
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def main() -> None:
    if not SQL_PATH.is_file():
        print(f"Missing SQL dump: {SQL_PATH}", file=sys.stderr)
        sys.exit(1)

    text = SQL_PATH.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines(keepends=True)
    start, end = find_articles_copy(lines)
    data_lines = lines[start + 1 : end]

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Clear previous generated markdown (keep folder)
    for old in OUT_DIR.glob("*.md"):
        old.unlink()

    written = []
    for raw in data_lines:
        if not raw.strip():
            continue
        cols = split_article_row(raw)
        if len(cols) != 15:
            raise SystemExit(
                f"Expected 15 columns, got {len(cols)} — parse may need escaping fix."
            )

        (
            article_id,
            url_short,
            title,
            content,
            draft_content,
            _created,
            _edited,
            published_on,
            published,
            _views,
            _category,
            _cover,
            _overwritten,
            draft_title,
            _draft_cover,
        ) = cols

        pub = published.strip().lower() in ("t", "true", "1")
        if not pub:
            continue

        body_html = content.strip() if content and content != r"\N" else ""
        if not body_html:
            body_html = (draft_content or "").strip()
            if body_html == r"\N":
                body_html = ""

        display_title = (title or "").strip()
        if not display_title:
            display_title = (draft_title or "").strip()
            if display_title == r"\N":
                display_title = f"Article {article_id}"

        md_body = html_to_markdown(body_html)
        slug = slug_from_short_code(url_short, display_title, article_id)
        date = parse_iso_datetime(published_on)
        date_str = date.strftime("%Y-%m-%d") if date else None

        front_matter = ["---", f'title: "{escape_yaml_string(display_title)}"']
        if date_str:
            front_matter.append(f"date: {date_str}")
        front_matter.append(f"article_id: {article_id}")
        front_matter.append("---")
        front_matter.append("")

        # Title rendered by theme (layout: post via _config defaults)
        out_path = OUT_DIR / f"{slug}.md"
        content_out = "\n".join(front_matter) + md_body + "\n"
        out_path.write_text(content_out, encoding="utf-8")
        written.append((display_title, slug, date_str))

    # Sort by date desc then title
    written.sort(key=lambda x: (x[2] or "", x[0]), reverse=True)

    print(f"Wrote {len(written)} articles to {OUT_DIR.relative_to(ROOT)}")


def escape_yaml_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


if __name__ == "__main__":
    main()
