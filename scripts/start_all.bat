@echo off
title RAG Blog - All Servers
color 0A
cd /d "%~dp0\.."

echo ========================================
echo  RAG Blog Chat - Starting Servers
echo ========================================
echo.

echo [1/2] Starting Backend on port 8000...
start "RAG-Backend" cmd /k "cd /d "%~dp0\.." && venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000 --host 127.0.0.1"

timeout /t 2 /nobreak > nul

echo [2/2] Starting Frontend on port 8501...
start "RAG-Frontend" cmd /k "cd /d "%~dp0\.." && venv\Scripts\python.exe -m streamlit run frontend\app.py --server.port 8501"

echo.
echo ========================================
echo  SERVERS STARTED!
echo ========================================
echo.
echo   Chat UI:  http://localhost:8501
echo   API Docs: http://localhost:8000/docs
echo.
echo   Close these windows to stop servers:
echo   - RAG-Backend
echo   - RAG-Frontend
echo.
pause
