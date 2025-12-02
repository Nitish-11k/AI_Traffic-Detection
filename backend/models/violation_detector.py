"""
NORMAL TRAFFIC DETECTOR (Pure Maths Logic)
No Custom Model Required.
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import Dict, List
import uuid
from datetime import datetime, timedelta
import logging
from models.data_structures import ViolationEvent, VehicleTracker, SpatialIndex, BoundingBox, TrafficLightState

logger = logging.getLogger(__name__)

class TrafficViolationDetector:
    def __init__(self):
        self.base_model = YOLO("yolov8n.pt")
        self.vehicle_trackers = {}
        self.violation_tracker = None 
        self.traffic_light = TrafficLightState()
        self.spatial_index = SpatialIndex()
        
        # --- CONFIGURATION ---
        self.stop_line = [(0, 800), (1920, 800)]
        # Wrong Side: Check Right Half (Pixel 800 to 1920)
        self.wrong_side_roi = np.array([[800, 0], [1920, 0], [1920, 1080], [800, 1080]], np.int32)
        # Traffic Flow: Up/Away (0, -1)
        self.expected_direction = np.array([0, -1]) 
        
        self.vehicle_classes = ['car', 'motorcycle', 'bus', 'truck', 'auto']

    def process_frame(self, frame, fnum, fps=30):
        violations = []
        self.traffic_light.update(fnum, fps)
        
        # Detect
        results = self.base_model.track(frame, persist=True, verbose=False, conf=0.40, iou=0.5)
        
        if not results or not results[0].boxes: return []
        
        for box, tid, cls in zip(results[0].boxes.xywh.cpu(), 
                               results[0].boxes.id.int().cpu().tolist() if results[0].boxes.id is not None else [],
                               results[0].boxes.cls.int().cpu().tolist()):
            
            x, y, w, h = box
            bbox = BoundingBox(float(x-w/2), float(y-h/2), float(x+w/2), float(y+h/2))
            name = results[0].names[cls]
            sid = str(tid)

            if w < 40 or h < 40: continue # Ignore noise

            if sid not in self.vehicle_trackers: self.vehicle_trackers[sid] = VehicleTracker(sid, bbox)
            else: self.vehicle_trackers[sid].update(bbox)
            tracker = self.vehicle_trackers[sid]

            # 1. HELMET (Maths Logic)
            if name == 'motorcycle' and not tracker.has_violation('no_helmet'):
                if self._check_no_helmet_maths(tracker, frame):
                    tracker.add_violation('no_helmet')
                    violations.append(self._evt('no_helmet', tracker, fnum, fps, "Visual Detection"))

            # 2. WRONG SIDE (Maths Logic)
            if name in self.vehicle_classes and not tracker.has_violation('wrong_side'):
                if self._check_wrong_side_vector(tracker):
                    tracker.add_violation('wrong_side')
                    violations.append(self._evt('wrong_side', tracker, fnum, fps, "Wrong Direction"))
        
        self._clean()
        return violations

    def _check_no_helmet_maths(self, tracker, frame):
        # Crop Top 35% (Head Area)
        x1, y1, x2, y2 = map(int, [tracker.bbox.x1, tracker.bbox.y1, tracker.bbox.x2, tracker.bbox.y2])
        h = y2 - y1
        head_roi = frame[y1:y1+int(h*0.35), x1:x2]
        if head_roi.size == 0: return False
        
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(head_roi, cv2.COLOR_BGR2HSV)
            sat = np.mean(hsv[:,:,1])
            val = np.mean(hsv[:,:,2])
            val_std = np.std(hsv[:,:,2])
            
            # --- SAFE CONDITIONS (HELMET HAI) ---
            # 1. Colorful (Red/Yellow/Blue)
            if sat > 50: return False
            # 2. Bright White/Silver
            if val > 165: return False
            # 3. Shiny Black (Dark + High Reflection/Variance)
            if 20 < val < 140 and val_std > 18: return False
            
            # Agar upar wala kuch nahi mila, toh ye Baal/Skin hai = NO HELMET
            return True
        except: return False

    def _check_wrong_side_vector(self, tracker):
        if tracker.bbox.center.x < 900: return False # Ignore Left/Center Lane
        if len(tracker.trajectory) < 6: return False
        
        # Calculate Vector
        start = tracker.trajectory[-6]
        end = tracker.trajectory[-1]
        dx, dy = end.x - start.x, end.y - start.y
        
        # Speed check
        speed = (dx**2 + dy**2)**0.5
        if speed < 4.0: return False # Too slow
        
        # Dot Product
        vec = np.array([dx, dy]) / speed
        dot = np.dot(vec, self.expected_direction)
        
        # If moving Opposite (< -0.5)
        return dot < -0.5

    def _evt(self, type, t, f, fps, reason):
        return ViolationEvent(
            str(uuid.uuid4()), type, datetime.now(), 0.85, t.bbox.center, t.id, f, 
            {"time": str(timedelta(seconds=int(f/fps))), "reason": reason}
        )

    def _clean(self):
        now = datetime.now()
        for k, v in list(self.vehicle_trackers.items()):
            if (now - v.last_seen).total_seconds() > 3: del self.vehicle_trackers[k]
            
    def get_all_violations(self): return []
    def add_violation(self, v): pass