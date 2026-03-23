"""Build script for DouK-Downloader GUI → .exe
Usage: .venv312\\Scripts\\python.exe build_exe.py
"""
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable
LOG = os.path.join(ROOT, "build.log")

def run(cmd, desc):
    print(f"[*] {desc}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if result.stdout:
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    if result.returncode != 0:
        print(f"[!] FAILED: {desc}")
        if result.stderr:
            print(result.stderr[-1000:])
        sys.exit(1)
    return result

print("=" * 50)
print("DouK-Downloader GUI — EXE Build")
print(f"Python: {sys.version}")
print("=" * 50)

# 1. Install PyInstaller
run([PYTHON, "-m", "pip", "install", "pyinstaller", "--quiet"], "Installing PyInstaller")

# 2. Build
print("[*] Running PyInstaller (this takes 1-2 min)...")
result = subprocess.run(
    [PYTHON, "-m", "PyInstaller", "gui.spec", "--noconfirm"],
    capture_output=True, text=True, cwd=ROOT
)

# Save full log
with open(LOG, "w", encoding="utf-8") as f:
    f.write("=== STDOUT ===\n")
    f.write(result.stdout or "(empty)")
    f.write("\n=== STDERR ===\n")
    f.write(result.stderr or "(empty)")

if result.returncode != 0:
    print(f"[!] Build failed! Full log: {LOG}")
    # Print last 1000 chars of stderr
    if result.stderr:
        print(result.stderr[-1000:])
    sys.exit(1)

# 3. Check output
exe_path = os.path.join(ROOT, "dist", "DouK-Downloader-GUI", "DouK-Downloader-GUI.exe")
if os.path.exists(exe_path):
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"\n{'=' * 50}")
    print(f"BUILD SUCCESS!")
    print(f"EXE:  {exe_path}")
    print(f"Size: {size_mb:.1f} MB")
    print(f"Full log: {LOG}")
    print(f"{'=' * 50}")
else:
    print(f"\n[!] EXE not found at {exe_path}")
    print(f"Full log: {LOG}")
    sys.exit(1)
