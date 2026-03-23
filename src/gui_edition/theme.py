"""Design tokens for the DouK-Downloader desktop application.

Centralises every colour, font size, spacing and border-radius constant so
that the entire UI can be re-themed by editing this single file.
"""

from __future__ import annotations

__all__ = ["Theme"]


class Theme:
    """Static namespace for all design tokens — no instantiation needed."""

    # ── brand / accent ────────────────────────────────────────────────
    ACCENT = "#6C5CE7"          # primary purple
    ACCENT_HOVER = "#8B7BF7"    # lighter on hover
    ACCENT_DARK = "#4B3DC6"     # pressed / active

    # ── surfaces ──────────────────────────────────────────────────────
    BG_PRIMARY = "#1A1A2E"      # main window background
    BG_SECONDARY = "#16213E"    # sidebar / panels
    BG_CARD = "#1C2541"         # cards / frames
    BG_INPUT = "#0F3460"        # input fields
    BG_HOVER = "#2A2F4F"        # row / button hover

    # ── text ──────────────────────────────────────────────────────────
    TEXT_PRIMARY = "#E8E8E8"
    TEXT_SECONDARY = "#A0A0B8"
    TEXT_MUTED = "#6C6C80"
    TEXT_ACCENT = ACCENT

    # ── semantic ──────────────────────────────────────────────────────
    SUCCESS = "#00E676"
    WARNING = "#FFD600"
    ERROR = "#FF1744"
    INFO = "#40E0D0"

    # ── sidebar ───────────────────────────────────────────────────────
    SIDEBAR_WIDTH = 200
    SIDEBAR_BG = BG_SECONDARY
    SIDEBAR_BTN_HOVER = BG_HOVER
    SIDEBAR_BTN_ACTIVE = ACCENT

    # ── status bar ────────────────────────────────────────────────────
    STATUSBAR_HEIGHT = 30
    STATUSBAR_BG = "#0D1B2A"

    # ── typography (font family, sizes) ───────────────────────────────
    FONT_FAMILY = "Segoe UI"
    FONT_FAMILY_MONO = "Cascadia Code"

    FONT_H1 = (FONT_FAMILY, 20, "bold")
    FONT_H2 = (FONT_FAMILY, 16, "bold")
    FONT_H3 = (FONT_FAMILY, 14, "bold")
    FONT_BODY = (FONT_FAMILY, 13)
    FONT_SMALL = (FONT_FAMILY, 11)
    FONT_MONO = (FONT_FAMILY_MONO, 12)

    # ── spacing & radius ──────────────────────────────────────────────
    PAD_XS = 4
    PAD_SM = 8
    PAD_MD = 12
    PAD_LG = 16
    PAD_XL = 24

    RADIUS_SM = 6
    RADIUS_MD = 10
    RADIUS_LG = 14

    # ── window defaults ───────────────────────────────────────────────
    WIN_MIN_WIDTH = 1100
    WIN_MIN_HEIGHT = 700
    WIN_DEFAULT_SIZE = "1200x780"
