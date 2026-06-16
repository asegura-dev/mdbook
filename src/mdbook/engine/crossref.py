"""Referencias cruzadas: detecta patrones tipo ``T1 §6`` y los enlaza.

Convención:

- ``T<n>`` = el documento número ``n`` según el orden de la obra (1-based).
- ``§<m>`` = la SECCIÓN NUMERADA ``m`` de ese documento, es decir el encabezado
  cuyo texto empieza con ``m.`` (p. ej. ``## 6. Validar la configuración`` es
  §6). Los subencabezados sin número no cuentan.

Si el destino no existe, el texto se deja igual.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from mdbook.engine.model import Section

CrossRefMap = dict[tuple[int, int], str]

# Acepta "T1 §6", "T1§6", "T1 § 6".
CROSSREF_RE = re.compile(r"\bT(\d+)\s*§\s*(\d+)")


def build_crossref_map(documents_sections: Iterable[list[Section]]) -> CrossRefMap:
    """Construye el mapa (documento, sección) -> id de ancla.

    ``documents_sections`` debe venir en el orden de la obra.
    """
    mapping: CrossRefMap = {}
    for doc_index, sections in enumerate(documents_sections, start=1):
        for section in sections:
            key = (doc_index, section.number)
            # Si una sección numerada se repite, gana la primera aparición.
            if section.number > 0 and key not in mapping:
                mapping[key] = section.id
    return mapping


def apply_crossref(escaped_text: str, mapping: CrossRefMap) -> str:
    """Reemplaza las referencias por enlaces internos sobre texto ya escapado."""

    def repl(match: re.Match[str]) -> str:
        doc_n = int(match.group(1))
        sec_n = int(match.group(2))
        target = mapping.get((doc_n, sec_n))
        if target is None:
            return match.group(0)
        return f'<a class="xref" href="#{target}">{match.group(0)}</a>'

    return CROSSREF_RE.sub(repl, escaped_text)
