"""MonitorFrame — Clipboard monitoring panel.

Polls the system clipboard for Douyin/TikTok links and routes them
to separate queues with live counters and a log panel.
"""

from __future__ import annotations

import tkinter as tk
from datetime import datetime
from typing import TYPE_CHECKING, List

import customtkinter as ctk

from ..theme import Theme
from ..widgets import LogPanel

if TYPE_CHECKING:
    pass

__all__ = ["MonitorFrame"]

# ── Keyword matchers ─────────────────────────────────────────────────────────

_DOUYIN_KEYWORDS = ("douyin.com", "douyin", "iesdouyin")
_TIKTOK_KEYWORDS = ("tiktok.com", "tiktok")

_POLL_MS = 1000  # clipboard poll interval


class MonitorFrame(ctk.CTkFrame):
    """Clipboard monitor — auto-detects Douyin/TikTok links and queues them."""

    def __init__(self, master, app_ref=None, **kwargs):
        super().__init__(master, fg_color=Theme.BG_PRIMARY, corner_radius=0, **kwargs)
        self._app = app_ref

        # state
        self._monitoring = False
        self._poll_id: str | None = None
        self._clipboard_cache = ""
        self._dy_count = 0
        self._tk_count = 0
        self._total_links = 0

        self.grid_columnconfigure(0, weight=1)
        # row 0: header + toggle
        # row 1: stats bar
        # row 2: log panel (expanding)
        # row 3: bottom controls
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_stats_bar()
        self._build_log_panel()
        self._build_controls()

    # ── Header ───────────────────────────────────────────────────────────────

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=Theme.PAD_LG, pady=(Theme.PAD_LG, Theme.PAD_SM), sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="📋  Clipboard Monitor",
            font=Theme.FONT_H1,
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        # ── Toggle button ─────────────────────────────────────────────
        self._toggle_btn = ctk.CTkButton(
            header,
            text="▶  Start Monitoring",
            width=180,
            height=36,
            font=Theme.FONT_H3,
            fg_color=Theme.SUCCESS,
            hover_color="#00C864",
            text_color=Theme.BG_PRIMARY,
            corner_radius=Theme.RADIUS_MD,
            command=self._toggle_monitoring,
        )
        self._toggle_btn.grid(row=0, column=1, sticky="e")

    # ── Statistics bar ───────────────────────────────────────────────────────

    def _build_stats_bar(self) -> None:
        bar = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MD, height=50)
        bar.grid(row=1, column=0, padx=Theme.PAD_LG, pady=(0, Theme.PAD_SM), sticky="ew")
        bar.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Status indicator
        self._status_label = ctk.CTkLabel(
            bar,
            text="⏸  Stopped",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_MUTED,
            anchor="w",
        )
        self._status_label.grid(row=0, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")

        # Douyin counter
        self._dy_label = ctk.CTkLabel(
            bar,
            text="🇨🇳 Douyin: 0",
            font=Theme.FONT_BODY,
            text_color=Theme.INFO,
        )
        self._dy_label.grid(row=0, column=1, padx=Theme.PAD_SM)

        # TikTok counter
        self._tk_label = ctk.CTkLabel(
            bar,
            text="🌍 TikTok: 0",
            font=Theme.FONT_BODY,
            text_color=Theme.ACCENT,
        )
        self._tk_label.grid(row=0, column=2, padx=Theme.PAD_SM)

        # Total counter
        self._total_label = ctk.CTkLabel(
            bar,
            text="Total: 0",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_SECONDARY,
        )
        self._total_label.grid(row=0, column=3, padx=Theme.PAD_MD, sticky="e")

    # ── Log panel ────────────────────────────────────────────────────────────

    def _build_log_panel(self) -> None:
        self._log_panel = LogPanel(self, height=300)
        self._log_panel._header.configure(text="📡  Monitor Log")
        self._log_panel.grid(
            row=2, column=0,
            padx=Theme.PAD_LG, pady=(0, Theme.PAD_SM),
            sticky="nsew",
        )

    # ── Bottom controls ──────────────────────────────────────────────────────

    def _build_controls(self) -> None:
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=3, column=0, padx=Theme.PAD_LG, pady=(0, Theme.PAD_LG), sticky="ew")
        controls.grid_columnconfigure(1, weight=1)

        # Clear log
        ctk.CTkButton(
            controls,
            text="🗑  Clear Log",
            width=120,
            height=32,
            font=Theme.FONT_BODY,
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            corner_radius=Theme.RADIUS_SM,
            command=self._clear_all,
        ).grid(row=0, column=0, sticky="w")

        # Reset counters
        ctk.CTkButton(
            controls,
            text="🔄  Reset Counters",
            width=140,
            height=32,
            font=Theme.FONT_BODY,
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            corner_radius=Theme.RADIUS_SM,
            command=self._reset_counters,
        ).grid(row=0, column=1, padx=(Theme.PAD_SM, 0), sticky="w")

        # Info label
        ctk.CTkLabel(
            controls,
            text="Copy any Douyin/TikTok link to auto-detect",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_MUTED,
        ).grid(row=0, column=2, sticky="e")

    # ── Toggle logic ─────────────────────────────────────────────────────────

    def _toggle_monitoring(self) -> None:
        if self._monitoring:
            self._stop_monitoring()
        else:
            self._start_monitoring()

    def _start_monitoring(self) -> None:
        self._monitoring = True
        self._clipboard_cache = self._safe_clipboard_get()

        # Update UI
        self._toggle_btn.configure(
            text="⏹  Stop Monitoring",
            fg_color=Theme.ERROR,
            hover_color="#E0143C",
        )
        self._status_label.configure(text="🟢  Listening…", text_color=Theme.SUCCESS)
        self._log_panel.info("Clipboard monitoring started. Waiting for links…")

        # Start polling
        self._poll_clipboard()

    def _stop_monitoring(self) -> None:
        self._monitoring = False
        if self._poll_id is not None:
            self.after_cancel(self._poll_id)
            self._poll_id = None

        # Update UI
        self._toggle_btn.configure(
            text="▶  Start Monitoring",
            fg_color=Theme.SUCCESS,
            hover_color="#00C864",
        )
        self._status_label.configure(text="⏸  Stopped", text_color=Theme.TEXT_MUTED)
        self._log_panel.warning("Clipboard monitoring stopped.")

    # ── Clipboard polling ────────────────────────────────────────────────────

    def _poll_clipboard(self) -> None:
        """Periodic check of system clipboard for Douyin/TikTok links."""
        if not self._monitoring:
            return

        current = self._safe_clipboard_get()

        if current and current != self._clipboard_cache:
            self._clipboard_cache = current
            self._process_text(current)

        self._poll_id = self.after(_POLL_MS, self._poll_clipboard)

    def _safe_clipboard_get(self) -> str:
        """Read clipboard, returning empty string on failure."""
        try:
            return self.clipboard_get()
        except (tk.TclError, Exception):
            return ""

    # ── Link detection ───────────────────────────────────────────────────────

    def _process_text(self, text: str) -> None:
        """Split text into tokens, classify as Douyin / TikTok links."""
        tokens = text.split()
        dy_links: List[str] = []
        tk_links: List[str] = []

        for token in tokens:
            lower = token.lower()
            if any(kw in lower for kw in _DOUYIN_KEYWORDS):
                dy_links.append(token)
            elif any(kw in lower for kw in _TIKTOK_KEYWORDS):
                tk_links.append(token)

        if not dy_links and not tk_links:
            return  # no relevant links found — ignore

        # Log & count Douyin links
        for link in dy_links:
            self._dy_count += 1
            self._total_links += 1
            self._log_panel.append(f"🇨🇳 Douyin  │ {link}", "info")

        # Log & count TikTok links
        for link in tk_links:
            self._tk_count += 1
            self._total_links += 1
            self._log_panel.append(f"🌍 TikTok  │ {link}", "accent")

        self._update_counters()

        # TODO Phase 7: submit to DownloadManager
        # if self._app:
        #     mgr = self._app.download_manager
        #     for link in dy_links:
        #         mgr.submit("detail", {"urls": link}, tiktok=False)
        #     for link in tk_links:
        #         mgr.submit("detail", {"urls": link}, tiktok=True)

    # ── Counter helpers ──────────────────────────────────────────────────────

    def _update_counters(self) -> None:
        self._dy_label.configure(text=f"🇨🇳 Douyin: {self._dy_count}")
        self._tk_label.configure(text=f"🌍 TikTok: {self._tk_count}")
        self._total_label.configure(text=f"Total: {self._total_links}")

    def _reset_counters(self) -> None:
        self._dy_count = 0
        self._tk_count = 0
        self._total_links = 0
        self._update_counters()
        self._log_panel.info("Counters reset.")

    def _clear_all(self) -> None:
        self._log_panel.clear()

    # ── Cleanup ──────────────────────────────────────────────────────────────

    def destroy(self) -> None:
        """Ensure polling stops on frame destruction."""
        self._monitoring = False
        if self._poll_id is not None:
            self.after_cancel(self._poll_id)
            self._poll_id = None
        super().destroy()
