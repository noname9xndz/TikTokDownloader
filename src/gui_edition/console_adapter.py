"""GUI-compatible console that replaces Rich's ColorfulConsole.

``GUIConsole`` has the same public API (``print``, ``info``, ``warning``,
``error``, ``debug``, ``input``) so existing backend code can work with
minimal modification — just inject a ``GUIConsole`` instead of
``ColorfulConsole``.

All output is forwarded to a ``customtkinter.CTkTextbox`` on the GUI thread.
``input()`` opens a blocking dialog.
"""

from __future__ import annotations

import tkinter as tk
from datetime import datetime
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


class GUIConsole:
    """Drop-in replacement for ``ColorfulConsole`` that writes to a CTkTextbox."""

    def __init__(self, textbox: Optional[ctk.CTkTextbox] = None, debug: bool = False):
        self.debug_mode = debug
        self._textbox: Optional[ctk.CTkTextbox] = textbox

    def bind_textbox(self, textbox: ctk.CTkTextbox) -> None:
        """Attach (or re-attach) the output widget."""
        self._textbox = textbox
        # configure colour tags
        for tag, colour in _STYLE_COLOURS.items():
            self._textbox._textbox.tag_configure(tag, foreground=colour)  # noqa: access internal

    # ---- output methods ---------------------------------------------------

    def print(self, *args, style="general", highlight=False, **kwargs) -> None:
        text = " ".join(str(a) for a in args)
        self._append(text, self._resolve_tag(style))

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
