# DouK-Downloader GUI - Build Script
# Usage: .venv312\Scripts\activate; .\build.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== DouK-Downloader GUI Build ===" -ForegroundColor Cyan

# 1. Check Python version
$pyVer = python --version 2>&1
Write-Host "[1/4] Python: $pyVer"

# 2. Install PyInstaller if missing
$hasPI = python -c "import PyInstaller; print('yes')" 2>&1
if ($hasPI -eq "yes") {
    Write-Host "[2/4] PyInstaller: already installed"
} else {
    Write-Host "[2/4] Installing PyInstaller..." -ForegroundColor Yellow
    python -m pip install pyinstaller --quiet
    Write-Host "[2/4] PyInstaller: installed"
}

# 3. Clean previous build
if (Test-Path "dist\DouK-Downloader-GUI") {
    Write-Host "[3/4] Cleaning previous build..."
    Remove-Item -Recurse -Force "dist\DouK-Downloader-GUI"
} else {
    Write-Host "[3/4] No previous build to clean"
}

# 4. Build
Write-Host "[4/4] Building .exe (this may take 1-2 minutes)..." -ForegroundColor Yellow
python -m PyInstaller gui.spec --noconfirm

# Done
$exePath = "dist\DouK-Downloader-GUI\DouK-Downloader-GUI.exe"
if (Test-Path $exePath) {
    $exe = Get-Item $exePath
    $sizeMB = [math]::Round($exe.Length / 1048576, 1)
    Write-Host ""
    Write-Host "=== BUILD SUCCESS ===" -ForegroundColor Green
    Write-Host "EXE:  $exePath ($sizeMB MB)"
    Write-Host "Run:  .\dist\DouK-Downloader-GUI\DouK-Downloader-GUI.exe"
    Write-Host "Share: zip the entire dist\DouK-Downloader-GUI\ folder"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "=== BUILD FAILED ===" -ForegroundColor Red
    Write-Host "Check error messages above"
    Write-Host ""
    exit 1
}
