@echo off
REM InsuraIQ - Initial Project Setup

echo =============================================
echo InsuraIQ - Project Setup
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

REM Setup Backend
echo =============================================
echo Setting up Backend Environment...
echo =============================================
cd /d %~dp0backend

echo Creating Python virtual environment...
python -m venv .venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements-local.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)

echo Initializing database...
python init_db.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)

echo Backend setup completed successfully!
echo.

REM Setup Frontend
echo =============================================
echo Setting up Frontend Environment...
echo =============================================
cd /d %~dp0frontend

echo Installing Node.js dependencies...
npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Node.js dependencies
    pause
    exit /b 1
)

echo Frontend setup completed successfully!
echo.

REM Return to root directory
cd /d %~dp0

echo =============================================
echo Setup Complete!
echo =============================================
echo.
echo Your InsuraIQ project is now ready to use.
echo.
echo To start the application, run:
echo   start_all.bat           (for regular use)
echo   start_all_with_setup.bat (if you need fresh setup each time)
echo.
pause
