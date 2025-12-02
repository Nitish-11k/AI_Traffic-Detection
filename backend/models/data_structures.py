"""
Efficient Data Structures for Traffic Violation Detection
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Any
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, deque
import heapq
import math

# ... (Point, BoundingBox classes same as before) ...
# ... (segments_intersect function same as before) ...

@dataclass
class Point:
    x: float
    y: float

    def distance_to(self, other: 'Point') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def to_numpy(self) -> np.ndarray:
        return np.array([self.x, self.y])

# --- ADD segments_intersect HERE IF NOT PRESENT ---
def segments_intersect(p1: Point, p2: Point, q1: Point, q2: Point) -> bool:
    def ccw(a, b, c):
        return (c.y - a.y) * (b.x - a.x) > (b.y - a.y) * (c.x - a.x)
    return (ccw(p1, q1, q2) != ccw(p2, q1, q2)) and (ccw(p1, p2, q1) != ccw(p1, p2, q2))

@dataclass
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def center(self) -> Point:
        return Point((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    @property
    def area(self) -> float:
        return (self.x2 - self.x1) * (self.y2 - self.y1)

    def intersects(self, other: 'BoundingBox') -> bool:
        return not (self.x2 < other.x1 or other.x2 < self.x1 or
                    self.y2 < other.y1 or other.y2 < self.y1)

    def contains_point(self, point: Point) -> bool:
        return (self.x1 <= point.x <= self.x2 and
                self.y1 <= point.y <= self.y2)

@dataclass
class ViolationEvent:
    id: str
    type: str
    timestamp: datetime
    confidence: float
    location: Point
    vehicle_id: Optional[str] = None
    frame_number: Optional[int] = None
    details: Dict = field(default_factory=dict)

# ... (SpatialIndex, VehicleTracker, ViolationTracker classes same as before) ...

class SpatialIndex:
    def __init__(self, cell_size: float = 50.0):
        self.cell_size = cell_size
        self.grid = defaultdict(set)
        self.objects = {}

    def _get_cell_coords(self, point: Point):
        return (int(point.x // self.cell_size), int(point.y // self.cell_size))

    def _get_cells_for_bbox(self, bbox: BoundingBox):
        min_cell = self._get_cell_coords(Point(bbox.x1, bbox.y1))
        max_cell = self._get_cell_coords(Point(bbox.x2, bbox.y2))
        cells = []
        for x in range(min_cell[0], max_cell[0] + 1):
            for y in range(min_cell[1], max_cell[1] + 1):
                cells.append((x, y))
        return cells

    def update(self, obj_id: str, bbox: BoundingBox):
        if obj_id in self.objects:
            old_bbox = self.objects[obj_id]
            for cell in self._get_cells_for_bbox(old_bbox):
                self.grid[cell].discard(obj_id)
        self.objects[obj_id] = bbox
        for cell in self._get_cells_for_bbox(bbox):
            self.grid[cell].add(obj_id)

    def remove(self, obj_id: str):
        if obj_id in self.objects:
            bbox = self.objects[obj_id]
            for cell in self._get_cells_for_bbox(bbox):
                self.grid[cell].discard(obj_id)
            del self.objects[obj_id]

    def query_radius(self, center: Point, radius: float) -> List[str]:
        min_x = int((center.x - radius) // self.cell_size)
        max_x = int((center.x + radius) // self.cell_size)
        min_y = int((center.y - radius) // self.cell_size)
        max_y = int((center.y + radius) // self.cell_size)
        candidates = set()
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                candidates.update(self.grid.get((x, y), set()))
        result = []
        for obj_id in candidates:
            if obj_id in self.objects:
                bbox = self.objects[obj_id]
                if center.distance_to(bbox.center) <= radius:
                    result.append(obj_id)
        return result

class VehicleTracker:
    def __init__(self, vehicle_id: str, initial_bbox: BoundingBox):
        self.id = vehicle_id
        self.bbox = initial_bbox
        self.trajectory = deque(maxlen=30)
        self.trajectory.append(initial_bbox.center)
        self.velocity = Point(0, 0)
        self.last_seen = datetime.now()
        self.recorded_violations = set()
        self.violation_count = 0

    def update(self, new_bbox: BoundingBox):
        self.bbox = new_bbox
        self.trajectory.append(new_bbox.center)
        self.last_seen = datetime.now()
        if len(self.trajectory) >= 2:
            prev = self.trajectory[-2]
            curr = self.trajectory[-1]
            self.velocity = Point(curr.x - prev.x, curr.y - prev.y)

    def has_violation(self, v_type): return v_type in self.recorded_violations
    def add_violation(self, v_type): self.recorded_violations.add(v_type)

class ViolationTracker:
    def __init__(self):
        self.violations = {}
        self.priority_queue = []
        self.violation_counts = defaultdict(int)

    def add_violation(self, violation: ViolationEvent):
        self.violations[violation.id] = violation
        self.violation_counts[violation.type] += 1
        heapq.heappush(self.priority_queue, (violation.timestamp, violation.id))

    def get_statistics(self):
        return {"total_violations": len(self.violations), "by_type": dict(self.violation_counts)}

# --- UPDATED TRAFFIC LIGHT LOGIC ---
class TrafficLightState:
    """Efficient traffic light state management using Frames"""

    def __init__(self):
        self.is_red = False
        self.change_interval_seconds = 5.0  # Light changes every 5 seconds
        self.fps = 30 # Default FPS assumption

    def update(self, frame_number: int, fps: int):
        """
        Update based on FRAMES, not TIME.
        This ensures it works correctly for uploaded videos processed at high speed.
        """
        self.fps = fps
        frames_per_cycle = self.fps * self.change_interval_seconds

        # Simple cycle: 0-150 frames (Green), 150-300 frames (Red), etc.
        cycle_position = frame_number % (frames_per_cycle * 2)

        if cycle_position > frames_per_cycle:
            self.is_red = True
        else:
            self.is_red = False

    def should_check_violation(self) -> bool:
        return self.is_red