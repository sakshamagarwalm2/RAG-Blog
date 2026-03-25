# RAG Blog Chat - PowerShell Launcher
# Usage: .\run.ps1

param(
    [int]$Option = -1
)

$ErrorActionPreference = "Continue"
$ScriptDir = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvPath = Join-Path $ProjectRoot "venv"
$BackendPort = 8000
$FrontendPort = 8501

$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$VenvPip = Join-Path $VenvPath "Scripts\pip.exe"

function Write-Banner {
    param([string]$Text)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Text)
    Write-Host "[SUCCESS] $Text" -ForegroundColor Green
}

function Write-Info {
    param([string]$Text)
    Write-Host "[INFO] $Text" -ForegroundColor Cyan
}

function Write-Error {
    param([string]$Text)
    Write-Host "[ERROR] $Text" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Text)
    Write-Host "[WARNING] $Text" -ForegroundColor Yellow
}

function Test-VenvExists {
    return Test-Path $VenvPython
}

function Get-VenvActive {
    return $env:VIRTUAL_ENV -ne $null
}

function Invoke-Setup {
    Write-Banner "SETUP"
    
    $pythonVersion = python --version 2>&1
    Write-Info "Python version: $pythonVersion"
    
    if (Test-VenvExists) {
        Write-Info "Removing existing virtual environment..."
        Remove-Item -Path $VenvPath -Recurse -Force
    }
    
    Write-Info "Creating virtual environment..."
    python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment"
        return $false
    }
    Write-Success "Virtual environment created"
    
    Write-Info "Upgrading pip..."
    & $VenvPip install --upgrade pip 2>$null
    
    Write-Info "Installing dependencies..."
    & $VenvPip install -r "$ProjectRoot\requirements.txt"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install dependencies"
        return $false
    }
    Write-Success "Dependencies installed"
    
    $envFile = Join-Path $ProjectRoot ".env"
    if (-not (Test-Path $envFile)) {
        Write-Info "Creating .env file..."
        Copy-Item "$ProjectRoot\.env.example" $envFile
        Write-Success ".env file created"
        Write-Warning "Please edit .env with your MongoDB and Gemini credentials"
    } else {
        Write-Success ".env file already exists"
    }
    
    $faissDir = Join-Path $ProjectRoot "faiss_index"
    if (-not (Test-Path $faissDir)) {
        New-Item -ItemType Directory -Path $faissDir | Out-Null
    }
    
    Write-Success "Setup complete!"
    return $true
}

function Invoke-TestConnections {
    Write-Banner "TESTING CONNECTIONS"
    
    if (-not (Test-VenvExists)) {
        Write-Error "Virtual environment not found. Run option 1 (Setup) first."
        return $false
    }
    
    Write-Info "Testing MongoDB and Gemini connections..."
    & $VenvPython "$ScriptDir\test_connection.py"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "All connections working!"
        return $true
    } else {
        Write-Error "Connection tests failed"
        return $false
    }
}

function Invoke-Ingest {
    Write-Banner "BUILDING FAISS INDEX"
    
    if (-not (Test-VenvExists)) {
        Write-Error "Virtual environment not found. Run option 1 (Setup) first."
        return $false
    }
    
    Write-Info "Building FAISS index from MongoDB..."
    & $VenvPython "$ScriptDir\ingest.py"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "FAISS index built!"
        return $true
    } else {
        Write-Error "Failed to build index"
        return $false
    }
}

function Invoke-RunBackend {
    Write-Banner "STARTING BACKEND"
    
    if (-not (Test-VenvExists)) {
        Write-Error "Virtual environment not found. Run option 1 (Setup) first."
        return $false
    }
    
    Write-Info "Starting FastAPI on http://127.0.0.1:$BackendPort"
    Write-Info "API docs: http://localhost:$BackendPort/docs"
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$ProjectRoot'; & '$VenvPython' -m uvicorn backend.main:app --reload --port $BackendPort --host 127.0.0.1"
    
    Write-Success "Backend should have opened in a new window!"
    Write-Info "URL: http://localhost:$BackendPort/docs"
}

function Invoke-RunFrontend {
    Write-Banner "STARTING FRONTEND"
    
    if (-not (Test-VenvExists)) {
        Write-Error "Virtual environment not found. Run option 1 (Setup) first."
        return $false
    }
    
    Write-Info "Starting Streamlit on http://localhost:$FrontendPort"
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$ProjectRoot'; & '$VenvPython' -m streamlit run '$ProjectRoot\frontend\app.py' --server.port $FrontendPort"
    
    Write-Success "Frontend should have opened in a new window!"
    Write-Info "URL: http://localhost:$FrontendPort"
}

function Invoke-RunAll {
    Write-Banner "STARTING ALL SERVERS"
    
    if (-not (Test-VenvExists)) {
        Write-Error "Virtual environment not found. Run option 1 (Setup) first."
        return $false
    }
    
    # Start backend in new window
    Write-Info "Starting backend server on port $BackendPort..."
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$ProjectRoot'; Write-Host 'Backend starting...' -ForegroundColor Green; & '$VenvPython' -m uvicorn backend.main:app --reload --port $BackendPort --host 127.0.0.1"
    
    Start-Sleep -Seconds 3
    
    # Start frontend in new window
    Write-Info "Starting frontend server on port $FrontendPort..."
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$ProjectRoot'; Write-Host 'Frontend starting...' -ForegroundColor Green; & '$VenvPython' -m streamlit run '$ProjectRoot\frontend\app.py' --server.port $FrontendPort"
    
    Write-Host ""
    Write-Success "========================================"
    Write-Success "  ALL SERVERS STARTING!"
    Write-Success "========================================"
    Write-Success "  Chat UI:  http://localhost:$FrontendPort" -ForegroundColor Yellow
    Write-Success "  API Docs: http://localhost:$BackendPort/docs" -ForegroundColor Yellow
    Write-Success "========================================"
    Write-Host ""
    Write-Info "New terminal windows should have opened."
    Write-Info "If not, check the terminal windows for errors."
    Write-Host ""
    Write-Info "To stop: Close the terminal windows or use Task Manager."
}

function Show-Menu {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  RAG BLOG CHAT - Setup & Run Tool" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [1] Setup - Create venv & install dependencies" -ForegroundColor Green
    Write-Host "  [2] Test connections - Verify MongoDB & Gemini" -ForegroundColor Green
    Write-Host "  [3] Build index - Create FAISS index from MongoDB" -ForegroundColor Green
    Write-Host "  [4] Run backend - Start FastAPI server only" -ForegroundColor Green
    Write-Host "  [5] Run frontend - Start Streamlit only" -ForegroundColor Green
    Write-Host "  [6] Run all - Start both servers together" -ForegroundColor Green
    Write-Host "  [0] Exit" -ForegroundColor Green
    Write-Host ""
}

# Main execution
Clear-Host

if ($Option -ge 0 -and $Option -le 6) {
    switch ($Option) {
        1 { Invoke-Setup }
        2 { Invoke-TestConnections }
        3 { Invoke-Ingest }
        4 { Invoke-RunBackend }
        5 { Invoke-RunFrontend }
        6 { Invoke-RunAll }
        0 { Write-Info "Goodbye!"; exit 0 }
    }
    exit $LASTEXITCODE
}

while ($true) {
    Show-Menu
    $choice = Read-Host "Enter choice [0-6]"
    
    switch ($choice) {
        "1" { Invoke-Setup }
        "2" { Invoke-TestConnections }
        "3" { Invoke-Ingest }
        "4" { Invoke-RunBackend }
        "5" { Invoke-RunFrontend }
        "6" { Invoke-RunAll }
        "0" { Write-Info "Goodbye!"; exit 0 }
        default { Write-Error "Invalid choice. Please try again." }
    }
    
    Write-Host ""
    Read-Host "Press Enter to continue..."
    Clear-Host
}
