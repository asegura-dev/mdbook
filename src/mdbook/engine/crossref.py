"""Cross-references: find patterns like ``T1 §6`` and turn them into links.

Convention:

- ``T<n>`` = document number ``n`` in the order of the work (1-based).
- ``§<m>`` = NUMBERED SECTION ``m`` of that document, i.e. the heading whose
  text starts with ``m.`` (e.g. ``## 6. Validate the config`` is §6).
  Unnumbered subheadings do not count.

If the target does not exist, the text is left untouched.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from mdbook.engine.model import Section

CrossRefMap = dict[tuple[int, int], str]

# Accepts "T1 §6", "T1§6", "T1 § 6".
CROSSREF_RE = re.compile(r"\bT(\d+)\s*§\s*(\d+)")


def build_crossref_map(documents_sections: Iterable[list[Section]]) -> CrossRefMap:
    """Build the (document, section) -> anchor id map.

    ``documents_sections`` must come in the order of the work.
    """
    mapping: CrossRefMap = {}
    for doc_index, sections in enumerate(documents_sections, start=1):
        for section in sections:
            key = (doc_index, section.number)
            # If a numbered section repeats, the first occurrence wins.
            if section.number > 0 and key not in mapping:
                mapping[key] = section.id
    return mapping


def apply_crossref(escaped_text: str, mapping: CrossRefMap) -> str:
    """Replace references with internal links over already-escaped text."""

    def repl(match: re.Match[str]) -> str:
        doc_n = int(match.group(1))
        sec_n = int(match.group(2))
        target = mapping.get((doc_n, sec_n))
        if target is None:
            return match.group(0)
        return f'<a class="xref" href="#{target}">{match.group(0)}</a>'

    return CROSSREF_RE.sub(repl, escaped_text)
