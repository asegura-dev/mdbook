"""Interfaz gráfica (CustomTkinter) de mdbook.

Es una interfaz delgada: construye un :class:`mdbook.config.BuildOptions`
validado y llama al motor. No contiene lógica de parseo ni de generación de
HTML.
"""

from __future__ import annotations
