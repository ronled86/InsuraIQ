param()
Write-Host "Initializing SQLite schema..." -ForegroundColor Cyan
& python -c "from app.database import Base, engine; from app import models; Base.metadata.create_all(bind=engine); print('SQLite schema ensured at', engine.url)"
if ($LASTEXITCODE -ne 0) { Write-Error "Schema initialization failed"; exit 1 }
Write-Host "Schema ready." -ForegroundColor Green
