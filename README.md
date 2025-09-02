# AI Traffic Violation Detection System

A comprehensive AI-powered traffic violation detection system built with advanced computer vision and modern web technologies. This system detects three types of traffic violations: red light violations, wrong-side driving, and helmet violations.

## 🚀 Features

### Core Detection Capabilities
- **Red Light Violation Detection**: Monitors vehicles crossing stop lines during red light phases
- **Wrong-Side Driving Detection**: Identifies vehicles moving against traffic flow using trajectory analysis
- **Helmet Violation Detection**: Detects motorcyclists not wearing helmets

### Advanced DSA Approaches
- **Spatial Indexing**: Grid-based spatial indexing for O(1) average case spatial queries
- **Trajectory Analysis**: Kalman filter-based vehicle tracking with direction vector analysis
- **Priority Queue Management**: Efficient violation tracking with time-based processing
- **Batch Processing**: Optimized video processing with frame sampling

### Modern Web Application
- **React TypeScript Frontend**: Modern, responsive UI with real-time updates
- **FastAPI Backend**: High-performance Python API with WebSocket support
- **Real-time Monitoring**: Live violation detection with WebSocket communication
- **Video Upload & Analysis**: Drag-and-drop video upload with AI analysis
- **Comprehensive Reporting**: Detailed violation statistics and export capabilities

## 🏗️ Architecture

```
AI Traffic Violation Detection System
├── backend/                    # Python FastAPI Backend
│   ├── main.py                # FastAPI application entry point
│   ├── models/                # Core detection models
│   │   ├── violation_detector.py    # Main detection engine
│   │   └── data_structures.py       # Efficient DSA implementations
│   └── utils/                 # Utility functions
│       └── video_processor.py       # Video processing utilities
├── frontend/                  # React TypeScript Frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── Dashboard.tsx         # Main dashboard
│   │   │   ├── VideoUpload.tsx       # Video upload interface
│   │   │   ├── ViolationReports.tsx  # Reports and analytics
│   │   │   └── RealTimeMonitoring.tsx # Live monitoring
│   │   └── services/          # API services
│   └── package.json
├── requirements.txt           # Python dependencies
└── README.md
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AITrafficVoilationSystem
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download YOLO model** (if not already present)
   ```bash
   # The yolov8n.pt model should be in the root directory
   # If not present, it will be downloaded automatically on first run
   ```

4. **Start the backend server**
   ```bash
   cd backend
   python main.py
   ```
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```
   The web application will be available at `http://localhost:3000`

## 🎯 Usage

### 1. Dashboard
- View real-time violation statistics
- Monitor system performance
- Access quick overview of recent violations

### 2. Video Upload & Analysis
- Upload traffic videos (MP4, AVI, MOV, MKV, WMV)
- Automatic AI analysis for violation detection
- Interactive video player with violation markers
- Export analysis results

### 3. Violation Reports
- Comprehensive violation analytics
- Filter and search capabilities
- Export data to CSV
- Visual charts and statistics

### 4. Real-Time Monitoring
- Live violation detection
- WebSocket-based real-time updates
- System status monitoring
- Live violation feed

## 🔧 Configuration

### Backend Configuration
Edit `backend/main.py` to configure:
- Model path and parameters
- Detection thresholds
- Traffic light simulation settings
- ROI (Region of Interest) coordinates

### Frontend Configuration
Edit `frontend/src/services/api.ts` to configure:
- API base URL
- Request timeouts
- WebSocket endpoints

## 📊 Technical Details

### Efficient DSA Approaches

1. **Spatial Indexing**
   - Grid-based spatial indexing for O(1) average case queries
   - Efficient collision detection and proximity searches
   - Memory-optimized data structures

2. **Trajectory Analysis**
   - Kalman filter-based vehicle tracking
   - Direction vector analysis for wrong-side detection
   - Sliding window trajectory processing

3. **Priority Queue Management**
   - Min-heap for time-based violation processing
   - Efficient violation tracking and statistics
   - Memory-bounded violation history

4. **Batch Processing**
   - Frame sampling for performance optimization
   - Parallel frame processing with asyncio
   - Configurable batch sizes and skip rates

### AI Detection Pipeline

1. **Object Detection**: YOLOv8 for vehicle and person detection
2. **Tracking**: DeepSORT-based object tracking
3. **Violation Analysis**: Rule-based violation detection
4. **Confidence Scoring**: Multi-factor confidence calculation

## 🚦 Detection Algorithms

### Red Light Violation
- Stop line intersection detection
- Traffic light state monitoring
- Vehicle trajectory analysis
- Temporal violation tracking

### Wrong-Side Driving
- Lane ROI (Region of Interest) definition
- Direction vector calculation
- Expected vs. actual direction comparison
- Trajectory-based validation

### Helmet Violation
- Person-motorcycle association
- Head region analysis
- Brightness-based helmet detection
- Proximity-based validation

## 📈 Performance Optimizations

- **Frame Sampling**: Process every 2nd frame for efficiency
- **Batch Processing**: Process frames in batches of 10
- **Spatial Indexing**: O(1) average case spatial queries
- **Memory Management**: Bounded data structures and cleanup
- **Async Processing**: Non-blocking video processing

## 🔒 Security Features

- CORS configuration for cross-origin requests
- Input validation and sanitization
- File type and size restrictions
- Error handling and logging

## 📱 Responsive Design

- Mobile-first responsive design
- Touch-friendly interface
- Adaptive layouts for different screen sizes
- Modern UI with smooth animations

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Backend Deployment
```bash
# Using uvicorn
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Using Docker (if Dockerfile provided)
docker build -t traffic-detection-backend .
docker run -p 8000:8000 traffic-detection-backend
```

### Frontend Deployment
```bash
cd frontend
npm run build
# Deploy the build folder to your web server
```

## 📝 API Documentation

Once the backend is running, visit:
- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

### Key Endpoints
- `POST /upload-video` - Upload and process video
- `GET /violations` - Get all violations
- `GET /violations/{id}` - Get specific violation
- `GET /health` - Health check
- `WebSocket /ws` - Real-time violation updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- YOLOv8 by Ultralytics for object detection
- FastAPI for the backend framework
- React and TypeScript for the frontend
- OpenCV for computer vision operations

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation and examples

---

**Note**: This system is designed for educational and research purposes. For production use, additional security measures, performance optimizations, and compliance considerations should be implemented.

