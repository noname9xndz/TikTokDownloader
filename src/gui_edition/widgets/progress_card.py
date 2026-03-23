"""Download progress card widget."""

from __future__ import annotations

from typing import Optional

import customtkinter as ctk

from ..theme import Theme

__all__ = ["ProgressCard"]


class ProgressCard(ctk.CTkFrame):
    """A compact card showing download progress for a single item.

    Displays: filename, progress bar, percentage, speed, status, and cancel.
    """

    def __init__(self, master, filename: str = "", on_cancel=None, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_CARD,
            corner_radius=Theme.RADIUS_MD,
            height=70,
            **kwargs,
        )
        self._on_cancel = on_cancel
        self.grid_columnconfigure(0, weight=1)
        self.grid_propagate(False)

        # ── Row 1: filename + status ──────────────────────────────────
        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.grid(row=0, column=0, padx=Theme.PAD_MD, pady=(Theme.PAD_SM, 0), sticky="ew")
        row1.grid_columnconfigure(0, weight=1)

        self._filename_label = ctk.CTkLabel(
            row1,
            text=filename or "—",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        )
        self._filename_label.grid(row=0, column=0, sticky="w")

        self._status_label = ctk.CTkLabel(
            row1,
            text="Waiting",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_MUTED,
            anchor="e",
        )
        self._status_label.grid(row=0, column=1, sticky="e")

        self._cancel_btn = ctk.CTkButton(
            row1,
            text="✕",
            width=24,
            height=24,
            font=Theme.FONT_SMALL,
            fg_color="transparent",
            hover_color=Theme.ERROR,
            text_color=Theme.TEXT_MUTED,
            corner_radius=4,
            command=self._on_cancel_click,
        )
        self._cancel_btn.grid(row=0, column=2, sticky="e", padx=(Theme.PAD_SM, 0))

        # ── Row 2: progress bar + percentage + speed ──────────────────
        row2 = ctk.CTkFrame(self, fg_color="transparent")
        row2.grid(row=1, column=0, padx=Theme.PAD_MD, pady=(Theme.PAD_XS, Theme.PAD_SM), sticky="ew")
        row2.grid_columnconfigure(0, weight=1)

        self._progress_bar = ctk.CTkProgressBar(
            row2,
            height=8,
            corner_radius=4,
            fg_color=Theme.BG_INPUT,
            progress_color=Theme.ACCENT,
        )
        self._progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, Theme.PAD_SM))
        self._progress_bar.set(0)

        self._percent_label = ctk.CTkLabel(
            row2,
            text="0%",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_SECONDARY,
            width=40,
        )
        self._percent_label.grid(row=0, column=1)

        self._speed_label = ctk.CTkLabel(
            row2,
            text="",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_MUTED,
            width=80,
            anchor="e",
        )
        self._speed_label.grid(row=0, column=2)

    # ── Public API ────────────────────────────────────────────────────

    def set_filename(self, name: str) -> None:
        self._filename_label.configure(text=name)

    def set_progress(self, value: float) -> None:
        """Set progress 0.0 – 1.0."""
        clamped = max(0.0, min(1.0, value))
        self._progress_bar.set(clamped)
        self._percent_label.configure(text=f"{int(clamped * 100)}%")

    def set_speed(self, speed: str) -> None:
        """E.g. '2.3 MB/s'."""
        self._speed_label.configure(text=speed)

    def set_status(self, status: str, colour: Optional[str] = None) -> None:
        self._status_label.configure(
            text=status,
            text_color=colour or Theme.TEXT_MUTED,
        )

    def mark_done(self) -> None:
        self.set_progress(1.0)
        self.set_status("✓ Done", Theme.SUCCESS)
        self.set_speed("")
        self.hide_cancel()

    def mark_error(self, msg: str = "Error") -> None:
        self.set_status(f"✕ {msg}", Theme.ERROR)
        self.set_speed("")
        self.hide_cancel()

    def cancel(self) -> None:
        """Programmatically trigger cancel."""
        self._on_cancel_click()

    def hide_cancel(self) -> None:
        """Hide the cancel button (e.g. after completion)."""
        self._cancel_btn.grid_forget()

    def _on_cancel_click(self) -> None:
        if self._on_cancel:
            self._on_cancel()

