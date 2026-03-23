@echo off
title DouK-Downloader Build
cd /d "%~dp0"
"%~dp0.venv312\Scripts\python.exe" "%~dp0build_exe.py"
echo.
echo %cmdcmdline% | find /i "/c" >nul
if errorlevel 1 pause
