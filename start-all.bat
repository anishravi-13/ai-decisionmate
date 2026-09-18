@echo off
title AI DecisionMate - Launcher
echo ========================================================
echo               AI DecisionMate Launcher
echo ========================================================
echo.
echo Starting Backend (FastAPI on http://localhost:8000)...
start "AI DecisionMate - Backend" cmd /k "cd /d %~dp0backend && py -m uvicorn main:app --reload --port 8000"

echo Starting Frontend (Vite/React on http://localhost:5173)...
start "AI DecisionMate - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================================
echo Servers are starting up!
echo   * Backend:  http://localhost:8000
echo   * API Docs: http://localhost:8000/docs
echo   * Frontend: http://localhost:5173
echo.
echo Please keep those two terminal windows open while using the app.
echo Opening browser in 4 seconds...
echo ========================================================
timeout /t 4 >nul
start http://localhost:5173
