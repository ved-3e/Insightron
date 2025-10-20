@echo off
echo ================================================
echo    Insightron v1.0.0 - Windows Installer
echo    Enhanced Whisper AI Transcription Tool
echo ================================================
echo.

REM Check Python version
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Installing Insightron dependencies for Windows...
echo.

REM Upgrade pip first
echo [1/4] Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo WARNING: pip upgrade failed, continuing anyway...
)

REM Install NumPy with pre-compiled wheel (Windows-specific)
echo.
echo [2/4] Installing NumPy with pre-compiled wheel...
python -m pip install numpy --only-binary=all --upgrade
if %errorlevel% neq 0 (
    echo ERROR: NumPy installation failed
    echo Please install Visual Studio Build Tools or try: conda install numpy
    pause
    exit /b 1
)

REM Install other dependencies
echo.
echo [3/4] Installing other dependencies...
python -m pip install -r requirements.txt --no-cache-dir
if %errorlevel% neq 0 (
    echo WARNING: Some dependencies failed, trying minimal installation...
    python -m pip install -r requirements-minimal.txt --no-cache-dir
    if %errorlevel% neq 0 (
        echo ERROR: Installation failed completely
        echo Please run: python troubleshoot.py
        pause
        exit /b 1
    )
)

REM Verify installation
echo.
echo [4/4] Verifying installation...
python -c "import whisper, librosa, numpy; print('All core dependencies working!')"
if %errorlevel% neq 0 (
    echo WARNING: Some dependencies may not be working correctly
    echo Run: python troubleshoot.py for diagnostics
)

echo.
echo ================================================
echo    Installation Complete!
echo ================================================
echo.
echo You can now run Insightron:
echo   python insightron.py    # GUI mode (recommended)
echo   python cli.py audio.mp3  # Command line mode
echo.
echo For help: python troubleshoot.py
echo Documentation: README.md
echo.
pause
