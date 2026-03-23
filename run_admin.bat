@echo off
:: ── Request Admin privileges automatically ──
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

title DouK-Downloader GUI (Admin)
cd /d "%~dp0"

set "PYTHONSTARTUP="
set "PYTHON_BASIC_REPL="
set "VIRTUAL_ENV=%~dp0.venv312"

rem Use system Python with venv site-packages
"C:\Users\LUKE\AppData\Local\Programs\Python\Python312\python.exe" -c "import site; site.addsitedir(r'%~dp0.venv312\Lib\site-packages'); exec(open(r'%~dp0gui_launcher.py').read())"
