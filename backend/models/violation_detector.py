"""
Fixed Traffic Violation Detector - Black Helmet & Wrong Side Support
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import Dict, List, Optional
import uuid
import math
from datetime import datetime, timedelta
import logging

from models.data_structures import (
    ViolationEvent, VehicleTracker, SpatialIndex,
    BoundingBox, Point, ViolationTracker, TrafficLightState,
    segments_intersect
)

logger = logging.getLogger(__name__)

class TrafficViolationDetector:

    def __init__(self, model_path: str = "yolov8n.pt"):
        self.model = YOLO(model_path)
        # Slightly lower confidence to catch objects further away
        self.model.overrides['conf'] = 0.30
        self.model.overrides['iou'] = 0.5

        self.vehicle_trackers: Dict[str, VehicleTracker] = {}
        self.spatial_index = SpatialIndex(cell_size=50.0)
        self.violation_tracker = ViolationTracker()
        self.traffic_light = TrafficLightState()

        # --- ROI CONFIGURATION ---
        self.stop_line = [(0, 800), (1920, 800)]

        # Full screen coverage
        self.lane_roi = np.array([[0, 0], [1920, 0], [1920, 1080], [0, 1080]], np.int32)
        # Wrong side often happens on the edges of the road, keep it full screen for dashcam
        self.wrong_side_roi = np.array([[0, 0], [1920, 0], [1920, 1080], [0, 1080]], np.int32)

        # Expected direction:
        # Standard traffic moves "Down and Out" (Positive Y).
        # Wrong side traffic moves "Up" or "Towards Camera" (Negative Y relative to flow).
        # We assume normal flow is (0, 1) [Down]
        self.expected_direction = np.array([0, 1])

        self.vehicle_classes = ['car', 'motorcycle', 'bus', 'truck']
        self.person_class = 'person'

        logger.info("Traffic Violation Detector initialized")

    def process_frame(self, frame: np.ndarray, frame_number: int, fps: int = 30) -> List[ViolationEvent]:
        violations = []
        self.traffic_light.update(frame_number, fps)

        results = self.model.track(frame, persist=True, verbose=False, conf=0.35, iou=0.5, max_det=50)

        if not results or not results[0].boxes:
            return violations

        boxes = results[0].boxes.xywh.cpu().numpy()

        if results[0].boxes.id is not None:
            track_ids = results[0].boxes.id.int().cpu().tolist()
        else:
            track_ids = list(range(len(boxes)))

        class_ids = results[0].boxes.cls.int().cpu().tolist()
        class_names = results[0].names

        for box, track_id, cls_id in zip(boxes, track_ids, class_ids):
            x_center, y_center, w, h = box
            bbox = BoundingBox(
                x_center - w/2, y_center - h/2,
                x_center + w/2, y_center + h/2
            )
            class_name = class_names[cls_id]
            self.spatial_index.update(str(track_id), bbox)

            if class_name == 'motorcycle':
                # 1. Standard Checks
                violations.extend(self._process_vehicle(
                    track_id, bbox, class_name, frame, frame_number, fps
                ))
                # 2. HELMET CHECK on the motorcycle object itself
                violations.extend(self._process_motorcycle_rider(
                    track_id, bbox, frame, frame_number, fps
                ))

            elif class_name in self.vehicle_classes:
                violations.extend(self._process_vehicle(
                    track_id, bbox, class_name, frame, frame_number, fps
                ))

            elif class_name == self.person_class:
                violations.extend(self._process_person(
                    track_id, bbox, frame, frame_number, fps
                ))

        self._cleanup_old_trackers()
        return violations

    def _get_video_time(self, frame_number, fps):
        seconds = int(frame_number / fps)
        return str(timedelta(seconds=seconds))

    def _process_vehicle(self, track_id: int, bbox: BoundingBox,
                        class_name: str, frame: np.ndarray,
                        frame_number: int, fps: int) -> List[ViolationEvent]:
        violations = []
        if track_id not in self.vehicle_trackers:
            self.vehicle_trackers[track_id] = VehicleTracker(str(track_id), bbox)
        else:
            self.vehicle_trackers[track_id].update(bbox)

        tracker = self.vehicle_trackers[track_id]

        red_light = self._check_red_light_violation(tracker, frame_number, fps)
        if red_light: violations.append(red_light)

        # --- RE-ENABLED WRONG SIDE ---
        wrong_side = self._check_wrong_side_violation(tracker, frame_number, fps)
        if wrong_side: violations.append(wrong_side)

        return violations

    def _process_motorcycle_rider(self, track_id: int, bbox: BoundingBox,
                                 frame: np.ndarray, frame_number: int, fps: int) -> List[ViolationEvent]:
        violations = []

        # Top 35% is the rider's head/upper body
        bike_height = bbox.y2 - bbox.y1
        head_y2 = bbox.y1 + (bike_height * 0.35)

        h, w, _ = frame.shape
        x1, y1 = max(0, int(bbox.x1)), max(0, int(bbox.y1))
        x2, y2 = min(w, int(bbox.x2)), min(h, int(head_y2))

        head_roi = frame[y1:y2, x1:x2]

        if head_roi.size == 0: return []

        # Check for helmet using IMPROVED logic
        has_helmet = self._detect_helmet_heuristic(head_roi)

        tracker = self.vehicle_trackers.get(track_id)
        if tracker and tracker.has_violation('no_helmet'):
            return []

        if not has_helmet:
            if tracker: tracker.add_violation('no_helmet')

            video_time = self._get_video_time(frame_number, fps)
            violation = ViolationEvent(
                id=str(uuid.uuid4()),
                type="no_helmet",
                timestamp=datetime.now(),
                confidence=0.80,
                location=bbox.center,
                vehicle_id=str(track_id),
                frame_number=frame_number,
                details={
                    "video_time": video_time,
                    "detection_source": "motorcycle_bbox"
                }
            )
            violations.append(violation)

        return violations

    def _process_person(self, track_id: int, bbox: BoundingBox,
                       frame: np.ndarray, frame_number: int, fps: int) -> List[ViolationEvent]:
        violations = []
        is_rider = False
        motorcycle_id = None
        nearby_objs = self.spatial_index.query_radius(bbox.center, 150)

        for obj_id in nearby_objs:
            if obj_id in self.vehicle_trackers:
                vehicle = self.vehicle_trackers[obj_id]
                if bbox.intersects(vehicle.bbox):
                    is_rider = True
                    motorcycle_id = obj_id
                    break

        if not is_rider: return []

        person_h = bbox.y2 - bbox.y1
        head_y2 = bbox.y1 + (person_h * 0.25)
        h, w, _ = frame.shape
        x1, y1 = max(0, int(bbox.x1)), max(0, int(bbox.y1))
        x2, y2 = min(w, int(bbox.x2)), min(h, int(head_y2))

        head_roi = frame[y1:y2, x1:x2]
        if head_roi.size == 0: return []

        if not self._detect_helmet_heuristic(head_roi):
            video_time = self._get_video_time(frame_number, fps)
            violation = ViolationEvent(
                id=str(uuid.uuid4()),
                type="no_helmet",
                timestamp=datetime.now(),
                confidence=0.75,
                location=bbox.center,
                vehicle_id=str(motorcycle_id) if motorcycle_id else str(track_id),
                frame_number=frame_number,
                details={
                    "video_time": video_time,
                    "detection_source": "person_bbox"
                }
            )
            violations.append(violation)
        return violations

    def _detect_helmet_heuristic(self, head_roi: np.ndarray) -> bool:
        """
        Improved Heuristic to detect Black/Dark Helmets.
        """
        try:
            # 1. Convert to HSV
            hsv = cv2.cvtColor(head_roi, cv2.COLOR_BGR2HSV)
            sat = hsv[:,:,1]
            val = hsv[:,:,2]

            sat_mean = np.mean(sat)
            val_mean = np.mean(val)

            # 2. Standard Color Checks (White/Yellow/Red helmets)
            if sat_mean > 50 or val_mean > 170:
                return True

            # 3. BLACK HELMET CHECK (The Fix)
            # Black helmets are dark (Val < 100) and low saturation (Sat < 50)
            # BUT they are SHINY (Plastic/Glass). Hair is MATTE.
            # We check the Standard Deviation (Contrast) of the brightness.
            # Shiny objects have high variance (bright reflection spots vs dark spots).

            val_std = np.std(val)

            # If it's dark-ish but has high contrast/reflection -> Helmet
            if 15 < val_mean < 150 and val_std > 15:
                # Likely a black helmet with a reflection
                return True

            return False # Likely hair (Dark, uniform, low contrast)
        except:
            return True # Fail safe

    def _check_red_light_violation(self, tracker: VehicleTracker,
                                frame_number: int, fps: int) -> Optional[ViolationEvent]:
        if not self.traffic_light.is_red: return None
        if tracker.has_violation('red_light'): return None
        if len(tracker.trajectory) < 2: return None

        line_start = Point(self.stop_line[0][0], self.stop_line[0][1])
        line_end = Point(self.stop_line[1][0], self.stop_line[1][1])
        curr_pos = tracker.trajectory[-1]
        prev_pos = tracker.trajectory[-2]

        if segments_intersect(prev_pos, curr_pos, line_start, line_end):
            speed = math.sqrt(tracker.velocity.x**2 + tracker.velocity.y**2)
            if speed > 2.0:
                tracker.add_violation('red_light')
                video_time = self._get_video_time(frame_number, fps)
                return ViolationEvent(
                    id=str(uuid.uuid4()),
                    type="red_light",
                    timestamp=datetime.now(),
                    confidence=0.95,
                    location=tracker.bbox.center,
                    vehicle_id=tracker.id,
                    frame_number=frame_number,
                    details={
                        "video_time": video_time,
                        "stop_line": self.stop_line,
                        "light_status": "RED"
                    }
                )
        return None

    def _check_wrong_side_violation(self, tracker: VehicleTracker, frame_number: int, fps: int) -> Optional[ViolationEvent]:
        """
        Dashcam Wrong Side Logic:
        Strictly looks for objects coming TOWARDS the camera (Expansion).
        """
        if tracker.has_violation('wrong_side'): return None
        if len(tracker.trajectory) < 5: return None

        # Calculate movement vector
        start_pt = tracker.trajectory[-5]
        end_pt = tracker.trajectory[-1]
        movement = np.array([end_pt.x - start_pt.x, end_pt.y - start_pt.y])
        norm = np.linalg.norm(movement)

        # Threshold: Object must be moving significantly
        if norm < 5.0: return None

        # Calculate Dot Product with Expected Direction (0, 1) [Down]
        # Normal traffic moves Down/Away from dashcam (Positive dot product)
        # Oncoming traffic moves Up/Towards dashcam (Negative dot product)

        normalized_movement = movement / norm
        dot_prod = np.dot(normalized_movement, self.expected_direction)

        # stricter threshold for Dashcam (-0.6) to avoid jitter
        if dot_prod < -0.6:
            tracker.add_violation('wrong_side')
            video_time = self._get_video_time(frame_number, fps)
            return ViolationEvent(
                id=str(uuid.uuid4()),
                type="wrong_side",
                timestamp=datetime.now(),
                confidence=0.85,
                location=tracker.bbox.center,
                vehicle_id=tracker.id,
                details={
                    "video_time": video_time,
                    "dot_product": dot_prod
                }
            )
        return None

    def _cleanup_old_trackers(self):
        current_time = datetime.now()
        for track_id, tracker in list(self.vehicle_trackers.items()):
            if (current_time - tracker.last_seen).total_seconds() > 5.0:
                del self.vehicle_trackers[track_id]
                self.spatial_index.remove(track_id)

    def get_all_violations(self) -> List[Dict]:
        return [
            {
                "id": v.id,
                "type": v.type,
                "timestamp": v.timestamp.isoformat(),
                "confidence": float(v.confidence),
                "location": {"x": float(v.location.x), "y": float(v.location.y)},
                "vehicle_id": v.vehicle_id,
                "frame_number": int(v.frame_number) if v.frame_number else 0,
                "details": v.details
            }
            for v in self.violation_tracker.violations.values()
        ]

    def add_violation(self, violation: ViolationEvent):
        self.violation_tracker.add_violation(violation)