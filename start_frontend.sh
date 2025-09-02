#!/bin/bash

# AI Traffic Violation Detection System - Frontend Startup Script

echo "🚀 Starting AI Traffic Violation Detection System - Frontend"
echo "============================================================="

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "❌ Frontend directory not found."
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found in frontend directory."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️ Dependencies not installed. Installing..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies. Please run install_frontend.sh first."
        exit 1
    fi
fi

echo "🚀 Starting React development server..."
echo "📍 Application will be available at: http://localhost:3000"
echo "🔗 Make sure the backend is running on http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the development server
npm start

