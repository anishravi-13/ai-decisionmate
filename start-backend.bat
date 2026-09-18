@echo off
title AI DecisionMate - Backend
cd /d %~dp0backend
echo Starting FastAPI backend on port 8000...
py -m uvicorn main:app --reload --port 8000
pause
