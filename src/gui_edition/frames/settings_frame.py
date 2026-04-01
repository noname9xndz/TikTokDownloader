"""SettingsFrame — full configuration panel for DouK-Downloader.

Sections:
  1. Cookie Management    (Douyin + TikTok paste / browser import)
  2. Directory & Format   (output folder, storage format, name template)
  3. Download Options     (platform toggles, type filter, folder mode, music)
  4. Advanced             (proxy, chunk, timeout, retry, record, logger, language)
  5. Text Replacement     (old → new pairs applied to file names)
  6. Download Records     (delete download records by ID or "ALL")

Settings are read from / written to ``settings.json`` via
``src.config.settings.Settings``.
"""

from __future__ import annotations

import json
from pathlib import Path
from tkinter import filedialog
from typing import Any, Callable, Dict, Optional

import customtkinter as ctk

from ..theme import Theme
from src.custom import PROJECT_ROOT

__all__ = ["SettingsFrame"]

# ── helpers ──────────────────────────────────────────────────────────────────

_SETTINGS_PATH = PROJECT_ROOT / "settings.json"
_ENCODE = "UTF-8-SIG"

_STORAGE_FORMATS = ["", "csv", "xlsx"]
_LANGUAGES = [("中文 (简体)", "zh_CN"), ("English", "en_US")]
_BROWSERS = ["chrome", "chromium", "opera", "opera_gx", "brave",
             "edge", "vivaldi", "firefox", "librewolf", "safari"]


def _read_settings() -> dict:
    """Read settings.json and return the dict (or defaults)."""
    try:
        if _SETTINGS_PATH.exists():
            with _SETTINGS_PATH.open("r", encoding=_ENCODE) as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def _save_settings(data: dict) -> None:
    """Write *data* to settings.json."""
    with _SETTINGS_PATH.open("w", encoding=_ENCODE) as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ── reusable row builders ────────────────────────────────────────────────────

def _section_label(parent: ctk.CTkFrame, text: str) -> ctk.CTkLabel:
    lbl = ctk.CTkLabel(
        parent, text=text,
        font=Theme.FONT_H3,
        text_color=Theme.ACCENT,
        anchor="w",
    )
    return lbl


def _field_row(
    parent: ctk.CTkFrame,
    label: str,
    widget_factory: Callable[..., ctk.CTkBaseClass],
    tooltip: str = "",
    **widget_kw,
) -> tuple[ctk.CTkLabel, ctk.CTkBaseClass]:
    """Create *label — widget* in a sub-frame and return both."""
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.grid_columnconfigure(1, weight=1)

    lbl = ctk.CTkLabel(
        row, text=label,
        font=Theme.FONT_BODY,
        text_color=Theme.TEXT_SECONDARY,
        width=180, anchor="w",
    )
    lbl.grid(row=0, column=0, padx=(0, Theme.PAD_SM), sticky="w")

    widget = widget_factory(row, **widget_kw)
    widget.grid(row=0, column=1, sticky="ew")

    if tooltip:
        tip = ctk.CTkLabel(
            row, text=tooltip,
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_MUTED,
            anchor="w",
        )
        tip.grid(row=1, column=1, sticky="w", pady=(2, 0))

    return row, lbl, widget


# ── Main Frame ──────────────────────────────────────────────────────────────

class SettingsFrame(ctk.CTkFrame):
    """Complete settings & configuration panel."""

    def __init__(self, master, app_ref=None, **kwargs):
        super().__init__(master, fg_color=Theme.BG_PRIMARY, corner_radius=0, **kwargs)
        self._app = app_ref
        self._widgets: Dict[str, Any] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # scrollable area
        self.grid_rowconfigure(1, weight=0)  # bottom buttons

        # ── scrollable container ──────────────────────────────────────
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=Theme.BG_PRIMARY,
            scrollbar_button_color=Theme.BG_CARD,
            scrollbar_button_hover_color=Theme.ACCENT,
        )
        self._scroll.grid(row=0, column=0, sticky="nsew", padx=Theme.PAD_MD, pady=Theme.PAD_SM)
        self._scroll.grid_columnconfigure(0, weight=1)

        row_idx = 0

        # ── Section 1: Cookie Management ──────────────────────────────
        row_idx = self._build_cookie_section(row_idx)

        # ── Section 2: Directory & Format ─────────────────────────────
        row_idx = self._build_directory_section(row_idx)

        # ── Section 3: Download Options ───────────────────────────────
        row_idx = self._build_download_section(row_idx)

        # ── Section 4: Advanced ───────────────────────────────────────
        row_idx = self._build_advanced_section(row_idx)

        # ── Section 5: Text Replacement ────────────────────────────────
        row_idx = self._build_text_replacement_section(row_idx)

        # ── Section 6: Download Records ────────────────────────────────
        row_idx = self._build_delete_records_section(row_idx)

        # ── Bottom bar: Save / Reset ──────────────────────────────────
        self._build_bottom_bar()

        # ── Load values ───────────────────────────────────────────────
        self._load_settings()

    # ══════════════════════════════════════════════════════════════════
    # Section builders
    # ══════════════════════════════════════════════════════════════════

    def _build_cookie_section(self, row: int) -> int:
        lbl = _section_label(self._scroll, "🍪  Cookie Management")
        lbl.grid(row=row, column=0, sticky="w", pady=(Theme.PAD_MD, Theme.PAD_SM))
        row += 1

        # Douyin cookie
        fr = ctk.CTkFrame(self._scroll, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MD)
        fr.grid(row=row, column=0, sticky="ew", pady=Theme.PAD_XS)
        fr.grid_columnconfigure(1, weight=1)
        row += 1

        ctk.CTkLabel(fr, text="Douyin Cookie", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_PRIMARY, width=140, anchor="w") \
            .grid(row=0, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")

        self._widgets["cookie_dy"] = ctk.CTkEntry(
            fr, placeholder_text="Paste Douyin cookie here…",
            font=Theme.FONT_MONO, fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY, border_color=Theme.BG_HOVER,
        )
        self._widgets["cookie_dy"].grid(row=0, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="ew")

        btn_row_dy = ctk.CTkFrame(fr, fg_color="transparent")
        btn_row_dy.grid(row=0, column=2, padx=(0, Theme.PAD_SM), pady=Theme.PAD_SM)

        ctk.CTkButton(
            btn_row_dy, text="📋 Paste", width=70, font=Theme.FONT_SMALL,
            fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_HOVER,
            command=lambda: self._paste_clipboard("cookie_dy"),
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            btn_row_dy, text="📋 JSON", width=70, font=Theme.FONT_SMALL,
            fg_color="#7C4DFF", hover_color="#651FFF",
            command=lambda: self._paste_json_cookie("cookie_dy", "douyin"),
        ).pack(side="left")

        # Browser import Douyin
        ctk.CTkLabel(fr, text="Import from browser", font=Theme.FONT_SMALL,
                      text_color=Theme.TEXT_MUTED, anchor="w") \
            .grid(row=1, column=0, padx=Theme.PAD_MD, sticky="w")

        browser_frame_dy = ctk.CTkFrame(fr, fg_color="transparent")
        browser_frame_dy.grid(row=1, column=1, columnspan=2, padx=Theme.PAD_SM,
                              pady=(0, Theme.PAD_SM), sticky="ew")
        browser_frame_dy.grid_columnconfigure(0, weight=1)

        self._widgets["browser_dy"] = ctk.CTkOptionMenu(
            browser_frame_dy, values=_BROWSERS,
            font=Theme.FONT_SMALL, fg_color=Theme.BG_INPUT,
            button_color=Theme.ACCENT, button_hover_color=Theme.ACCENT_HOVER,
            dropdown_fg_color=Theme.BG_CARD, width=160,
        )
        self._widgets["browser_dy"].grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            browser_frame_dy, text="⬇ Import", width=80,
            font=Theme.FONT_SMALL, fg_color=Theme.ACCENT_DARK,
            hover_color=Theme.ACCENT_HOVER,
            command=lambda: self._import_browser_cookie("douyin"),
        ).grid(row=0, column=1, padx=(Theme.PAD_SM, 0))

        # ── TikTok cookie ─────────────────────────────────────────────
        fr2 = ctk.CTkFrame(self._scroll, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MD)
        fr2.grid(row=row, column=0, sticky="ew", pady=Theme.PAD_XS)
        fr2.grid_columnconfigure(1, weight=1)
        row += 1

        ctk.CTkLabel(fr2, text="TikTok Cookie", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_PRIMARY, width=140, anchor="w") \
            .grid(row=0, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")

        self._widgets["cookie_tt"] = ctk.CTkEntry(
            fr2, placeholder_text="Paste TikTok cookie here…",
            font=Theme.FONT_MONO, fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY, border_color=Theme.BG_HOVER,
        )
        self._widgets["cookie_tt"].grid(row=0, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="ew")

        btn_row_tt = ctk.CTkFrame(fr2, fg_color="transparent")
        btn_row_tt.grid(row=0, column=2, padx=(0, Theme.PAD_SM), pady=Theme.PAD_SM)

        ctk.CTkButton(
            btn_row_tt, text="📋 Paste", width=70, font=Theme.FONT_SMALL,
            fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_HOVER,
            command=lambda: self._paste_clipboard("cookie_tt"),
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            btn_row_tt, text="📋 JSON", width=70, font=Theme.FONT_SMALL,
            fg_color="#7C4DFF", hover_color="#651FFF",
            command=lambda: self._paste_json_cookie("cookie_tt", "tiktok"),
        ).pack(side="left")

        # Browser import TikTok
        ctk.CTkLabel(fr2, text="Import from browser", font=Theme.FONT_SMALL,
                      text_color=Theme.TEXT_MUTED, anchor="w") \
            .grid(row=1, column=0, padx=Theme.PAD_MD, sticky="w")

        browser_frame_tt = ctk.CTkFrame(fr2, fg_color="transparent")
        browser_frame_tt.grid(row=1, column=1, columnspan=2, padx=Theme.PAD_SM,
                              pady=(0, Theme.PAD_SM), sticky="ew")
        browser_frame_tt.grid_columnconfigure(0, weight=1)

        self._widgets["browser_tt"] = ctk.CTkOptionMenu(
            browser_frame_tt, values=_BROWSERS,
            font=Theme.FONT_SMALL, fg_color=Theme.BG_INPUT,
            button_color=Theme.ACCENT, button_hover_color=Theme.ACCENT_HOVER,
            dropdown_fg_color=Theme.BG_CARD, width=160,
        )
        self._widgets["browser_tt"].grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            browser_frame_tt, text="⬇ Import", width=80,
            font=Theme.FONT_SMALL, fg_color=Theme.ACCENT_DARK,
            hover_color=Theme.ACCENT_HOVER,
            command=lambda: self._import_browser_cookie("tiktok"),
        ).grid(row=0, column=1, padx=(Theme.PAD_SM, 0))

        return row

    # ──────────────────────────────────────────────────────────────────

    def _build_directory_section(self, row: int) -> int:
        lbl = _section_label(self._scroll, "📁  Directory & Format")
        lbl.grid(row=row, column=0, sticky="w", pady=(Theme.PAD_LG, Theme.PAD_SM))
        row += 1

        card = ctk.CTkFrame(self._scroll, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MD)
        card.grid(row=row, column=0, sticky="ew", pady=Theme.PAD_XS)
        card.grid_columnconfigure(1, weight=1)
        row += 1
        r = 0

        # Output directory
        ctk.CTkLabel(card, text="Output Directory", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")

        dir_frame = ctk.CTkFrame(card, fg_color="transparent")
        dir_frame.grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="ew")
        dir_frame.grid_columnconfigure(0, weight=1)

        self._widgets["root"] = ctk.CTkEntry(
            dir_frame, placeholder_text="Default: ./Download",
            font=Theme.FONT_BODY, fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY, border_color=Theme.BG_HOVER,
        )
        self._widgets["root"].grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(
            dir_frame, text="📂", width=40,
            font=Theme.FONT_BODY, fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            command=self._pick_directory,
        ).grid(row=0, column=1, padx=(Theme.PAD_XS, 0))
        r += 1

        # Folder name
        ctk.CTkLabel(card, text="Folder Name", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")
        self._widgets["folder_name"] = ctk.CTkEntry(
            card, placeholder_text="Download",
            font=Theme.FONT_BODY, fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY, border_color=Theme.BG_HOVER,
        )
        self._widgets["folder_name"].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="ew")
        r += 1

        # Storage format
        ctk.CTkLabel(card, text="Storage Format", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")
        self._widgets["storage_format"] = ctk.CTkOptionMenu(
            card, values=["(none)", "CSV", "XLSX"],
            font=Theme.FONT_BODY, fg_color=Theme.BG_INPUT,
            button_color=Theme.ACCENT, button_hover_color=Theme.ACCENT_HOVER,
            dropdown_fg_color=Theme.BG_CARD, width=160,
        )
        self._widgets["storage_format"].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="w")
        r += 1

        # Name format
        ctk.CTkLabel(card, text="Name Format", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")
        self._widgets["name_format"] = ctk.CTkEntry(
            card, placeholder_text="create_time type nickname desc",
            font=Theme.FONT_MONO, fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY, border_color=Theme.BG_HOVER,
        )
        self._widgets["name_format"].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="ew")
        ctk.CTkLabel(card, text="Tokens: create_time  type  nickname  desc  id",
                      font=Theme.FONT_SMALL, text_color=Theme.TEXT_MUTED, anchor="w") \
            .grid(row=r + 1, column=1, padx=Theme.PAD_SM, sticky="w")
        r += 2

        # Date format
        ctk.CTkLabel(card, text="Date Format", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")
        self._widgets["date_format"] = ctk.CTkEntry(
            card, placeholder_text="%Y-%m-%d %H:%M:%S",
            font=Theme.FONT_MONO, fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY, border_color=Theme.BG_HOVER,
        )
        self._widgets["date_format"].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="ew")
        r += 1

        # Split character
        ctk.CTkLabel(card, text="Split Character", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")
        self._widgets["split"] = ctk.CTkEntry(
            card, placeholder_text="-", width=80,
            font=Theme.FONT_MONO, fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY, border_color=Theme.BG_HOVER,
        )
        self._widgets["split"].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="w")
        r += 1

        return row

    # ──────────────────────────────────────────────────────────────────

    def _build_download_section(self, row: int) -> int:
        lbl = _section_label(self._scroll, "⬇  Download Options")
        lbl.grid(row=row, column=0, sticky="w", pady=(Theme.PAD_LG, Theme.PAD_SM))
        row += 1

        card = ctk.CTkFrame(self._scroll, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MD)
        card.grid(row=row, column=0, sticky="ew", pady=Theme.PAD_XS)
        card.grid_columnconfigure(1, weight=1)
        row += 1
        r = 0

        # Platform toggles
        ctk.CTkLabel(card, text="Platforms", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")

        plat_frame = ctk.CTkFrame(card, fg_color="transparent")
        plat_frame.grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="w")

        self._widgets["douyin_platform"] = ctk.CTkSwitch(
            plat_frame, text="Douyin (抖音)",
            font=Theme.FONT_BODY, text_color=Theme.TEXT_PRIMARY,
            progress_color=Theme.ACCENT, button_color=Theme.TEXT_SECONDARY,
            button_hover_color=Theme.ACCENT_HOVER,
        )
        self._widgets["douyin_platform"].grid(row=0, column=0, padx=(0, Theme.PAD_LG))

        self._widgets["tiktok_platform"] = ctk.CTkSwitch(
            plat_frame, text="TikTok",
            font=Theme.FONT_BODY, text_color=Theme.TEXT_PRIMARY,
            progress_color=Theme.ACCENT, button_color=Theme.TEXT_SECONDARY,
            button_hover_color=Theme.ACCENT_HOVER,
        )
        self._widgets["tiktok_platform"].grid(row=0, column=1)
        r += 1

        # Folder mode
        ctk.CTkLabel(card, text="Folder Mode", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")
        self._widgets["folder_mode"] = ctk.CTkSwitch(
            card, text="Classify by user",
            font=Theme.FONT_BODY, text_color=Theme.TEXT_PRIMARY,
            progress_color=Theme.ACCENT, button_color=Theme.TEXT_SECONDARY,
            button_hover_color=Theme.ACCENT_HOVER,
        )
        self._widgets["folder_mode"].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="w")
        r += 1

        # Download toggle
        ctk.CTkLabel(card, text="Auto Download", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")
        self._widgets["download"] = ctk.CTkSwitch(
            card, text="Download files after fetching data",
            font=Theme.FONT_BODY, text_color=Theme.TEXT_PRIMARY,
            progress_color=Theme.ACCENT, button_color=Theme.TEXT_SECONDARY,
            button_hover_color=Theme.ACCENT_HOVER,
        )
        self._widgets["download"].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="w")
        r += 1

        # Music
        ctk.CTkLabel(card, text="Download Music", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")
        self._widgets["music"] = ctk.CTkSwitch(
            card, text="Include background music",
            font=Theme.FONT_BODY, text_color=Theme.TEXT_PRIMARY,
            progress_color=Theme.ACCENT, button_color=Theme.TEXT_SECONDARY,
            button_hover_color=Theme.ACCENT_HOVER,
        )
        self._widgets["music"].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="w")
        r += 1

        # Dynamic cover
        ctk.CTkLabel(card, text="Dynamic Cover", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")
        self._widgets["dynamic_cover"] = ctk.CTkSwitch(
            card, text="Download animated cover",
            font=Theme.FONT_BODY, text_color=Theme.TEXT_PRIMARY,
            progress_color=Theme.ACCENT, button_color=Theme.TEXT_SECONDARY,
            button_hover_color=Theme.ACCENT_HOVER,
        )
        self._widgets["dynamic_cover"].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="w")
        r += 1

        # Static cover
        ctk.CTkLabel(card, text="Static Cover", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")
        self._widgets["static_cover"] = ctk.CTkSwitch(
            card, text="Download static cover image",
            font=Theme.FONT_BODY, text_color=Theme.TEXT_PRIMARY,
            progress_color=Theme.ACCENT, button_color=Theme.TEXT_SECONDARY,
            button_hover_color=Theme.ACCENT_HOVER,
        )
        self._widgets["static_cover"].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="w")
        r += 1

        return row

    # ──────────────────────────────────────────────────────────────────

    def _build_advanced_section(self, row: int) -> int:
        lbl = _section_label(self._scroll, "🔧  Advanced")
        lbl.grid(row=row, column=0, sticky="w", pady=(Theme.PAD_LG, Theme.PAD_SM))
        row += 1

        card = ctk.CTkFrame(self._scroll, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MD)
        card.grid(row=row, column=0, sticky="ew", pady=Theme.PAD_XS)
        card.grid_columnconfigure(1, weight=1)
        row += 1
        r = 0

        # Proxy
        ctk.CTkLabel(card, text="Proxy (Douyin)", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")
        self._widgets["proxy"] = ctk.CTkEntry(
            card, placeholder_text="http://127.0.0.1:7890",
            font=Theme.FONT_MONO, fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY, border_color=Theme.BG_HOVER,
        )
        self._widgets["proxy"].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="ew")
        r += 1

        # Proxy TikTok
        ctk.CTkLabel(card, text="Proxy (TikTok)", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")
        self._widgets["proxy_tiktok"] = ctk.CTkEntry(
            card, placeholder_text="http://127.0.0.1:7890",
            font=Theme.FONT_MONO, fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY, border_color=Theme.BG_HOVER,
        )
        self._widgets["proxy_tiktok"].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="ew")
        r += 1

        # Chunk size
        num_fields = [
            ("Chunk Size (bytes)", "chunk", "2097152"),
            ("Timeout (seconds)", "timeout", "10"),
            ("Max Retry", "max_retry", "5"),
            ("Max Pages (0=all)", "max_pages", "0"),
            ("Max File Size (0=no limit)", "max_size", "0"),
            ("Desc Length", "desc_length", "64"),
            ("Name Length", "name_length", "128"),
            ("Truncate", "truncate", "50"),
        ]
        for label_text, key, placeholder in num_fields:
            ctk.CTkLabel(card, text=label_text, font=Theme.FONT_BODY,
                          text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
                .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")
            self._widgets[key] = ctk.CTkEntry(
                card, placeholder_text=placeholder, width=160,
                font=Theme.FONT_MONO, fg_color=Theme.BG_INPUT,
                text_color=Theme.TEXT_PRIMARY, border_color=Theme.BG_HOVER,
            )
            self._widgets[key].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="w")
            r += 1

        # FFmpeg path
        ctk.CTkLabel(card, text="FFmpeg Path", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")
        self._widgets["ffmpeg"] = ctk.CTkEntry(
            card, placeholder_text="(auto-detect or full path)",
            font=Theme.FONT_MONO, fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY, border_color=Theme.BG_HOVER,
        )
        self._widgets["ffmpeg"].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="ew")
        r += 1

        # Live stream qualities
        ctk.CTkLabel(card, text="Live Qualities", font=Theme.FONT_BODY,
                      text_color=Theme.TEXT_SECONDARY, width=180, anchor="w") \
            .grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")
        self._widgets["live_qualities"] = ctk.CTkEntry(
            card, placeholder_text="e.g. origin, uhd, hd",
            font=Theme.FONT_MONO, fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY, border_color=Theme.BG_HOVER,
        )
        self._widgets["live_qualities"].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="ew")
        r += 1

        return row

    # ──────────────────────────────────────────────────────────────────

    def _build_text_replacement_section(self, row: int) -> int:
        """Section 5 — old→new text-replacement rules for file names."""
        lbl = _section_label(self._scroll, "🔤  Text Replacement")
        lbl.grid(row=row, column=0, sticky="w", pady=(Theme.PAD_LG, Theme.PAD_SM))
        row += 1

        card = ctk.CTkFrame(self._scroll, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MD)
        card.grid(row=row, column=0, sticky="ew", pady=Theme.PAD_XS)
        card.grid_columnconfigure(0, weight=1)
        row += 1

        ctk.CTkLabel(
            card, text="Add from → to pairs. These rules are applied to file names.",
            font=Theme.FONT_SMALL, text_color=Theme.TEXT_MUTED, anchor="w",
        ).grid(row=0, column=0, padx=Theme.PAD_MD, pady=(Theme.PAD_SM, 0), sticky="w")

        # Container for rule rows
        self._tr_rows_frame = ctk.CTkFrame(card, fg_color="transparent")
        self._tr_rows_frame.grid(row=1, column=0, sticky="ew", padx=Theme.PAD_SM, pady=Theme.PAD_XS)
        self._tr_rows_frame.grid_columnconfigure(0, weight=1)
        self._tr_rows_frame.grid_columnconfigure(1, weight=1)

        self._tr_rows: list[dict] = []  # [{"from": CTkEntry, "to": CTkEntry, "frame": CTkFrame}]

        ctk.CTkButton(
            card, text="+ Add Rule", width=120,
            font=Theme.FONT_SMALL,
            fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_HOVER,
            command=self._add_tr_row,
        ).grid(row=2, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")

        return row

    def _add_tr_row(self, from_val: str = "", to_val: str = "") -> None:
        """Append a text-replacement row."""
        idx = len(self._tr_rows)
        fr = ctk.CTkFrame(self._tr_rows_frame, fg_color="transparent")
        fr.grid(row=idx, column=0, columnspan=3, sticky="ew", pady=2)
        fr.grid_columnconfigure(0, weight=1)
        fr.grid_columnconfigure(1, weight=1)

        entry_from = ctk.CTkEntry(
            fr, placeholder_text="Find…",
            font=Theme.FONT_MONO, fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY, border_color=Theme.BG_HOVER,
        )
        entry_from.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        if from_val:
            entry_from.insert(0, from_val)

        ctk.CTkLabel(fr, text="→", font=Theme.FONT_BODY,
                     text_color=Theme.TEXT_MUTED).grid(row=0, column=1, padx=4)

        entry_to = ctk.CTkEntry(
            fr, placeholder_text="Replace with…",
            font=Theme.FONT_MONO, fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY, border_color=Theme.BG_HOVER,
        )
        entry_to.grid(row=0, column=2, padx=(4, 4), sticky="ew")
        if to_val:
            entry_to.insert(0, to_val)

        row_data = {"from": entry_from, "to": entry_to, "frame": fr}

        btn_del = ctk.CTkButton(
            fr, text="✕", width=30,
            font=Theme.FONT_SMALL,
            fg_color=Theme.ERROR, hover_color=Theme.BG_HOVER,
            command=lambda rd=row_data: self._remove_tr_row(rd),
        )
        btn_del.grid(row=0, column=3, padx=(4, 0))

        self._tr_rows.append(row_data)

    def _remove_tr_row(self, row_data: dict) -> None:
        """Remove a single text-replacement row."""
        row_data["frame"].destroy()
        self._tr_rows.remove(row_data)
        # Re-grid remaining rows
        for i, rd in enumerate(self._tr_rows):
            rd["frame"].grid(row=i)

    # ──────────────────────────────────────────────────────────────────

    def _build_delete_records_section(self, row: int) -> int:
        """Section 6 — delete download records by work ID."""
        lbl = _section_label(self._scroll, "🗑  Download Records")
        lbl.grid(row=row, column=0, sticky="w", pady=(Theme.PAD_LG, Theme.PAD_SM))
        row += 1

        card = ctk.CTkFrame(self._scroll, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MD)
        card.grid(row=row, column=0, sticky="ew", pady=Theme.PAD_XS)
        card.grid_columnconfigure(1, weight=1)
        row += 1
        r = 0

        ctk.CTkLabel(
            card, text="Work IDs", font=Theme.FONT_BODY,
            text_color=Theme.TEXT_SECONDARY, width=180, anchor="w",
        ).grid(row=r, column=0, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")

        self._widgets["delete_ids"] = ctk.CTkEntry(
            card, placeholder_text='Space-separated IDs or "ALL"',
            font=Theme.FONT_MONO, fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY, border_color=Theme.BG_HOVER,
        )
        self._widgets["delete_ids"].grid(row=r, column=1, padx=Theme.PAD_SM, pady=Theme.PAD_SM, sticky="ew")
        r += 1

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.grid(row=r, column=0, columnspan=2, padx=Theme.PAD_MD, pady=Theme.PAD_SM, sticky="w")

        ctk.CTkButton(
            btn_row, text="🗑 Delete Records", width=150,
            font=Theme.FONT_BODY,
            fg_color=Theme.ERROR, hover_color=Theme.ACCENT_HOVER,
            command=self._delete_records,
        ).grid(row=0, column=0)

        self._delete_status_label = ctk.CTkLabel(
            btn_row, text="", font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_MUTED, anchor="w",
        )
        self._delete_status_label.grid(row=0, column=1, padx=(Theme.PAD_SM, 0))
        r += 1

        return row

    def _delete_records(self) -> None:
        """Invoke backend's DownloadRecorder.delete_ids."""
        ids_text = self._widgets["delete_ids"].get().strip()
        if not ids_text:
            self._delete_status_label.configure(
                text="⚠ Enter IDs or \"ALL\"", text_color=Theme.WARNING,
            )
            return

        app = self._app
        if not app or not hasattr(app, "backend") or not app.backend.is_ready:
            self._delete_status_label.configure(
                text="❌ Backend not ready", text_color=Theme.ERROR,
            )
            return

        recorder = getattr(app.backend, "recorder", None)
        if recorder is None or not recorder.switch:
            self._delete_status_label.configure(
                text="❌ Download-record feature is disabled",
                text_color=Theme.ERROR,
            )
            return

        async def _do_delete():
            await recorder.delete_ids(ids_text)

        try:
            import asyncio
            asyncio.get_event_loop().create_task(_do_delete())
            self._delete_status_label.configure(
                text=f"✅ Delete request sent for: {ids_text}",
                text_color=Theme.SUCCESS,
            )
            self._log(f"🗑 Delete records: {ids_text}")
        except Exception as exc:
            self._delete_status_label.configure(
                text=f"❌ {exc}", text_color=Theme.ERROR,
            )

    # ──────────────────────────────────────────────────────────────────

    def _build_bottom_bar(self) -> None:
        bar = ctk.CTkFrame(self, fg_color=Theme.BG_SECONDARY, corner_radius=0, height=56)
        bar.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        bar.grid_columnconfigure(0, weight=1)

        btn_frame = ctk.CTkFrame(bar, fg_color="transparent")
        btn_frame.grid(row=0, column=0, padx=Theme.PAD_LG, pady=Theme.PAD_SM, sticky="e")

        ctk.CTkButton(
            btn_frame, text="↺  Reset to Defaults", width=150,
            font=Theme.FONT_BODY,
            fg_color=Theme.BG_CARD, hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            command=self._reset_defaults,
        ).grid(row=0, column=0, padx=(0, Theme.PAD_SM))

        ctk.CTkButton(
            btn_frame, text="💾  Save Settings", width=150,
            font=Theme.FONT_H3,
            fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_HOVER,
            command=self._save_settings,
        ).grid(row=0, column=1)

    # ══════════════════════════════════════════════════════════════════
    # Data load / save
    # ══════════════════════════════════════════════════════════════════

    def _load_settings(self) -> None:
        """Populate all widgets from settings.json."""
        data = _read_settings()
        if not data:
            return

        text_fields = [
            "root", "folder_name", "name_format", "date_format", "split",
            "proxy", "proxy_tiktok", "ffmpeg", "live_qualities",
        ]
        for key in text_fields:
            widget = self._widgets.get(key)
            if widget and key in data:
                widget.delete(0, "end")
                widget.insert(0, str(data[key]))

        int_fields = [
            "chunk", "timeout", "max_retry", "max_pages",
            "max_size", "desc_length", "name_length", "truncate",
        ]
        for key in int_fields:
            widget = self._widgets.get(key)
            if widget and key in data:
                widget.delete(0, "end")
                widget.insert(0, str(data[key]))

        bool_fields = [
            "douyin_platform", "tiktok_platform", "folder_mode",
            "download", "music", "dynamic_cover", "static_cover",
        ]
        for key in bool_fields:
            widget = self._widgets.get(key)
            if widget and key in data:
                if data[key]:
                    widget.select()
                else:
                    widget.deselect()

        # Cookies (string or dict → string)
        for ck_key, wk_key in [("cookie", "cookie_dy"), ("cookie_tiktok", "cookie_tt")]:
            widget = self._widgets.get(wk_key)
            val = data.get(ck_key, "")
            if widget and val:
                widget.delete(0, "end")
                if isinstance(val, dict):
                    widget.insert(0, "; ".join(f"{k}={v}" for k, v in val.items()))
                else:
                    widget.insert(0, str(val))

        # Storage format
        sf = data.get("storage_format", "")
        display = {"": "(none)", "csv": "CSV", "xlsx": "XLSX"}.get(sf, "(none)")
        self._widgets["storage_format"].set(display)

        # Text replacement rules
        for rd in list(self._tr_rows):
            self._remove_tr_row(rd)
        for old, new in data.get("text_replacement", []):
            self._add_tr_row(old, new)

    def _collect_settings(self) -> dict:
        """Read all widget values into a settings dict."""
        data = _read_settings() or {}

        # Text fields
        for key in ["root", "folder_name", "name_format", "date_format", "split",
                     "proxy", "proxy_tiktok", "ffmpeg", "live_qualities"]:
            widget = self._widgets.get(key)
            if widget:
                data[key] = widget.get().strip()

        # Int fields
        for key in ["chunk", "timeout", "max_retry", "max_pages",
                     "max_size", "desc_length", "name_length", "truncate"]:
            widget = self._widgets.get(key)
            if widget:
                text = widget.get().strip()
                try:
                    data[key] = int(text) if text else 0
                except ValueError:
                    pass  # keep old value

        # Bool fields (switches)
        for key in ["douyin_platform", "tiktok_platform", "folder_mode",
                     "download", "music", "dynamic_cover", "static_cover"]:
            widget = self._widgets.get(key)
            if widget:
                data[key] = bool(widget.get())
        # Cookies — convert "key=val; key2=val2" string to dict for the backend
        for entry_key, settings_key in [("cookie_dy", "cookie"), ("cookie_tt", "cookie_tiktok")]:
            raw = self._widgets[entry_key].get().strip()
            if raw:
                from src.tools import cookie_str_to_dict
                data[settings_key] = cookie_str_to_dict(raw)
            else:
                data[settings_key] = {}

        # Storage format
        sf_map = {"(none)": "", "CSV": "csv", "XLSX": "xlsx"}
        sf_raw = self._widgets["storage_format"].get()
        data["storage_format"] = sf_map.get(sf_raw, "")

        # Text replacement rules
        rules = []
        for rd in self._tr_rows:
            old = rd["from"].get().strip()
            new = rd["to"].get().strip()
            if old:  # skip empty "from" entries
                rules.append([old, new])
        data["text_replacement"] = rules

        return data

    def _save_settings(self) -> None:
        """Collect values and write to settings.json, then reload backend."""
        data = self._collect_settings()
        _save_settings(data)
        self._log("✅ Settings saved to disk.")

        # Reload the backend Parameter so changes take effect immediately
        if (self._app
                and hasattr(self._app, "backend") and self._app.backend
                and hasattr(self._app, "async_handler")):
            self._app.async_handler.run_async(
                self._app.backend.reload_parameter(),
                on_done=lambda _: self._on_backend_reloaded(),
                on_error=lambda exc: self._log(
                    f"⚠ Settings saved but backend reload failed: {exc}"
                ),
            )
        else:
            self._log("⚠ Settings saved to disk (restart to apply).")

    def _on_backend_reloaded(self) -> None:
        """Called after backend.reload_parameter() completes — refresh UI."""
        self._log("✅ Backend reloaded — settings are now active!")
        # Update status bar cookie indicators
        if self._app and hasattr(self._app, "status_bar") and hasattr(self._app, "backend"):
            p = self._app.backend.parameter
            if p:
                self._app.status_bar.set_cookie_status(
                    "Douyin", bool(p.cookie_state),
                )
                self._app.status_bar.set_cookie_status(
                    "TikTok", bool(p.cookie_tiktok_state),
                )

    def _reset_defaults(self) -> None:
        """Reset all fields to the defaults from config/settings.py."""
        from src.config.settings import Settings as ConfigSettings
        defaults = ConfigSettings.default.copy()
        _save_settings(defaults)
        self._load_settings()
        self._log("↺ Settings reset to defaults.")

    # ══════════════════════════════════════════════════════════════════
    # Actions
    # ══════════════════════════════════════════════════════════════════

    def _paste_clipboard(self, widget_key: str) -> None:
        """Paste clipboard content into the given entry widget."""
        try:
            text = self.clipboard_get()
        except Exception:
            self._log("⚠ Clipboard is empty or inaccessible.")
            return
        widget = self._widgets.get(widget_key)
        if widget:
            widget.delete(0, "end")
            widget.insert(0, text)
            self._log(f"📋 Pasted {len(text)} chars into {widget_key}.")

    def _import_browser_cookie(self, platform: str) -> None:
        """Import cookie from selected browser using rookiepy."""
        try:
            import rookiepy  # noqa: F401
        except ImportError:
            self._log("⚠ rookiepy not installed. Run: pip install rookiepy")
            return

        browser_key = "browser_dy" if platform == "douyin" else "browser_tt"
        cookie_key = "cookie_dy" if platform == "douyin" else "cookie_tt"
        browser_name = self._widgets[browser_key].get()

        try:
            func = getattr(rookiepy, browser_name, None)
            if func is None:
                self._log(f"⚠ Browser '{browser_name}' not supported by rookiepy.")
                return

            domain = ".douyin.com" if platform == "douyin" else ".tiktok.com"
            cookies = func(domains=[domain])
            cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies)

            widget = self._widgets[cookie_key]
            widget.delete(0, "end")
            widget.insert(0, cookie_str)
            self._log(f"✅ Imported {len(cookies)} cookies from {browser_name} ({platform}).")
        except Exception as exc:
            self._log(f"❌ Failed to import cookies: {exc}")

    def _paste_json_cookie(self, widget_key: str, platform: str) -> None:
        """Parse Cookie-Editor JSON from clipboard and set as cookie string.

        Cookie-Editor exports an array of objects like:
            [{"name": "key", "value": "val", "domain": ".tiktok.com", ...}, ...]
        We convert this to the standard ``key1=value1; key2=value2`` format.
        """
        try:
            text = self.clipboard_get()
        except Exception:
            self._log("⚠ Clipboard is empty or inaccessible.")
            return

        if not text or not text.strip():
            self._log("⚠ Clipboard is empty.")
            return

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            self._log("⚠ Clipboard does not contain valid JSON. "
                      "Copy the full JSON array from Cookie-Editor.")
            return

        if not isinstance(data, list):
            self._log("⚠ Expected a JSON array [...] from Cookie-Editor.")
            return

        # Deduplicate: keep the last occurrence of each cookie name
        seen: dict[str, str] = {}
        for item in data:
            if not isinstance(item, dict):
                continue
            name = item.get("name", "").strip()
            value = item.get("value", "").strip()
            if name:
                seen[name] = value

        if not seen:
            self._log("⚠ No valid cookies found in the JSON array.")
            return

        cookie_str = "; ".join(f"{k}={v}" for k, v in seen.items())

        widget = self._widgets.get(widget_key)
        if widget:
            widget.delete(0, "end")
            widget.insert(0, cookie_str)

        self._log(
            f"✅ Imported {len(seen)} cookies from Cookie-Editor JSON ({platform})."
        )

    def _pick_directory(self) -> None:
        """Open native folder picker dialog."""
        path = filedialog.askdirectory(title="Select download directory")
        if path:
            widget = self._widgets["root"]
            widget.delete(0, "end")
            widget.insert(0, path)
            self._log(f"📂 Output directory set to: {path}")

    # ── logging ──────────────────────────────────────────────────────

    def _log(self, msg: str) -> None:
        """Send message to the app log panel if available."""
        if self._app and hasattr(self._app, "log"):
            self._app.log.info(msg)
