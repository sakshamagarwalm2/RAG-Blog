@echo off
cd /d "D:\Recks\RAG Blog"
start /B "Backend" cmd /c "venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000 --host 127.0.0.1"
timeout /t 3 /nobreak > nul
start /B "Frontend" cmd /c "venv\Scripts\python.exe -m streamlit run frontend\app.py --server.port 8501 --server.headless true"
echo Servers starting...
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:8501
echo.
echo Press any key to exit (servers will keep running)
pause > nul
