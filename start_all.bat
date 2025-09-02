@echo off
REM AI Traffic Violation Detection System - Complete Startup Script (Windows)

echo 🚀 Starting AI Traffic Violation Detection System - Complete
echo ============================================================

echo 🔧 Starting Backend Server...
start "Backend Server" cmd /k "start_backend.bat"

REM Wait a moment for backend to start
timeout /t 5 /nobreak >nul

echo 🔧 Starting Frontend Server...
start "Frontend Server" cmd /k "start_frontend.bat"

echo.
echo 🎉 Both servers are starting up!
echo.
echo 📍 Access Points:
echo    - Web Application: http://localhost:3000
echo    - API Documentation: http://localhost:8000/docs
echo    - API Health Check: http://localhost:8000/health
echo.
echo Both servers are running in separate windows.
echo Close the windows to stop the servers.
echo.

pause

