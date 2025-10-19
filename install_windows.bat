@echo off
echo Installing Insightron dependencies for Windows...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install NumPy with pre-compiled wheel (Windows-specific)
echo Installing NumPy with pre-compiled wheel...
python -m pip install numpy --only-binary=all

REM Install other dependencies
echo Installing other dependencies...
python -m pip install -r requirements.txt

echo.
echo Installation complete! You can now run: python main.py
pause
