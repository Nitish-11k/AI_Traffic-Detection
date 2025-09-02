#!/bin/bash

# AI Traffic Violation Detection System - Frontend Installation Script
# This script installs all necessary Node.js dependencies and sets up the frontend

echo "🚀 Installing AI Traffic Violation Detection System - Frontend"
echo "==============================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed."
    echo "Please install Node.js 16+ from https://nodejs.org/ and try again."
    exit 1
fi

# Check Node.js version
node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
required_version=16

if [ "$node_version" -lt "$required_version" ]; then
    echo "❌ Error: Node.js 16+ is required. Current version: $(node --version)"
    echo "Please upgrade Node.js and try again."
    exit 1
fi

echo "✅ Node.js version check passed: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed."
    echo "Please install npm and try again."
    exit 1
fi

echo "✅ npm is available: $(npm --version)"

# Navigate to frontend directory
if [ ! -d "frontend" ]; then
    echo "❌ Error: frontend directory not found."
    echo "Please run this script from the project root directory."
    exit 1
fi

cd frontend

# Install dependencies
echo "📚 Installing frontend dependencies..."
npm install

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Frontend dependencies installed successfully"
else
    echo "❌ Error: Failed to install frontend dependencies"
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating environment configuration..."
    cat > .env << EOF
# AI Traffic Violation Detection System - Frontend Environment
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
EOF
    echo "✅ Environment file created"
else
    echo "✅ Environment file already exists"
fi

echo ""
echo "🎉 Frontend installation completed successfully!"
echo ""
echo "To start the frontend development server:"
echo "1. Navigate to frontend: cd frontend"
echo "2. Start development server: npm start"
echo "3. Application will be available at: http://localhost:3000"
echo ""
echo "📋 Next steps:"
echo "- Make sure the backend is running on http://localhost:8000"
echo "- Start the frontend: npm start"
echo "- Open http://localhost:3000 in your browser"
echo ""

