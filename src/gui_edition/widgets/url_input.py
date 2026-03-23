"""URL input widget with paste and clear buttons."""

from __future__ import annotations

from typing import Callable, List, Optional

import customtkinter as ctk

from ..theme import Theme

__all__ = ["URLInput"]


class URLInput(ctk.CTkFrame):
    """A text-area based URL input with paste-from-clipboard and clear actions.

    Supports both single-line and multi-line (one URL per line) input.
    """

    def __init__(
        self,
        master,
        placeholder: str = "Paste URL(s) here — one per line…",
        on_submit: Optional[Callable[[List[str]], None]] = None,
        height: int = 100,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_submit = on_submit
        self._placeholder = placeholder

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Text area ─────────────────────────────────────────────────
        self._textbox = ctk.CTkTextbox(
            self,
            height=height,
            font=Theme.FONT_BODY,
            fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=Theme.RADIUS_SM,
            wrap="word",
        )
        self._textbox.grid(row=0, column=0, sticky="nsew")

        # ── Button bar ────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=(Theme.PAD_SM, 0), sticky="e")

        self._paste_btn = ctk.CTkButton(
            btn_frame,
            text="📋 Paste",
            width=80,
            height=30,
            font=Theme.FONT_SMALL,
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=Theme.RADIUS_SM,
            command=self._paste_clipboard,
        )
        self._paste_btn.grid(row=0, column=0, padx=(0, Theme.PAD_SM))

        self._clear_btn = ctk.CTkButton(
            btn_frame,
            text="✕ Clear",
            width=80,
            height=30,
            font=Theme.FONT_SMALL,
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            corner_radius=Theme.RADIUS_SM,
            command=self.clear,
        )
        self._clear_btn.grid(row=0, column=1, padx=(0, Theme.PAD_SM))

        self._submit_btn = ctk.CTkButton(
            btn_frame,
            text="▶  Start",
            width=100,
            height=30,
            font=Theme.FONT_BODY,
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=Theme.RADIUS_SM,
            command=self._handle_submit,
        )
        self._submit_btn.grid(row=0, column=2)

    # ── Public API ────────────────────────────────────────────────────

    def get_urls(self) -> List[str]:
        """Return a cleaned list of URLs (non-empty, stripped)."""
        raw = self._textbox.get("1.0", "end-1c")
        return [line.strip() for line in raw.splitlines() if line.strip()]

    def clear(self) -> None:
        self._textbox.delete("1.0", "end")

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the input and buttons."""
        state = "normal" if enabled else "disabled"
        self._textbox.configure(state=state)
        self._submit_btn.configure(state=state)

    # ── Internals ─────────────────────────────────────────────────────

    def _paste_clipboard(self) -> None:
        try:
            text = self.clipboard_get()
            if text:
                self._textbox.insert("end", text)
        except Exception:
            pass  # clipboard empty or unavailable

    def _handle_submit(self) -> None:
        urls = self.get_urls()
        if urls and self._on_submit:
            self._on_submit(urls)
