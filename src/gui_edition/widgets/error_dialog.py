"""User-friendly error dialog for the DouK-Downloader GUI.

Provides a ``CTkToplevel`` modal and a convenience function.
"""

from __future__ import annotations

import traceback
from typing import Optional

import customtkinter as ctk

from ..theme import Theme

__all__ = ["ErrorDialog", "show_error"]


class ErrorDialog(ctk.CTkToplevel):
    """Modal error dialog with an icon, message, and optional details."""

    def __init__(
        self,
        master,
        title: str = "Error",
        message: str = "",
        detail: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.title(title)
        self.geometry("480x280")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_PRIMARY)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)

        # Icon + heading
        ctk.CTkLabel(
            self, text="❌  " + title,
            font=Theme.FONT_H2,
            text_color=Theme.DANGER,
        ).grid(row=0, column=0, padx=Theme.PAD_LG, pady=(Theme.PAD_LG, Theme.PAD_SM), sticky="w")

        # Message
        ctk.CTkLabel(
            self, text=message,
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_PRIMARY,
            wraplength=440, justify="left", anchor="nw",
        ).grid(row=1, column=0, padx=Theme.PAD_LG, pady=Theme.PAD_XS, sticky="nw")

        # Detail (scrollable text)
        self._detail = detail or ""
        if self._detail:
            tb = ctk.CTkTextbox(
                self, height=100,
                font=Theme.FONT_MONO,
                fg_color=Theme.BG_CARD,
                text_color=Theme.TEXT_SECONDARY,
                wrap="word",
            )
            tb.grid(row=2, column=0, padx=Theme.PAD_LG, pady=Theme.PAD_SM, sticky="ew")
            tb.insert("1.0", self._detail)
            tb.configure(state="disabled")

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=Theme.PAD_LG, pady=(Theme.PAD_SM, Theme.PAD_LG), sticky="e")

        if self._detail:
            ctk.CTkButton(
                btn_frame, text="📋 Copy Details", width=120,
                font=Theme.FONT_BODY,
                fg_color=Theme.BG_CARD, hover_color=Theme.BG_HOVER,
                text_color=Theme.TEXT_SECONDARY,
                command=self._copy_detail,
            ).grid(row=0, column=0, padx=(0, Theme.PAD_SM))

        ctk.CTkButton(
            btn_frame, text="OK", width=80,
            font=Theme.FONT_H3,
            fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_HOVER,
            command=self.destroy,
        ).grid(row=0, column=1)

    def _copy_detail(self) -> None:
        self.clipboard_clear()
        self.clipboard_append(self._detail)


def show_error(
    parent,
    title: str = "Error",
    message: str = "An unexpected error occurred.",
    detail: str | None = None,
    exc: BaseException | None = None,
) -> None:
    """One-liner to show an error dialog.

    If *exc* is given and *detail* is not, the traceback is formatted
    automatically.
    """
    if exc and not detail:
        detail = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    ErrorDialog(parent, title=title, message=message, detail=detail)
