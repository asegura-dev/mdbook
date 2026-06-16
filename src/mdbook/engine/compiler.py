"""Orquestación del motor: de una lista de .md validada al HTML final."""

from __future__ import annotations

from pathlib import Path

from mdbook.config import BuildOptions
from mdbook.engine.crossref import build_crossref_map
from mdbook.engine.model import Book, Document
from mdbook.engine.parser import ParsedDocument, build_md, parse_document, render_document
from mdbook.engine.renderer import build_html


def compile_html(options: BuildOptions) -> str:
    """Compila las opciones a la cadena HTML completa (sin escribir a disco)."""
    md = build_md()

    parsed_docs: list[ParsedDocument] = []
    titles: list[str] = []
    for index, path in enumerate(options.inputs, start=1):
        text = path.read_text(encoding="utf-8")
        parsed = parse_document(md, text, doc_id=f"doc{index}")
        parsed_docs.append(parsed)
        titles.append(parsed.title or path.stem)

    crossref_map = (
        build_crossref_map(p.sections for p in parsed_docs) if options.cross_references else None
    )

    documents: list[Document] = []
    for parsed, title in zip(parsed_docs, titles, strict=True):
        html = render_document(md, parsed, crossref_map)
        documents.append(Document(id=parsed.id, title=title, html=html, sections=parsed.sections))

    book = Book(title=options.title, theme=options.theme, documents=documents)
    return build_html(book)


def compile_book(options: BuildOptions) -> Path:
    """Compila y escribe el HTML en ``options.output``. Devuelve la ruta escrita."""
    html = compile_html(options)
    output = options.output.expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    return output
