"""Entry point for the DouK-Downloader desktop GUI.

Usage:
    python -m src.gui_edition.gui_main
    python gui_main.py            (if run from gui_edition directory)
    python main.py --gui          (after adding --gui flag to main.py)
"""

from __future__ import annotations

import sys


def launch_gui() -> None:
    """Create and run the desktop application."""
    # Ensure customtkinter is available
    try:
        import customtkinter  # noqa: F401
    except ImportError:
        print(
            "[ERROR] customtkinter not installed.\n"
            "Run: pip install customtkinter Pillow",
            file=sys.stderr,
        )
        sys.exit(1)

    from .app import App

    app = App()
    app.run()


if __name__ == "__main__":
    # Allow running directly: python -m src.gui_edition.gui_main
    launch_gui()
