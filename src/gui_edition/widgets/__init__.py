"""Widgets sub-package for DouK-Downloader GUI."""

from .about_dialog import AboutDialog
from .error_dialog import ErrorDialog, show_error
from .log_panel import LogPanel
from .progress_card import ProgressCard
from .sidebar import Sidebar
from .status_bar import StatusBar
from .url_input import URLInput

__all__ = [
    "AboutDialog",
    "ErrorDialog",
    "LogPanel",
    "ProgressCard",
    "Sidebar",
    "StatusBar",
    "URLInput",
    "show_error",
]

