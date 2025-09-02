@echo off
REM AI Traffic Violation Detection System - Backend Startup Script (Windows)

echo 🚀 Starting AI Traffic Violation Detection System - Backend
echo ===========================================================

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup.py first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if backend directory exists
if not exist "backend" (
    echo ❌ Backend directory not found.
    pause
    exit /b 1
)

REM Navigate to backend directory
cd backend

REM Check if main.py exists
if not exist "main.py" (
    echo ❌ main.py not found in backend directory.
    pause
    exit /b 1
)

REM Check if YOLO model exists
if not exist "..\yolov8n.pt" (
    echo ⚠️ YOLO model not found. Downloading...
    python -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt'); print('✅ YOLOv8 model downloaded successfully')"
)

echo 🚀 Starting FastAPI server...
echo 📍 Server will be available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo 🔍 Health Check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python main.py

pause

