@echo off
REM InsuraIQ - Start Backend and Frontend (Batch-only version)

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

REM Start backend using direct Python commands
echo Starting FastAPI backend server...
start "InsuraIQ Backend (FastAPI)" cmd /k "cd /d %~dp0backend && echo Starting FastAPI backend... && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements-local.txt && python -c \"from app.database import Base, engine; from app import models; Base.metadata.create_all(bind=engine)\" && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a moment for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in a new terminal window
echo Starting React frontend...
start "InsuraIQ Frontend (React)" cmd /k "cd /d %~dp0frontend && echo Installing dependencies and starting React... && npm install && npm run dev"

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
