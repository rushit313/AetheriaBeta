@echo off
echo Starting Aetheria Backend Server...
echo.

cd /d "%~dp0backend"

echo Checking if Python is installed...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting server on port 5001...
echo Backend will be accessible at http://127.0.0.1:5001
echo For Android emulator, use http://10.0.2.2:5001
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
