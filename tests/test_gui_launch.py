"""Manual GUI launch test — requires a display.

This test creates the App, verifies basic navigation works, then
exits after a short timeout.  NOT intended for CI (needs a display).

Run:
    python tests/test_gui_launch.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main() -> None:
    try:
        import customtkinter  # noqa: F401
    except ImportError:
        print("[FAIL] customtkinter not installed", file=sys.stderr)
        sys.exit(1)

    from src.gui_edition.app import App

    print("[TEST] Creating App …")
    app = App()

    errors: list[str] = []

    def _run_checks() -> None:
        """Scheduled callback: exercise navigation + verify frames."""
        try:
            # 1. Verify three sidebar buttons exist
            sidebar = app._sidebar
            assert len(sidebar._buttons) >= 3, "Sidebar missing buttons"
            print("[OK] Sidebar has ≥3 nav buttons")

            # 2. Navigate to each frame
            for name in ("download", "settings", "monitor"):
                app._show_frame(name)
                assert app._frames[name].winfo_viewable(), f"{name} frame not visible"
                print(f"[OK] Frame '{name}' visible")

            # 3. Verify status bar exists and has text
            sb = app._status_bar
            assert sb.winfo_exists(), "StatusBar missing"
            print("[OK] StatusBar exists")

            # 4. Verify log panel
            lp = app._log_panel
            assert lp.winfo_exists(), "LogPanel missing"
            lp.info("Launch test message")
            print("[OK] LogPanel exists and accepts messages")

            print("\n✅ All checks passed!")
        except Exception as exc:
            errors.append(str(exc))
            print(f"\n❌ Check failed: {exc}", file=sys.stderr)
        finally:
            app.after(500, app.destroy)

    # Schedule checks after the window is fully drawn
    app.after(1500, _run_checks)

    # Safety timeout — destroy after 10 s even if checks hang
    app.after(10_000, app.destroy)

    print("[TEST] Running mainloop (auto-closes in ≤10 s) …")
    app.mainloop()

    if errors:
        print(f"\n❌ {len(errors)} error(s) — see above", file=sys.stderr)
        sys.exit(1)
    else:
        print("\n🎉 Launch test complete.")
        sys.exit(0)


if __name__ == "__main__":
    main()
