"""Unit tests for cross-references."""

from __future__ import annotations

import pytest

from mdbook.engine.crossref import apply_crossref, build_crossref_map
from mdbook.engine.model import Section

pytestmark = pytest.mark.unit


def _sec(sid: str, number: int, *, is_title: bool = False) -> Section:
    return Section(id=sid, level=2, title=sid, number=number, is_title=is_title)


def test_build_map_excludes_titles() -> None:
    doc1 = [_sec("doc1--t", 0, is_title=True), _sec("doc1--a", 1), _sec("doc1--b", 2)]
    doc2 = [_sec("doc2--t", 0, is_title=True), _sec("doc2--x", 1)]
    mapping = build_crossref_map([doc1, doc2])
    assert mapping == {(1, 1): "doc1--a", (1, 2): "doc1--b", (2, 1): "doc2--x"}


def test_apply_crossref_links() -> None:
    mapping = {(2, 1): "doc2--decorators"}
    out = apply_crossref("see T2 §1 here", mapping)
    assert out == 'see <a class="xref" href="#doc2--decorators">T2 §1</a> here'


def test_apply_crossref_spacing_variants() -> None:
    mapping = {(1, 6): "doc1--s6"}
    assert 'href="#doc1--s6"' in apply_crossref("T1§6", mapping)
    assert 'href="#doc1--s6"' in apply_crossref("T1 § 6", mapping)


def test_apply_crossref_unknown_target_left_untouched() -> None:
    assert apply_crossref("T9 §9", {(1, 1): "x"}) == "T9 §9"
