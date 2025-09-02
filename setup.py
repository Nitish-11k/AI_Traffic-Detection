#!/usr/bin/env python3
"""
AI Traffic Violation Detection System - Setup Script
This script helps with initial setup and dependency installation
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8+ is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version check passed: {version.major}.{version.minor}.{version.micro}")
    return True

def check_node_version():
    """Check if Node.js version is 16 or higher"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Error: Node.js is not installed")
            return False
        
        version_str = result.stdout.strip().lstrip('v')
        major_version = int(version_str.split('.')[0])
        
        if major_version < 16:
            print(f"❌ Error: Node.js 16+ is required. Current version: {version_str}")
            return False
        
        print(f"✅ Node.js version check passed: {version_str}")
        return True
    except FileNotFoundError:
        print("❌ Error: Node.js is not installed")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("📚 Installing Python dependencies...")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists('venv'):
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
    
    # Determine the correct pip path based on OS
    if platform.system() == "Windows":
        pip_path = os.path.join('venv', 'Scripts', 'pip')
        python_path = os.path.join('venv', 'Scripts', 'python')
    else:
        pip_path = os.path.join('venv', 'bin', 'pip')
        python_path = os.path.join('venv', 'bin', 'python')
    
    # Upgrade pip
    print("⬆️ Upgrading pip...")
    subprocess.run([python_path, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
    
    # Install requirements
    subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
    print("✅ Python dependencies installed successfully")
    return True

def install_node_dependencies():
    """Install Node.js dependencies"""
    print("📚 Installing Node.js dependencies...")
    
    frontend_dir = Path('frontend')
    if not frontend_dir.exists():
        print("❌ Error: frontend directory not found")
        return False
    
    # Change to frontend directory and install dependencies
    os.chdir(frontend_dir)
    subprocess.run(['npm', 'install'], check=True)
    os.chdir('..')
    print("✅ Node.js dependencies installed successfully")
    return True

def download_yolo_model():
    """Download YOLO model if it doesn't exist"""
    if os.path.exists('yolov8n.pt'):
        print("✅ YOLO model already exists")
        return True
    
    print("🤖 Downloading YOLO model...")
    try:
        # Determine the correct python path based on OS
        if platform.system() == "Windows":
            python_path = os.path.join('venv', 'Scripts', 'python')
        else:
            python_path = os.path.join('venv', 'bin', 'python')
        
        subprocess.run([
            python_path, '-c',
            "from ultralytics import YOLO; model = YOLO('yolov8n.pt'); print('✅ YOLO model downloaded successfully')"
        ], check=True)
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Warning: Could not download YOLO model automatically")
        print("The model will be downloaded on first run")
        return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating necessary directories...")
    
    directories = [
        'backend/logs',
        'backend/uploads',
        'backend/outputs',
        'frontend/public'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created successfully")

def create_env_files():
    """Create environment files"""
    print("📝 Creating environment files...")
    
    # Frontend .env file
    frontend_env = Path('frontend/.env')
    if not frontend_env.exists():
        with open(frontend_env, 'w') as f:
            f.write("""# AI Traffic Violation Detection System - Frontend Environment
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
""")
        print("✅ Frontend environment file created")
    else:
        print("✅ Frontend environment file already exists")
    
    # Backend .env file (optional)
    backend_env = Path('backend/.env')
    if not backend_env.exists():
        with open(backend_env, 'w') as f:
            f.write("""# AI Traffic Violation Detection System - Backend Environment
# Add any backend-specific environment variables here
""")
        print("✅ Backend environment file created")
    else:
        print("✅ Backend environment file already exists")

def main():
    """Main setup function"""
    print("🚀 AI Traffic Violation Detection System - Setup")
    print("=" * 50)
    
    # Check system requirements
    if not check_python_version():
        return 1
    
    if not check_node_version():
        return 1
    
    # Install dependencies
    try:
        install_python_dependencies()
        install_node_dependencies()
        download_yolo_model()
        create_directories()
        create_env_files()
        
        print("")
        print("🎉 Setup completed successfully!")
        print("")
        print("🚀 To start the application:")
        print("1. Backend: source venv/bin/activate && cd backend && python main.py")
        print("2. Frontend: cd frontend && npm start")
        print("")
        print("Or use the provided scripts:")
        print("- ./start_backend.sh (Linux/Mac) or start_backend.bat (Windows)")
        print("- ./start_frontend.sh (Linux/Mac) or start_frontend.bat (Windows)")
        print("- ./start_all.sh (Linux/Mac) to start both")
        print("")
        print("📍 Access Points:")
        print("- Web Application: http://localhost:3000")
        print("- API Documentation: http://localhost:8000/docs")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during setup: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

