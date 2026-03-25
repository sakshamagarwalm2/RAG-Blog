import subprocess
import sys
import time

backend_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000", "--host", "127.0.0.1"],
    cwd="D:\\Recks\\RAG Blog"
)

time.sleep(3)

frontend_process = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "D:\\Recks\\RAG Blog\\frontend\\app.py", "--server.port", "8501", "--server.headless", "true"],
    cwd="D:\\Recks\\RAG Blog"
)

print("Backend running on http://127.0.0.1:8000")
print("Frontend running on http://localhost:8501")
print("Press Ctrl+C to stop")

try:
    backend_process.wait()
    frontend_process.wait()
except KeyboardInterrupt:
    backend_process.terminate()
    frontend_process.terminate()
    print("\nServers stopped")
