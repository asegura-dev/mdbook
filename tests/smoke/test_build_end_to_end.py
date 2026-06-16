"""Smoke test: compile the example guide end to end."""

from __future__ import annotations

from pathlib import Path

import pytest

from mdbook.config import BuildOptions
from mdbook.engine import compile_book, compile_html

pytestmark = pytest.mark.smoke


def test_compiles_and_writes_html(sample_files: list[Path], tmp_path: Path) -> None:
    assert len(sample_files) == 5  # the five guide documents
    output = tmp_path / "book.html"
    options = BuildOptions(
        title="Clean Architecture Guide",
        inputs=sample_files,
        output=output,
        theme="dark",
        cross_references=True,
    )
    written = compile_book(options)

    assert written == output.resolve() or written == output
    assert output.exists()
    html = output.read_text(encoding="utf-8")

    # Self-contained: CSS and JS embedded, no external links.
    assert "<style>" in html and "</style>" in html
    assert "<script>" in html and "addEventListener" in html
    assert "http://" not in html and "https://" not in html

    # Key structure.
    assert "Clean Architecture Guide" in html
    assert 'data-theme="dark"' in html  # default theme applied
    assert 'class="search"' in html
    assert "theme-btn" in html
    assert "copy-btn" in html

    # Document titles (first H1 of the first and last file).
    assert "Coupling and cohesion" in html
    assert "When not to add structure" in html

    # Navigation: one section per document.
    assert 'class="toc"' in html
    assert 'id="doc1"' in html and 'id="doc5"' in html

    # Cross-reference enabled: T2 §1 -> "## 1. Dependencies point inward".
    assert '<a class="xref" href="#doc2--1-dependencies-point-inward">T2 §1</a>' in html


def test_crossref_disabled_does_not_link(sample_files: list[Path], tmp_path: Path) -> None:
    options = BuildOptions(
        title="Guide",
        inputs=sample_files,
        output=tmp_path / "book.html",
        theme="light",
        cross_references=False,
    )
    html = compile_html(options)
    assert "T2 §1" in html  # the text is still there
    assert 'class="xref"' not in html  # but no inline link
    assert 'data-theme="light"' in html
