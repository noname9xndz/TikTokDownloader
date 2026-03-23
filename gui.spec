# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for DouK-Downloader GUI edition.

Build:
    pip install pyinstaller
    pyinstaller gui.spec

Output:
    dist/DouK-Downloader-GUI/DouK-Downloader-GUI.exe
"""

import os
import sys
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────
ROOT = Path(SPECPATH)  # noqa: F821  (SPECPATH injected by PyInstaller)
SRC = ROOT / "src"

# ── Hidden imports ───────────────────────────────────────────────────
#  Modules that PyInstaller cannot auto-detect via static analysis.
hidden_imports = [
    # GUI
    "customtkinter",
    "PIL",
    "PIL._tkinter_finder",
    # Backend
    "aiofiles",
    "aiosqlite",
    "emoji",
    "gmssl",
    "httpx",
    "lxml",
    "openpyxl",
    "pydantic",
    "pyperclip",
    "rookiepy",
    # stdlib async
    "asyncio",
    "sqlite3",
    # project internals (dynamic imports in backend)
    "src.application",
    "src.config",
    "src.custom",
    "src.encrypt",
    "src.extract",
    "src.interface",
    "src.link",
    "src.manager",
    "src.module",
    "src.record",
    "src.storage",
    "src.tools",
    "src.translation",
]

# ── Data files ───────────────────────────────────────────────────────
#  (source_path, dest_folder_inside_bundle)
datas = [
    (str(ROOT / "static" / "images"), os.path.join("static", "images")),
    (str(ROOT / "static" / "js"), os.path.join("static", "js")),
]

# ── CustomTkinter assets (themes, etc.) ──────────────────────────────
import customtkinter
ctk_path = Path(customtkinter.__file__).parent
datas.append((str(ctk_path), "customtkinter"))

# ── Analysis ─────────────────────────────────────────────────────────
a = Analysis(
    [str(ROOT / "gui_launcher.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter.test",
        "unittest",
        "test",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# ── Executable ───────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DouK-Downloader-GUI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                 # windowed — no CMD window
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=str(ROOT / "static" / "images" / "DouK-Downloader.ico"),
)

# ── Collect (one-dir mode) ───────────────────────────────────────────
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="DouK-Downloader-GUI",
)
