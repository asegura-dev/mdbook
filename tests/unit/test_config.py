"""Unitarias del contrato Pydantic y el descubrimiento de archivos."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from mdbook.config import BuildOptions, discover_markdown

pytestmark = pytest.mark.unit


def _md(tmp_path: Path, name: str = "a.md") -> Path:
    path = tmp_path / name
    path.write_text("# Título\n\nTexto.", encoding="utf-8")
    return path


def test_opciones_validas(tmp_path: Path) -> None:
    md = _md(tmp_path)
    opts = BuildOptions(
        title="  Mi obra  ",
        inputs=[md],
        output=tmp_path / "out.html",
        theme="oscuro",
        cross_references=True,
    )
    assert opts.title == "Mi obra"  # se recorta
    assert opts.theme == "oscuro"
    assert opts.cross_references is True
    assert opts.inputs[0].is_absolute()  # se resuelve


def test_titulo_vacio_falla(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        BuildOptions(title="   ", inputs=[_md(tmp_path)], output=tmp_path / "o.html")


def test_tema_invalido_falla(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        BuildOptions(
            title="x",
            inputs=[_md(tmp_path)],
            output=tmp_path / "o.html",
            theme="dark",  # type: ignore[arg-type]
        )


def test_archivo_inexistente_falla(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        BuildOptions(title="x", inputs=[tmp_path / "no.md"], output=tmp_path / "o.html")


def test_archivo_no_md_falla(tmp_path: Path) -> None:
    txt = tmp_path / "a.txt"
    txt.write_text("hola", encoding="utf-8")
    with pytest.raises(ValidationError):
        BuildOptions(title="x", inputs=[txt], output=tmp_path / "o.html")


def test_lista_vacia_falla(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        BuildOptions(title="x", inputs=[], output=tmp_path / "o.html")


def test_salida_no_html_falla(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        BuildOptions(title="x", inputs=[_md(tmp_path)], output=tmp_path / "o.txt")


def test_discover_markdown_ordenado(tmp_path: Path) -> None:
    (tmp_path / "b.md").write_text("# B", encoding="utf-8")
    (tmp_path / "a.md").write_text("# A", encoding="utf-8")
    (tmp_path / "nota.txt").write_text("x", encoding="utf-8")
    encontrados = discover_markdown(tmp_path)
    assert [p.name for p in encontrados] == ["a.md", "b.md"]


def test_discover_markdown_carpeta_invalida(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        discover_markdown(tmp_path / "no-existe")
