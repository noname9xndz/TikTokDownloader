"""GUI-compatible console that replaces Rich's ColorfulConsole.

``GUIConsole`` has the same public API (``print``, ``info``, ``warning``,
``error``, ``debug``, ``input``) so existing backend code can work with
minimal modification — just inject a ``GUIConsole`` instead of
``ColorfulConsole``.

All output is forwarded to a ``customtkinter.CTkTextbox`` on the GUI thread.
``input()`` opens a blocking dialog.

Phase 9: added optional file logging with rotation (gui.log, 5 MB max).
"""

from __future__ import annotations

import logging
import os
import tkinter as tk
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

import customtkinter as ctk

if TYPE_CHECKING:
    pass

__all__ = ["GUIConsole"]

# Tag → colour mapping (dark-mode friendly colours)
_STYLE_COLOURS = {
    "general": "#FFFFFF",
    "info": "#00E676",
    "warning": "#FFD600",
    "error": "#FF1744",
    "debug": "#FF9100",
    "master": "#FFF200",
    "prompt": "#40E0D0",
    "progress": "#FF00FF",
}

# Map our style tags to Python logging levels
_LEVEL_MAP = {
    "general": logging.INFO,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "debug": logging.DEBUG,
    "master": logging.INFO,
    "prompt": logging.INFO,
    "progress": logging.INFO,
}


def _setup_file_logger(debug: bool = False) -> logging.Logger:
    """Create a rotating file logger writing to ~/.DouK-Downloader/gui.log."""
    log_dir = Path.home() / ".DouK-Downloader"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "gui.log"

    logger = logging.getLogger("douk.gui")
    if logger.handlers:
        # Already set up (e.g. multiple GUIConsole instances)
        return logger

    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(handler)
    return logger


class GUIConsole:
    """Drop-in replacement for ``ColorfulConsole`` that writes to a CTkTextbox."""

    def __init__(self, textbox: Optional[ctk.CTkTextbox] = None, debug: bool = False):
        self.debug_mode = debug
        self._textbox: Optional[ctk.CTkTextbox] = textbox
        self._file_logger = _setup_file_logger(debug)

    def bind_textbox(self, textbox: ctk.CTkTextbox) -> None:
        """Attach (or re-attach) the output widget."""
        self._textbox = textbox
        # configure colour tags
        for tag, colour in _STYLE_COLOURS.items():
            self._textbox._textbox.tag_configure(tag, foreground=colour)  # noqa: access internal

    # ---- output methods ---------------------------------------------------

    def print(self, *args, style="general", highlight=False, **kwargs) -> None:
        text = " ".join(str(a) for a in args)
        tag = self._resolve_tag(style)
        self._append(text, tag)
        self._log_to_file(text, tag)

    def info(self, *args, highlight=False, **kwargs) -> None:
        self.print(*args, style="info", highlight=highlight, **kwargs)

    def warning(self, *args, highlight=False, **kwargs) -> None:
        self.print(*args, style="warning", highlight=highlight, **kwargs)

    def error(self, *args, highlight=False, **kwargs) -> None:
        self.print(*args, style="error", highlight=highlight, **kwargs)

    def debug(self, *args, highlight=False, **kwargs) -> None:
        if self.debug_mode:
            self.print(*args, style="debug", highlight=highlight, **kwargs)

    # ---- input method (blocking dialog) -----------------------------------

    def input(self, prompt: str = "", style=None, *args, **kwargs) -> str:
        """Show a popup dialog and return the user's text input."""
        dialog = ctk.CTkInputDialog(
            text=prompt or "Input:",
            title="DouK-Downloader",
        )
        result = dialog.get_input()
        return result if result is not None else ""

    # ---- helpers ----------------------------------------------------------

    @staticmethod
    def _resolve_tag(style) -> str:
        """Map a Rich-style string or plain tag name to a textbox tag."""
        if isinstance(style, str):
            s = style.lower()
            for tag in _STYLE_COLOURS:
                if tag in s:
                    return tag
        return "general"

    def _append(self, text: str, tag: str = "general") -> None:
        if self._textbox is None:
            return
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {text}\n"
        self._textbox.configure(state="normal")
        self._textbox._textbox.insert(tk.END, line, tag)  # noqa: access internal
        self._textbox.configure(state="disabled")
        self._textbox._textbox.see(tk.END)  # noqa: auto-scroll

    def _log_to_file(self, text: str, tag: str) -> None:
        """Also write the log line to the rotating file logger."""
        level = _LEVEL_MAP.get(tag, logging.INFO)
        self._file_logger.log(level, text)
