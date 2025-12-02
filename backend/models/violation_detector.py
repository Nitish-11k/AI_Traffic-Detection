"""
FINAL ROBUST DETECTOR (FIXED FOR TRAFFIC JAMS & MISSING FILES)
1. Strict Model Check: Will warn if custom model is missing.
2. Low Speed Detection: Detects wrong side even in traffic jams.
3. Smart Helmet Association: Captures passengers even if slightly misaligned.
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import Dict, List
import uuid
from datetime import datetime, timedelta
import logging
import math
from models.data_structures import ViolationEvent, VehicleTracker, BoundingBox, TrafficLightState

logger = logging.getLogger(__name__)

class TrafficViolationDetector:
    def __init__(self):
        # 1. LOAD YOUR CUSTOM MODEL (Must exist!)
        try:
            # Ye file backend folder mein honi chahiye!
            self.model = YOLO("helmet_model.pt") 
            logger.info("✅ SUCCESS: Custom Helmet Model Loaded!")
        except Exception as e:
            logger.critical("❌ CRITICAL ERROR: 'helmet_model.pt' not found!")
            logger.critical("👉 Download 'best.pt' from Colab, rename to 'helmet_model.pt' and put in backend folder.")
            # Fallback (sirf testing ke liye, real detection nahi karega)
            self.model = YOLO("yolov8n.pt")

        self.vehicle_trackers = {}
        self.traffic_light = TrafficLightState()
        
        # --- CLASS ID CONFIGURATION (CHECK YOUR DATA.YAML IN COLAB) ---
        # Roboflow usually exports like this. Verify these numbers!
        self.class_map = {
            'helmet': 0,      # Agar 'Head' ya 'Helmet' class 0 hai
            'no_helmet': 1,   # Agar 'No-Helmet' class 1 hai
            'rider': 2,       # Agar 'Motorcyclist' class 2 hai
            'vehicle': 3      # Cars/Trucks
        }
        
        # --- WRONG SIDE CONFIGURATION ---
        # Traffic Jam video ke hisab se coordinates
        self.wrong_side_poly = np.array([[960, 0], [1920, 0], [1920, 1080], [960, 1080]], np.int32)
        
        # Flow: Traffic should go UP (Away from camera) -> Vector (0, -1)
        self.expected_flow_vector = np.array([0, -1]) 

    def process_frame(self, frame, fnum, fps=30):
        violations = []
        
        # Confidence thoda kam kiya taaki door wale bhi detect hon
        results = self.model.track(frame, persist=True, verbose=False, conf=0.20, iou=0.5)
        
        if not results or not results[0].boxes: return []

        # Data Parsing
        boxes = results[0].boxes.xyxy.cpu().numpy()
        cls_ids = results[0].boxes.cls.int().cpu().tolist()
        track_ids = results[0].boxes.id.int().cpu().tolist() if results[0].boxes.id is not None else [-1] * len(boxes)

        current_riders = []
        current_helmets = []

        for box, cls_id, track_id in zip(boxes, cls_ids, track_ids):
            if track_id == -1: continue

            bbox = BoundingBox(float(box[0]), float(box[1]), float(box[2]), float(box[3]))
            sid = str(track_id)

            if sid not in self.vehicle_trackers:
                self.vehicle_trackers[sid] = VehicleTracker(sid, bbox)
            else:
                self.vehicle_trackers[sid].update(bbox)
            
            tracker = self.vehicle_trackers[sid]

            # --- LOGIC 1: WRONG SIDE (Updated for Slow Traffic) ---
            if self._check_wrong_side_robust(tracker):
                if not tracker.has_violation('wrong_side'):
                    tracker.add_violation('wrong_side')
                    violations.append(self._create_event('wrong_side', tracker, fnum, fps, "Wrong Way Driving"))

            # --- DATA FOR HELMET ---
            # Map classes correctly
            if cls_id == self.class_map['rider']:
                current_riders.append(tracker)
            elif cls_id == self.class_map['helmet']:
                current_helmets.append(bbox)
            
            # Method A: Direct Model Detection
            if cls_id == self.class_map['no_helmet']:
                if not tracker.has_violation('no_helmet'):
                    tracker.add_violation('no_helmet')
                    violations.append(self._create_event('no_helmet', tracker, fnum, fps, "No Helmet (Model Detected)"))

        # --- LOGIC 2: HELMET GEOMETRY (Method B) ---
        for rider in current_riders:
            if rider.has_violation('no_helmet'): continue

            rider_h = rider.bbox.y2 - rider.bbox.y1
            
            # Expanded Head Region (Look UP 15%, Look DOWN 35%)
            head_roi = BoundingBox(
                rider.bbox.x1, 
                rider.bbox.y1 - (rider_h * 0.15), 
                rider.bbox.x2, 
                rider.bbox.y1 + (rider_h * 0.35)
            )

            has_helmet = False
            for helmet_box in current_helmets:
                # Check Overlap (IoU)
                if self._check_overlap(head_roi, helmet_box):
                    has_helmet = True
                    break
            
            if not has_helmet:
                rider.add_violation('no_helmet')
                violations.append(self._create_event('no_helmet', rider, fnum, fps, "No Helmet (Geometry Check)"))

        self._clean_trackers()
        return violations

    def _check_wrong_side_robust(self, tracker):
        # 1. Zone Check
        center = (int(tracker.bbox.center.x), int(tracker.bbox.center.y))
        if cv2.pointPolygonTest(self.wrong_side_poly, center, False) < 0: return False

        # 2. History Check
        if len(tracker.trajectory) < 10: return False

        # 3. Vector Calculation
        start = tracker.trajectory[-10]
        end = tracker.trajectory[-1]
        dx = end.x - start.x
        dy = end.y - start.y
        
        # Speed calculation
        dist = math.sqrt(dx**2 + dy**2)
        
        # --- FIX: Traffic Jam Handling ---
        # Agar speed bilkul 0 hai (dist < 1.0), toh ignore karo (ruki hui gadi)
        # Par agar thodi bhi movement hai (dist > 1.0), toh direction check karo
        if dist < 1.0: return False 

        # 4. Dot Product         vec = np.array([dx, dy]) / dist
        dot = np.dot(vec, self.expected_flow_vector)

        # Negative dot product means opposite direction
        return dot < -0.4

    def _check_overlap(self, boxA, boxB):
        # Simple overlap check
        xA = max(boxA.x1, boxB.x1)
        yA = max(boxA.y1, boxB.y1)
        xB = min(boxA.x2, boxB.x2)
        yB = min(boxA.y2, boxB.y2)
        
        interArea = max(0, xB - xA) * max(0, yB - yA)
        
        # If any significant overlap exists
        return interArea > 50  # 50 pixels overlap minimum

    def _create_event(self, v_type, tracker, fnum, fps, reason):
        return ViolationEvent(
            str(uuid.uuid4()), v_type, datetime.now(), 0.95, 
            tracker.bbox.center, tracker.id, fnum, {"reason": reason}
        )

    def _clean_trackers(self):
        now = datetime.now()
        for k, v in list(self.vehicle_trackers.items()):
            if (now - v.last_seen).total_seconds() > 3:
                del self.vehicle_trackers[k]
    
    def add_violation(self, v): pass