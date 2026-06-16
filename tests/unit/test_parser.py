"""Unitarias del parser: slugs, títulos, secciones y render del subset."""

from __future__ import annotations

import pytest

from mdbook.engine.parser import build_md, parse_document, render_document, slugify

pytestmark = pytest.mark.unit


def test_slugify() -> None:
    assert slugify("Tipos de datos") == "tipos-de-datos"
    assert slugify("  ¡Hola, Mundo!  ") == "hola-mundo"
    assert slugify("###") == "sec"


def test_titulo_desde_primer_h1() -> None:
    md = build_md()
    parsed = parse_document(md, "# Mi Documento\n\nTexto.\n\n## Sección", "doc1")
    assert parsed.title == "Mi Documento"


def test_sin_h1_titulo_none() -> None:
    md = build_md()
    parsed = parse_document(md, "## Solo H2\n\nTexto.", "doc1")
    assert parsed.title is None


def test_numeracion_de_secciones_lee_el_texto() -> None:
    md = build_md()
    src = "# T\n\n## 1. Intro\n\n### Sub sin numero\n\n## 2. Avanzado\n\n## 10. Salto"
    parsed = parse_document(md, src, "doc1")
    nums = {s.title: s.number for s in parsed.sections}
    # §N se lee del texto: no numeradas -> 0; "10." -> 10 (no posicional).
    assert nums == {
        "T": 0,
        "1. Intro": 1,
        "Sub sin numero": 0,
        "2. Avanzado": 2,
        "10. Salto": 10,
    }
    titulo = next(s for s in parsed.sections if s.is_title)
    assert titulo.title == "T"


def test_ids_unicos_en_encabezados_repetidos() -> None:
    md = build_md()
    parsed = parse_document(md, "# T\n\n## Notas\n\n## Notas", "doc1")
    ids = [s.id for s in parsed.sections]
    assert ids == ["doc1--t", "doc1--notas", "doc1--notas-2"]


def test_render_subset_completo() -> None:
    md = build_md()
    src = (
        "# Título\n\nPárrafo con **negrita**, *cursiva* e `código`.\n\n"
        "> Una cita\n\n- a\n- b\n\n| X | Y |\n| - | - |\n| 1 | 2 |\n\n"
        "```python\nprint('hi')\n```\n"
    )
    parsed = parse_document(md, src, "doc1")
    html = render_document(md, parsed, crossref_map=None)
    assert 'id="doc1--titulo"' in html
    assert "<strong>negrita</strong>" in html
    assert "<em>cursiva</em>" in html
    assert "<code>código</code>" in html
    assert "<blockquote>" in html
    assert "<table>" in html and "<td>1</td>" in html
    assert "<li>a</li>" in html


def test_render_bloque_codigo_con_lenguaje_y_copiar() -> None:
    md = build_md()
    parsed = parse_document(md, "# T\n\n```python\nx = 1\n```\n", "doc1")
    html = render_document(md, parsed, crossref_map=None)
    assert 'class="code-block"' in html
    assert 'class="language-python"' in html
    assert ">python</span>" in html
    assert "copy-btn" in html


def test_escape_html_en_codigo() -> None:
    md = build_md()
    parsed = parse_document(md, "# T\n\n```\n<script>\n```\n", "doc1")
    html = render_document(md, parsed, crossref_map=None)
    assert "&lt;script&gt;" in html
    assert "<script>" not in html
