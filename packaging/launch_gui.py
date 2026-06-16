"""Punto de entrada del ejecutable empaquetado (PyInstaller).

Lanza la GUI. Con ``--selftest`` ejecuta una verificación sin interfaz: compila
un Markdown mínimo (lo que prueba que los assets embebidos se cargan desde el
bundle) y abre el navegador (lo que prueba ``webbrowser`` desde el .exe),
dejando el resultado en ``%TEMP%/mdbook_selftest.log``.
"""

from __future__ import annotations

import sys


def _selftest() -> int:
    import tempfile
    import traceback
    import webbrowser
    from pathlib import Path

    log = Path(tempfile.gettempdir()) / "mdbook_selftest.log"
    try:
        from mdbook.config import BuildOptions
        from mdbook.engine import compile_book

        work = Path(tempfile.mkdtemp(prefix="mdbook_selftest_"))
        md = work / "demo.md"
        md.write_text(
            "# Demo\n\n## 1. Intro\n\nContenido de prueba; ver T1 §1.\n",
            encoding="utf-8",
        )
        out = work / "demo.html"
        written = compile_book(
            BuildOptions(
                title="Selftest",
                inputs=[md],
                output=out,
                theme="oscuro",
                cross_references=True,
            )
        )
        html = written.read_text(encoding="utf-8")
        ok_assets = "<style>" in html and 'data-theme="dark"' in html
        ok_browser = bool(webbrowser.open(written.as_uri()))
        log.write_text(
            f"compile={ok_assets} browser={ok_browser} output={written}\n",
            encoding="utf-8",
        )
        return 0 if (ok_assets and ok_browser) else 1
    except Exception:
        log.write_text("ERROR\n" + traceback.format_exc(), encoding="utf-8")
        return 2


def main() -> None:
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    from mdbook.gui.app import main as gui_main

    gui_main()


if __name__ == "__main__":
    main()
