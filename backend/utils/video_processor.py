"""
Video Processing Utilities with Efficient Algorithms
"""

import cv2
import numpy as np
import asyncio
import tempfile
import os
import base64
import json
from typing import List, Dict, Any
import logging
from datetime import datetime

from models.violation_detector import TrafficViolationDetector
from models.data_structures import ViolationEvent

logger = logging.getLogger(__name__)

class VideoProcessor:
    """
    Efficient video processing with frame sampling and batch processing
    """
    
    def __init__(self):
        self.frame_skip = 5  # Process every 5th frame for better performance
        self.batch_size = 10  # Process frames in batches for efficiency
    
    async def process_video(self, video_path: str, detector: TrafficViolationDetector) -> List[Dict[str, Any]]:
        """
        Process video file and detect violations
        Uses efficient frame sampling and batch processing
        """
        violations = []
        
        try:
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            logger.info(f"Processing video: {total_frames} frames, {fps} FPS, {duration:.2f}s duration")
            
            frame_number = 0
            processed_frames = 0
            
            # Process video in batches for efficiency
            while True:
                batch_frames = []
                batch_frame_numbers = []
                
                # Collect batch of frames
                for _ in range(self.batch_size):
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Skip frames for efficiency
                    if frame_number % self.frame_skip == 0:
                        batch_frames.append(frame)
                        batch_frame_numbers.append(frame_number)
                    
                    frame_number += 1
                
                if not batch_frames:
                    break
                
                # Process batch
                batch_violations = await self._process_frame_batch(
                    batch_frames, batch_frame_numbers, detector
                )
                violations.extend(batch_violations)
                
                processed_frames += len(batch_frames)
                
                # Log progress
                if processed_frames % 100 == 0:
                    progress = (frame_number / total_frames) * 100
                    logger.info(f"Processing progress: {progress:.1f}% ({processed_frames} frames processed)")
            
            cap.release()
            
            # Add violations to detector's tracker
            for violation in violations:
                detector.add_violation(violation)
            
            logger.info(f"Video processing completed. Found {len(violations)} violations")
            
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            raise
        
        return [
            {
                "id": v.id,
                "type": v.type,
                "timestamp": v.timestamp.isoformat(),
                "confidence": v.confidence,
                "location": {"x": v.location.x, "y": v.location.y},
                "vehicle_id": v.vehicle_id,
                "frame_number": v.frame_number,
                "details": v.details
            }
            for v in violations
        ]
    
    async def process_video_with_display(self, video_path: str, detector: TrafficViolationDetector) -> List[Dict[str, Any]]:
        """
        Process video file with real-time display and WebSocket broadcasting
        """
        violations = []
        
        try:
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            logger.info(f"Processing video with display: {total_frames} frames, {fps} FPS, {duration:.2f}s duration")
            
            frame_number = 0
            processed_frames = 0
            
            # Process video frame by frame for real-time display
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process every 3rd frame for real-time display (faster processing)
                if frame_number % 3 == 0:
                    # Process frame and get violations
                    frame_violations = detector.process_frame(frame, frame_number)
                    violations.extend(frame_violations)
                    
                    # Create display frame with annotations
                    display_frame = self._create_display_frame(frame, frame_violations, frame_number, fps)
                    
                    # Broadcast frame via WebSocket with actual frame number
                    await self._broadcast_frame(display_frame, frame_number, len(violations))
                    
                    # Add small delay to simulate real-time video (faster but visible)
                    frame_delay = 1.0 / fps  # Calculate delay based on video FPS
                    await asyncio.sleep(frame_delay * 0.2)  # Faster but still visible
                    
                    processed_frames += 1
                    
                    # Log frame broadcasting for debugging
                    logger.info(f"Broadcasting frame {frame_number} with {len(frame_violations)} violations")
                
                frame_number += 1
                
                # Log progress
                if processed_frames % 30 == 0:  # More frequent logging
                    progress = (frame_number / total_frames) * 100
                    logger.info(f"Processing progress: {progress:.1f}% ({processed_frames} frames processed)")
            
            cap.release()
            
            # Add violations to detector's tracker
            for violation in violations:
                detector.add_violation(violation)
            
            logger.info(f"Video processing with display completed. Found {len(violations)} violations")
            
        except Exception as e:
            logger.error(f"Error processing video with display: {str(e)}")
            raise
        
        return [
            {
                "id": v.id,
                "type": v.type,
                "timestamp": v.timestamp.isoformat(),
                "confidence": v.confidence,
                "location": {"x": v.location.x, "y": v.location.y},
                "vehicle_id": v.vehicle_id,
                "frame_number": v.frame_number,
                "details": v.details
            }
            for v in violations
        ]
    
    def _create_display_frame(self, frame: np.ndarray, violations: List, frame_number: int, fps: int) -> np.ndarray:
        """
        Create a display frame with annotations and lane ROIs
        """
        display_frame = frame.copy()
        
        # Add frame info
        cv2.putText(display_frame, f"Frame: {frame_number}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(display_frame, f"Time: {frame_number/fps:.1f}s", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(display_frame, f"Violations: {len(violations)}", (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Draw lane ROIs for better visualization
        # Normal lane (green)
        normal_lane = np.array([[1000, 350], [1800, 350], [1800, 1000], [1000, 1000]], np.int32)
        cv2.polylines(display_frame, [normal_lane], True, (0, 255, 0), 2)
        cv2.putText(display_frame, "Normal Lane", (1000, 340),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Wrong-side lane (red)
        wrong_side_lane = np.array([[200, 350], [1000, 350], [1000, 1000], [200, 1000]], np.int32)
        cv2.polylines(display_frame, [wrong_side_lane], True, (0, 0, 255), 2)
        cv2.putText(display_frame, "Wrong Side Lane", (200, 340),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Stop line (yellow)
        stop_line = [(500, 650), (1300, 650)]
        cv2.line(display_frame, stop_line[0], stop_line[1], (0, 255, 255), 3)
        cv2.putText(display_frame, "Stop Line", (500, 640),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Add violation annotations
        for i, violation in enumerate(violations):
            x, y = int(violation.location.x), int(violation.location.y)
            
            # Color coding for different violation types
            colors = {
                'red_light': (0, 0, 255),      # Red
                'wrong_side': (0, 255, 255),   # Yellow/Cyan
                'no_helmet': (255, 0, 255)     # Magenta
            }
            
            color = colors.get(violation.type, (255, 255, 255))
            
            # Draw violation marker with larger size for better visibility
            cv2.circle(display_frame, (x, y), 25, color, -1)
            cv2.circle(display_frame, (x, y), 30, (255, 255, 255), 3)
            
            # Draw violation text with background
            text = f"{violation.type.upper()}: {violation.confidence:.2f}"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            cv2.rectangle(display_frame, (x - text_size[0]//2 - 5, y - 50), 
                         (x + text_size[0]//2 + 5, y - 20), color, -1)
            cv2.putText(display_frame, text, (x - text_size[0]//2, y - 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        return display_frame
    
    async def _broadcast_frame(self, frame: np.ndarray, frame_number: int, total_violations: int):
        """
        Broadcast frame via WebSocket to connected clients
        """
        try:
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_bytes = buffer.tobytes()
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            
            # Create message
            message = {
                "type": "frame",
                "data": {
                    "frame_number": frame_number,
                    "total_violations": total_violations,
                    "frame_data": frame_base64
                }
            }
            
            # Import here to avoid circular imports
            from main import active_connections
            
            # Send to all active connections
            logger.info(f"Broadcasting frame {frame_number} to {len(active_connections)} connections")
            disconnected_connections = []
            for connection in active_connections:
                try:
                    await connection.send_text(json.dumps(message))
                    logger.debug(f"Frame {frame_number} sent successfully")
                except Exception as e:
                    logger.error(f"Error sending frame {frame_number}: {str(e)}")
                    # Mark for removal
                    disconnected_connections.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected_connections:
                if connection in active_connections:
                    active_connections.remove(connection)
                    logger.info(f"Removed disconnected WebSocket. Remaining connections: {len(active_connections)}")
                    
        except Exception as e:
            logger.error(f"Error broadcasting frame: {str(e)}")
    
    async def _process_frame_batch(self, frames: List[np.ndarray], 
                                  frame_numbers: List[int], 
                                  detector: TrafficViolationDetector) -> List[ViolationEvent]:
        """
        Process a batch of frames efficiently
        """
        violations = []
        
        # Process frames in parallel (simulated with asyncio)
        tasks = []
        for frame, frame_num in zip(frames, frame_numbers):
            task = asyncio.create_task(
                self._process_single_frame(frame, frame_num, detector)
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect violations
        for result in results:
            if isinstance(result, list):
                violations.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Error processing frame: {str(result)}")
        
        return violations
    
    async def _process_single_frame(self, frame: np.ndarray, 
                                   frame_number: int, 
                                   detector: TrafficViolationDetector) -> List[ViolationEvent]:
        """
        Process a single frame
        """
        try:
            # Run violation detection
            violations = detector.process_frame(frame, frame_number)
            return violations
        except Exception as e:
            logger.error(f"Error processing frame {frame_number}: {str(e)}")
            return []
    
    def extract_frames_with_violations(self, video_path: str, 
                                     violations: List[Dict[str, Any]], 
                                     output_dir: str) -> List[str]:
        """
        Extract frames that contain violations for visualization
        """
        if not violations:
            return []
        
        # Get unique frame numbers with violations
        violation_frames = set()
        for violation in violations:
            if violation.get('frame_number'):
                violation_frames.add(violation['frame_number'])
        
        if not violation_frames:
            return []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        extracted_files = []
        frame_number = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_number in violation_frames:
                # Save frame
                filename = f"violation_frame_{frame_number:06d}.jpg"
                filepath = os.path.join(output_dir, filename)
                cv2.imwrite(filepath, frame)
                extracted_files.append(filepath)
            
            frame_number += 1
        
        cap.release()
        return extracted_files
    
    def create_violation_summary_video(self, video_path: str, 
                                     violations: List[Dict[str, Any]], 
                                     output_path: str) -> str:
        """
        Create a summary video highlighting violations
        """
        if not violations:
            return ""
        
        # Open input video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Create violation lookup by frame number
        violations_by_frame = {}
        for violation in violations:
            frame_num = violation.get('frame_number')
            if frame_num is not None:
                if frame_num not in violations_by_frame:
                    violations_by_frame[frame_num] = []
                violations_by_frame[frame_num].append(violation)
        
        frame_number = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Check if this frame has violations
            if frame_number in violations_by_frame:
                # Draw violation annotations
                frame_violations = violations_by_frame[frame_number]
                for violation in frame_violations:
                    self._draw_violation_annotation(frame, violation)
            
            out.write(frame)
            frame_number += 1
        
        cap.release()
        out.release()
        
        return output_path
    
    def _draw_violation_annotation(self, frame: np.ndarray, violation: Dict[str, Any]):
        """
        Draw violation annotation on frame
        """
        violation_type = violation['type']
        location = violation['location']
        confidence = violation['confidence']
        
        # Color coding for different violation types
        colors = {
            'red_light': (0, 0, 255),      # Red
            'wrong_side': (0, 255, 255),   # Yellow
            'no_helmet': (255, 0, 255)     # Magenta
        }
        
        color = colors.get(violation_type, (255, 255, 255))
        
        # Draw violation marker
        center = (int(location['x']), int(location['y']))
        cv2.circle(frame, center, 20, color, -1)
        cv2.circle(frame, center, 25, (255, 255, 255), 2)
        
        # Draw violation text
        text = f"{violation_type.upper()}: {confidence:.2f}"
        cv2.putText(frame, text, (center[0] - 50, center[1] - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
