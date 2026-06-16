"""Assemble a ``Book`` into a single self-contained HTML file.

Reads the assets (``template.html``, ``style.css``, ``app.js``) from the
package and inlines them, so the result has no external dependencies.
"""

from __future__ import annotations

from html import escape
from importlib.resources import files

from mdbook.engine.model import Book


def _asset(name: str) -> str:
    return (files("mdbook.engine") / "assets" / name).read_text(encoding="utf-8")


def _build_sidebar(book: Book) -> str:
    items: list[str] = []
    for doc in book.documents:
        secs: list[str] = []
        for sec in doc.sections:
            if sec.is_title:
                continue
            secs.append(
                f'<li class="toc-sec lvl{sec.level}" data-target="{sec.id}">'
                f'<a href="#{sec.id}">{escape(sec.title)}</a></li>'
            )
        sublist = f'<ul class="toc-subs">{"".join(secs)}</ul>' if secs else ""
        items.append(
            f'<li class="toc-doc" data-doc="{doc.id}">'
            f'<a href="#{doc.id}" class="toc-doc-link">{escape(doc.title)}</a>'
            f"{sublist}</li>"
        )
    return f'<ul class="toc">{"".join(items)}</ul>'


def _build_index(book: Book) -> str:
    items = "".join(
        f'<li><a href="#{doc.id}">{escape(doc.title)}</a></li>' for doc in book.documents
    )
    return f'<ol class="index-list">{items}</ol>'


def _build_content(book: Book) -> str:
    cover = (
        '<header class="cover">'
        f"<h1>{escape(book.title)}</h1>"
        '<nav class="index"><h2>Contents</h2>'
        f"{_build_index(book)}</nav>"
        "</header>"
    )
    articles = "".join(
        f'<article class="doc" id="{doc.id}">{doc.html}</article>' for doc in book.documents
    )
    return cover + articles


def build_html(book: Book) -> str:
    """Return the full HTML for the work."""
    template = _asset("template.html")
    style = _asset("style.css")
    script = _asset("app.js")

    replacements = {
        "{{TITLE}}": escape(book.title),
        "{{DEFAULT_THEME}}": book.theme,
        "{{STYLE}}": style,
        "{{SIDEBAR}}": _build_sidebar(book),
        "{{CONTENT}}": _build_content(book),
        "{{SCRIPT}}": script,
    }
    html = template
    for key, value in replacements.items():
        html = html.replace(key, value)
    return html
