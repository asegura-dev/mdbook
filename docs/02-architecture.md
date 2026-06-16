# Architecture

The point of the layout is that the compilation logic never imports an
interface. You can run and test the engine with no GUI and no CLI present.

## 1. The engine

`mdbook.engine` is the core. It holds the parser (`parser.py`, built on
markdown-it-py), the internal model (`model.py`: `Book`, `Document`, `Section`),
the cross-reference logic (`crossref.py`), the HTML assembler (`renderer.py`),
and the orchestration (`compiler.py`). The HTML template, CSS and JS live in
`engine/assets/` and get inlined into the output.

The engine depends on nothing from the interfaces. A test enforces this; see
T6 §3.

## 2. The validation boundary

`mdbook.config` defines `BuildOptions`, a frozen Pydantic model. It is the one
place where input is checked: the title isn't empty, every input path exists and
ends in `.md`, the output ends in `.html`, the theme is `light` or `dark`. Once
built, the engine trusts it and does not re-validate.

Both interfaces construct the same `BuildOptions` — see T5 §3.

## 3. The interfaces

There are two: a Typer CLI (`cli.py`) and a CustomTkinter GUI (`gui/app.py`).
Each collects input its own way and then builds a `BuildOptions` and calls the
engine. Neither contains parsing or rendering code. The GUI uses composition,
not subclassing, so the strict type checker stays clean.

## 4. Why the separation

Keeping the logic free of the interface means two things in practice. The engine
is testable without spawning a window, and a second interface (the CLI was added
after the GUI) costs almost nothing because the core doesn't change. When you
extend the project, keep this boundary intact — the rules are in T6 §1.
