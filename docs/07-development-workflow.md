# Development workflow

T6 §3 lists the checks a change has to pass. This document covers what enforces
them and how the repository is set up so the enforcement survives a clone.

## 1. The four gates

`ruff check`, `ruff format --check`, `mypy` (strict) and `pytest`. Nothing is
done while one of them is red. Run them with the project runner:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

`.github/workflows/ci.yml` runs the same four on every push and pull request to
`main` and `v2`. The list is intentionally identical to the one above — a CI
that checks something different from the documented workflow only teaches you
to ignore one of the two.

The workflow splits them in two jobs. Lint, format and types run once on Linux,
because their result cannot differ by platform. Tests run on Linux and Windows,
because the engine is pure Python but the product ships as a Windows `.exe`, and
path and encoding behaviour is exactly what differs. `uv sync --locked` makes a
job fail if `uv.lock` drifted from `pyproject.toml`, so the lock file stays
trustworthy instead of quietly rotting.

## 2. The pre-commit hook

Git has no undo for a blob that reaches a pushed history: removing one means
rewriting history and breaking every clone. So `.githooks/pre-commit` checks
before the commit exists. It reads the staged blobs rather than the working
tree — what it measures is exactly what would be recorded — and refuses any file
over 250 KB. The threshold sits above the largest tracked asset
(`docs/img/demo-dark.png`, ~197 KB) so screenshots still pass, and low enough to
catch a stray binary or dataset.

It also refuses paths that must never be committed (`.env`, `.venv/`,
`.claude/`, `data/`, `dist/`, `build/`) even when someone forces them past
`.gitignore` with `git add -f`. If a large asset genuinely belongs in the repo,
`git commit --no-verify` is the escape hatch.

The hook is versioned instead of living in `.git/hooks`, so it survives a clone
and can be reviewed in a diff. The cost is one command per clone:

```bash
git config core.hooksPath .githooks
```

`.gitattributes` pins `.githooks/*` to LF endings. This repository is developed
on Windows with `core.autocrlf=true`, and a hook checked out with CRLF fails on
its own shebang — which would disable the guard without saying so, the worst
failure mode a safety net can have.

## 3. Gotchas

Moving the repository to a different folder breaks the `.venv`. The console
scripts in `.venv/Scripts/` are trampolines with the original path baked in, so
after a move `mypy` and `pytest` die with `uv trampoline failed to canonicalize
script path` while `ruff` still works. It looks like a broken toolchain and
isn't: run `uv sync --reinstall`, or invoke the tools as modules
(`uv run python -m pytest`) to confirm the code itself is fine before
diagnosing further.

Work outside synced folders (OneDrive, Dropbox, Google Drive). The sync client
locks files under `.venv` and causes intermittent failures when `uv` installs or
reinstalls dependencies.
