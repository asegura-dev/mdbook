"""Frontera de validación: el contrato Pydantic que comparten GUI y CLI.

Tanto la interfaz gráfica como la línea de comandos construyen un
:class:`BuildOptions` y se lo pasan al motor. El motor confía en él y no
vuelve a validar.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Theme = Literal["claro", "oscuro"]
"""Únicos temas admitidos por el contrato."""


class BuildOptions(BaseModel):
    """Opciones validadas de una compilación.

    Es inmutable a propósito: una vez validada, no debe mutarse antes de
    llegar al motor.
    """

    model_config = ConfigDict(frozen=True)

    title: str = Field(min_length=1, description="Título de la obra.")
    inputs: list[Path] = Field(min_length=1, description="Archivos .md en orden.")
    output: Path = Field(description="Ruta del HTML a generar (.html).")
    theme: Theme = Field(default="claro", description="Tema por defecto.")
    cross_references: bool = Field(
        default=False,
        description="Si está activo, convierte patrones tipo 'T1 §6' en enlaces internos.",
    )

    @field_validator("title")
    @classmethod
    def _title_no_vacio(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("El título no puede estar vacío.")
        return stripped

    @field_validator("inputs")
    @classmethod
    def _inputs_validos(cls, value: list[Path]) -> list[Path]:
        if not value:
            raise ValueError("Se requiere al menos un archivo .md.")
        resueltos: list[Path] = []
        for ruta in value:
            ruta = ruta.expanduser()
            if not ruta.exists():
                raise ValueError(f"El archivo no existe: {ruta}")
            if not ruta.is_file():
                raise ValueError(f"No es un archivo: {ruta}")
            if ruta.suffix.lower() != ".md":
                raise ValueError(f"No es un archivo .md: {ruta}")
            resueltos.append(ruta.resolve())
        return resueltos

    @field_validator("output")
    @classmethod
    def _output_valido(cls, value: Path) -> Path:
        value = value.expanduser()
        if value.suffix.lower() != ".html":
            raise ValueError(f"La salida debe terminar en .html: {value}")
        return value


def discover_markdown(folder: Path) -> list[Path]:
    """Devuelve los .md de una carpeta, ordenados por nombre.

    Helper de las interfaces (GUI/CLI) para el modo "elegir carpeta". No es
    parte del motor: solo descubre archivos, no compila.
    """
    folder = folder.expanduser()
    if not folder.is_dir():
        raise ValueError(f"No es una carpeta: {folder}")
    return sorted(
        (p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".md"),
        key=lambda p: p.name.lower(),
    )
