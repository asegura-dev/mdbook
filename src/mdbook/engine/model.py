"""Engine's internal model: the intermediate representation between parsing
and HTML.

Flat structures with no external dependencies. They know nothing about Pydantic
or the interfaces.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Section:
    """A heading inside a document.

    ``number`` is the numbered-section number read from the heading text
    itself: the one that starts with ``N.`` (e.g. ``## 6. Validate`` -> 6). It
    is 0 for the title and for unnumbered headings. Cross-references like
    ``T1 §6`` (section 6 of document 1) rely on it.
    """

    id: str
    level: int
    title: str
    number: int
    is_title: bool


@dataclass
class Document:
    """A converted .md file: its title, its HTML and its list of sections."""

    id: str
    title: str
    html: str
    sections: list[Section] = field(default_factory=list)


@dataclass
class Book:
    """The whole work, ready to pour into the HTML template."""

    title: str
    theme: str
    documents: list[Document] = field(default_factory=list)
