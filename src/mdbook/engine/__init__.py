"""Motor puro de compilación de mdbook (sin GUI ni CLI).

Punto de entrada público: :func:`compile_book` (escribe el HTML) y
:func:`compile_html` (lo devuelve como cadena).
"""

from __future__ import annotations

from mdbook.engine.compiler import compile_book, compile_html

__all__ = ["compile_book", "compile_html"]
