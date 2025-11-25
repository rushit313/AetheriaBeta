@echo off
echo ========================================
echo   Aetheria Backend + ngrok Launcher
echo ========================================
echo.

REM Start backend in new window
echo [1/2] Starting Backend Server...
start "Aetheria Backend" cmd /k "cd /d %~dp0backend && python app.py"

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start ngrok in new window
echo [2/2] Starting ngrok tunnel...
echo.
echo IMPORTANT: Copy the HTTPS URL from the ngrok window!
echo Example: https://abc123.ngrok.io
echo.
echo Then update your Android app settings with that URL.
echo.

REM Check if ngrok exists in common locations
if exist "C:\ngrok\ngrok.exe" (
    start "ngrok Tunnel" cmd /k "C:\ngrok\ngrok.exe http 5001"
) else if exist "%USERPROFILE%\ngrok.exe" (
    start "ngrok Tunnel" cmd /k "%USERPROFILE%\ngrok.exe http 5001"
) else if exist "ngrok.exe" (
    start "ngrok Tunnel" cmd /k "ngrok.exe http 5001"
) else (
    echo ERROR: ngrok.exe not found!
    echo Please download from https://ngrok.com/download
    echo and place in C:\ngrok\ or current directory
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Both services started!
echo ========================================
echo.
echo 1. Check ngrok window for your public URL
echo 2. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
echo 3. Open Android app Settings
echo 4. Paste the URL
echo 5. Test API!
echo.
pause
