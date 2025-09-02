#!/bin/bash

# AI Traffic Violation Detection System - Complete Installation Script
# This script installs both backend and frontend dependencies

echo "🚀 Installing AI Traffic Violation Detection System - Complete Setup"
echo "===================================================================="

# Make installation scripts executable
chmod +x install_backend.sh
chmod +x install_frontend.sh

# Install backend
echo "🔧 Installing Backend..."
./install_backend.sh

if [ $? -ne 0 ]; then
    echo "❌ Backend installation failed. Please check the errors above."
    exit 1
fi

echo ""
echo "🔧 Installing Frontend..."
./install_frontend.sh

if [ $? -ne 0 ]; then
    echo "❌ Frontend installation failed. Please check the errors above."
    exit 1
fi

echo ""
echo "🎉 Complete installation finished successfully!"
echo ""
echo "🚀 To start the application:"
echo ""
echo "1. Start the Backend:"
echo "   source venv/bin/activate"
echo "   cd backend"
echo "   python main.py"
echo ""
echo "2. Start the Frontend (in a new terminal):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "3. Access the application:"
echo "   - Web Application: http://localhost:3000"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - API Health Check: http://localhost:8000/health"
echo ""
echo "📋 System Requirements:"
echo "- Python 3.8+"
echo "- Node.js 16+"
echo "- 4GB+ RAM recommended"
echo "- Webcam or video files for testing"
echo ""
echo "🔧 Troubleshooting:"
echo "- If backend fails to start, check if port 8000 is available"
echo "- If frontend fails to start, check if port 3000 is available"
echo "- Make sure all dependencies are installed correctly"
echo ""
echo "📚 Documentation:"
echo "- README.md contains detailed setup instructions"
echo "- API documentation available at http://localhost:8000/docs"
echo ""

