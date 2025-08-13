@echo off
REM InsuraIQ - Start Backend and Frontend

echo =============================================
echo Starting InsuraIQ - Insurance Management Platform
echo =============================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 20+ and try again
    pause
    exit /b 1
)

echo Prerequisites check passed!
echo.

REM =============================================
REM CLEANUP EXISTING PROCESSES
REM =============================================
echo Stopping any existing InsuraIQ processes...

REM Kill any existing terminal windows with InsuraIQ titles
echo Closing existing InsuraIQ terminal windows...
tasklist /FI "WINDOWTITLE eq InsuraIQ Backend (FastAPI)" >nul 2>&1 && (
    echo Found existing backend window, closing it...
    taskkill /FI "WINDOWTITLE eq InsuraIQ Backend (FastAPI)" /F >nul 2>&1
)
tasklist /FI "WINDOWTITLE eq InsuraIQ Frontend (React)" >nul 2>&1 && (
    echo Found existing frontend window, closing it...
    taskkill /FI "WINDOWTITLE eq InsuraIQ Frontend (React)" /F >nul 2>&1
)

REM Kill processes by port (more reliable)
echo Checking for processes on ports 8000 and 5173...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    if not "%%a"=="0" (
        echo Stopping process on port 8000 (PID: %%a)
        taskkill /PID %%a /F >nul 2>&1
    )
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    if not "%%a"=="0" (
        echo Stopping process on port 5173 (PID: %%a)
        taskkill /PID %%a /F >nul 2>&1
    )
)

REM Kill any uvicorn processes (backend)
echo Checking for uvicorn processes...
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr uvicorn') do (
    echo Stopping uvicorn process (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)

REM Kill any node processes running from our frontend directory
echo Checking for node processes in frontend directory...
wmic process where "name='node.exe' and commandline like '%%InsuraIQ%%frontend%%'" get processid /format:value 2>nul | findstr "ProcessId" > temp_pids.txt
for /f "tokens=2 delims==" %%a in (temp_pids.txt) do (
    if not "%%a"=="" (
        echo Stopping frontend node process (PID: %%a)
        taskkill /PID %%a /F >nul 2>&1
    )
)
del temp_pids.txt >nul 2>&1

echo Waiting for processes to fully terminate...
timeout /t 3 /nobreak >nul

REM =============================================
REM START NEW PROCESSES
REM =============================================

REM Start backend with full setup in a new terminal window
echo Starting FastAPI backend server with setup...
start "InsuraIQ Backend (FastAPI)" cmd /k "cd /d %~dp0backend && echo Setting up and starting FastAPI backend... && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements-local.txt && python init_db.py && echo Backend setup complete, starting server... && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a moment for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend with dependency installation in a new terminal window
echo Starting React frontend with setup...
start "InsuraIQ Frontend (React)" cmd /k "cd /d %~dp0frontend && echo Installing dependencies and starting React... && npm install && echo Frontend setup complete, starting development server... && npm run dev"

echo.
echo =============================================
echo Both services are starting in separate windows:
echo - Backend (FastAPI): http://localhost:8000
echo - Frontend (React): http://localhost:5173
echo - API Docs: http://localhost:8000/api/docs
echo =============================================
echo.
echo Wait for both services to fully start, then open:
echo http://localhost:5173
echo.
pause
