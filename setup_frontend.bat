@echo off
setlocal

echo [INFO] Checking for Node.js installation...
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Node.js is not installed or not in PATH.
    echo [INFO] Attempting to install Node.js LTS via Winget...
    winget install -e --id OpenJS.NodeJS.LTS
    
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install Node.js. Please install it manually from https://nodejs.org/
        pause
        exit /b 1
    )
    
    echo [SUCCESS] Node.js installed successfully.
    echo [INFO] IMPORTANT: You may need to restart your terminal or computer for the changes to take effect.
    echo [INFO] After restarting, please run this script again.
    pause
    exit /b 0
)

echo [INFO] Node.js is detected. Version:
node -v

echo [INFO] Checking if 'frontend' directory exists...
if exist "frontend" (
    echo [WARN] 'frontend' directory already exists. Skipping creation to avoid overwrite.
    echo [INFO] If you want to recreate it, please delete or rename the existing 'frontend' folder.
) else (
    echo [INFO] Creating Next.js frontend application...
    call npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --no-git --yes
    
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create Next.js app.
        pause
        exit /b 1
    )
    echo [SUCCESS] Frontend application created successfully!
)

echo [INFO] Verifying backend environment...
if not exist "backend\.env" (
    if exist "backend\.env.example" (
        echo [INFO] Creating backend/.env from example...
        copy "backend\.env.example" "backend\.env"
    ) else (
        echo [WARN] backend/.env.example not found. Skipping .env creation.
    )
) else (
    echo [INFO] backend/.env already exists.
)

echo.
echo [SUCCESS] Setup process completed!
echo [INFO] To start the development environment:
echo 1. Backend: cd backend ^&^& uvicorn main:app --reload
echo 2. Frontend: cd frontend ^&^& npm run dev
echo.
pause
