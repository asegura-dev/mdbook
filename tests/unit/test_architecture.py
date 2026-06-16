"""Architecture guards: the logic must not depend on the interface.

Done by scanning the source (without importing the interfaces) so it needs
neither Tk nor a display.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import mdbook

pytestmark = pytest.mark.unit

ROOT = Path(mdbook.__file__).parent


def test_engine_does_not_import_interfaces() -> None:
    forbidden = ("customtkinter", "tkinter", "import typer", "import rich", "from rich")
    for py in (ROOT / "engine").rglob("*.py"):
        src = py.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in src, f"{py.name} should not reference '{token}'"


def test_gui_has_no_compilation_logic() -> None:
    src = (ROOT / "gui" / "app.py").read_text(encoding="utf-8")
    # It must not parse Markdown or touch the engine's internal modules.
    assert "markdown_it" not in src
    assert "engine.parser" not in src
    assert "engine.renderer" not in src
    assert "engine.compiler" not in src
    # It only uses the engine's public facade and the options contract.
    assert "from mdbook.engine import compile_book" in src
    assert "BuildOptions" in src
