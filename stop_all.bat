@echo off
REM InsuraIQ - Stop all running services

echo =============================================
echo Stopping InsuraIQ Services
echo =============================================

REM Close terminal windows by title
echo Closing InsuraIQ terminal windows...
tasklist /FI "WINDOWTITLE eq InsuraIQ Backend (FastAPI)" >nul 2>&1 && (
    echo Closing backend terminal window...
    taskkill /FI "WINDOWTITLE eq InsuraIQ Backend (FastAPI)" /F >nul 2>&1
)
tasklist /FI "WINDOWTITLE eq InsuraIQ Frontend (React)" >nul 2>&1 && (
    echo Closing frontend terminal window...
    taskkill /FI "WINDOWTITLE eq InsuraIQ Frontend (React)" /F >nul 2>&1
)

REM Stop processes on port 8000 (Backend)
echo Stopping backend services on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    if not "%%a"=="0" (
        echo Stopping backend process PID: %%a
        taskkill /PID %%a /F >nul 2>&1
    )
)

REM Stop processes on port 5173 (Frontend)
echo Stopping frontend services on port 5173...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    if not "%%a"=="0" (
        echo Stopping frontend process PID: %%a
        taskkill /PID %%a /F >nul 2>&1
    )
)

REM Stop any uvicorn processes specifically
echo Stopping uvicorn processes...
for /f "skip=1 tokens=2" %%a in ('wmic process where "name='python.exe' and commandline like '%%uvicorn%%'" get processid /format:value 2^>nul ^| findstr "ProcessId"') do (
    if not "%%a"=="" (
        echo Stopping uvicorn process PID: %%a
        taskkill /PID %%a /F >nul 2>&1
    )
)

REM Stop node processes in InsuraIQ frontend directory
echo Stopping InsuraIQ node processes...
for /f "skip=1 tokens=2 delims==" %%a in ('wmic process where "name='node.exe' and commandline like '%%InsuraIQ%%frontend%%'" get processid /format:value 2^>nul ^| findstr "ProcessId"') do (
    if not "%%a"=="" (
        echo Stopping frontend node process PID: %%a
        taskkill /PID %%a /F >nul 2>&1
    )
)

REM Final cleanup - kill any remaining python processes with app.main in command line
echo Final cleanup of any remaining InsuraIQ processes...
for /f "skip=1 tokens=2 delims==" %%a in ('wmic process where "name='python.exe' and commandline like '%%app.main%%'" get processid /format:value 2^>nul ^| findstr "ProcessId"') do (
    if not "%%a"=="" (
        echo Stopping remaining backend process PID: %%a
        taskkill /PID %%a /F >nul 2>&1
    )
)

echo.
echo Verifying cleanup...
timeout /t 2 /nobreak >nul

REM Check if ports are now free
netstat -ano | findstr :8000 | findstr LISTENING >nul && (
    echo WARNING: Port 8000 still in use
) || (
    echo ✓ Port 8000 is now free
)

netstat -ano | findstr :5173 | findstr LISTENING >nul && (
    echo WARNING: Port 5173 still in use
) || (
    echo ✓ Port 5173 is now free
)

echo.
echo =============================================
echo All InsuraIQ services have been stopped
echo =============================================
echo.
pause
