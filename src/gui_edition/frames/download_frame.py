"""DownloadFrame — 7-tab download hub.

Tabs:
  Account / Link / Mix        — URL text input (both platforms)
  Live                        — URL text input (both platforms)
  Collection                  — action buttons, Douyin-only, cookie required
  Data                        — comment / user URL input + Hot button, Douyin-only
  Search                      — keyword + params dropdowns, Douyin-only
"""

from __future__ import annotations

from pathlib import Path
from tkinter import filedialog
from typing import TYPE_CHECKING, Dict, Optional

import customtkinter as ctk

from ..download_manager import DownloadManager, TaskInfo, TaskStatus
from ..theme import Theme
from ..widgets import ProgressCard

if TYPE_CHECKING:
    pass

__all__ = ["DownloadFrame"]


# ── helpers ──────────────────────────────────────────────────────────────────

_PLATFORMS = ["Douyin", "TikTok"]

# Tabs that only work with Douyin
_DOUYIN_ONLY_TABS = {"Collection", "Data", "Search"}


# ═══════════════════════════════════════════════════════════════════════════
#  Reusable tab widget: URL text area + Load .txt + Start
# ═══════════════════════════════════════════════════════════════════════════


class _DownloadTab(ctk.CTkFrame):
    """Reusable tab body: URL text area + Load .txt + Start."""

    def __init__(
        self,
        master,
        tab_name: str,
        placeholder: str = "",
        on_start=None,
        start_label: str = "▶  Start Download",
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._tab_name = tab_name
        self._on_start = on_start

        self.grid_columnconfigure(0, weight=1)

        # ── Label ─────────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text=tab_name,
            font=Theme.FONT_H3,
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=Theme.PAD_MD, pady=(Theme.PAD_MD, Theme.PAD_SM))

        # ── URL text area ─────────────────────────────────────────────
        self._textbox = ctk.CTkTextbox(
            self,
            height=120,
            font=Theme.FONT_MONO,
            fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY,
            border_width=1,
            border_color=Theme.BG_HOVER,
            corner_radius=Theme.RADIUS_SM,
            wrap="word",
        )
        self._textbox.grid(
            row=1, column=0, sticky="ew",
            padx=Theme.PAD_MD, pady=(0, Theme.PAD_SM),
        )
        if placeholder:
            self._textbox.insert("1.0", placeholder)
            self._textbox.bind("<FocusIn>", self._clear_placeholder)

        # ── Button row ────────────────────────────────────────────────
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=Theme.PAD_MD, pady=(0, Theme.PAD_MD))
        btn_row.grid_columnconfigure(1, weight=1)

        self._load_btn = ctk.CTkButton(
            btn_row,
            text="📂  Load .txt",
            width=120,
            height=32,
            font=Theme.FONT_BODY,
            fg_color=Theme.BG_HOVER,
            hover_color=Theme.ACCENT_DARK,
            corner_radius=Theme.RADIUS_SM,
            command=self._load_txt,
        )
        self._load_btn.grid(row=0, column=0, sticky="w")

        self._start_btn = ctk.CTkButton(
            btn_row,
            text=start_label,
            width=160,
            height=36,
            font=Theme.FONT_H3,
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            corner_radius=Theme.RADIUS_MD,
            command=self._on_start_click,
        )
        self._start_btn.grid(row=0, column=2, sticky="e")

        self._placeholder = placeholder

    # ── helpers ────────────────────────────────────────────────────────

    def _clear_placeholder(self, _event=None):
        current = self._textbox.get("1.0", "end").strip()
        if current == self._placeholder:
            self._textbox.delete("1.0", "end")

    def _load_txt(self):
        path = filedialog.askopenfilename(
            title="Select URL list",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path and Path(path).is_file():
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read().strip()
            if content:
                self._clear_placeholder()
                self._textbox.delete("1.0", "end")
                self._textbox.insert("1.0", content)

    def get_urls(self) -> list[str]:
        """Parse non-empty lines from the text area."""
        raw = self._textbox.get("1.0", "end").strip()
        if raw == self._placeholder:
            return []
        return [ln.strip() for ln in raw.splitlines() if ln.strip()]

    def _on_start_click(self):
        urls = self.get_urls()
        if urls and self._on_start:
            self._on_start(self._tab_name.lower(), urls)


# ═══════════════════════════════════════════════════════════════════════════
#  _CollectionTab — 3 action buttons (Douyin-only, cookie required)
# ═══════════════════════════════════════════════════════════════════════════


class _CollectionTab(ctk.CTkFrame):
    """Collection tab: Saved Posts / Folder Favorites / Saved Music.

    These features need a valid Douyin cookie and take no URL input.
    """

    _ACTIONS = [
        ("collection",       "📂  Saved Posts",       "Download saved/liked posts"),
        ("collects",         "📁  Folder Favorites",  "Download posts from favourite folders"),
        ("collection_music", "🎵  Saved Music",       "Download saved music tracks"),
    ]

    def __init__(self, master, on_action=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_action = on_action
        self.grid_columnconfigure(0, weight=1)

        # ── Header ────────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="Collection",
            font=Theme.FONT_H3,
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=Theme.PAD_MD, pady=(Theme.PAD_MD, Theme.PAD_SM))

        # ── Cookie warning ────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="⚠  Requires a valid Douyin cookie (set in Settings tab)",
            font=Theme.FONT_SMALL,
            text_color=Theme.WARNING,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=Theme.PAD_MD, pady=(0, Theme.PAD_SM))

        # ── Action cards ──────────────────────────────────────────────
        for idx, (action_id, btn_text, desc_text) in enumerate(self._ACTIONS):
            card = ctk.CTkFrame(
                self,
                fg_color=Theme.BG_INPUT,
                corner_radius=Theme.RADIUS_SM,
            )
            card.grid(
                row=idx + 2, column=0, sticky="ew",
                padx=Theme.PAD_MD, pady=(0, Theme.PAD_SM),
            )
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkButton(
                card,
                text=btn_text,
                width=200,
                height=40,
                font=Theme.FONT_BODY,
                fg_color=Theme.ACCENT,
                hover_color=Theme.ACCENT_HOVER,
                corner_radius=Theme.RADIUS_SM,
                command=lambda a=action_id: self._on_click(a),
            ).grid(row=0, column=0, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="w")

            ctk.CTkLabel(
                card,
                text=desc_text,
                font=Theme.FONT_SMALL,
                text_color=Theme.TEXT_SECONDARY,
                anchor="w",
            ).grid(row=0, column=1, padx=Theme.PAD_SM, sticky="w")

    def _on_click(self, action_id: str):
        if self._on_action:
            self._on_action(action_id, [])


# ═══════════════════════════════════════════════════════════════════════════
#  _DataTab — Comment / User (URL input) + Hot/Trending (no input)
# ═══════════════════════════════════════════════════════════════════════════


class _DataTab(ctk.CTkFrame):
    """Data collection tab (Douyin-only).

    Sub-modes: Comment, User (take URL input), Hot/Trending (no input).
    """

    _MODES = ["Comment", "User"]

    def __init__(self, master, on_start=None, on_hot=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_start = on_start
        self._on_hot = on_hot
        self.grid_columnconfigure(0, weight=1)

        # ── Header ────────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="Data Collection",
            font=Theme.FONT_H3,
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=Theme.PAD_MD, pady=(Theme.PAD_MD, Theme.PAD_SM))

        # ── Sub-mode selector ─────────────────────────────────────────
        self._mode_seg = ctk.CTkSegmentedButton(
            self,
            values=self._MODES,
            font=Theme.FONT_BODY,
            selected_color=Theme.ACCENT,
            selected_hover_color=Theme.ACCENT_HOVER,
            unselected_color=Theme.BG_HOVER,
            unselected_hover_color=Theme.BG_SECONDARY,
            text_color=Theme.TEXT_PRIMARY,
            width=260,
        )
        self._mode_seg.set("Comment")
        self._mode_seg.grid(
            row=1, column=0, sticky="w",
            padx=Theme.PAD_MD, pady=(0, Theme.PAD_SM),
        )

        # ── URL text area ─────────────────────────────────────────────
        self._textbox = ctk.CTkTextbox(
            self,
            height=100,
            font=Theme.FONT_MONO,
            fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY,
            border_width=1,
            border_color=Theme.BG_HOVER,
            corner_radius=Theme.RADIUS_SM,
            wrap="word",
        )
        self._textbox.grid(
            row=2, column=0, sticky="ew",
            padx=Theme.PAD_MD, pady=(0, Theme.PAD_SM),
        )
        self._placeholder = "Paste post/account URLs here (one per line)…"
        self._textbox.insert("1.0", self._placeholder)
        self._textbox.bind("<FocusIn>", self._clear_placeholder)

        # ── Button row ────────────────────────────────────────────────
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=3, column=0, sticky="ew", padx=Theme.PAD_MD, pady=(0, Theme.PAD_SM))
        btn_row.grid_columnconfigure(1, weight=1)

        # Load .txt
        ctk.CTkButton(
            btn_row,
            text="📂  Load .txt",
            width=120,
            height=32,
            font=Theme.FONT_BODY,
            fg_color=Theme.BG_HOVER,
            hover_color=Theme.ACCENT_DARK,
            corner_radius=Theme.RADIUS_SM,
            command=self._load_txt,
        ).grid(row=0, column=0, sticky="w")

        # Start collect
        ctk.CTkButton(
            btn_row,
            text="▶  Collect Data",
            width=160,
            height=36,
            font=Theme.FONT_H3,
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            corner_radius=Theme.RADIUS_MD,
            command=self._on_collect_click,
        ).grid(row=0, column=2, sticky="e")

        # ── Hot / Trending button ─────────────────────────────────────
        sep = ctk.CTkFrame(self, fg_color=Theme.BG_HOVER, height=1)
        sep.grid(row=4, column=0, sticky="ew", padx=Theme.PAD_MD, pady=Theme.PAD_SM)

        hot_row = ctk.CTkFrame(self, fg_color="transparent")
        hot_row.grid(row=5, column=0, sticky="ew", padx=Theme.PAD_MD, pady=(0, Theme.PAD_MD))
        hot_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            hot_row,
            text="🔥  Hot / Trending — no input needed",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            hot_row,
            text="Fetch Hot",
            width=120,
            height=32,
            font=Theme.FONT_BODY,
            fg_color=Theme.WARNING,
            hover_color=Theme.ACCENT_HOVER,
            text_color=Theme.BG_PRIMARY,
            corner_radius=Theme.RADIUS_SM,
            command=self._on_hot_click,
        ).grid(row=0, column=2, sticky="e")

    # ── helpers ────────────────────────────────────────────────────────

    def _clear_placeholder(self, _event=None):
        current = self._textbox.get("1.0", "end").strip()
        if current == self._placeholder:
            self._textbox.delete("1.0", "end")

    def _load_txt(self):
        path = filedialog.askopenfilename(
            title="Select URL list",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path and Path(path).is_file():
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read().strip()
            if content:
                self._clear_placeholder()
                self._textbox.delete("1.0", "end")
                self._textbox.insert("1.0", content)

    def get_urls(self) -> list[str]:
        raw = self._textbox.get("1.0", "end").strip()
        if raw == self._placeholder:
            return []
        return [ln.strip() for ln in raw.splitlines() if ln.strip()]

    def _on_collect_click(self):
        urls = self.get_urls()
        mode = self._mode_seg.get().lower()  # "comment" or "user"
        if urls and self._on_start:
            self._on_start(mode, urls)

    def _on_hot_click(self):
        if self._on_hot:
            self._on_hot("hot", [])


# ═══════════════════════════════════════════════════════════════════════════
#  _SearchTab — keyword + parameters (Douyin-only)
# ═══════════════════════════════════════════════════════════════════════════


class _SearchTab(ctk.CTkFrame):
    """Search tab with keyword, channel, and filter parameters (Douyin-only)."""

    _CHANNELS = ["General", "Video", "User", "Live"]

    _SORT_TYPES = ["Default", "Most Liked", "Newest"]
    _PUBLISH_TIMES = ["Any Time", "Last Day", "Last Week", "Last 6 Months"]
    _DURATIONS = ["Any Duration", "< 1 min", "1–5 min", "> 5 min"]

    def __init__(self, master, on_search=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_search = on_search
        self.grid_columnconfigure(0, weight=1)

        # ── Header ────────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="Search",
            font=Theme.FONT_H3,
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=Theme.PAD_MD, pady=(Theme.PAD_MD, Theme.PAD_SM))

        # ── Search channel ────────────────────────────────────────────
        channel_row = ctk.CTkFrame(self, fg_color="transparent")
        channel_row.grid(row=1, column=0, sticky="ew", padx=Theme.PAD_MD, pady=(0, Theme.PAD_SM))

        ctk.CTkLabel(
            channel_row,
            text="Channel:",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_SECONDARY,
            width=80,
        ).pack(side="left")

        self._channel_seg = ctk.CTkSegmentedButton(
            channel_row,
            values=self._CHANNELS,
            font=Theme.FONT_BODY,
            selected_color=Theme.ACCENT,
            selected_hover_color=Theme.ACCENT_HOVER,
            unselected_color=Theme.BG_HOVER,
            unselected_hover_color=Theme.BG_SECONDARY,
            text_color=Theme.TEXT_PRIMARY,
            width=340,
        )
        self._channel_seg.set("General")
        self._channel_seg.pack(side="left", padx=(Theme.PAD_SM, 0))

        # ── Keyword input ─────────────────────────────────────────────
        kw_row = ctk.CTkFrame(self, fg_color="transparent")
        kw_row.grid(row=2, column=0, sticky="ew", padx=Theme.PAD_MD, pady=(0, Theme.PAD_SM))
        kw_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            kw_row,
            text="Keyword:",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_SECONDARY,
            width=80,
        ).grid(row=0, column=0, sticky="w")

        self._keyword_entry = ctk.CTkEntry(
            kw_row,
            placeholder_text="Enter search keyword…",
            font=Theme.FONT_BODY,
            fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY,
            border_color=Theme.BG_HOVER,
            corner_radius=Theme.RADIUS_SM,
            height=34,
        )
        self._keyword_entry.grid(row=0, column=1, sticky="ew", padx=(Theme.PAD_SM, 0))

        # ── Filter row ────────────────────────────────────────────────
        filter_row = ctk.CTkFrame(self, fg_color="transparent")
        filter_row.grid(row=3, column=0, sticky="ew", padx=Theme.PAD_MD, pady=(0, Theme.PAD_SM))

        # Pages
        ctk.CTkLabel(
            filter_row, text="Pages:", font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_SECONDARY,
        ).pack(side="left")
        self._pages_var = ctk.StringVar(value="1")
        ctk.CTkEntry(
            filter_row,
            textvariable=self._pages_var,
            width=50, height=30,
            font=Theme.FONT_SMALL,
            fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY,
            border_color=Theme.BG_HOVER,
            corner_radius=Theme.RADIUS_SM,
        ).pack(side="left", padx=(4, Theme.PAD_MD))

        # Sort
        ctk.CTkLabel(
            filter_row, text="Sort:", font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_SECONDARY,
        ).pack(side="left")
        self._sort_menu = ctk.CTkOptionMenu(
            filter_row,
            values=self._SORT_TYPES,
            font=Theme.FONT_SMALL,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BG_HOVER,
            button_hover_color=Theme.ACCENT_DARK,
            text_color=Theme.TEXT_PRIMARY,
            width=120, height=30,
        )
        self._sort_menu.pack(side="left", padx=(4, Theme.PAD_MD))

        # Publish time
        ctk.CTkLabel(
            filter_row, text="Time:", font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_SECONDARY,
        ).pack(side="left")
        self._time_menu = ctk.CTkOptionMenu(
            filter_row,
            values=self._PUBLISH_TIMES,
            font=Theme.FONT_SMALL,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BG_HOVER,
            button_hover_color=Theme.ACCENT_DARK,
            text_color=Theme.TEXT_PRIMARY,
            width=130, height=30,
        )
        self._time_menu.pack(side="left", padx=(4, Theme.PAD_MD))

        # Duration
        ctk.CTkLabel(
            filter_row, text="Duration:", font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_SECONDARY,
        ).pack(side="left")
        self._duration_menu = ctk.CTkOptionMenu(
            filter_row,
            values=self._DURATIONS,
            font=Theme.FONT_SMALL,
            fg_color=Theme.BG_INPUT,
            button_color=Theme.BG_HOVER,
            button_hover_color=Theme.ACCENT_DARK,
            text_color=Theme.TEXT_PRIMARY,
            width=120, height=30,
        )
        self._duration_menu.pack(side="left", padx=(4, 0))

        # ── Start button ──────────────────────────────────────────────
        ctk.CTkButton(
            self,
            text="🔍  Search",
            width=160,
            height=36,
            font=Theme.FONT_H3,
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            corner_radius=Theme.RADIUS_MD,
            command=self._on_search_click,
        ).grid(row=4, column=0, sticky="e", padx=Theme.PAD_MD, pady=(0, Theme.PAD_MD))

    # ── helpers ────────────────────────────────────────────────────────

    def get_search_params(self) -> dict:
        """Return search parameters as a dict for the backend."""
        channel_idx = self._CHANNELS.index(self._channel_seg.get())
        try:
            pages = max(1, int(self._pages_var.get()))
        except ValueError:
            pages = 1
        return {
            "channel": channel_idx,
            "keyword": self._keyword_entry.get().strip(),
            "pages": pages,
            "sort_type": self._SORT_TYPES.index(self._sort_menu.get()),
            "publish_time": self._PUBLISH_TIMES.index(self._time_menu.get()),
            "duration": self._DURATIONS.index(self._duration_menu.get()),
        }

    def _on_search_click(self):
        params = self.get_search_params()
        if not params["keyword"]:
            return
        if self._on_search:
            self._on_search("search", params)


# ═══════════════════════════════════════════════════════════════════════════
#  _UnavailableOverlay — shown on Douyin-only tabs when TikTok is selected
# ═══════════════════════════════════════════════════════════════════════════


class _UnavailableOverlay(ctk.CTkFrame):
    """Semi-transparent overlay: 'Not available for TikTok'."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=Theme.BG_PRIMARY, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        ctk.CTkLabel(
            self,
            text="⛔  This feature is available for Douyin only",
            font=Theme.FONT_H3,
            text_color=Theme.TEXT_MUTED,
        ).grid(row=0, column=0)


# ═══════════════════════════════════════════════════════════════════════════
#  DownloadFrame
# ═══════════════════════════════════════════════════════════════════════════


class DownloadFrame(ctk.CTkFrame):
    """Main download tab container with 7 tabs."""

    def __init__(self, master, app_ref=None, **kwargs):
        super().__init__(master, fg_color=Theme.BG_PRIMARY, corner_radius=0, **kwargs)
        self._app = app_ref
        self._platform = "Douyin"
        self._cards: Dict[str, ProgressCard] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)   # tabs stretch
        self.grid_rowconfigure(2, weight=0)   # queue area

        # ── Header: platform toggle ───────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=Theme.PAD_LG, pady=(Theme.PAD_LG, 0))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="⬇  Download",
            font=Theme.FONT_H1,
            text_color=Theme.TEXT_PRIMARY,
        ).grid(row=0, column=0, sticky="w")

        self._platform_seg = ctk.CTkSegmentedButton(
            header,
            values=_PLATFORMS,
            font=Theme.FONT_BODY,
            selected_color=Theme.ACCENT,
            selected_hover_color=Theme.ACCENT_HOVER,
            unselected_color=Theme.BG_CARD,
            unselected_hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            command=self._on_platform_change,
            width=200,
        )
        self._platform_seg.set("Douyin")
        self._platform_seg.grid(row=0, column=1, sticky="e")

        # ── Tabview ───────────────────────────────────────────────────
        self._tabview = ctk.CTkTabview(
            self,
            fg_color=Theme.BG_CARD,
            segmented_button_fg_color=Theme.BG_SECONDARY,
            segmented_button_selected_color=Theme.ACCENT,
            segmented_button_selected_hover_color=Theme.ACCENT_HOVER,
            segmented_button_unselected_color=Theme.BG_SECONDARY,
            segmented_button_unselected_hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=Theme.RADIUS_LG,
        )
        self._tabview.grid(
            row=1, column=0, sticky="nsew",
            padx=Theme.PAD_LG, pady=Theme.PAD_MD,
        )

        # ── Create all 7 tabs ─────────────────────────────────────────
        tab_names = ["Account", "Link", "Mix", "Live", "Collection", "Data", "Search"]
        for t in tab_names:
            self._tabview.add(t)

        # --- Account / Link / Mix / Live  (URL-based, both platforms) --
        self._tab_account = _DownloadTab(
            self._tabview.tab("Account"),
            tab_name="Account",
            placeholder="Paste account profile URLs here (one per line)…",
            on_start=self._on_start,
        )
        self._tab_account.pack(fill="both", expand=True)

        self._tab_link = _DownloadTab(
            self._tabview.tab("Link"),
            tab_name="Link",
            placeholder="Paste video/post URLs here (one per line)…",
            on_start=self._on_start,
        )
        self._tab_link.pack(fill="both", expand=True)

        self._tab_mix = _DownloadTab(
            self._tabview.tab("Mix"),
            tab_name="Mix",
            placeholder="Paste mix / playlist URLs here (one per line)…",
            on_start=self._on_start,
        )
        self._tab_mix.pack(fill="both", expand=True)

        self._tab_live = _DownloadTab(
            self._tabview.tab("Live"),
            tab_name="Live",
            placeholder="Paste livestream URLs here (one per line)…",
            on_start=self._on_start,
            start_label="▶  Get Livestream",
        )
        self._tab_live.pack(fill="both", expand=True)

        # --- Collection (Douyin-only, cookie-based) ---
        self._tab_collection = _CollectionTab(
            self._tabview.tab("Collection"),
            on_action=self._on_start,
        )
        self._tab_collection.pack(fill="both", expand=True)

        # --- Data (Douyin-only) ---
        self._tab_data = _DataTab(
            self._tabview.tab("Data"),
            on_start=self._on_start,
            on_hot=self._on_start,
        )
        self._tab_data.pack(fill="both", expand=True)

        # --- Search (Douyin-only) ---
        self._tab_search = _SearchTab(
            self._tabview.tab("Search"),
            on_search=self._on_search,
        )
        self._tab_search.pack(fill="both", expand=True)

        # ── Overlays for Douyin-only tabs ─────────────────────────────
        self._overlays: Dict[str, _UnavailableOverlay] = {}
        for tab_name in _DOUYIN_ONLY_TABS:
            overlay = _UnavailableOverlay(self._tabview.tab(tab_name))
            self._overlays[tab_name] = overlay
            # Initially hidden (Douyin is selected)

        # ── Queue area (scrollable) ──────────────────────────────────
        queue_label = ctk.CTkLabel(
            self,
            text="Download Queue",
            font=Theme.FONT_H3,
            text_color=Theme.TEXT_SECONDARY,
            anchor="w",
        )
        queue_label.grid(
            row=2, column=0, sticky="w",
            padx=Theme.PAD_LG, pady=(Theme.PAD_SM, 0),
        )

        self._queue_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=Theme.BG_SECONDARY,
            corner_radius=Theme.RADIUS_MD,
            height=180,
        )
        self._queue_scroll.grid(
            row=3, column=0, sticky="nsew",
            padx=Theme.PAD_LG, pady=(Theme.PAD_XS, Theme.PAD_LG),
        )
        self._queue_scroll.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # ── Empty-queue placeholder ──────────────────────────────────
        self._empty_label = ctk.CTkLabel(
            self._queue_scroll,
            text="No active downloads — paste URLs above and press Start",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_MUTED,
        )
        self._empty_label.grid(row=0, column=0, pady=Theme.PAD_XL)

        # ── Download manager ─────────────────────────────────────────
        ah = getattr(app_ref, "async_handler", None)
        if ah:
            self._manager = DownloadManager(ah, on_card_update=self._update_card)
        else:
            self._manager: Optional[DownloadManager] = None

    # ── platform toggle ──────────────────────────────────────────────

    def _on_platform_change(self, value: str):
        self._platform = value
        is_tiktok = value == "TikTok"

        for tab_name, overlay in self._overlays.items():
            if is_tiktok:
                overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            else:
                overlay.place_forget()

    # ── start download / action ──────────────────────────────────────

    def _on_start(self, mode: str, urls: list):
        """Called by tab buttons.  ``mode`` is 'account'/'link'/'mix'/'live'/
        'collection'/'collects'/'collection_music'/'comment'/'user'/'hot'."""
        platform = self._platform.lower()
        n = len(urls)
        if n:
            label = f"{self._platform} {mode.title()} ({n} URL{'s' if n > 1 else ''})"
        else:
            label = f"{self._platform} {mode.title()}"

        if self._manager is None:
            self._log(f"⚠ Backend not initialised — cannot start {label}")
            return

        info = self._manager.submit(
            mode=mode,
            platform=platform,
            urls=urls,
            label=label,
            backend_coro_factory=None,  # placeholder — Phase 7
        )
        self._log(f"📥 Queued: {label} [{info.task_id}]")

    def _on_search(self, _mode: str, params: dict):
        """Called by SearchTab.  Params is a dict with keyword, channel, etc."""
        platform = self._platform.lower()
        keyword = params.get("keyword", "")
        channel_names = _SearchTab._CHANNELS
        channel = params.get("channel", 0)
        ch_name = channel_names[channel] if channel < len(channel_names) else "General"
        label = f"{self._platform} Search: \"{keyword}\" ({ch_name})"

        if self._manager is None:
            self._log(f"⚠ Backend not initialised — cannot start {label}")
            return

        info = self._manager.submit(
            mode="search",
            platform=platform,
            urls=[],
            label=label,
            backend_coro_factory=None,  # placeholder — Phase 7
        )
        self._log(f"🔍 Queued: {label} [{info.task_id}]")

    # ── progress card management ─────────────────────────────────────

    def _update_card(self, info: TaskInfo):
        """Callback from DownloadManager — runs on main thread."""
        card = self._cards.get(info.task_id)

        if card is None:
            # Remove empty-queue placeholder on first task
            self._empty_label.grid_forget()

            card = ProgressCard(self._queue_scroll, filename=info.label)
            card.grid(
                row=len(self._cards),
                column=0,
                sticky="ew",
                pady=(0, Theme.PAD_XS),
            )
            self._cards[info.task_id] = card

        # Update card state from TaskInfo
        match info.status:
            case TaskStatus.QUEUED:
                card.set_status("Waiting…")
            case TaskStatus.RUNNING:
                card.set_status("Downloading…", Theme.ACCENT)
            case TaskStatus.DONE:
                card.mark_done()
            case TaskStatus.ERROR:
                card.mark_error(info.error_msg or "Error")
            case TaskStatus.CANCELLED:
                card.set_status("Cancelled", Theme.WARNING)

    # ── logging shortcut ─────────────────────────────────────────────

    def _log(self, msg: str):
        console = getattr(self._app, "console", None)
        if console:
            console.info(msg)
