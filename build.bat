@echo off
title DouK-Downloader Build
cd /d "%~dp0"

echo ==================================================
echo   DouK-Downloader GUI - Build to EXE
echo ==================================================
echo.

REM --- Find Python in venv ---
set "VENV_PY=%~dp0.venv312\Scripts\python.exe"
if not exist "%VENV_PY%" (
    echo [ERROR] .venv312 not found!
    echo Please run: py -3.12 -m venv .venv312
    goto :end
)

"%VENV_PY%" --version
echo.

REM --- Install/upgrade PyInstaller ---
echo [1/3] Installing PyInstaller...
"%VENV_PY%" -m pip install pyinstaller -q
if errorlevel 1 (
    echo [ERROR] pip install failed
    goto :end
)
echo       Done.
echo.

REM --- Clean old build ---
echo [2/3] Cleaning old build...
if exist "dist\DouK-Downloader-GUI" rmdir /s /q "dist\DouK-Downloader-GUI"
if exist "build\DouK-Downloader-GUI" rmdir /s /q "build\DouK-Downloader-GUI"
echo       Done.
echo.

REM --- Build ---
echo [3/3] Building EXE (1-3 minutes, please wait)...
echo.
"%VENV_PY%" -m PyInstaller gui.spec --noconfirm
echo.

REM --- Result ---
if exist "dist\DouK-Downloader-GUI\DouK-Downloader-GUI.exe" (
    echo ==================================================
    echo   BUILD SUCCESS!
    echo   dist\DouK-Downloader-GUI\DouK-Downloader-GUI.exe
    echo ==================================================
) else (
    echo ==================================================
    echo   BUILD FAILED - check errors above
    echo ==================================================
)

:end
echo.
REM Only pause if launched from Explorer (not piped/redirected)
echo %cmdcmdline% | find /i "/c" >nul
if errorlevel 1 pause
