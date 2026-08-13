"""Print guards: what the PDF export depends on and cannot be seen in a test.

Nothing here proves the PDF *looks* right — that needs a human and a print
dialog. What these pin down are the decisions the print stylesheet rests on,
each of which fails silently: a theme token leaking into the export, a search
filter truncating it, a table that stops paginating.
"""

from __future__ import annotations

import re
from importlib.resources import files

import pytest

from mdbook.engine.model import Book, Document
from mdbook.engine.renderer import build_html

pytestmark = pytest.mark.unit

STYLE = (files("mdbook.engine") / "assets" / "style.css").read_text(encoding="utf-8")


def _print_block() -> str:
    """The body of the ``@media print`` rule, braces balanced."""
    start = STYLE.find("@media print")
    assert start != -1, "style.css has no @media print block"
    depth = 0
    for index in range(STYLE.index("{", start), len(STYLE)):
        if STYLE[index] == "{":
            depth += 1
        elif STYLE[index] == "}":
            depth -= 1
            if depth == 0:
                return STYLE[start:index]
    raise AssertionError("unterminated @media print block")


def _theme_tokens() -> set[str]:
    """Every custom property any [data-theme] block overrides."""
    tokens: set[str] = set()
    for body in re.findall(r'\[data-theme="[a-z]+"\]\s*\{([^}]*)\}', STYLE):
        tokens.update(re.findall(r"(--[a-z-]+)\s*:", body))
    return tokens


def _strip_comments(css: str) -> str:
    """Drop /* … */ so assertions read the rules, not the prose about them."""
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


# Comments are stripped: these tests are about what the stylesheet does, and a
# comment explaining a decision must not be able to satisfy — or break — a check
# about the rules themselves.
PRINT = _strip_comments(_print_block())


def test_print_block_exists() -> None:
    assert PRINT.startswith("@media print")


@pytest.mark.parametrize("selector", [".topbar", ".sidebar", ".copy-btn"])
def test_interactive_chrome_is_hidden(selector: str) -> None:
    hidden = re.search(r"([^{}]*)\{[^}]*display:\s*none[^}]*\}", PRINT)
    assert hidden is not None
    assert selector in hidden.group(1)


def test_print_overrides_every_token_a_theme_can_change() -> None:
    # The leak this prevents: a theme adds a token, the print block does not
    # override it, and that theme bleeds into an otherwise light PDF.
    missing = sorted(token for token in _theme_tokens() if f"{token}:" not in PRINT)
    assert not missing, f"@media print does not neutralise {missing}"


def test_print_names_no_theme() -> None:
    # The light palette is forced by specificity (:root:root), not by listing
    # the themes. Listing them would be a second copy of the theme set.
    assert ":root:root" in PRINT
    assert "data-theme" not in PRINT


def test_print_forces_a_light_serif_page() -> None:
    assert "--bg: #ffffff" in PRINT
    assert re.search(r"--font-body:[^;]*serif", PRINT)


def test_search_filter_cannot_truncate_the_export() -> None:
    # The filter sets display:none inline; only !important outranks that.
    match = re.search(r"([^{}]*)\{\s*display:\s*revert\s*!important", PRINT)
    assert match is not None, "print block does not undo the search filter"
    assert ".doc" in match.group(1) and ".cover" in match.group(1)


def test_code_blocks_and_quotes_resist_breaking() -> None:
    assert re.search(r"\.code-block\s*\{[^}]*break-inside:\s*avoid", PRINT)
    assert re.search(r"blockquote\s*\{[^}]*break-inside:\s*avoid", PRINT)


def test_documents_start_on_a_new_page() -> None:
    assert re.search(r"\.cover\s*\{[^}]*break-after:\s*page", PRINT)
    assert re.search(r"\.doc \+ \.doc\s*\{[^}]*break-before:\s*page", PRINT)


def test_tables_paginate_as_tables() -> None:
    # On screen a table is display:block for horizontal scrolling, which stops
    # it breaking across pages or repeating its header.
    assert re.search(r"table\s*\{[^}]*display:\s*table", PRINT)
    assert re.search(r"thead\s*\{[^}]*display:\s*table-header-group", PRINT)


def test_only_external_links_show_their_url() -> None:
    assert re.search(r'a\[href\^="http"\]::after\s*\{[^}]*attr\(href\)', PRINT)
    # Internal cross-references must not be expanded.
    assert 'a[href^="#"]::after' not in PRINT


def test_rendered_page_offers_the_print_button() -> None:
    book = Book(
        title="B", theme="dark", documents=[Document(id="doc1", title="T", html="<p>x</p>")]
    )
    html = build_html(book)
    assert 'class="icon-btn print-btn"' in html
    assert 'aria-label="Export to PDF"' in html
