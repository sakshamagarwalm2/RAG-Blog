#!/usr/bin/env python3
"""
RAG Blog Chat - Setup and Run Script
Usage: python run.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
VENV_PATH = PROJECT_ROOT / "venv"
BACKEND_PORT = 8000
FRONTEND_PORT = 8501

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*50}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*50}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}[SUCCESS] {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}[ERROR] {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.CYAN}[INFO] {text}{Colors.ENDC}")

def run_command(cmd, cwd=None, capture=False):
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
            return result.returncode, result.stdout, result.stderr
        else:
            subprocess.run(cmd, shell=True, cwd=cwd, check=True)
            return 0, "", ""
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr

def check_python():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_error(f"Python 3.10+ required. You have {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def is_venv_active():
    return sys.prefix != sys.base_prefix

def check_venv():
    if is_venv_active():
        print_success("Virtual environment is active")
        return True
    print_info("Virtual environment not active")
    return False

def get_venv_python():
    if os.name == 'nt':
        return VENV_PATH / "Scripts" / "python.exe"
    return VENV_PATH / "bin" / "python"

def get_venv_pip():
    if os.name == 'nt':
        return VENV_PATH / "Scripts" / "pip.exe"
    return VENV_PATH / "bin" / "pip"

def setup():
    print_header("SETUP")
    
    if not check_python():
        return False
    
    print_info("Creating virtual environment...")
    if VENV_PATH.exists():
        print_info("Virtual environment already exists, removing...")
        shutil.rmtree(VENV_PATH)
    
    try:
        subprocess.run([sys.executable, "-m", "venv", str(VENV_PATH)], check=True)
        print_success("Virtual environment created")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create venv: {e}")
        return False
    
    pip = get_venv_pip()
    print_info("Installing dependencies...")
    
    try:
        subprocess.run([str(pip), "install", "--upgrade", "pip"], check=True, cwd=PROJECT_ROOT)
        subprocess.run([str(pip), "install", "-r", "requirements.txt"], check=True, cwd=PROJECT_ROOT)
        print_success("Dependencies installed")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        return False
    
    if not Path(".env").exists():
        print_info("Creating .env file from .env.example...")
        shutil.copy(".env.example", ".env")
        print_success(".env file created")
        print_warning("Please edit .env with your MongoDB and Gemini credentials")
    else:
        print_success(".env file already exists")
    
    print_info("Creating faiss_index directory...")
    Path("faiss_index").mkdir(exist_ok=True)
    print_success("Setup complete!")
    
    return True

def test_connections():
    print_header("TESTING CONNECTIONS")
    python = get_venv_python()
    
    print_info("Testing connections...")
    code, stdout, stderr = run_command(f'"{python}" scripts/test_connection.py', cwd=PROJECT_ROOT, capture=True)
    
    print(stdout)
    if stderr and "FutureWarning" not in stderr:
        print(stderr)
    
    if code == 0:
        print_success("All connections working!")
        return True
    else:
        print_error("Connection tests failed")
        return False

def ingest():
    print_header("BUILDING FAISS INDEX")
    python = get_venv_python()
    
    print_info("Building FAISS index from MongoDB...")
    code, stdout, stderr = run_command(f'"{python}" scripts/ingest.py', cwd=PROJECT_ROOT, capture=True)
    
    print(stdout)
    if stderr and "FutureWarning" not in stderr:
        print(stderr)
    
    if code == 0:
        print_success("FAISS index built!")
        return True
    else:
        print_error("Failed to build index")
        return False

def run_backend():
    print_header("STARTING BACKEND")
    python = get_venv_python()
    
    print_info(f"Starting FastAPI on http://127.0.0.1:{BACKEND_PORT}")
    print_info("API docs: http://localhost:8000/docs")
    
    cmd = f'"{python}" -m uvicorn backend.main:app --reload --port {BACKEND_PORT} --host 127.0.0.1'
    
    try:
        subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT)
    except KeyboardInterrupt:
        print_info("Backend stopped")

def run_frontend():
    print_header("STARTING FRONTEND")
    python = get_venv_python()
    
    print_info(f"Starting Streamlit on http://localhost:{FRONTEND_PORT}")
    
    cmd = f'"{python}" -m streamlit run frontend/app.py --server.port {FRONTEND_PORT}'
    
    try:
        subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT)
    except KeyboardInterrupt:
        print_info("Frontend stopped")

def run_all():
    print_header("STARTING ALL SERVERS")
    
    backend_process = None
    frontend_process = None
    python = get_venv_python()
    
    try:
        print_info("Starting backend server...")
        backend_cmd = f'"{python}" -m uvicorn backend.main:app --reload --port {BACKEND_PORT} --host 127.0.0.1'
        backend_process = subprocess.Popen(backend_cmd, shell=True, cwd=PROJECT_ROOT)
        print_success(f"Backend running on http://127.0.0.1:{BACKEND_PORT}")
        
        import time
        time.sleep(3)
        
        print_info("Starting frontend server...")
        frontend_cmd = f'"{python}" -m streamlit run frontend/app.py --server.port {FRONTEND_PORT}'
        frontend_process = subprocess.Popen(frontend_cmd, shell=True, cwd=PROJECT_ROOT)
        print_success(f"Frontend running on http://localhost:{FRONTEND_PORT}")
        
        print_success("\n" + "="*50)
        print_success("ALL SERVERS RUNNING!")
        print_success(f"  Chat UI:  http://localhost:{FRONTEND_PORT}")
        print_success(f"  API Docs: http://localhost:{BACKEND_PORT}/docs")
        print_success("="*50)
        print_info("\nPress Ctrl+C to stop all servers...")
        
        backend_process.wait()
        
    except KeyboardInterrupt:
        print_info("\nStopping servers...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print_success("Servers stopped")

def print_warning(text):
    print(f"{Colors.YELLOW}[WARNING] {text}{Colors.ENDC}")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(f"""
{Colors.CYAN}========================================
      RAG BLOG CHAT - Setup & Run Tool
========================================{Colors.ENDC}
""")
    
    while True:
        print(f"""
{Colors.BOLD}What would you like to do?{Colors.ENDC}

  {Colors.GREEN}[1]{Colors.ENDC} Setup - Create venv & install dependencies
  {Colors.GREEN}[2]{Colors.ENDC} Test connections - Verify MongoDB & Gemini
  {Colors.GREEN}[3]{Colors.ENDC} Build index - Create FAISS index from MongoDB
  {Colors.GREEN}[4]{Colors.ENDC} Run backend - Start FastAPI server only
  {Colors.GREEN}[5]{Colors.ENDC} Run frontend - Start Streamlit only
  {Colors.GREEN}[6]{Colors.ENDC} Run all - Start both servers together
  {Colors.GREEN}[0]{Colors.ENDC} Exit

        """)
        
        choice = input(f"{Colors.CYAN}Enter choice [0-6]: {Colors.ENDC}").strip()
        
        if choice == '1':
            setup()
        elif choice == '2':
            if check_venv():
                test_connections()
            else:
                print_error("Please run option 1 (Setup) first")
        elif choice == '3':
            if check_venv():
                ingest()
            else:
                print_error("Please run option 1 (Setup) first")
        elif choice == '4':
            if check_venv():
                run_backend()
            else:
                print_error("Please run option 1 (Setup) first")
        elif choice == '5':
            if check_venv():
                run_frontend()
            else:
                print_error("Please run option 1 (Setup) first")
        elif choice == '6':
            if check_venv():
                run_all()
            else:
                print_error("Please run option 1 (Setup) first")
        elif choice == '0':
            print_info("Goodbye!")
            sys.exit(0)
        else:
            print_error("Invalid choice. Please try again.")
        
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")

if __name__ == "__main__":
    main()
