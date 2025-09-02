#!/bin/bash

# AI Traffic Violation Detection System - Backend Installation Script
# This script installs all necessary Python dependencies and sets up the backend

echo "🚀 Installing AI Traffic Violation Detection System - Backend"
echo "=============================================================="

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.8+ is required. Current version: $python_version"
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed. Please install pip3 and try again."
    exit 1
fi

echo "✅ pip3 is available"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Check if YOLO model exists, if not download it
if [ ! -f "yolov8n.pt" ]; then
    echo "🤖 Downloading YOLOv8 model..."
    python3 -c "
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
print('✅ YOLOv8 model downloaded successfully')
"
else
    echo "✅ YOLOv8 model already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/logs
mkdir -p backend/uploads
mkdir -p backend/outputs

echo ""
echo "🎉 Backend installation completed successfully!"
echo ""
echo "To start the backend server:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start server: cd backend && python main.py"
echo "3. API will be available at: http://localhost:8000"
echo "4. API documentation: http://localhost:8000/docs"
echo ""
echo "📋 Next steps:"
echo "- Run the frontend installation script: ./install_frontend.sh"
echo "- Or manually install frontend dependencies: cd frontend && npm install"
echo ""

