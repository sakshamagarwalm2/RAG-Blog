@echo off
title RAG Blog - Backend
color 0A
cd /d "%~dp0\.."
echo Starting Backend Server...
echo.
echo API Docs: http://localhost:8000/docs
echo.
venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000 --host 127.0.0.1
pause
