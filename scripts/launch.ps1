# Quick launcher for RAG Blog Chat
# Double-click this to start everything

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvPath = Join-Path $ProjectRoot "venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$FrontendPort = 8501
$BackendPort = 8000

if (-not (Test-Path $VenvPython)) {
    Write-Host "Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: .\run.ps1" -ForegroundColor Yellow
    Write-Host "And select option 1 to setup." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting RAG Blog Chat..." -ForegroundColor Cyan
Write-Host ""

# Start backend
Write-Host "Starting Backend on http://127.0.0.1:$BackendPort..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$ProjectRoot'; & '$VenvPython' -m uvicorn backend.main:app --reload --port $BackendPort --host 127.0.0.1"

Start-Sleep -Seconds 2

# Start frontend
Write-Host "Starting Frontend on http://localhost:$FrontendPort..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$ProjectRoot'; & '$VenvPython' -m streamlit run '$ProjectRoot\frontend\app.py' --server.port $FrontendPort"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SERVERS STARTED!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Chat UI:  http://localhost:$FrontendPort" -ForegroundColor Green
Write-Host "  API Docs: http://localhost:$BackendPort/docs" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Enter to close this window (servers will keep running)" -ForegroundColor Yellow
Read-Host
