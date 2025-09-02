#!/bin/bash

echo "🚀 Starting AI Traffic Violation Detection System - Cloud Deployment"
echo "=================================================================="

# Set environment variables for cloud deployment
export PORT=${PORT:-8000}
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "🔧 Installing Python dependencies..."
pip install -r requirements.txt

echo "🔧 Installing Node.js dependencies..."
cd frontend
npm install
npm run build
cd ..

echo "🚀 Starting Backend Server on port $PORT..."
cd backend
python main.py
