# 🚀 Installation Guide - AI Traffic Violation Detection System

This guide will help you install and set up the AI Traffic Violation Detection System on your machine.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **npm**: Comes with Node.js

### Hardware Requirements
- **CPU**: Multi-core processor recommended
- **GPU**: Optional but recommended for faster processing
- **Webcam**: For real-time monitoring (optional)
- **Video Files**: For testing and analysis

## 🛠️ Quick Installation

### Option 1: Automated Setup (Recommended)

#### For Linux/macOS:
```bash
# Clone or download the project
cd AITrafficVoilationSystem

# Run the complete installation script
./install_all.sh
```

#### For Windows:
```cmd
# Clone or download the project
cd AITrafficVoilationSystem

# Run the Python setup script
python setup.py
```

### Option 2: Manual Installation

#### Step 1: Install Backend Dependencies

**Linux/macOS:**
```bash
./install_backend.sh
```

**Windows:**
```cmd
python setup.py
```

#### Step 2: Install Frontend Dependencies

**Linux/macOS:**
```bash
./install_frontend.sh
```

**Windows:**
```cmd
cd frontend
npm install
cd ..
```

## 🔧 Detailed Installation Steps

### 1. Python Backend Setup

#### Check Python Version
```bash
python3 --version
# Should be 3.8 or higher
```

#### Create Virtual Environment
```bash
python3 -m venv venv
```

#### Activate Virtual Environment
**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```cmd
venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Download YOLO Model
```bash
python3 -c "from ultralytics import YOLO; model = YOLO('yolov8n.pt')"
```

### 2. Node.js Frontend Setup

#### Check Node.js Version
```bash
node --version
# Should be 16 or higher
```

#### Install Dependencies
```bash
cd frontend
npm install
cd ..
```

#### Create Environment File
```bash
# Create frontend/.env file
echo "REACT_APP_API_URL=http://localhost:8000" > frontend/.env
echo "REACT_APP_WS_URL=ws://localhost:8000" >> frontend/.env
```

## 🚀 Starting the Application

### Option 1: Start Both Servers (Recommended)

**Linux/macOS:**
```bash
./start_all.sh
```

**Windows:**
```cmd
start_all.bat
```

### Option 2: Start Servers Separately

#### Start Backend Server

**Linux/macOS:**
```bash
./start_backend.sh
```

**Windows:**
```cmd
start_backend.bat
```

#### Start Frontend Server (in a new terminal)

**Linux/macOS:**
```bash
./start_frontend.sh
```

**Windows:**
```cmd
start_frontend.bat
```

### Option 3: Manual Start

#### Backend:
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Start backend
cd backend
python main.py
```

#### Frontend:
```bash
cd frontend
npm start
```

## 🌐 Access Points

Once both servers are running:

- **Web Application**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health
- **Alternative API Docs**: http://localhost:8000/redoc

## 🔍 Verification

### Check Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Check Frontend
Open http://localhost:3000 in your browser. You should see the AI Traffic Violation Detection System dashboard.

## 🐛 Troubleshooting

### Common Issues

#### 1. Python Version Issues
```bash
# If you have multiple Python versions
python3.8 -m venv venv
# or
python3.9 -m venv venv
```

#### 2. Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in backend/main.py
```

#### 3. Node.js Version Issues
```bash
# Install Node Version Manager (nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 16
nvm use 16
```

#### 4. Permission Issues (Linux/macOS)
```bash
# Make scripts executable
chmod +x *.sh
```

#### 5. Virtual Environment Issues
```bash
# Remove and recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 6. YOLO Model Download Issues
```bash
# Manual download
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

### Error Messages and Solutions

#### "ModuleNotFoundError: No module named 'ultralytics'"
```bash
# Reinstall ultralytics
pip install ultralytics
```

#### "npm: command not found"
- Install Node.js from https://nodejs.org/
- Make sure npm is in your PATH

#### "Permission denied" (Linux/macOS)
```bash
# Fix permissions
chmod +x *.sh
sudo chown -R $USER:$USER .
```

#### "Port 3000 is already in use"
```bash
# Kill process using port 3000
lsof -ti:3000 | xargs kill -9  # Linux/macOS
```

## 📦 Dependencies

### Python Dependencies (requirements.txt)
- fastapi==0.104.1
- uvicorn==0.24.0
- opencv-python==4.8.1.78
- ultralytics==8.0.196
- numpy==1.24.3
- python-multipart==0.0.6
- websockets==12.0
- aiofiles==23.2.1
- python-jose[cryptography]==3.3.0
- passlib[bcrypt]==1.7.4
- pydantic==2.5.0
- Pillow==10.1.0
- scipy==1.11.4
- scikit-learn==1.3.2

### Node.js Dependencies (package.json)
- React 18.2.0
- TypeScript 5.2.2
- Tailwind CSS 3.3.3
- Recharts 2.8.0
- Framer Motion 10.16.4
- React Player 2.13.0
- And more...

## 🔧 Configuration

### Backend Configuration
Edit `backend/main.py` to modify:
- Server host and port
- Model parameters
- Detection thresholds

### Frontend Configuration
Edit `frontend/src/services/api.ts` to modify:
- API base URL
- Request timeouts
- WebSocket endpoints

### Environment Variables
Create `frontend/.env`:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## 📚 Next Steps

1. **Test the Installation**: Upload a sample video and verify detection works
2. **Configure Detection Parameters**: Adjust thresholds in the backend
3. **Customize UI**: Modify the frontend components as needed
4. **Add More Violation Types**: Extend the detection algorithms
5. **Deploy to Production**: Use Docker or cloud services for deployment

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review the error logs in the terminal
3. Check the API documentation at http://localhost:8000/docs
4. Create an issue in the project repository
5. Contact the development team

## 🎉 Success!

If everything is working correctly, you should see:
- Backend server running on port 8000
- Frontend application running on port 3000
- API documentation accessible
- Web interface loading without errors

Congratulations! Your AI Traffic Violation Detection System is ready to use! 🚀

