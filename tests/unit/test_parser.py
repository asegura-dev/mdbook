"""Unit tests for the parser: slugs, titles, sections and subset rendering."""

from __future__ import annotations

import pytest

from mdbook.engine.parser import build_md, parse_document, render_document, slugify

pytestmark = pytest.mark.unit


def test_slugify() -> None:
    assert slugify("Data types") == "data-types"
    assert slugify("  ¡Hello, World!  ") == "hello-world"
    assert slugify("###") == "sec"


def test_title_from_first_h1() -> None:
    md = build_md()
    parsed = parse_document(md, "# My Document\n\nText.\n\n## Section", "doc1")
    assert parsed.title == "My Document"


def test_no_h1_means_no_title() -> None:
    md = build_md()
    parsed = parse_document(md, "## Only H2\n\nText.", "doc1")
    assert parsed.title is None


def test_section_number_read_from_text() -> None:
    md = build_md()
    src = "# T\n\n## 1. Intro\n\n### Unnumbered sub\n\n## 2. Advanced\n\n## 10. Jump"
    parsed = parse_document(md, src, "doc1")
    nums = {s.title: s.number for s in parsed.sections}
    # §N is read from the text: unnumbered -> 0; "10." -> 10 (not positional).
    assert nums == {
        "T": 0,
        "1. Intro": 1,
        "Unnumbered sub": 0,
        "2. Advanced": 2,
        "10. Jump": 10,
    }
    title = next(s for s in parsed.sections if s.is_title)
    assert title.title == "T"


def test_unique_ids_for_repeated_headings() -> None:
    md = build_md()
    parsed = parse_document(md, "# T\n\n## Notes\n\n## Notes", "doc1")
    ids = [s.id for s in parsed.sections]
    assert ids == ["doc1--t", "doc1--notes", "doc1--notes-2"]


def test_render_full_subset() -> None:
    md = build_md()
    src = (
        "# Title\n\nParagraph with **bold**, *italic* and `code`.\n\n"
        "> A quote\n\n- a\n- b\n\n| X | Y |\n| - | - |\n| 1 | 2 |\n\n"
        "```python\nprint('hi')\n```\n"
    )
    parsed = parse_document(md, src, "doc1")
    html = render_document(md, parsed, crossref_map=None)
    assert 'id="doc1--title"' in html
    assert "<strong>bold</strong>" in html
    assert "<em>italic</em>" in html
    assert "<code>code</code>" in html
    assert "<blockquote>" in html
    assert "<table>" in html and "<td>1</td>" in html
    assert "<li>a</li>" in html


def test_render_code_block_with_language_and_copy() -> None:
    md = build_md()
    parsed = parse_document(md, "# T\n\n```python\nx = 1\n```\n", "doc1")
    html = render_document(md, parsed, crossref_map=None)
    assert 'class="code-block"' in html
    assert 'class="language-python"' in html
    assert ">python</span>" in html
    assert "copy-btn" in html


def test_html_escaped_in_code() -> None:
    md = build_md()
    parsed = parse_document(md, "# T\n\n```\n<script>\n```\n", "doc1")
    html = render_document(md, parsed, crossref_map=None)
    assert "&lt;script&gt;" in html
    assert "<script>" not in html
