from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import asyncio
import json
import os
from typing import List, Dict, Any
import cv2
import numpy as np
from ultralytics import YOLO
import tempfile
import shutil
from datetime import datetime
import logging

from models.violation_detector import TrafficViolationDetector
from models.data_structures import ViolationEvent, VehicleTracker, SpatialIndex
from utils.video_processor import VideoProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Traffic Violation Detection System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
detector = None
active_connections: List[WebSocket] = []
video_processor = VideoProcessor()
processing_progress = {"status": "idle", "progress": 0, "message": ""}

@app.on_event("startup")
async def startup_event():
    """Initialize the traffic violation detector on startup"""
    global detector
    detector = TrafficViolationDetector()
    logger.info("Traffic Violation Detection System initialized")

@app.get("/")
async def root():
    return {"message": "AI Traffic Violation Detection System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """Upload and process a video file for violation detection"""
    global processing_progress
    try:
        processing_progress = {"status": "processing", "progress": 0, "message": "Uploading video..."}
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            temp_path = tmp_file.name
        
        processing_progress = {"status": "processing", "progress": 10, "message": "Starting video analysis..."}
        
        # Process video and get violations with real-time display
        violations = await video_processor.process_video_with_display(temp_path, detector)
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        processing_progress = {"status": "completed", "progress": 100, "message": "Analysis complete!"}
        
        return {
            "status": "success",
            "filename": file.filename,
            "violations": violations,
            "total_violations": len(violations)
        }
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        processing_progress = {"status": "error", "progress": 0, "message": str(e)}
        return {"status": "error", "message": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time violation detection"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"WebSocket connection established. Total connections: {len(active_connections)}")
    
    try:
        while True:
            # Keep connection alive with ping/pong
            try:
                # Wait for any message from client (ping, text, etc.)
                message = await websocket.receive()
                logger.debug(f"Received WebSocket message: {message}")
            except Exception as e:
                logger.error(f"WebSocket receive error: {str(e)}")
                break
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.info(f"WebSocket connection closed. Total connections: {len(active_connections)}")

async def broadcast_violation(violation: ViolationEvent):
    """Broadcast violation to all connected WebSocket clients"""
    if active_connections:
        message = {
            "type": "violation",
            "data": {
                "id": violation.id,
                "type": violation.type,
                "timestamp": violation.timestamp.isoformat(),
                "confidence": violation.confidence,
                "location": violation.location,
                "vehicle_id": violation.vehicle_id
            }
        }
        
        # Send to all active connections
        for connection in active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Remove disconnected clients
                active_connections.remove(connection)

@app.get("/violations")
async def get_violations():
    """Get all detected violations"""
    if detector:
        return {
            "violations": detector.get_all_violations(),
            "statistics": detector.get_violation_statistics()
        }
    return {"violations": [], "statistics": {}}

@app.get("/violations/{violation_id}")
async def get_violation(violation_id: str):
    """Get specific violation details"""
    if detector:
        violation = detector.get_violation_by_id(violation_id)
        if violation:
            return violation
    return {"error": "Violation not found"}

@app.get("/processing-status")
async def get_processing_status():
    """Get current video processing status"""
    return processing_progress

if __name__ == "__main__":
    import os
    
    # Get port from environment variable (for cloud deployment) or default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

