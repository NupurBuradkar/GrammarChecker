@echo off
title GrammaCheck AI Server
echo ============================================================
echo  Starting GrammaCheck AI Server on Port 8080...
echo ============================================================

:: Terminate any stale process on port 8080 if present
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080 ^| findstr LISTENING') do (
    echo Terminating old server process (PID %%a) on port 8080...
    taskkill /F /PID %%a >nul 2>&1
)

echo Opening http://127.0.0.1:8080 in your browser...
start "" "http://127.0.0.1:8080"
python run_server.py
pause


