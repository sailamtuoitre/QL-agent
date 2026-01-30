@echo off
setlocal
title Restaurant Revenue Analytics Agent - Launcher

echo ===================================================
echo   Restaurant Revenue Analytics Agent - Launcher
echo ===================================================
echo.

:: 1. Start Redis (Docker)
echo [1/4] Starting Redis Infrastructure (Docker)...
docker-compose -f docker-compose.dev.yml up -d
if %errorlevel% neq 0 (
    echo [WARN] Docker command failed. Is Docker Desktop running?
    echo [WARN] Proceeding without Redis (Backend might warn)...
) else (
    echo [OK] Redis container started.
)
echo.

:: 2. Start Backend
echo [2/4] Launching Backend Server...
echo    - Starting FastAPI on Port 8000...
start "Backend API (Port 8000)" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: 2b. Start Celery Worker
echo [2b/4] Launching Celery Worker...
start "Celery Worker" cmd /k "cd backend && python -m celery -A app.workers.celery_app worker --loglevel=info -P solo"

:: 3. Start Frontend
echo [3/4] Launching Frontend Application...
echo    - Starting Next.js on Port 3000...
start "Frontend App (Port 3000)" cmd /k "cd frontend && npm run dev"

:: 4. Open Browser
echo [4/4] Waiting for servers to initialize (10 seconds)...
timeout /t 10 >nul
echo    - Opening http://localhost:3000
start http://localhost:3000
echo    - Opening http://localhost:8000/docs
start http://localhost:8000/docs

echo.
echo [SUCCESS] All services launched!
echo.
echo  - Backend Logs: Check the "Backend API" window.
echo  - Frontend Logs: Check the "Frontend App" window.
echo.
echo Press any key to exit this launcher (Servers will keep running)...
pause >nul
