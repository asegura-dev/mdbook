"""Overlays stayed on screen because an author `display` beats `[hidden]`.

The script hides the selection toolbar and the note popover by setting the
`hidden` attribute, which works through the browser's own
`[hidden] { display: none }` rule. Any author rule setting `display` outranks
that regardless of specificity, so `.ann-bar { display: flex }` kept both
overlays painted no matter what the script did. The review panel had the guard
and closed correctly, which is what made the other two look like a scripting
bug rather than a stylesheet one.
"""

from __future__ import annotations

import re
from importlib.resources import files

import pytest

pytestmark = pytest.mark.regression

STYLE = (files("mdbook.engine") / "assets" / "style.css").read_text(encoding="utf-8")

# Every element the script shows and hides through the `hidden` attribute.
TOGGLED = [".ann-bar", ".ann-pop", ".review"]


def _sets_display(selector: str) -> bool:
    """Does any rule whose selector list includes `selector` set `display`?"""
    for selectors, body in re.findall(r"([^{}]+)\{([^}]*)\}", STYLE):
        names = [part.strip() for part in selectors.split(",")]
        if selector in names and re.search(r"\bdisplay\s*:", body):
            return True
    return False


@pytest.mark.parametrize("selector", TOGGLED)
def test_hidden_beats_the_author_display(selector: str) -> None:
    if not _sets_display(selector):
        pytest.skip(f"{selector} does not set display, so [hidden] still works")
    guard = re.search(re.escape(selector) + r"\[hidden\][^{]*\{[^}]*display:\s*none", STYLE)
    assert guard is not None, (
        f"{selector} sets display, so it needs a {selector}[hidden] rule; "
        "without it the element can never be hidden from the script"
    )
