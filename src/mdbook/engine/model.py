"""Modelo interno del motor: representación intermedia entre el parseo y el HTML.

Son estructuras planas y sin dependencias externas. No conocen Pydantic ni
las interfaces.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Section:
    """Un encabezado dentro de un documento.

    ``number`` es el número de SECCIÓN NUMERADA leído del propio texto del
    encabezado: el que empieza con ``N.`` (p. ej. ``## 6. Validar`` → 6). Vale
    0 para el título y para los encabezados no numerados. Se usa para las
    referencias cruzadas tipo ``T1 §6`` (la sección 6 del documento 1).
    """

    id: str
    level: int
    title: str
    number: int
    is_title: bool


@dataclass
class Document:
    """Un .md ya convertido: su título, su HTML y su lista de secciones."""

    id: str
    title: str
    html: str
    sections: list[Section] = field(default_factory=list)


@dataclass
class Book:
    """La obra completa lista para volcarse a la plantilla HTML."""

    title: str
    theme: str
    documents: list[Document] = field(default_factory=list)
