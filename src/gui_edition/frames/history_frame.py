"""HistoryFrame — Downloaded files browser.

Scans the download folder on disk and presents a scrollable list of
files.  Each row shows filename, size, date and an "Open" button that
launches the system file viewer.
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, List, Tuple

import customtkinter as ctk

from ..theme import Theme
from src.custom import PROJECT_ROOT

if TYPE_CHECKING:
    pass

__all__ = ["HistoryFrame"]

# ── helpers ──────────────────────────────────────────────────────────────────

_DOWNLOAD_DIR = PROJECT_ROOT / "Download"

_VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv"}
_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
_AUDIO_EXTS = {".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"}
_DATA_EXTS  = {".csv", ".xlsx", ".json", ".txt"}


def _icon_for(ext: str) -> str:
    ext = ext.lower()
    if ext in _VIDEO_EXTS:
        return "🎬"
    if ext in _IMAGE_EXTS:
        return "🖼"
    if ext in _AUDIO_EXTS:
        return "🎵"
    if ext in _DATA_EXTS:
        return "📄"
    return "📁"


def _human_size(nbytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(nbytes) < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} TB"


def _scan_downloads(folder: Path) -> List[Tuple[Path, float, int]]:
    """Return list of (path, mtime, size) sorted newest-first."""
    if not folder.is_dir():
        return []
    items = []
    for entry in folder.iterdir():
        if entry.is_file() and not entry.name.startswith("."):
            stat = entry.stat()
            items.append((entry, stat.st_mtime, stat.st_size))
    items.sort(key=lambda t: t[1], reverse=True)
    return items


def _open_file(path: Path) -> None:
    """Open a file with the system default application."""
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception:
        pass


def _open_folder(folder: Path) -> None:
    """Open the folder in the system file manager."""
    try:
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(folder)])
        else:
            subprocess.Popen(["xdg-open", str(folder)])
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────


class HistoryFrame(ctk.CTkFrame):
    """Browseable list of downloaded files."""

    def __init__(self, master, app_ref=None, **kwargs):
        super().__init__(master, fg_color=Theme.BG_PRIMARY, corner_radius=0, **kwargs)
        self._app = app_ref

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # scrollable area stretches

        self._build_header()
        self._build_file_list()
        self._build_footer()

        # Initial scan
        self._refresh()

    # ── Header ───────────────────────────────────────────────────────────────

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0,
                    padx=Theme.PAD_LG, pady=(Theme.PAD_LG, Theme.PAD_SM),
                    sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="📂  Downloaded Files",
            font=Theme.FONT_H1,
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        # ── Refresh button ─────────────────────────────────────────────
        self._refresh_btn = ctk.CTkButton(
            header,
            text="🔄  Refresh",
            width=120,
            height=34,
            font=Theme.FONT_H3,
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            corner_radius=Theme.RADIUS_SM,
            command=self._refresh,
        )
        self._refresh_btn.grid(row=0, column=2, padx=(Theme.PAD_SM, 0), sticky="e")

        # ── Open folder button ─────────────────────────────────────────
        self._folder_btn = ctk.CTkButton(
            header,
            text="📁  Open Folder",
            width=140,
            height=34,
            font=Theme.FONT_H3,
            fg_color=Theme.BG_INPUT,
            hover_color=Theme.BG_HOVER,
            corner_radius=Theme.RADIUS_SM,
            command=lambda: _open_folder(_DOWNLOAD_DIR),
        )
        self._folder_btn.grid(row=0, column=3, padx=(Theme.PAD_SM, 0), sticky="e")

        # ── File count label ───────────────────────────────────────────
        self._count_label = ctk.CTkLabel(
            header,
            text="",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_SECONDARY,
            anchor="e",
        )
        self._count_label.grid(row=1, column=0, columnspan=4, sticky="e",
                               pady=(Theme.PAD_XS, 0))

    # ── Scrollable file list ─────────────────────────────────────────────────

    def _build_file_list(self) -> None:
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=Theme.BG_CARD,
            corner_radius=Theme.RADIUS_MD,
            scrollbar_button_color=Theme.ACCENT,
            scrollbar_button_hover_color=Theme.ACCENT_HOVER,
        )
        self._scroll.grid(row=1, column=0,
                          padx=Theme.PAD_LG, pady=Theme.PAD_SM,
                          sticky="nsew")
        self._scroll.grid_columnconfigure(0, weight=1)

    # ── Footer ───────────────────────────────────────────────────────────────

    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(self, fg_color="transparent", height=30)
        footer.grid(row=2, column=0,
                    padx=Theme.PAD_LG, pady=(0, Theme.PAD_SM),
                    sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        self._total_size_label = ctk.CTkLabel(
            footer,
            text="",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_MUTED,
            anchor="w",
        )
        self._total_size_label.grid(row=0, column=0, sticky="w")

        self._path_label = ctk.CTkLabel(
            footer,
            text=f"📍  {_DOWNLOAD_DIR}",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_MUTED,
            anchor="e",
        )
        self._path_label.grid(row=0, column=1, sticky="e")

    # ── Refresh logic ────────────────────────────────────────────────────────

    def _refresh(self) -> None:
        """Rescan the download folder and rebuild the file list."""
        # Clear existing rows
        for widget in self._scroll.winfo_children():
            widget.destroy()

        items = _scan_downloads(_DOWNLOAD_DIR)

        if not items:
            self._show_empty_state()
            self._count_label.configure(text="No files found")
            self._total_size_label.configure(text="")
            return

        total_size = 0
        for idx, (path, mtime, size) in enumerate(items):
            total_size += size
            self._create_file_row(idx, path, mtime, size)

        self._count_label.configure(text=f"{len(items)} file{'s' if len(items) != 1 else ''}")
        self._total_size_label.configure(text=f"Total: {_human_size(total_size)}")

    def _show_empty_state(self) -> None:
        """Show a message when no files exist."""
        empty = ctk.CTkFrame(self._scroll, fg_color="transparent")
        empty.grid(row=0, column=0, sticky="ew", pady=Theme.PAD_XL * 3)
        empty.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            empty,
            text="📭",
            font=(Theme.FONT_FAMILY, 48),
            text_color=Theme.TEXT_MUTED,
        ).grid(row=0, column=0)

        ctk.CTkLabel(
            empty,
            text="No downloaded files yet",
            font=Theme.FONT_H2,
            text_color=Theme.TEXT_MUTED,
        ).grid(row=1, column=0, pady=(Theme.PAD_SM, Theme.PAD_XS))

        ctk.CTkLabel(
            empty,
            text="Download some videos first, then come back here!",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_MUTED,
        ).grid(row=2, column=0)

    def _create_file_row(self, idx: int, path: Path, mtime: float, size: int) -> None:
        """Build a single row widget for a downloaded file."""
        ext = path.suffix.lower()
        icon = _icon_for(ext)
        dt = datetime.fromtimestamp(mtime)
        date_str = dt.strftime("%Y-%m-%d  %H:%M")
        size_str = _human_size(size)

        # Truncate long filenames
        name = path.stem
        if len(name) > 80:
            name = name[:77] + "…"
        display_name = f"{name}{ext}"

        # Row container
        bg = Theme.BG_CARD if idx % 2 == 0 else Theme.BG_SECONDARY
        row = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=Theme.RADIUS_SM)
        row.grid(row=idx, column=0, sticky="ew", padx=Theme.PAD_XS, pady=1)
        row.grid_columnconfigure(1, weight=1)

        # Icon
        ctk.CTkLabel(
            row,
            text=icon,
            font=(Theme.FONT_FAMILY, 20),
            width=36,
            text_color=Theme.TEXT_PRIMARY,
        ).grid(row=0, column=0, rowspan=2, padx=(Theme.PAD_SM, Theme.PAD_XS),
               pady=Theme.PAD_XS)

        # Filename
        name_label = ctk.CTkLabel(
            row,
            text=display_name,
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_PRIMARY,
            anchor="w",
        )
        name_label.grid(row=0, column=1, sticky="ew", padx=Theme.PAD_XS,
                        pady=(Theme.PAD_XS, 0))

        # Meta line: date + size + extension
        ext_badge = ext.upper().lstrip(".")
        meta_text = f"{date_str}    •    {size_str}    •    {ext_badge}"
        ctk.CTkLabel(
            row,
            text=meta_text,
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=1, sticky="ew", padx=Theme.PAD_XS,
               pady=(0, Theme.PAD_XS))

        # ── Open button ────────────────────────────────────────────────
        open_btn = ctk.CTkButton(
            row,
            text="▶  Open",
            width=90,
            height=30,
            font=Theme.FONT_SMALL,
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            corner_radius=Theme.RADIUS_SM,
            command=lambda p=path: _open_file(p),
        )
        open_btn.grid(row=0, column=2, rowspan=2, padx=Theme.PAD_SM, pady=Theme.PAD_XS)

        # ── Hover effect ───────────────────────────────────────────────
        def on_enter(_e, r=row):
            r.configure(fg_color=Theme.BG_HOVER)

        def on_leave(_e, r=row, b=bg):
            r.configure(fg_color=b)

        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)
        # Also bind children for consistent effect
        for child in row.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
