@echo off
cd /d "D:\Recks\RAG-Blog"
start /B "Backend-NestJS" cmd /c "cd backend && npm run start:dev"
timeout /t 5 /nobreak > nul
start /B "Frontend" cmd /c "venv\Scripts\python.exe -m streamlit run frontend\app.py --server.port 8501 --server.headless true"
echo NestJS Servers starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8501
echo.
echo Press any key to exit (servers will keep running)
pause > nul
