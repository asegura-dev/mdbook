"""Two headings could end up sharing an id, so a TOC link jumped to the wrong one.

De-duplication used to count occurrences of each slug and append the count. The
suffixed name it produced could itself be another heading's real slug: with
"Intro", "Intro" and "Intro 2", both the second and the third became
``intro-2``.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from mdbook.config import BuildOptions
from mdbook.engine import compile_html
from mdbook.engine.parser import build_md, parse_document

pytestmark = pytest.mark.regression


def test_suffixed_slug_does_not_collide_with_a_real_heading() -> None:
    md = build_md()
    text = "# Doc\n\n## Intro\n\n## Intro\n\n## Intro 2\n"
    parsed = parse_document(md, text, doc_id="doc1")

    ids = [section.id for section in parsed.sections]
    assert len(ids) == len(set(ids)), f"duplicate heading ids: {ids}"
    assert ids == [
        "doc1--doc",
        "doc1--intro",
        "doc1--intro-2",
        "doc1--intro-2-2",
    ]


def test_plain_repeats_keep_the_familiar_numbering() -> None:
    # The fix must not renumber ordinary documents: already published anchors
    # (docs/manual.html, examples/demo.html) have to keep working.
    md = build_md()
    parsed = parse_document(md, "# Doc\n\n## Notes\n\n## Notes\n\n## Notes\n", doc_id="doc1")
    assert [s.id for s in parsed.sections] == [
        "doc1--doc",
        "doc1--notes",
        "doc1--notes-2",
        "doc1--notes-3",
    ]


def test_rendered_html_has_no_duplicate_ids(tmp_path: Path) -> None:
    source = tmp_path / "a.md"
    source.write_text("# Doc\n\n## Intro\n\n## Intro\n\n## Intro 2\n", encoding="utf-8")
    html = compile_html(BuildOptions(title="x", inputs=[source], output=tmp_path / "o.html"))

    ids = re.findall(r'<h[1-6] id="([^"]+)"', html)
    assert len(ids) == len(set(ids)), f"duplicate ids in the page: {ids}"
