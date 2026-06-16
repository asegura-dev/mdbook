"""Validation boundary: the Pydantic contract shared by the GUI and the CLI.

Both interfaces build a :class:`BuildOptions` and hand it to the engine. The
engine trusts it and does not validate again.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Theme = Literal["light", "dark"]
"""The only themes the contract accepts."""


class BuildOptions(BaseModel):
    """Validated options for one build.

    Frozen on purpose: once validated, nothing should mutate it before it
    reaches the engine.
    """

    model_config = ConfigDict(frozen=True)

    title: str = Field(min_length=1, description="Title of the work.")
    inputs: list[Path] = Field(min_length=1, description="Markdown files, in order.")
    output: Path = Field(description="Path of the HTML file to write (.html).")
    theme: Theme = Field(default="light", description="Default theme.")
    cross_references: bool = Field(
        default=False,
        description="When on, turns patterns like 'T1 §6' into internal links.",
    )

    @field_validator("title")
    @classmethod
    def _strip_title(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Title must not be empty.")
        return stripped

    @field_validator("inputs")
    @classmethod
    def _check_inputs(cls, value: list[Path]) -> list[Path]:
        if not value:
            raise ValueError("At least one .md file is required.")
        resolved: list[Path] = []
        for raw in value:
            path = raw.expanduser()
            if not path.exists():
                raise ValueError(f"File does not exist: {path}")
            if not path.is_file():
                raise ValueError(f"Not a file: {path}")
            if path.suffix.lower() != ".md":
                raise ValueError(f"Not a .md file: {path}")
            resolved.append(path.resolve())
        return resolved

    @field_validator("output")
    @classmethod
    def _check_output(cls, value: Path) -> Path:
        value = value.expanduser()
        if value.suffix.lower() != ".html":
            raise ValueError(f"Output must end in .html: {value}")
        return value


def discover_markdown(folder: Path) -> list[Path]:
    """Return the .md files in a folder, sorted by name.

    Helper for the interfaces (GUI/CLI) in "pick a folder" mode. Not part of
    the engine: it only finds files, it does not compile.
    """
    folder = folder.expanduser()
    if not folder.is_dir():
        raise ValueError(f"Not a folder: {folder}")
    return sorted(
        (p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".md"),
        key=lambda p: p.name.lower(),
    )
