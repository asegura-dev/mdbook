"""Theme guards: every declared theme must actually be rendered.

The failure these prevent is silent. A theme added to the contract but missing
its CSS block still validates, still appears in the picker, and still produces a
page — it just falls back to the base palette, so it looks like the theme "does
nothing" instead of like a bug.
"""

from __future__ import annotations

import re
from importlib.resources import files

import pytest

from mdbook.config import THEMES, Theme
from mdbook.engine.model import Book, Document
from mdbook.engine.renderer import build_html

pytestmark = pytest.mark.unit

# The base palette lives in :root rather than in a [data-theme] block, so it is
# what every other theme overrides on top of.
BASE_THEME = "light"

# A theme that set only --bg would render unreadable text on a new background.
REQUIRED_TOKENS = (
    "--bg",
    "--bg-soft",
    "--bg-code",
    "--text",
    "--text-soft",
    "--border",
    "--accent",
    "--accent-soft",
    "--mark",
)

STYLE = (files("mdbook.engine") / "assets" / "style.css").read_text(encoding="utf-8")


def _block(selector: str) -> str:
    """Return the declarations inside the first ``selector { ... }`` rule."""
    match = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", STYLE)
    assert match is not None, f"style.css has no '{selector}' rule"
    return match.group(1)


def _book(theme: str) -> Book:
    doc = Document(id="doc1", title="T", html="<p>x</p>", sections=[])
    return Book(title="Book", theme=theme, documents=[doc])


def test_base_theme_is_declared() -> None:
    assert BASE_THEME in THEMES


@pytest.mark.parametrize("token", REQUIRED_TOKENS)
def test_root_defines_the_full_palette(token: str) -> None:
    assert f"{token}:" in _block(":root")


@pytest.mark.parametrize("theme", [t for t in THEMES if t != BASE_THEME])
def test_every_theme_has_a_css_block(theme: Theme) -> None:
    block = _block(f'[data-theme="{theme}"]')
    missing = [token for token in REQUIRED_TOKENS if f"{token}:" not in block]
    assert not missing, f"theme '{theme}' does not override {missing}"


def test_stylesheet_requests_nothing_external() -> None:
    # A webfont would be the easy way to give the serif theme its typeface, and
    # it would silently break the self-contained guarantee.
    assert "@import" not in STYLE
    assert "http://" not in STYLE and "https://" not in STYLE
    assert "url(" not in STYLE


@pytest.mark.parametrize("theme", THEMES)
def test_picker_offers_every_theme_and_preselects_the_default(theme: Theme) -> None:
    html = build_html(_book(theme))
    for candidate in THEMES:
        assert f'<option value="{candidate}"' in html
    assert f'<option value="{theme}" selected' in html
    assert f'data-theme="{theme}"' in html


def test_serif_theme_overrides_the_font() -> None:
    # The point of the serif theme: it is the only one that changes the
    # typeface, and it does so through the token, not a duplicated rule.
    assert "--font-body:" in _block('[data-theme="serif"]')
    assert "serif" in _block('[data-theme="serif"]')
    assert "font-family: var(--font-body)" in _block(":root")
