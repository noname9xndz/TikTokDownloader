"""Main application window for DouK-Downloader desktop GUI.

Composes the sidebar, content frames, log panel, and status bar into
a single ``customtkinter`` window.
"""

from __future__ import annotations

from typing import Dict, Optional

import customtkinter as ctk

from .async_handler import AsyncHandler
from .backend_bootstrap import BackendBootstrap
from .console_adapter import GUIConsole
from .frames import DownloadFrame, MonitorFrame, SettingsFrame
from .theme import Theme
from .widgets import LogPanel, Sidebar, StatusBar, show_error

__all__ = ["App"]


class App(ctk.CTk):
    """Root window — the only class exported from ``gui_edition``."""

    def __init__(self) -> None:
        super().__init__()

        # ── Window setup ──────────────────────────────────────────────
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("DouK-Downloader")
        self.geometry(Theme.WIN_DEFAULT_SIZE)
        self.minsize(Theme.WIN_MIN_WIDTH, Theme.WIN_MIN_HEIGHT)
        self.configure(fg_color=Theme.BG_PRIMARY)

        # ── Async bridge ──────────────────────────────────────────────
        self.async_handler = AsyncHandler(self)

        # ── Console adapter (for backend compatibility) ───────────────
        self.console = GUIConsole()

        # ── Backend bootstrap (populated async after mainloop) ────────
        self.backend = BackendBootstrap(self.console)

        # ── Layout grid ───────────────────────────────────────────────
        #  ┌──────────┬────────────────────────────┐
        #  │          │        content_area         │  row 0 (weight=1)
        #  │ sidebar  ├────────────────────────────┤
        #  │          │         log_panel           │  row 1
        #  ├──────────┴────────────────────────────┤
        #  │            status_bar                  │  row 2
        #  └───────────────────────────────────────┘
        self.grid_columnconfigure(0, weight=0)   # sidebar fixed
        self.grid_columnconfigure(1, weight=1)   # content stretches
        self.grid_rowconfigure(0, weight=1)      # content stretches
        self.grid_rowconfigure(1, weight=0)      # log panel fixed
        self.grid_rowconfigure(2, weight=0)      # status bar fixed

        # ── Sidebar ───────────────────────────────────────────────────
        self._sidebar = Sidebar(self, on_navigate=self._on_navigate)
        self._sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")

        # ── Content frames (stacked, only one visible) ────────────────
        self._content_area = ctk.CTkFrame(self, fg_color=Theme.BG_PRIMARY, corner_radius=0)
        self._content_area.grid(row=0, column=1, sticky="nsew")
        self._content_area.grid_columnconfigure(0, weight=1)
        self._content_area.grid_rowconfigure(0, weight=1)

        self._frames: Dict[str, ctk.CTkFrame] = {}
        self._current_frame: Optional[str] = None

        self._frames["download"] = DownloadFrame(self._content_area, app_ref=self)
        self._frames["settings"] = SettingsFrame(self._content_area, app_ref=self)
        self._frames["monitor"] = MonitorFrame(self._content_area, app_ref=self)

        for frame in self._frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        # ── Log panel ─────────────────────────────────────────────────
        self._log_panel = LogPanel(self, height=160)
        self._log_panel.grid(
            row=1, column=1,
            padx=Theme.PAD_SM, pady=(Theme.PAD_SM, 0),
            sticky="nsew",
        )
        # Bind console → log panel textbox
        self.console.bind_textbox(self._log_panel.textbox)

        # ── Status bar ────────────────────────────────────────────────
        self._status_bar = StatusBar(self)
        self._status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")

        # ── Show default frame ────────────────────────────────────────
        self._show_frame("download")

        # ── Window close handler ──────────────────────────────────────
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── Startup log ──────────────────────────────────────────────
        self._log_panel.info("DouK-Downloader GUI started — ready.")

        # ── Kick off backend init (non-blocking) ─────────────────────
        self._log_panel.info("Initialising backend…")
        self._status_bar.set_message("Initialising backend…")
        self.async_handler.run_async(
            self.backend.start(),
            on_done=lambda _: self._on_backend_ready(),
            on_error=self._on_backend_error,
        )

    # ── Navigation ────────────────────────────────────────────────────

    def _on_navigate(self, nav_id: str) -> None:
        """Called by sidebar when user clicks a nav button."""
        self._show_frame(nav_id)

    def _show_frame(self, name: str) -> None:
        """Raise the named frame to the top."""
        if name in self._frames:
            self._frames[name].tkraise()
            self._current_frame = name

    # ── Convenience accessors ─────────────────────────────────────────

    @property
    def log(self) -> LogPanel:
        return self._log_panel

    @property
    def status_bar(self) -> StatusBar:
        return self._status_bar

    @property
    def download_frame(self) -> DownloadFrame:
        return self._frames["download"]

    @property
    def settings_frame(self) -> SettingsFrame:
        return self._frames["settings"]

    @property
    def monitor_frame(self) -> MonitorFrame:
        return self._frames["monitor"]

    # ── Backend lifecycle ──────────────────────────────────────────────

    def _on_backend_ready(self) -> None:
        """Called on the GUI thread after backend.start() succeeds."""
        self._log_panel.info("Backend ready — database, settings, and cookies loaded.")
        self._status_bar.set_message("Ready")
        self._status_bar.set_cookie_status(
            "Douyin",
            bool(self.backend.parameter and self.backend.parameter.cookie),
        )
        self._status_bar.set_cookie_status(
            "TikTok",
            bool(self.backend.parameter and self.backend.parameter.cookie_tiktok),
        )
        # Update FFmpeg indicator
        ffmpeg_ok = bool(
            self.backend.parameter and self.backend.parameter.ffmpeg
        )
        self._status_bar.set_ffmpeg(ffmpeg_ok)

    def _on_backend_error(self, exc: BaseException) -> None:
        """Called on the GUI thread if backend.start() raises."""
        self._log_panel.error(f"Backend init failed: {exc}")
        self._status_bar.set_message("Backend init failed — check logs")
        show_error(
            self,
            title="Backend Initialisation Failed",
            message="The backend could not start. Some features may be unavailable.",
            exc=exc,
        )

    # ── Lifecycle ─────────────────────────────────────────────────────

    def _on_close(self) -> None:
        """Cleanup before exit."""
        try:
            self._log_panel.info("Shutting down…")
            # Tear down backend (fire-and-forget on the async loop)
            if self.backend.is_ready:
                self.async_handler.run_async(self.backend.shutdown())
            self.async_handler.shutdown()
        except Exception:
            pass  # best-effort cleanup — never block exit
        self.destroy()

    def run(self) -> None:
        """Start the main event loop (blocking)."""
        self.mainloop()
