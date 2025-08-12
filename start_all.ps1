# InsuraIQ - Start Backend and Frontend (PowerShell Version)

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Starting InsuraIQ - Insurance Management Platform" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node.js is available
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js 20+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`nPrerequisites check passed!" -ForegroundColor Green
Write-Host ""

# Start backend in a new PowerShell window
Write-Host "Starting FastAPI backend server..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; Write-Host 'Starting FastAPI backend...' -ForegroundColor Cyan; .\run_local_dev.ps1" -WindowStyle Normal

# Wait a moment for backend to start
Write-Host "Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start frontend in a new PowerShell window  
Write-Host "Starting React frontend..." -ForegroundColor Yellow
$frontendPath = Join-Path $PSScriptRoot "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; Write-Host 'Installing dependencies and starting React...' -ForegroundColor Cyan; npm install; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Both services are starting in separate windows:" -ForegroundColor White
Write-Host "- Backend (FastAPI): http://localhost:8000" -ForegroundColor Green
Write-Host "- Frontend (React): http://localhost:5173" -ForegroundColor Green  
Write-Host "- API Docs: http://localhost:8000/api/docs" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Wait for both services to fully start, then open:" -ForegroundColor Yellow
Write-Host "http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

# Check if services are running after a delay
Write-Host "Checking if services started successfully..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

try {
    $backendCheck = Invoke-WebRequest -Uri "http://localhost:8000/api/docs" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✓ Backend is running!" -ForegroundColor Green
} catch {
    Write-Host "⚠ Backend may still be starting or failed to start" -ForegroundColor Yellow
    Write-Host "Check the Backend window for error messages" -ForegroundColor Yellow
}

try {
    $frontendCheck = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✓ Frontend is running!" -ForegroundColor Green
} catch {
    Write-Host "⚠ Frontend may still be starting or failed to start" -ForegroundColor Yellow
    Write-Host "Check the Frontend window for error messages" -ForegroundColor Yellow
}

Read-Host "`nPress Enter to exit"
