@echo off
title RAG Blog - Frontend
color 0A
cd /d "%~dp0\.."
echo Starting Frontend Server...
echo.
echo Chat UI: http://localhost:8501
echo.
venv\Scripts\python.exe -m streamlit run frontend\app.py --server.port 8501
pause
