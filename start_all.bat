@echo off
REM InsuraIQ - Start Backend and Frontend

REM Start backend in a new terminal window
echo Starting backend...
start "Backend" cmd /k "cd backend && powershell -NoExit -Command .\run_local_dev.ps1"

REM Start frontend in a new terminal window
echo Starting frontend...
start "Frontend" cmd /k "cd frontend && npm install && npm run dev"

echo Both backend and frontend are starting in separate windows.
pause
