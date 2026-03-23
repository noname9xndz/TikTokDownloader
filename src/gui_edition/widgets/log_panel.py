"""Scrollable log output panel widget."""

from __future__ import annotations

import tkinter as tk
from datetime import datetime
from typing import Optional

import customtkinter as ctk

from ..theme import Theme

__all__ = ["LogPanel"]

# Tag → colour mapping (dark-mode friendly)
_TAG_COLOURS = {
    "general": Theme.TEXT_PRIMARY,
    "info": Theme.SUCCESS,
    "warning": Theme.WARNING,
    "error": Theme.ERROR,
    "debug": "#FF9100",
    "success": Theme.SUCCESS,
    "accent": Theme.ACCENT,
}


class LogPanel(ctk.CTkFrame):
    """A read-only scrollable text panel with coloured log lines.

    Used as the main output area — replaces the Rich console terminal.
    """

    def __init__(self, master, height: int = 200, **kwargs):
        super().__init__(master, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MD, **kwargs)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Header ────────────────────────────────────────────────────
        self._header = ctk.CTkLabel(
            self,
            text="📜  Output Log",
            font=Theme.FONT_H3,
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        )
        self._header.grid(row=0, column=0, padx=Theme.PAD_MD, pady=(Theme.PAD_SM, 0), sticky="w")

        # ── Clear button ──────────────────────────────────────────────
        self._clear_btn = ctk.CTkButton(
            self,
            text="Clear",
            width=60,
            height=26,
            font=Theme.FONT_SMALL,
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            corner_radius=Theme.RADIUS_SM,
            command=self.clear,
        )
        self._clear_btn.grid(row=0, column=0, padx=Theme.PAD_MD, pady=(Theme.PAD_SM, 0), sticky="e")

        # ── Textbox ───────────────────────────────────────────────────
        self._textbox = ctk.CTkTextbox(
            self,
            height=height,
            font=Theme.FONT_MONO,
            fg_color=Theme.BG_PRIMARY,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=Theme.RADIUS_SM,
            state="disabled",
            wrap="word",
        )
        self._textbox.grid(
            row=1, column=0,
            padx=Theme.PAD_SM, pady=Theme.PAD_SM,
            sticky="nsew",
        )

        # Configure colour tags
        for tag, colour in _TAG_COLOURS.items():
            self._textbox._textbox.tag_configure(tag, foreground=colour)

    # ── Public API ────────────────────────────────────────────────────

    def append(self, text: str, tag: str = "general") -> None:
        """Add a timestamped line to the log."""
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {text}\n"
        self._textbox.configure(state="normal")
        self._textbox._textbox.insert(tk.END, line, tag)
        self._textbox.configure(state="disabled")
        self._textbox._textbox.see(tk.END)

    def info(self, text: str) -> None:
        self.append(text, "info")

    def warning(self, text: str) -> None:
        self.append(text, "warning")

    def error(self, text: str) -> None:
        self.append(text, "error")

    def success(self, text: str) -> None:
        self.append(text, "success")

    def clear(self) -> None:
        """Remove all log content."""
        self._textbox.configure(state="normal")
        self._textbox._textbox.delete("1.0", tk.END)
        self._textbox.configure(state="disabled")

    @property
    def textbox(self) -> ctk.CTkTextbox:
        """Return the underlying textbox (for ``GUIConsole.bind_textbox``)."""
        return self._textbox
