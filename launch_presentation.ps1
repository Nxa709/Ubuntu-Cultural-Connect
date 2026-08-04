# Launch Ubuntu Cultural Connect — no visible terminals
$root = Split-Path -Parent $PSCommandPath

# Start backend (hidden)
$backendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    uvicorn main:app --host 127.0.0.1 --port 8001
} -ArgumentList "$root\backend"

# Start frontend (hidden)
$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    npm run dev
} -ArgumentList "$root\frontend"

Write-Host "Ubuntu Cultural Connect is starting..."
Write-Host "Frontend: http://localhost:5173"
Write-Host "Backend:  http://127.0.0.1:8001"
Write-Host ""
Write-Host "Press any key to stop..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Stop-Job $backendJob; Stop-Job $frontendJob
Remove-Job $backendJob; Remove-Job $frontendJob
