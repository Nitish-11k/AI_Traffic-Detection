#!/bin/bash

# AI Traffic Violation Detection System - Complete Startup Script
# This script starts both backend and frontend servers

echo "🚀 Starting AI Traffic Violation Detection System - Complete"
echo "============================================================="

# Make startup scripts executable
chmod +x start_backend.sh
chmod +x start_frontend.sh

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "🔧 Starting Backend Server..."
./start_backend.sh &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

echo "🔧 Starting Frontend Server..."
./start_frontend.sh &
FRONTEND_PID=$!

echo ""
echo "🎉 Both servers are starting up!"
echo ""
echo "📍 Access Points:"
echo "   - Web Application: http://localhost:3000"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - API Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

