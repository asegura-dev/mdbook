"""Pure compilation engine for mdbook (no GUI, no CLI).

Public entry points: :func:`compile_book` (writes the HTML) and
:func:`compile_html` (returns it as a string).
"""

from __future__ import annotations

from mdbook.engine.compiler import compile_book, compile_html

__all__ = ["compile_book", "compile_html"]
