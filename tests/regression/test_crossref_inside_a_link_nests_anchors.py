"""A reference inside a link used to produce nested <a> elements.

``See [T1 §1](https://example.com)`` rendered as
``<a href="..."><a class="xref" ...>T1 §1</a></a>``. HTML forbids nesting
anchors, so the browser closes the outer one early and the author's own link
stops working.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mdbook.config import BuildOptions
from mdbook.engine import compile_html

pytestmark = pytest.mark.regression


def _html(tmp_path: Path, body: str) -> str:
    source = tmp_path / "a.md"
    source.write_text(f"# Doc\n\n## 1. First\n\n{body}\n", encoding="utf-8")
    return compile_html(
        BuildOptions(
            title="x",
            inputs=[source],
            output=tmp_path / "o.html",
            cross_references=True,
        )
    )


def test_reference_inside_a_link_is_left_as_text(tmp_path: Path) -> None:
    html = _html(tmp_path, "See [T1 §1](https://example.com) here.")

    assert '<a href="https://example.com">T1 §1</a>' in html
    assert '<a href="https://example.com"><a' not in html
    # The author's link survives intact; the reference stays plain text inside
    # it, exactly as an unresolvable reference would.
    assert 'class="xref"' not in html


def test_reference_outside_a_link_still_becomes_one(tmp_path: Path) -> None:
    html = _html(tmp_path, "Plain T1 §1 reference.")
    assert '<a class="xref" href="#doc1--1-first">T1 §1</a>' in html


def test_reference_after_a_link_still_becomes_one(tmp_path: Path) -> None:
    # The link has closed by then, so the guard must not swallow what follows.
    html = _html(tmp_path, "See [the site](https://example.com) and then T1 §1.")
    assert '<a href="https://example.com">the site</a>' in html
    assert '<a class="xref" href="#doc1--1-first">T1 §1</a>' in html
