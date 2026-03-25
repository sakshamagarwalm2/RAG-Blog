@echo off
title RAG Blog Chat
color 0A

echo.
echo  ========================================
echo   RAG Blog Chat - Starting Servers...
echo  ========================================
echo.

cd /d "%~dp0"

if not exist "venv" (
    echo [SETUP] Virtual environment not found. Creating...
    python -m venv venv
    echo [SETUP] Installing dependencies...
    venv\Scripts\pip install -r requirements.txt
    echo [SETUP] Done!
    echo.
    echo [IMPORTANT] Please edit .env with your credentials before running!
    echo.
    pause
    exit /b 1
)

echo [START] Starting backend on http://127.0.0.1:8000...
start /B "Backend" cmd /c "venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000 --host 127.0.0.1"

timeout /t 2 /nobreak > nul

echo [START] Starting frontend on http://localhost:8501...
start /B "Frontend" cmd /c "venv\Scripts\python.exe -m streamlit run frontend\app.py --server.port 8501"

echo.
echo  ========================================
echo   SERVERS STARTED!
echo  ========================================
echo.
echo   Chat UI:  http://localhost:8501
echo   API Docs: http://localhost:8000/docs
echo.
echo   Press any key to close this window
echo   (Servers will keep running in background)
echo.
pause > nul
