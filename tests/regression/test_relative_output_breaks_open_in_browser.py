"""A relative --output used to come back relative, and Path.as_uri() rejects it.

The symptom was silent. Compiling reported success, and the GUI's "Open in
browser" raised inside a Tk callback: the traceback went to stderr, which the
packaged app does not have, so the button simply did nothing.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from mdbook.config import BuildOptions
from mdbook.engine import compile_book

pytestmark = pytest.mark.regression


def _md(folder: Path) -> Path:
    path = folder / "a.md"
    path.write_text("# Title\n\nText.", encoding="utf-8")
    return path


def test_relative_output_is_resolved_by_the_contract(tmp_path: Path) -> None:
    options = BuildOptions(title="x", inputs=[_md(tmp_path)], output=Path("book.html"))
    assert options.output.is_absolute()


def test_written_path_can_become_a_file_uri(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    options = BuildOptions(title="x", inputs=[_md(tmp_path)], output=Path("book.html"))
    written = compile_book(options)

    assert written.is_absolute()
    assert written.exists()
    # The call that used to raise ValueError: relative path can't be expressed
    # as a file URI.
    assert written.as_uri().startswith("file://")


def test_output_lands_where_the_relative_path_pointed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Resolving must not move the file: it is still written next to the cwd the
    # user was in, only expressed absolutely.
    monkeypatch.chdir(tmp_path)
    options = BuildOptions(title="x", inputs=[_md(tmp_path)], output=Path("sub") / "book.html")
    written = compile_book(options)

    assert written == (Path(os.getcwd()) / "sub" / "book.html").resolve()
    assert written.read_text(encoding="utf-8").startswith("<!DOCTYPE html>")
