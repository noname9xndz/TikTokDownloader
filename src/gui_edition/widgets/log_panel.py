"""Scrollable log output panel widget.

Phase 9: added log level filter dropdown, copy-to-clipboard button,
and auto-trim to prevent memory bloat on long sessions.
"""

from __future__ import annotations

import tkinter as tk
from datetime import datetime
from typing import List, Optional, Tuple

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

# Maximum lines to keep in the log before auto-trimming
_MAX_LINES = 500

# Filter options → which tags to show
_FILTER_OPTIONS = {
    "All": None,  # None means show everything
    "Info": {"info", "success"},
    "Warning": {"warning"},
    "Error": {"error"},
}


class LogPanel(ctk.CTkFrame):
    """A read-only scrollable text panel with coloured log lines.

    Used as the main output area — replaces the Rich console terminal.
    """

    def __init__(self, master, height: int = 200, **kwargs):
        super().__init__(master, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MD, **kwargs)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # internal line buffer for filtering: (text, tag)
        self._lines: List[Tuple[str, str]] = []
        self._current_filter: Optional[str] = None  # None = All

        # ── Header row ────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=Theme.PAD_MD, pady=(Theme.PAD_SM, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        self._header = ctk.CTkLabel(
            header,
            text="📜  Output Log",
            font=Theme.FONT_H3,
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        )
        self._header.grid(row=0, column=0, sticky="w")

        # Filter dropdown
        self._filter_var = ctk.StringVar(value="All")
        self._filter_menu = ctk.CTkOptionMenu(
            header,
            values=list(_FILTER_OPTIONS.keys()),
            variable=self._filter_var,
            command=self._on_filter_change,
            width=90,
            height=26,
            font=Theme.FONT_SMALL,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BG_HOVER,
            button_hover_color=Theme.ACCENT,
            dropdown_fg_color=Theme.BG_CARD,
            dropdown_hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            corner_radius=Theme.RADIUS_SM,
        )
        self._filter_menu.grid(row=0, column=1, padx=(Theme.PAD_SM, 0), sticky="e")

        # Copy button
        self._copy_btn = ctk.CTkButton(
            header,
            text="📋 Copy",
            width=64,
            height=26,
            font=Theme.FONT_SMALL,
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            corner_radius=Theme.RADIUS_SM,
            command=self._copy_to_clipboard,
        )
        self._copy_btn.grid(row=0, column=2, padx=(Theme.PAD_SM, 0), sticky="e")

        # Clear button
        self._clear_btn = ctk.CTkButton(
            header,
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
        self._clear_btn.grid(row=0, column=3, padx=(Theme.PAD_SM, 0), sticky="e")

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
        line = f"[{ts}] {text}"
        self._lines.append((line, tag))

        # Auto-trim buffer
        if len(self._lines) > _MAX_LINES:
            self._lines = self._lines[-_MAX_LINES:]

        # Only insert into textbox if it passes the current filter
        allowed = _FILTER_OPTIONS.get(self._filter_var.get())
        if allowed is None or tag in allowed:
            self._insert_line(line, tag)

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
        self._lines.clear()
        self._textbox.configure(state="normal")
        self._textbox._textbox.delete("1.0", tk.END)
        self._textbox.configure(state="disabled")

    @property
    def textbox(self) -> ctk.CTkTextbox:
        """Return the underlying textbox (for ``GUIConsole.bind_textbox``)."""
        return self._textbox

    # ── Private ───────────────────────────────────────────────────────

    def _insert_line(self, line: str, tag: str) -> None:
        self._textbox.configure(state="normal")
        self._textbox._textbox.insert(tk.END, line + "\n", tag)
        self._textbox.configure(state="disabled")
        self._textbox._textbox.see(tk.END)

    def _on_filter_change(self, choice: str) -> None:
        """Re-render visible lines based on current filter."""
        allowed = _FILTER_OPTIONS.get(choice)
        self._textbox.configure(state="normal")
        self._textbox._textbox.delete("1.0", tk.END)
        for line, tag in self._lines:
            if allowed is None or tag in allowed:
                self._textbox._textbox.insert(tk.END, line + "\n", tag)
        self._textbox.configure(state="disabled")
        self._textbox._textbox.see(tk.END)

    def _copy_to_clipboard(self) -> None:
        """Copy all visible log text to system clipboard."""
        content = self._textbox._textbox.get("1.0", tk.END).strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
