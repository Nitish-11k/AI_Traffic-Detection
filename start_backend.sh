#!/bin/bash

# AI Traffic Violation Detection System - Backend Startup Script

echo "🚀 Starting AI Traffic Violation Detection System - Backend"
echo "==========================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run install_backend.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Backend directory not found."
    exit 1
fi

# Navigate to backend directory
cd backend

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found in backend directory."
    exit 1
fi

# Check if YOLO model exists
if [ ! -f "../yolov8n.pt" ]; then
    echo "⚠️ YOLO model not found. Downloading..."
    python3 -c "
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
print('✅ YOLOv8 model downloaded successfully')
"
fi

echo "🚀 Starting FastAPI server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python main.py

