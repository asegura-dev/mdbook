"""Interfaz de línea de comandos (Typer + Rich) sobre el mismo motor.

GUI y CLI son dos interfaces sobre el mismo núcleo: ambas construyen un
:class:`mdbook.config.BuildOptions` validado y llaman al motor.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console

from mdbook.config import BuildOptions, discover_markdown
from mdbook.engine import compile_book

app = typer.Typer(
    help="Compila archivos Markdown en un único HTML de estudio.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)


@app.callback()
def _root() -> None:
    """mdbook: Markdown → un HTML de estudio (navegable, con búsqueda y temas)."""


@app.command()
def build(
    title: Annotated[str, typer.Option("--title", "-t", help="Título de la obra.")],
    input_dir: Annotated[
        Path | None,
        typer.Option("--input", "-i", help="Carpeta: toma todos los .md (orden alfabético)."),
    ] = None,
    files: Annotated[
        list[Path] | None,
        typer.Option("--file", "-f", help="Archivo .md suelto (repetible, define el orden)."),
    ] = None,
    output: Annotated[Path, typer.Option("--output", "-o", help="Ruta del HTML de salida.")] = Path(
        "mdbook.html"
    ),
    theme: Annotated[str, typer.Option("--theme", help="Tema por defecto: claro | oscuro.")] = (
        "claro"
    ),
    cross_references: Annotated[
        bool,
        typer.Option("--cross-refs/--no-cross-refs", help="Activa referencias tipo 'T1 §6'."),
    ] = False,
) -> None:
    """Compila uno o varios .md a un HTML autocontenido."""
    inputs: list[Path] = []
    if input_dir is not None:
        try:
            inputs.extend(discover_markdown(input_dir))
        except ValueError as exc:
            err_console.print(f"[bold red]Error:[/] {exc}")
            raise typer.Exit(code=1) from exc
    if files:
        inputs.extend(files)

    if not inputs:
        err_console.print(
            "[bold red]Error:[/] indica una carpeta con --input o archivos con --file."
        )
        raise typer.Exit(code=1)

    try:
        options = BuildOptions(
            title=title,
            inputs=inputs,
            output=output,
            theme=theme,  # type: ignore[arg-type]  # validado por Pydantic
            cross_references=cross_references,
        )
    except ValidationError as exc:
        err_console.print("[bold red]Opciones inválidas:[/]")
        for error in exc.errors():
            loc = ".".join(str(p) for p in error["loc"])
            err_console.print(f"  • [yellow]{loc}[/]: {error['msg']}")
        raise typer.Exit(code=1) from exc

    written = compile_book(options)
    console.print(
        f"[bold green]OK[/] Compilados [bold]{len(options.inputs)}[/] documento(s) -> "
        f"[cyan]{written}[/]"
    )


def main() -> None:
    """Entry point alternativo (no usado por el script, útil para pruebas)."""
    app()


if __name__ == "__main__":
    app()
