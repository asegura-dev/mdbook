"""mdbook: compile Markdown files into a single HTML study file.

The package has two independent layers:

- ``mdbook.engine``: the pure compilation engine (no GUI, no CLI).
- ``mdbook.cli`` / ``mdbook.gui``: interfaces that build a validated
  :class:`mdbook.config.BuildOptions` and pass it to the engine.

The validation boundary is :mod:`mdbook.config`.
"""

from __future__ import annotations

__version__ = "1.0.0"
