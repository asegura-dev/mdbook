"""Guardas de arquitectura: la lógica no depende de la interfaz.

Se hace por análisis del código fuente (sin importar las interfaces) para no
requerir Tk ni un display.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import mdbook

pytestmark = pytest.mark.unit

ROOT = Path(mdbook.__file__).parent


def test_el_motor_no_importa_interfaces() -> None:
    prohibido = ("customtkinter", "tkinter", "import typer", "import rich", "from rich")
    for py in (ROOT / "engine").rglob("*.py"):
        src = py.read_text(encoding="utf-8")
        for token in prohibido:
            assert token not in src, f"{py.name} no debería referirse a '{token}'"


def test_la_gui_no_contiene_logica_de_compilacion() -> None:
    src = (ROOT / "gui" / "app.py").read_text(encoding="utf-8")
    # No parsea Markdown ni toca los submódulos internos del motor.
    assert "markdown_it" not in src
    assert "engine.parser" not in src
    assert "engine.renderer" not in src
    assert "engine.compiler" not in src
    # Solo usa la fachada pública del motor y el contrato de opciones.
    assert "from mdbook.engine import compile_book" in src
    assert "BuildOptions" in src
