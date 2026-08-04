Write-Output "Starting Ubuntu Cultural Connect..."
Write-Output ""

# Start backend
Write-Output "Starting Backend (FastAPI on http://127.0.0.1:8001)..."
$backendProc = Start-Process python -ArgumentList "-m","uvicorn","main:app","--reload","--host","127.0.0.1","--port","8001" -WorkingDirectory "$PSScriptRoot\backend" -PassThru -WindowStyle Minimized

# Wait for backend
Start-Sleep -Seconds 4
try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:8001/" -UseBasicParsing -TimeoutSec 3
    Write-Output "  Backend OK: $($r.Content)"
} catch {
    Write-Output "  Backend FAILED to start!"
}

# Start frontend
Write-Output ""
Write-Output "Starting Frontend (Vite on http://localhost:5173)..."
$frontendProc = Start-Process npm -ArgumentList "run","dev" -WorkingDirectory "$PSScriptRoot\frontend" -PassThru -WindowStyle Minimized

Start-Sleep -Seconds 5

Write-Output ""
Write-Output "==========================================="
Write-Output "  Open in browser: http://localhost:5173"
Write-Output "==========================================="
Write-Output ""
Write-Output "Backend PID: $($backendProc.Id)"
Write-Output "Frontend PID: $($frontendProc.Id)"
Write-Output ""
Write-Output "Press any key to stop both servers..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Cleanup
Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $frontendProc.Id -Force -ErrorAction SilentlyContinue
Write-Output "Servers stopped."
