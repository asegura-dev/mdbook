# -*- mode: python ; coding: utf-8 -*-
"""Spec de PyInstaller: empaqueta la GUI de mdbook en un único .exe.

Incluye los assets embebidos del motor (template.html, style.css, app.js) y los
datos de customtkinter. Construir desde la raíz del proyecto:

    uv run pyinstaller packaging/mdbook.spec
"""

import os

from PyInstaller.utils.hooks import collect_data_files

ROOT = os.path.dirname(SPECPATH)  # noqa: F821 - SPECPATH lo inyecta PyInstaller
ASSETS = os.path.join(ROOT, "src", "mdbook", "engine", "assets")

datas = [
    (os.path.join(ASSETS, "template.html"), "mdbook/engine/assets"),
    (os.path.join(ASSETS, "style.css"), "mdbook/engine/assets"),
    (os.path.join(ASSETS, "app.js"), "mdbook/engine/assets"),
]
datas += collect_data_files("customtkinter")

a = Analysis(
    [os.path.join(SPECPATH, "launch_gui.py")],  # noqa: F821
    pathex=[os.path.join(ROOT, "src")],
    binaries=[],
    datas=datas,
    hiddenimports=["customtkinter"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="mdbook",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
