"""About dialog with version info and update checker.

Opens as a ``CTkToplevel`` modal from the sidebar.
"""

from __future__ import annotations

import threading
from typing import Optional

import customtkinter as ctk

from ..theme import Theme

__all__ = ["AboutDialog"]

# GitHub releases URL (same as backend)
_RELEASES = "https://github.com/JoeanAmier/TikTokDownloader/releases/latest"


class AboutDialog(ctk.CTkToplevel):
    """Modal About / Update dialog."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("About DouK-Downloader")
        self.geometry("420x340")
        self.resizable(False, False)
        self.configure(fg_color=Theme.BG_PRIMARY)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)

        # ── Version info ──────────────────────────────────────────────
        try:
            from src.custom import VERSION_MAJOR, VERSION_MINOR, VERSION_BETA
        except ImportError:
            VERSION_MAJOR, VERSION_MINOR, VERSION_BETA = "?", "?", False

        version_str = f"v{VERSION_MAJOR}.{VERSION_MINOR}"
        if VERSION_BETA:
            version_str += "  (beta)"

        ctk.CTkLabel(
            self, text="DouK-Downloader",
            font=Theme.FONT_H1,
            text_color=Theme.ACCENT,
        ).grid(row=0, column=0, padx=Theme.PAD_LG, pady=(Theme.PAD_XL, Theme.PAD_XS))

        ctk.CTkLabel(
            self, text=version_str,
            font=Theme.FONT_H3,
            text_color=Theme.TEXT_PRIMARY,
        ).grid(row=1, column=0, padx=Theme.PAD_LG, pady=Theme.PAD_XS)

        ctk.CTkLabel(
            self, text="TikTok / Douyin video downloader",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_SECONDARY,
        ).grid(row=2, column=0, padx=Theme.PAD_LG, pady=Theme.PAD_XS)

        # GitHub link
        link = ctk.CTkLabel(
            self, text=_RELEASES.replace("/releases/latest", ""),
            font=Theme.FONT_SMALL,
            text_color=Theme.ACCENT,
            cursor="hand2",
        )
        link.grid(row=3, column=0, padx=Theme.PAD_LG, pady=Theme.PAD_SM)
        link.bind("<Button-1>", lambda e: self._open_url(
            _RELEASES.replace("/releases/latest", ""),
        ))

        # ── Update result label ───────────────────────────────────────
        self._result_label = ctk.CTkLabel(
            self, text="",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_MUTED,
            wraplength=380, justify="center",
        )
        self._result_label.grid(row=4, column=0, padx=Theme.PAD_LG, pady=Theme.PAD_SM)

        # ── Buttons ───────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=5, column=0, padx=Theme.PAD_LG, pady=(Theme.PAD_SM, Theme.PAD_LG))

        self._check_btn = ctk.CTkButton(
            btn_frame, text="🔄  Check for Updates", width=180,
            font=Theme.FONT_BODY,
            fg_color=Theme.BG_CARD, hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            command=self._check_update,
        )
        self._check_btn.grid(row=0, column=0, padx=(0, Theme.PAD_SM))

        ctk.CTkButton(
            btn_frame, text="Close", width=80,
            font=Theme.FONT_BODY,
            fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_HOVER,
            command=self.destroy,
        ).grid(row=0, column=1)

        # Store version for comparison
        self._major = VERSION_MAJOR
        self._minor = VERSION_MINOR
        self._beta = VERSION_BETA

    # ── Update check ──────────────────────────────────────────────────

    def _check_update(self) -> None:
        """Run HTTP check in a background thread."""
        self._check_btn.configure(state="disabled", text="⏳ Checking…")
        self._result_label.configure(text="", text_color=Theme.TEXT_MUTED)
        threading.Thread(target=self._do_check, daemon=True).start()

    def _do_check(self) -> None:
        """Background: GET releases URL, compare version."""
        try:
            from httpx import get as httpx_get, RequestError
            response = httpx_get(_RELEASES, timeout=5, follow_redirects=True)
            latest_major, latest_minor = map(
                int, str(response.url).split("/")[-1].split(".", 1),
            )
            self._show_result(latest_major, latest_minor)
        except Exception as exc:
            self.after(0, lambda: self._show_error(str(exc)))

    def _show_result(self, latest_major: int, latest_minor: int) -> None:
        """Schedule UI update on the main thread."""
        def _update():
            try:
                cur_major = int(self._major)
                cur_minor = int(self._minor)
            except (ValueError, TypeError):
                self._show_error("Cannot determine current version.")
                return

            if latest_major > cur_major or latest_minor > cur_minor:
                self._result_label.configure(
                    text=f"🆕 New version available: {latest_major}.{latest_minor}",
                    text_color=Theme.WARNING,
                )
            elif latest_minor == cur_minor and self._beta:
                self._result_label.configure(
                    text="⚠ You're on a dev build — a stable release is available.",
                    text_color=Theme.WARNING,
                )
            elif self._beta:
                self._result_label.configure(
                    text="✅ You're on the latest dev build.",
                    text_color=Theme.SUCCESS,
                )
            else:
                self._result_label.configure(
                    text="✅ You're on the latest stable release!",
                    text_color=Theme.SUCCESS,
                )
            self._check_btn.configure(state="normal", text="🔄  Check for Updates")

        self.after(0, _update)

    def _show_error(self, msg: str) -> None:
        self._result_label.configure(
            text=f"❌ Update check failed: {msg}",
            text_color=Theme.DANGER,
        )
        self._check_btn.configure(state="normal", text="🔄  Check for Updates")

    @staticmethod
    def _open_url(url: str) -> None:
        import webbrowser
        webbrowser.open(url)
