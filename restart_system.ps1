# Restart Altrosyn JD Parser System (Docker, DB Migration, Backend, Frontend)

Write-Host "Stopping existing backend (port 8000) and frontend (port 3000) processes..." -ForegroundColor Yellow
$ports = @(8000, 3000)
foreach ($port in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conn) {
        foreach ($c in $conn) {
            if ($c.OwningProcess) {
                Write-Host "Stopping process ID $($c.OwningProcess) on port $port..." -ForegroundColor Cyan
                Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

Write-Host "Restarting Docker Database container..." -ForegroundColor Yellow
docker compose down db
docker compose up -d db

Write-Host "Waiting 5 seconds for PostgreSQL database to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "Running Alembic migrations..." -ForegroundColor Yellow
.venv\Scripts\alembic upgrade head

Write-Host "Starting Uvicorn Backend server on http://localhost:8000..." -ForegroundColor Green
Start-Process -FilePath ".venv\Scripts\uvicorn.exe" -ArgumentList "app.main:app --host 0.0.0.0 --port 8000" -NoNewWindow

Write-Host "Starting Next.js Frontend server on http://localhost:3000..." -ForegroundColor Green
Start-Process -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory "frontend" -NoNewWindow

Write-Host "System restarted successfully!" -ForegroundColor Green
