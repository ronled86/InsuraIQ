# Run backend locally without Docker using SQLite and relaxed auth.
$ErrorActionPreference = "Stop"
$env:LOCAL_DEV = "true"
if (-Not $env:SQLALCHEMY_DATABASE_URL -or $env:SQLALCHEMY_DATABASE_URL -eq "") { $env:SQLALCHEMY_DATABASE_URL = "sqlite:///./local_dev.db" }
$usingSQLite = $env:SQLALCHEMY_DATABASE_URL.StartsWith('sqlite')
$env:PYTHONWARNINGS = "ignore::DeprecationWarning"

if (-Not (Test-Path .venv)) { python -m venv .venv }
. .venv/Scripts/Activate.ps1
python --version
pip install --upgrade pip > $null

# Install dependencies
if ($usingSQLite -and (Test-Path requirements-local.txt)) {
	Write-Host "Installing dependencies from requirements-local.txt (SQLite mode)" -ForegroundColor Cyan
	pip install -r requirements-local.txt
} elseif ($usingSQLite) {
	# Fallback dynamic filter
	$reqLines = Get-Content requirements.txt | Where-Object { $_.Trim() -ne "" }
	$filtered = $reqLines | Where-Object { $_ -notmatch '^psycopg2-binary' }
	$filtered | Set-Content requirements.local.tmp
	Write-Host "Installing filtered dependencies (SQLite mode, skipping psycopg2-binary)..." -ForegroundColor Cyan
	pip install -r requirements.local.tmp
	Remove-Item requirements.local.tmp -ErrorAction SilentlyContinue
	Write-Host "(If you need Postgres later, install psycopg2-binary separately)" -ForegroundColor DarkGray
} else {
	Write-Host "Installing full dependencies (Postgres mode)..." -ForegroundColor Cyan
	pip install -r requirements.txt
}

# Initialize schema for SQLite only
if ($usingSQLite) { pwsh -NoLogo -File scripts/Init-SQLite.ps1 }

Write-Host "Starting Uvicorn (logs will also go to backend-dev.log)" -ForegroundColor Green
$env:PYTHONUNBUFFERED = "1"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --no-use-colors *>&1 | Tee-Object -FilePath backend-dev.log
