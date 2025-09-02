@echo off
REM AI Traffic Violation Detection System - Frontend Startup Script (Windows)

echo 🚀 Starting AI Traffic Violation Detection System - Frontend
echo ============================================================

REM Check if frontend directory exists
if not exist "frontend" (
    echo ❌ Frontend directory not found.
    pause
    exit /b 1
)

REM Navigate to frontend directory
cd frontend

REM Check if package.json exists
if not exist "package.json" (
    echo ❌ package.json not found in frontend directory.
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "node_modules" (
    echo ⚠️ Dependencies not installed. Installing...
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install dependencies. Please run setup.py first.
        pause
        exit /b 1
    )
)

echo 🚀 Starting React development server...
echo 📍 Application will be available at: http://localhost:3000
echo 🔗 Make sure the backend is running on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the development server
npm start

pause

