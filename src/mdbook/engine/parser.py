"""Parse a Markdown subset into tokens, with navigation metadata.

Uses markdown-it-py. The flow is two passes so cross-references can point
between documents:

1. :func:`parse_document` extracts the title and sections and sets the ``id``
   on the headings (on the tokens themselves).
2. :func:`render_document` pours those tokens to HTML, optionally applying the
   cross-reference map.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, cast

from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml
from markdown_it.token import Token

from mdbook.engine.crossref import CrossRefMap, apply_crossref
from mdbook.engine.model import Section

_NON_WORD = re.compile(r"[^\w\s-]", re.UNICODE)
_SPACES = re.compile(r"[\s_-]+", re.UNICODE)
# Numbered section: the heading text starts with "N." (e.g. "6. Validate").
_SECTION_NUM = re.compile(r"^\s*(\d+)\.")


@dataclass
class ParsedDocument:
    """Result of pass 1: tokens ready to render plus metadata."""

    id: str
    title: str | None
    tokens: list[Token]
    sections: list[Section] = field(default_factory=list)


def slugify(text: str) -> str:
    """Turn text into an ASCII slug usable as an ``id``/fragment.

    Strips accents (``Sección`` -> ``seccion``) so anchors stay portable in
    URLs.
    """
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = _NON_WORD.sub("", text.strip().lower())
    text = _SPACES.sub("-", text).strip("-")
    return text or "sec"


def build_md() -> MarkdownIt:
    """Create the parser with the supported subset and our own render rules."""
    md = MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False})
    md.enable("table")
    md.add_render_rule("fence", _render_fence)
    md.add_render_rule("code_block", _render_code_block)
    md.add_render_rule("text", _render_text)
    return md


def _plain_text(inline: Token) -> str:
    """Plain text of an inline token (used for section titles)."""
    if not inline.children:
        return inline.content.strip()
    parts: list[str] = []
    for child in inline.children:
        if child.type in ("text", "code_inline"):
            parts.append(child.content)
        elif child.type in ("softbreak", "hardbreak"):
            parts.append(" ")
    return "".join(parts).strip()


def parse_document(md: MarkdownIt, text: str, doc_id: str) -> ParsedDocument:
    """Pass 1: parse, assign ids to headings and collect sections."""
    tokens = md.parse(text)
    sections: list[Section] = []
    title: str | None = None
    seen: dict[str, int] = {}

    for i, tok in enumerate(tokens):
        if tok.type != "heading_open":
            continue
        level = int(tok.tag[1])
        heading_text = _plain_text(tokens[i + 1])
        base = slugify(heading_text)
        n = seen.get(base, 0)
        seen[base] = n + 1
        unique = base if n == 0 else f"{base}-{n + 1}"
        section_id = f"{doc_id}--{unique}"
        tok.attrSet("id", section_id)

        is_title = title is None and level == 1
        if is_title:
            title = heading_text
            number = 0
        else:
            match = _SECTION_NUM.match(heading_text)
            number = int(match.group(1)) if match else 0
        sections.append(
            Section(
                id=section_id,
                level=level,
                title=heading_text,
                number=number,
                is_title=is_title,
            )
        )

    return ParsedDocument(id=doc_id, title=title, tokens=tokens, sections=sections)


def render_document(
    md: MarkdownIt, parsed: ParsedDocument, crossref_map: CrossRefMap | None
) -> str:
    """Pass 2: pour the tokens to HTML."""
    env: dict[str, Any] = {}
    if crossref_map:
        env["crossref_map"] = crossref_map
    return cast(str, md.renderer.render(parsed.tokens, md.options, env))


# --- Custom render rules --------------------------------------------------
# markdown-it-py calls these with (renderer, tokens, idx, options, env).


def _render_fence(
    renderer: Any, tokens: list[Token], idx: int, options: Any, env: dict[str, Any]
) -> str:
    token = tokens[idx]
    info = token.info.strip()
    lang = info.split(maxsplit=1)[0] if info else ""
    code = escapeHtml(token.content)
    lang_attr = f' class="language-{escapeHtml(lang)}"' if lang else ""
    label = escapeHtml(lang) if lang else "text"
    return (
        '<div class="code-block">'
        f'<div class="code-head"><span class="code-lang">{label}</span>'
        '<button class="copy-btn" type="button" aria-label="Copy code">Copy</button>'
        "</div>"
        f"<pre><code{lang_attr}>{code}</code></pre>"
        "</div>\n"
    )


def _render_code_block(
    renderer: Any, tokens: list[Token], idx: int, options: Any, env: dict[str, Any]
) -> str:
    # Indented blocks (4 spaces): same wrapper, no language.
    code = escapeHtml(tokens[idx].content)
    return (
        '<div class="code-block">'
        '<div class="code-head"><span class="code-lang">text</span>'
        '<button class="copy-btn" type="button" aria-label="Copy code">Copy</button>'
        "</div>"
        f"<pre><code>{code}</code></pre>"
        "</div>\n"
    )


def _render_text(
    renderer: Any, tokens: list[Token], idx: int, options: Any, env: dict[str, Any]
) -> str:
    content = escapeHtml(tokens[idx].content)
    crossref_map: CrossRefMap | None = env.get("crossref_map")
    if crossref_map:
        return apply_crossref(content, crossref_map)
    return content
