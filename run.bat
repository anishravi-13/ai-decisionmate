@echo off
title AI DecisionMate Launcher
echo ========================================================
echo          Starting AI DecisionMate System...
echo ========================================================
echo.
cd /d "%~dp0backend"

echo [1/2] Starting Unified Server (Backend + React UI)...
start /b py -m uvicorn main:app --port 8000 --host 0.0.0.0

echo [2/2] Launching your default browser...
timeout /t 2 /nobreak >nul
start http://localhost:8000

echo.
echo ========================================================
echo   AI DecisionMate is now LIVE at http://localhost:8000 !
echo   (Keep this window open while using the website)
echo ========================================================
echo.
pause
