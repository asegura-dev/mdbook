"""Prueba de humo: compila los .md de ejemplo de punta a punta."""

from __future__ import annotations

from pathlib import Path

import pytest

from mdbook.config import BuildOptions
from mdbook.engine import compile_book, compile_html

pytestmark = pytest.mark.smoke


def test_compila_y_escribe_html(sample_files: list[Path], tmp_path: Path) -> None:
    output = tmp_path / "libro.html"
    options = BuildOptions(
        title="Mi Obra de Estudio",
        inputs=sample_files,
        output=output,
        theme="oscuro",
        cross_references=True,
    )
    written = compile_book(options)

    assert written == output.resolve() or written == output
    assert output.exists()
    html = output.read_text(encoding="utf-8")

    # Autocontenido: CSS y JS embebidos, sin enlaces externos.
    assert "<style>" in html and "</style>" in html
    assert "<script>" in html and "addEventListener" in html
    assert "http://" not in html and "https://" not in html

    # Estructura clave.
    assert "Mi Obra de Estudio" in html
    assert 'data-theme="dark"' in html  # tema por defecto aplicado
    assert 'class="search"' in html
    assert "theme-btn" in html
    assert "copy-btn" in html

    # Títulos de los documentos (primer H1 de cada archivo).
    assert "Tomo 1: Fundamentos" in html
    assert "Tomo 2: Temas avanzados" in html

    # Navegación e índice.
    assert 'class="toc"' in html
    assert 'id="doc1"' in html and 'id="doc2"' in html

    # Referencia cruzada activada: T2 §1 -> "## 1. Decoradores" del doc2.
    assert '<a class="xref" href="#doc2--1-decoradores">T2 §1</a>' in html


def test_crossref_desactivado_no_enlaza(sample_files: list[Path], tmp_path: Path) -> None:
    options = BuildOptions(
        title="Obra",
        inputs=sample_files,
        output=tmp_path / "libro.html",
        theme="claro",
        cross_references=False,
    )
    html = compile_html(options)
    assert "T2 §1" in html  # el texto sigue ahí
    assert 'class="xref"' not in html  # pero sin enlace inline
    assert 'data-theme="light"' in html
