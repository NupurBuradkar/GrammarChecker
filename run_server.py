import os
import sys
import time
import socket
import subprocess
import uvicorn
from backend.main import app

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def kill_process_on_port(port: int):
    """Terminates any stale zombie process occupying the port on Windows."""
    if sys.platform == "win32":
        try:
            output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode(errors="ignore")
            my_pid = os.getpid()
            for line in output.strip().splitlines():
                parts = line.strip().split()
                if len(parts) >= 5 and "LISTENING" in parts:
                    pid = int(parts[-1])
                    if pid != my_pid and pid > 0:
                        print(f"[GrammaCheck] Freeing port {port} by terminating old process (PID {pid})...")
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                        time.sleep(1)
        except Exception:
            pass

def find_available_port(start_port: int = 8000) -> int:
    for p in [start_port, 8080, 8001, 8081, 5000]:
        if not is_port_in_use(p):
            return p
    return start_port

if __name__ == "__main__":
    # Use port 8080 by default to bypass any stale process stuck on 8000
    target_port = 8080

    if is_port_in_use(target_port):
        print(f"[GrammaCheck] Port {target_port} is currently in use.")
        print("[GrammaCheck] Closing previous server process...")
        kill_process_on_port(target_port)

    # If port 8080 is still busy, fallback to next available port
    if is_port_in_use(target_port):
        target_port = find_available_port(8081)
        print(f"[GrammaCheck] Switching to port {target_port}!")

    url = f"http://127.0.0.1:{target_port}"
    print("=" * 60)
    print(" 🚀 Starting GrammaCheck AI - NLP Grammar & Spell Checker")
    print(f" Dashboard URL: {url}")
    print(f" Open {url} in your browser to view the updated Dashboard")
    print("=" * 60)

    uvicorn.run(app, host="127.0.0.1", port=target_port)


