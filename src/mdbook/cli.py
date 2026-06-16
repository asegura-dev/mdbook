"""Command-line interface (Typer + Rich) over the same engine.

The GUI and the CLI are two interfaces over one core: both build a validated
:class:`mdbook.config.BuildOptions` and call the engine.
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
    help="Compile Markdown files into a single HTML study file.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)


@app.callback()
def _root() -> None:
    """mdbook: Markdown to a single HTML study file (navigable, searchable, themed)."""


@app.command()
def build(
    title: Annotated[str, typer.Option("--title", "-t", help="Title of the work.")],
    input_dir: Annotated[
        Path | None,
        typer.Option("--input", "-i", help="Folder: take every .md (alphabetical order)."),
    ] = None,
    files: Annotated[
        list[Path] | None,
        typer.Option("--file", "-f", help="A single .md file (repeatable; sets the order)."),
    ] = None,
    output: Annotated[Path, typer.Option("--output", "-o", help="Output HTML path.")] = Path(
        "mdbook.html"
    ),
    theme: Annotated[str, typer.Option("--theme", help="Default theme: light | dark.")] = "light",
    cross_references: Annotated[
        bool,
        typer.Option("--cross-refs/--no-cross-refs", help="Enable 'T1 §6' references."),
    ] = False,
) -> None:
    """Compile one or more .md files into a self-contained HTML file."""
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
        err_console.print("[bold red]Error:[/] pass a folder with --input or files with --file.")
        raise typer.Exit(code=1)

    try:
        options = BuildOptions(
            title=title,
            inputs=inputs,
            output=output,
            theme=theme,  # type: ignore[arg-type]  # validated by Pydantic
            cross_references=cross_references,
        )
    except ValidationError as exc:
        err_console.print("[bold red]Invalid options:[/]")
        for error in exc.errors():
            loc = ".".join(str(p) for p in error["loc"])
            err_console.print(f"  • [yellow]{loc}[/]: {error['msg']}")
        raise typer.Exit(code=1) from exc

    written = compile_book(options)
    console.print(
        f"[bold green]OK[/] Compiled [bold]{len(options.inputs)}[/] document(s) -> "
        f"[cyan]{written}[/]"
    )


def main() -> None:
    """Alternate entry point (not used by the script; handy for tests)."""
    app()


if __name__ == "__main__":
    app()
