"""Sidebar navigation widget for the DouK-Downloader desktop app."""

from __future__ import annotations

from typing import Callable, Dict, Optional

import customtkinter as ctk

from ..theme import Theme

__all__ = ["Sidebar"]

# Navigation items: (id, label, icon character)
NAV_ITEMS = [
    ("download", "⬇  Download", "⬇"),
    ("settings", "⚙  Settings", "⚙"),
    ("monitor", "📋  Monitor", "📋"),
]


class Sidebar(ctk.CTkFrame):
    """Left-side navigation bar with brand header and nav buttons."""

    def __init__(
        self,
        master,
        on_navigate: Callable[[str], None],
        **kwargs,
    ):
        super().__init__(
            master,
            width=Theme.SIDEBAR_WIDTH,
            corner_radius=0,
            fg_color=Theme.SIDEBAR_BG,
            **kwargs,
        )
        self._on_navigate = on_navigate
        self._buttons: Dict[str, ctk.CTkButton] = {}
        self._active: Optional[str] = None

        # Rows: 0=logo, 1..N=nav, N+1=spacer(weight), N+2=about, N+3=version
        self.grid_rowconfigure(len(NAV_ITEMS) + 1, weight=1)  # spacer row
        self.grid_columnconfigure(0, weight=1)

        # ── Logo / Brand ──────────────────────────────────────────────
        self._logo_label = ctk.CTkLabel(
            self,
            text="DouK\nDownloader",
            font=Theme.FONT_H2,
            text_color=Theme.ACCENT,
            justify="center",
        )
        self._logo_label.grid(
            row=0, column=0,
            padx=Theme.PAD_MD, pady=(Theme.PAD_XL, Theme.PAD_LG),
            sticky="ew",
        )

        # ── Nav buttons ───────────────────────────────────────────────
        for idx, (nav_id, label, _icon) in enumerate(NAV_ITEMS, start=1):
            btn = ctk.CTkButton(
                self,
                text=label,
                font=Theme.FONT_BODY,
                fg_color="transparent",
                text_color=Theme.TEXT_SECONDARY,
                hover_color=Theme.SIDEBAR_BTN_HOVER,
                anchor="w",
                height=40,
                corner_radius=Theme.RADIUS_SM,
                command=lambda nid=nav_id: self._handle_click(nid),
            )
            btn.grid(
                row=idx, column=0,
                padx=Theme.PAD_SM, pady=2,
                sticky="ew",
            )
            self._buttons[nav_id] = btn

        # ── About button (pinned near bottom) ─────────────────────────
        about_btn = ctk.CTkButton(
            self,
            text="ℹ️  About",
            font=Theme.FONT_BODY,
            fg_color="transparent",
            text_color=Theme.TEXT_SECONDARY,
            hover_color=Theme.SIDEBAR_BTN_HOVER,
            anchor="w",
            height=36,
            corner_radius=Theme.RADIUS_SM,
            command=self._open_about,
        )
        about_btn.grid(
            row=len(NAV_ITEMS) + 2, column=0,
            padx=Theme.PAD_SM, pady=(0, 2),
            sticky="ew",
        )

        # ── Version label (bottom) ────────────────────────────────────
        try:
            from src.custom import VERSION_MAJOR, VERSION_MINOR
            version_text = f"v{VERSION_MAJOR}.{VERSION_MINOR}"
        except ImportError:
            version_text = "v?.?"
        self._version_label = ctk.CTkLabel(
            self,
            text=version_text,
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_MUTED,
        )
        self._version_label.grid(
            row=len(NAV_ITEMS) + 3, column=0,
            padx=Theme.PAD_MD, pady=(0, Theme.PAD_MD),
            sticky="s",
        )

        # Activate first item by default
        self.set_active("download")

    def _handle_click(self, nav_id: str) -> None:
        self.set_active(nav_id)
        self._on_navigate(nav_id)

    def set_active(self, nav_id: str) -> None:
        """Highlight the active nav button."""
        if self._active == nav_id:
            return
        # Reset previous
        if self._active and self._active in self._buttons:
            self._buttons[self._active].configure(
                fg_color="transparent",
                text_color=Theme.TEXT_SECONDARY,
            )
        # Activate new
        if nav_id in self._buttons:
            self._buttons[nav_id].configure(
                fg_color=Theme.SIDEBAR_BTN_ACTIVE,
                text_color=Theme.TEXT_PRIMARY,
            )
            self._active = nav_id

    def _open_about(self) -> None:
        """Open the About dialog."""
        from .about_dialog import AboutDialog
        AboutDialog(self.winfo_toplevel())

