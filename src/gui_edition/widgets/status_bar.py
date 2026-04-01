"""Status bar widget — sits at the bottom of the main window."""

from __future__ import annotations

from typing import Optional

import customtkinter as ctk

from ..theme import Theme

__all__ = ["StatusBar"]


class StatusBar(ctk.CTkFrame):
    """Thin bar at the bottom showing cookie state, FFmpeg status, and messages."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            height=Theme.STATUSBAR_HEIGHT,
            corner_radius=0,
            fg_color=Theme.STATUSBAR_BG,
            **kwargs,
        )
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        # ── Cookie indicators (Douyin + TikTok) ────────────────────────
        cookie_frame = ctk.CTkFrame(self, fg_color="transparent", height=20)
        cookie_frame.grid(row=0, column=0, padx=Theme.PAD_MD, sticky="w")

        self._cookie_dy_label = ctk.CTkLabel(
            cookie_frame,
            text="● Douyin cookie: N/A",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_MUTED,
        )
        self._cookie_dy_label.pack(side="left", padx=(0, Theme.PAD_SM))

        self._cookie_tt_label = ctk.CTkLabel(
            cookie_frame,
            text="● TikTok cookie: N/A",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_MUTED,
        )
        self._cookie_tt_label.pack(side="left")

        # ── Centre message ────────────────────────────────────────────
        self._message_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_SECONDARY,
        )
        self._message_label.grid(row=0, column=1, sticky="ew")

        # ── FFmpeg indicator ──────────────────────────────────────────
        self._ffmpeg_label = ctk.CTkLabel(
            self,
            text="FFmpeg: ?",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_MUTED,
        )
        self._ffmpeg_label.grid(row=0, column=2, padx=Theme.PAD_MD, sticky="e")

    # ── Public API ────────────────────────────────────────────────────

    def set_cookie_status(self, platform: str, ok: bool) -> None:
        """Update cookie indicator. ``platform``: 'Douyin' or 'TikTok'."""
        lbl = self._cookie_dy_label if platform == "Douyin" else self._cookie_tt_label
        if ok:
            lbl.configure(
                text=f"● {platform} cookie ✓",
                text_color=Theme.SUCCESS,
            )
        else:
            lbl.configure(
                text=f"● {platform} cookie ✕",
                text_color=Theme.ERROR,
            )

    def set_message(self, text: str, colour: Optional[str] = None) -> None:
        self._message_label.configure(
            text=text,
            text_color=colour or Theme.TEXT_SECONDARY,
        )

    def set_ffmpeg(self, available: bool) -> None:
        if available:
            self._ffmpeg_label.configure(text="FFmpeg ✓", text_color=Theme.SUCCESS)
        else:
            self._ffmpeg_label.configure(text="FFmpeg ✕", text_color=Theme.WARNING)
