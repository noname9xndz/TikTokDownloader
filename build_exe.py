"""Build DouK-Downloader GUI → standalone .exe

Usage (one of):
  - Double-click build.bat
  - Or: .venv312\Scripts\python.exe build_exe.py
"""
import subprocess, sys, os, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))

def main():
    print("=" * 50)
    print("  DouK-Downloader GUI — Build to EXE")
    print(f"  Python {sys.version.split()[0]}")
    print("=" * 50)
    print()

    # 1. Install PyInstaller
    print("[1/3] Installing PyInstaller...")
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pyinstaller", "-q"],
        cwd=ROOT,
    )
    if r.returncode != 0:
        print("[ERROR] pip install pyinstaller failed")
        return 1
    print("      Done.\n")

    # 2. Clean
    print("[2/3] Cleaning old build...")
    for d in ["dist/DouK-Downloader-GUI", "build/DouK-Downloader-GUI"]:
        p = os.path.join(ROOT, d)
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
    print("      Done.\n")

    # 3. Build
    print("[3/3] Building EXE (1-3 minutes, please wait)...\n")
    r = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "gui.spec", "--noconfirm"],
        cwd=ROOT,
    )
    print()

    # Result
    exe = os.path.join(ROOT, "dist", "DouK-Downloader-GUI", "DouK-Downloader-GUI.exe")
    if os.path.isfile(exe):
        mb = os.path.getsize(exe) / 1048576
        print("=" * 50)
        print(f"  BUILD SUCCESS!  ({mb:.0f} MB)")
        print(f"  {exe}")
        print("=" * 50)
        return 0
    else:
        print("=" * 50)
        print("  BUILD FAILED — check errors above")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    sys.exit(main())
