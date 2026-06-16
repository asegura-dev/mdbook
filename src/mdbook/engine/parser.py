"""Parseo de Markdown (subset) a tokens, con metadatos de navegación.

Usa markdown-it-py. El flujo es de dos pasadas para que las referencias
cruzadas puedan apuntar entre documentos:

1. :func:`parse_document` extrae título y secciones y fija los ``id`` en los
   encabezados (sobre los tokens).
2. :func:`render_document` vuelca esos tokens a HTML, opcionalmente aplicando
   el mapa de referencias cruzadas.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, cast

from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml
from markdown_it.token import Token

from mdbook.engine.crossref import CrossRefMap, apply_crossref
from mdbook.engine.model import Section

_NON_WORD = re.compile(r"[^\w\s-]", re.UNICODE)
_SPACES = re.compile(r"[\s_-]+", re.UNICODE)
# Sección numerada: el texto del encabezado empieza con "N." (p. ej. "6. Validar").
_SECTION_NUM = re.compile(r"^\s*(\d+)\.")


@dataclass
class ParsedDocument:
    """Resultado de la pasada 1: tokens listos para render + metadatos."""

    id: str
    title: str | None
    tokens: list[Token]
    sections: list[Section] = field(default_factory=list)


def slugify(text: str) -> str:
    """Convierte un texto en un slug ASCII apto para ``id``/fragmento.

    Quita acentos (``Sección`` -> ``seccion``) para que las anclas sean
    portables en URLs.
    """
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = _NON_WORD.sub("", text.strip().lower())
    text = _SPACES.sub("-", text).strip("-")
    return text or "sec"


def build_md() -> MarkdownIt:
    """Crea el parser con el subset soportado y las reglas de render propias."""
    md = MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False})
    md.enable("table")
    md.add_render_rule("fence", _render_fence)
    md.add_render_rule("code_block", _render_code_block)
    md.add_render_rule("text", _render_text)
    return md


def _plain_text(inline: Token) -> str:
    """Texto plano de un token inline (para títulos de secciones)."""
    if not inline.children:
        return inline.content.strip()
    parts: list[str] = []
    for child in inline.children:
        if child.type in ("text", "code_inline"):
            parts.append(child.content)
        elif child.type in ("softbreak", "hardbreak"):
            parts.append(" ")
    return "".join(parts).strip()


def parse_document(md: MarkdownIt, text: str, doc_id: str) -> ParsedDocument:
    """Pasada 1: parsea, asigna ids a encabezados y recolecta secciones."""
    tokens = md.parse(text)
    sections: list[Section] = []
    title: str | None = None
    seen: dict[str, int] = {}

    for i, tok in enumerate(tokens):
        if tok.type != "heading_open":
            continue
        level = int(tok.tag[1])
        heading_text = _plain_text(tokens[i + 1])
        base = slugify(heading_text)
        n = seen.get(base, 0)
        seen[base] = n + 1
        unique = base if n == 0 else f"{base}-{n + 1}"
        section_id = f"{doc_id}--{unique}"
        tok.attrSet("id", section_id)

        is_title = title is None and level == 1
        if is_title:
            title = heading_text
            number = 0
        else:
            match = _SECTION_NUM.match(heading_text)
            number = int(match.group(1)) if match else 0
        sections.append(
            Section(
                id=section_id,
                level=level,
                title=heading_text,
                number=number,
                is_title=is_title,
            )
        )

    return ParsedDocument(id=doc_id, title=title, tokens=tokens, sections=sections)


def render_document(
    md: MarkdownIt, parsed: ParsedDocument, crossref_map: CrossRefMap | None
) -> str:
    """Pasada 2: vuelca los tokens a HTML."""
    env: dict[str, Any] = {}
    if crossref_map:
        env["crossref_map"] = crossref_map
    return cast(str, md.renderer.render(parsed.tokens, md.options, env))


# --- Reglas de render personalizadas -------------------------------------
# markdown-it-py las invoca con (renderer, tokens, idx, options, env).


def _render_fence(
    renderer: Any, tokens: list[Token], idx: int, options: Any, env: dict[str, Any]
) -> str:
    token = tokens[idx]
    info = token.info.strip()
    lang = info.split(maxsplit=1)[0] if info else ""
    code = escapeHtml(token.content)
    lang_attr = f' class="language-{escapeHtml(lang)}"' if lang else ""
    label = escapeHtml(lang) if lang else "texto"
    return (
        '<div class="code-block">'
        f'<div class="code-head"><span class="code-lang">{label}</span>'
        '<button class="copy-btn" type="button" aria-label="Copiar código">Copiar</button>'
        "</div>"
        f"<pre><code{lang_attr}>{code}</code></pre>"
        "</div>\n"
    )


def _render_code_block(
    renderer: Any, tokens: list[Token], idx: int, options: Any, env: dict[str, Any]
) -> str:
    # Bloques indentados (4 espacios): mismo envoltorio, sin lenguaje.
    code = escapeHtml(tokens[idx].content)
    return (
        '<div class="code-block">'
        '<div class="code-head"><span class="code-lang">texto</span>'
        '<button class="copy-btn" type="button" aria-label="Copiar código">Copiar</button>'
        "</div>"
        f"<pre><code>{code}</code></pre>"
        "</div>\n"
    )


def _render_text(
    renderer: Any, tokens: list[Token], idx: int, options: Any, env: dict[str, Any]
) -> str:
    content = escapeHtml(tokens[idx].content)
    crossref_map: CrossRefMap | None = env.get("crossref_map")
    if crossref_map:
        return apply_crossref(content, crossref_map)
    return content
