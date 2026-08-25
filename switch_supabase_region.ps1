# Switch Supabase to a new (closer) region
#
# HOW TO USE:
#   1. Create a new Supabase project in the closer region (e.g. Central EU / Frankfurt).
#   2. Copy its Session pooler connection string (Project Settings -> Database -> URI).
#   3. Run this script and paste the connection string when prompted.
#   4. It will: update backend/.env -> migrate data from SQLite -> restart the backend.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File switch_supabase_region.ps1

$ErrorActionPreference = "Stop"
$BackendDir = Join-Path $PSScriptRoot "backend"
$EnvFile = Join-Path $BackendDir ".env"

Write-Host "=== Supabase region switch ===" -ForegroundColor Cyan

if (-not (Test-Path $EnvFile)) {
    Write-Error "Cannot find backend/.env at $EnvFile"
    exit 1
}

Write-Host ""
Write-Host "Paste your NEW Supabase connection string (Session pooler), then press Enter:" -ForegroundColor Yellow
$NewUrl = Read-Host

$NewUrl = $NewUrl.Trim()
if ($NewUrl -eq "") {
    Write-Error "No connection string provided. Aborting."
    exit 1
}

# Normalize: ensure prefix and URL-encode any # in the password portion
if (-not $NewUrl.StartsWith("DATABASE_URL=")) {
    $NewUrl = "DATABASE_URL=" + $NewUrl
}
# URL-encode # -> %23 (so it is not treated as a comment)
$NewUrl = $NewUrl.Replace("#@", "%23@")

Write-Host ""
Write-Host "Updating $EnvFile ..." -ForegroundColor Cyan
Set-Content -Path $EnvFile -Value $NewUrl -NoNewline
Write-Host "  Updated: $NewUrl" -ForegroundColor Green

Write-Host ""
Write-Host "Verifying connection to new database..." -ForegroundColor Cyan
Push-Location $BackendDir
try {
    $connUrl = ($NewUrl -replace "^DATABASE_URL=", "")
    python -c "import psycopg2; from urllib.parse import unquote; u=[x for x in '$connUrl'.split('@')]; pw=unquote('$connUrl'.split('@')[0].split(':')[-1]); conn=psycopg2.connect(host='$($connUrl.Split('@')[1].Split(':')[0])', port=int('$($connUrl.Split('@')[1].Split(':')[1].Split('/')[0])'), user='$($connUrl.Split('@')[0].Split('://')[1].Split(':')[0])', password=pw, dbname='postgres', connect_timeout=10, sslmode='require'); print('CONNECTION OK')" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Connection check failed - continuing anyway. The migration will reveal the real error." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Connection check failed - continuing anyway." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Migrating data from SQLite to the new database..." -ForegroundColor Cyan
$env:DATABASE_URL = "sqlite:///./data.db"
$env:POSTGRESQL_DATABASE_URL = $connUrl
"yes" | python migrate_to_postgresql.py
Write-Host ""
Write-Host "Migration done." -ForegroundColor Green
Pop-Location

Write-Host ""
Write-Host "Stopping old backend if running..." -ForegroundColor Cyan
$listeners = Get-NetTCPConnection -State Listen -LocalPort 8001 -ErrorAction SilentlyContinue
foreach ($l in $listeners) {
    Stop-Process -Id $l.OwningProcess -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Starting backend on port 8001..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001" -WorkingDirectory $BackendDir -RedirectStandardOutput (Join-Path $BackendDir "backend_out.txt") -RedirectStandardError (Join-Path $BackendDir "backend_err.txt") -PassThru | Out-Null
Start-Sleep -Seconds 8

$listener = Get-NetTCPConnection -State Listen -LocalPort 8001 -ErrorAction SilentlyContinue
if ($listener) {
    Write-Host "Backend is running on http://127.0.0.1:8001" -ForegroundColor Green
    Write-Host "Done! The app should now be faster." -ForegroundColor Green
} else {
    Write-Host "Backend did not start. Check backend/backend_err.txt for errors." -ForegroundColor Red
}
