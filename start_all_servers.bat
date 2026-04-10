@echo off

rem Set the current directory to the script's directory
cd /d "%~dp0"

echo Activating Python virtual environment...
call venv\Scripts\activate

echo Starting NestJS Backend...
rem Start backend in a new window, but don't wait for it
start "NestJS Backend" cmd /c "cd backend && npm run start:dev"

echo Starting Streamlit Frontend...
rem Start frontend in a new window, but don't wait for it
start "Streamlit Frontend" cmd /c "streamlit run frontend\app.py --server.port 8501 --server.headless true"

echo.
echo Both backend and frontend servers are attempting to start.
echo Please check the new command prompt windows for their status.
echo You can close this window now.
exit