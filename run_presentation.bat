@echo off
title Ubuntu Cultural Connect
cd /d "%~dp0"

:: Start backend (minimized)
start /min cmd /c "cd backend && uvicorn main:app --host 127.0.0.1 --port 8001"

:: Start frontend (minimized)
start /min cmd /c "cd frontend && npm run dev"

timeout /t 5 >nul

echo Ubuntu Cultural Connect is running!
echo Frontend: http://localhost:5173
echo Backend:  http://127.0.0.1:8001
echo.
echo Close this window to stop both servers.
pause

:: Kill both
taskkill /f /im uvicorn.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
