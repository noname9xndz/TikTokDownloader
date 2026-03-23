"""Top-level entry point for PyInstaller packaging.

PyInstaller has trouble with ``python -m src.gui_edition.gui_main``
relative imports, so this thin wrapper lives at the repo root.
"""

from src.gui_edition.gui_main import launch_gui

if __name__ == "__main__":
    launch_gui()
