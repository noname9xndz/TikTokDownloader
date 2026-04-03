@echo off
title DouK-Downloader CLI
cd /d "%~dp0"

set "PYTHONSTARTUP="
set "PYTHON_BASIC_REPL="
set "VIRTUAL_ENV=%~dp0.venv312"

rem Use system Python with venv site-packages — terminal interactive mode (no GUI)
"C:\Users\LUKE\AppData\Local\Programs\Python\Python312\python.exe" -c "import site; site.addsitedir(r'%~dp0.venv312\Lib\site-packages'); exec(open(r'%~dp0main.py').read())"
pause
