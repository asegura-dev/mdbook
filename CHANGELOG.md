# Changelog

Notable changes to mdbook, newest first. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[semantic versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Work on v2, on the `v2` branch.

### Added

- Reader highlights and notes, stored in the browser and never leaving the
  device. Three colours, notes on a passage or on a whole section, a review
  panel listing everything in reading order, and export to Markdown by clipboard
  or download. Highlights print as coloured underlines and the panel prints as
  an appendix, so a printed chapter carries the reader's notes with it.
- Annotations are anchored by text, not by position, so they survive the book
  being recompiled: edits elsewhere, chapters reordered, sections renumbered.
  Editing the highlighted words themselves orphans the annotation instead of
  relocating it — a wrong anchor corrupts a review silently, an orphan does not
  — and orphans are kept, grouped separately, and reattach on their own if the
  text returns. The model and an acceptance procedure are in T3 §6.
- `tests/js`, run under Node's built-in runner from pytest, covering the anchor
  resolver — the one part where a bug loses a reader's work without saying so.
  Node is a development tool only, and the suite skips these without it.
- PDF export: a "PDF" button in the top bar prints the page through the
  browser's own pipeline, with `@media print` rules doing the work — white page
  and serif type whatever theme is on screen, screen chrome hidden, a page per
  document, code blocks and quotes kept whole, table headers repeated across
  pages, and external links printing their URL. No PDF library, no server, and
  the output stays one self-contained file. Its limits are documented in T3 §5
  and in the README: no page numbers of ours, breaks are requests rather than
  guarantees, and results differ between browsers.
- Two themes, `sepia` and `serif`, next to the existing `light` and `dark`.
  Sepia is warm paper for long reading; serif also swaps the typeface for a
  system serif stack and loosens the leading. Both use system fonts only — a
  webfont would need a network request and break the self-contained output.
- `THEMES` in `mdbook.config`, the theme set derived from the `Theme` literal
  with `typing.get_args`. The GUI dropdown, the CLI help and the rendered picker
  all read from it, so adding a theme is one edit instead of four.
- `tests/unit/test_themes.py`: every declared theme must override the full set
  of colour tokens, and the stylesheet must not reference anything external.
- Continuous integration (`.github/workflows/ci.yml`): ruff, `ruff format
  --check`, strict mypy and pytest on every push and pull request to `main` and
  `v2`. Lint and types run once on Linux; tests run on a Linux and Windows
  matrix, because the product ships as a Windows executable. `uv sync --locked`
  fails the build if `uv.lock` drifted from `pyproject.toml`.
- Versioned pre-commit hook (`.githooks/pre-commit`) that refuses staged files
  over 250 KB and paths that must never be committed (`.env`, `.venv/`,
  `.claude/`, `data/`, `dist/`, `build/`). Enable it per clone with `git config
  core.hooksPath .githooks`; bypass a legitimate large asset with
  `git commit --no-verify`.
- `.gitattributes`, pinning `.githooks/*` to LF so the hook survives checkout on
  Windows with `core.autocrlf=true` instead of failing silently on its shebang.
- `docs/07-development-workflow.md`: the gates, what enforces them, the setup a
  fresh clone needs, and the gotchas (moved repository breaking the `.venv`
  console scripts, synced folders locking `.venv`).
- T7 §3, on the Windows executable: how to build it, and the fact that the
  engine's assets are frozen into the binary — so a stale executable keeps
  producing the previous HTML without warning.
- This changelog.

### Fixed

- A relative `--output` came back relative, and `Path.as_uri()` rejects those,
  so the GUI's "Open in browser" raised inside a Tk callback and — with no
  console in the packaged app — did nothing at all, after reporting a
  successful build. The contract now resolves the output path as it already
  resolved the inputs. `open_browser` also reports failures in a dialog and no
  longer ignores `webbrowser.open()` returning `False`.
- Repeated headings could share an `id`: de-duplication counted occurrences and
  appended the count, and the name it produced could be another heading's real
  slug ("Intro", "Intro", "Intro 2" all landed on `intro-2`). A table-of-
  contents link then jumped to the wrong heading. Candidates are now checked
  against the ids actually taken; existing anchors are unchanged.
- A cross-reference inside a link produced nested `<a>` elements, which HTML
  forbids, breaking the author's own link. Inside a link the reference is left
  as plain text, exactly as an unresolvable reference already was.
- The GUI kept "Open in browser" enabled after the inputs changed, so it opened
  the previous build; accepted files that were not `.md` and only rejected them
  at compile time; and hard-coded `"light"` as its initial theme instead of
  reading `THEMES`. The CLI answered an empty folder by telling you to pass a
  folder; it now says the folder has no `.md` files.

### Changed

- The theme control in the generated HTML is a `<select>` instead of a button
  that toggled between two values. A two-state toggle does not survive a third
  theme. The picker is rendered server-side, one option per theme, so the page
  script holds no copy of the theme list; that removed the sun/moon glyph
  branch and left `app.js` shorter. A theme restored from `localStorage` now
  syncs the control, and a stale stored theme falls back to the default instead
  of leaving the page on an undefined palette.
- The font stack is the `--font-body` token rather than a hard-coded rule, so a
  theme can change the typeface without duplicating the typography rules.

## [1.0.0] - 2026-06-16

First public release: the engine, both interfaces, packaging and documentation.

### Added

- Compilation engine (`mdbook.engine`): markdown-it-py parser with a fixed
  Markdown subset, internal model (`Book`, `Document`, `Section`), HTML renderer
  and orchestration. Output is self-contained — CSS and JS inlined, no external
  requests.
- Validation boundary (`mdbook.config`): frozen Pydantic `BuildOptions`, the one
  place input is checked. The engine trusts it and does not re-validate.
- Cross-references: `T1 §3` becomes an internal link to numbered section 3 of
  document 1; unresolved references are left as plain text.
- Desktop app (`mdbook-gui`, CustomTkinter): add files or a folder, reorder,
  title, theme, cross-reference toggle, compile and open in the browser.
- Command line (`mdbook build`, Typer + Rich) over the same engine.
- Generated HTML features: cover, table of contents, sidebar, instant search
  with highlighting, light/dark theme that remembers the choice, and a copy
  button with a language label on every code block.
- Windows executable via PyInstaller (`packaging/mdbook.spec`): one window, no
  console, assets embedded, no Python needed to run it.
- Architecture guard (`tests/unit/test_architecture.py`): fails if the engine
  imports an interface or if the GUI reaches into parsing or rendering.
- Project manual (`docs/*.md`), compiled with mdbook itself into
  `docs/manual.html`, and a five-part clean-architecture guide in `examples/`
  that doubles as the smoke-test input and the published demo.
- MIT license.

### Changed

- The whole project was translated from Spanish to English — docstrings,
  comments, identifiers, user-facing strings and metadata. Theme values became
  `light`/`dark`, which removed the redundant `_THEME_TO_HTML` mapping.

[Unreleased]: https://github.com/asegura-dev/mdbook/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/asegura-dev/mdbook/releases/tag/v1.0.0
