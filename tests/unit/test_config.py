"""Unit tests for the Pydantic contract and file discovery."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from mdbook.config import BuildOptions, discover_markdown

pytestmark = pytest.mark.unit


def _md(tmp_path: Path, name: str = "a.md") -> Path:
    path = tmp_path / name
    path.write_text("# Title\n\nText.", encoding="utf-8")
    return path


def test_valid_options(tmp_path: Path) -> None:
    md = _md(tmp_path)
    opts = BuildOptions(
        title="  My book  ",
        inputs=[md],
        output=tmp_path / "out.html",
        theme="dark",
        cross_references=True,
    )
    assert opts.title == "My book"  # stripped
    assert opts.theme == "dark"
    assert opts.cross_references is True
    assert opts.inputs[0].is_absolute()  # resolved


def test_empty_title_fails(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        BuildOptions(title="   ", inputs=[_md(tmp_path)], output=tmp_path / "o.html")


def test_invalid_theme_fails(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        BuildOptions(
            title="x",
            inputs=[_md(tmp_path)],
            output=tmp_path / "o.html",
            theme="blue",  # type: ignore[arg-type]
        )


def test_missing_file_fails(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        BuildOptions(title="x", inputs=[tmp_path / "no.md"], output=tmp_path / "o.html")


def test_non_md_file_fails(tmp_path: Path) -> None:
    txt = tmp_path / "a.txt"
    txt.write_text("hi", encoding="utf-8")
    with pytest.raises(ValidationError):
        BuildOptions(title="x", inputs=[txt], output=tmp_path / "o.html")


def test_empty_input_list_fails(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        BuildOptions(title="x", inputs=[], output=tmp_path / "o.html")


def test_non_html_output_fails(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        BuildOptions(title="x", inputs=[_md(tmp_path)], output=tmp_path / "o.txt")


def test_discover_markdown_sorted(tmp_path: Path) -> None:
    (tmp_path / "b.md").write_text("# B", encoding="utf-8")
    (tmp_path / "a.md").write_text("# A", encoding="utf-8")
    (tmp_path / "note.txt").write_text("x", encoding="utf-8")
    found = discover_markdown(tmp_path)
    assert [p.name for p in found] == ["a.md", "b.md"]


def test_discover_markdown_invalid_folder(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        discover_markdown(tmp_path / "does-not-exist")
