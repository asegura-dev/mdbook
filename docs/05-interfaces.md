# Interfaces

Two front ends sit on the engine. They differ only in how they collect input;
both end at the same `BuildOptions` and the same `compile_book` call.

## 1. The CLI

`mdbook build` is a Typer command. You pass a folder with `--input` (it takes
every `.md` in alphabetical order) or individual files with repeated `--file`
flags (the flag order sets the document order). `--title`, `--theme`,
`--cross-refs` and `--output` cover the rest. Errors from the contract are
printed as a readable list via Rich, and the command exits non-zero.

## 2. The GUI

`mdbook-gui` opens the desktop window. It does the same job with buttons: add a
folder or files, reorder the list with Up/Down (that order is the document
order), type a title, pick the theme, toggle cross-references, then Compile.
"Open in browser" hands the generated file to the system browser rather than
rendering it in-window — that's more robust and portable.

## 3. The shared contract

Both interfaces build the `BuildOptions` described in T2 §2 and hand it over.
Validation lives there, once, so the two front ends can't drift apart on what
counts as valid input. Adding a third interface would follow the same shape:
gather input, build the contract, call the engine.
