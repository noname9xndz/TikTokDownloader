"""Smoke tests for the GUI edition.

These tests verify that all modules are importable and structurally
sound WITHOUT needing a display server (no Tk mainloop).

Run:
    pytest tests/test_gui_smoke.py -v
"""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

import pytest

# ── Path to the gui_edition package ──────────────────────────────────
_GUI_PKG = Path(__file__).resolve().parents[1] / "src" / "gui_edition"

# Modules that can be imported without the full backend dependency chain
_STANDALONE_MODULES = [
    "src.gui_edition.async_handler",
    "src.gui_edition.console_adapter",
    "src.gui_edition.download_manager",
    "src.gui_edition.gui_main",
    "src.gui_edition.theme",
]

# Modules that cascade-import backend (src.config, src.custom, rookiepy…)
_BACKEND_MODULES = [
    "src.gui_edition",
    "src.gui_edition.app",
    "src.gui_edition.backend_bootstrap",
    "src.gui_edition.coroutine_factory",
    "src.gui_edition.frames",
    "src.gui_edition.frames.download_frame",
    "src.gui_edition.frames.monitor_frame",
    "src.gui_edition.frames.settings_frame",
    "src.gui_edition.widgets",
]

_ALL_MODULES = _STANDALONE_MODULES + _BACKEND_MODULES

# Modules that ALSO need Tk (display) — subset of _BACKEND_MODULES
_NEEDS_TK = {
    "src.gui_edition.app",
    "src.gui_edition.frames.download_frame",
    "src.gui_edition.frames.monitor_frame",
    "src.gui_edition.frames.settings_frame",
    "src.gui_edition.widgets",
}


# ── Helpers ──────────────────────────────────────────────────────────
def _tk_available() -> bool:
    """Return True if tkinter can be initialised (even headless)."""
    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        root.destroy()
        return True
    except Exception:
        return False


_HAS_TK = _tk_available()


# ── Tests ────────────────────────────────────────────────────────────
class TestAstParse:
    """Every .py file should be valid Python syntax."""

    @staticmethod
    def _py_files():
        return sorted(_GUI_PKG.rglob("*.py"))

    @pytest.mark.parametrize(
        "path",
        _py_files.__func__(),  # type: ignore[attr-defined]
        ids=lambda p: p.relative_to(_GUI_PKG).as_posix(),
    )
    def test_syntax(self, path: Path) -> None:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))


class TestImports:
    """All modules should be importable (if deps are available)."""

    @pytest.mark.parametrize("module", _ALL_MODULES)
    def test_import(self, module: str) -> None:
        if module in _NEEDS_TK and not _HAS_TK:
            pytest.skip("No display / Tk not available")
        try:
            importlib.import_module(module)
        except ModuleNotFoundError as exc:
            # Backend-dependent modules may fail if optional deps
            # (rookiepy, gmssl, etc.) are not installed — skip them.
            if module in _BACKEND_MODULES:
                pytest.skip(f"Missing backend dependency: {exc.name}")
            raise


class TestThemeConstants:
    """The Theme class should expose required design tokens."""

    _REQUIRED_ATTRS = [
        "BG_PRIMARY",
        "BG_SECONDARY",
        "BG_CARD",
        "ACCENT",
        "TEXT_PRIMARY",
        "TEXT_SECONDARY",
        "SUCCESS",
        "WARNING",
        "ERROR",
        "FONT_FAMILY",
        "WIN_DEFAULT_SIZE",
        "WIN_MIN_WIDTH",
        "WIN_MIN_HEIGHT",
    ]

    def test_tokens_exist(self) -> None:
        from src.gui_edition.theme import Theme

        for attr in self._REQUIRED_ATTRS:
            assert hasattr(Theme, attr), f"Theme missing {attr}"


class TestDownloadManager:
    """DownloadManager can be instantiated without Tk."""

    def test_instantiate(self) -> None:
        from unittest.mock import MagicMock
        from src.gui_edition.download_manager import DownloadManager

        mock_ah = MagicMock()
        dm = DownloadManager(mock_ah)
        assert dm.tasks == {}
        assert len(dm.tasks) == 0


class TestConsoleAdapter:
    """GUIConsole captures log output."""

    def test_log_capture(self) -> None:
        from src.gui_edition.console_adapter import GUIConsole

        c = GUIConsole()
        c.print("hello")
        # Should not raise
