@echo off
title DouK-Downloader GUI
cd /d "%~dp0"

set "PYTHONSTARTUP="
set "PYTHON_BASIC_REPL="
set "VIRTUAL_ENV=%~dp0.venv312"

rem Use system Python with venv site-packages (avoids Windows Terminal/VS Code REPL interception)
"C:\Users\LUKE\AppData\Local\Programs\Python\Python312\python.exe" -c "import site; site.addsitedir(r'%~dp0.venv312\Lib\site-packages'); exec(open(r'%~dp0gui_launcher.py').read())"
