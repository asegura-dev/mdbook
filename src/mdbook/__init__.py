"""mdbook: compila archivos Markdown en un único HTML de estudio.

El paquete se divide en dos capas independientes:

- ``mdbook.engine``: el MOTOR puro de compilación (sin GUI ni CLI).
- ``mdbook.cli`` / ``mdbook.gui``: interfaces que construyen un
  :class:`mdbook.config.BuildOptions` validado y lo pasan al motor.

La frontera de validación es :mod:`mdbook.config`.
"""

from __future__ import annotations

__version__ = "0.1.0"
