# Extending mdbook

The codebase is small, so most changes land in one or two files. The rules below
keep it from rotting.

## 1. Add a Markdown feature

Rendering goes through markdown-it-py. To change how something renders, add or
override a render rule in `parser.py` (that's how fenced code blocks get their
copy button). To enable a CommonMark feature that's off, enable it on the
`MarkdownIt` instance in `build_md`. Keep all of this inside `engine/` — the
boundary from T2 §4 says the interfaces never see tokens.

## 2. Add a build option

Add the field to `BuildOptions` in `config.py` with a validator if it needs one.
Then thread it through: read it in the engine where it applies, expose it as a
Typer option in the CLI, and add the matching widget in the GUI. Because both
interfaces build the same contract, you can't forget one without the type
checker or a test noticing.

## 3. Tests to keep green

Run `pytest`, `ruff check`, `ruff format --check` and `mypy` before you call a
change done. Two tests matter most here. `test_architecture.py` fails if the
engine imports an interface or if the GUI reaches into parsing or rendering —
don't work around it, fix the import. The smoke test compiles the sample files
end to end; if you change the output structure, update its assertions in the
same commit. When you fix a bug, add a regression test next to it.
