"""
Efficient Data Structures for Traffic Violation Detection
Using advanced DSA approaches for optimal performance
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Any
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, deque
import heapq
import math

@dataclass
class Point:
    """2D Point with efficient distance calculations"""
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        """Calculate Euclidean distance to another point"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def to_numpy(self) -> np.ndarray:
        return np.array([self.x, self.y])

@dataclass
class BoundingBox:
    """Efficient bounding box with collision detection"""
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
        """Check if this bounding box intersects with another"""
        return not (self.x2 < other.x1 or other.x2 < self.x1 or 
                   self.y2 < other.y1 or other.y2 < self.y1)
    
    def contains_point(self, point: Point) -> bool:
        """Check if point is inside this bounding box"""
        return (self.x1 <= point.x <= self.x2 and 
                self.y1 <= point.y <= self.y2)

@dataclass
class ViolationEvent:
    """Represents a traffic violation event"""
    id: str
    type: str  # 'red_light', 'wrong_side', 'no_helmet'
    timestamp: datetime
    confidence: float
    location: Point
    vehicle_id: Optional[str] = None
    frame_number: Optional[int] = None
    details: Dict = field(default_factory=dict)

class SpatialIndex:
    """
    Efficient spatial indexing using grid-based approach
    O(1) average case for spatial queries
    """
    
    def __init__(self, cell_size: float = 50.0):
        self.cell_size = cell_size
        self.grid: Dict[Tuple[int, int], Set[str]] = defaultdict(set)
        self.objects: Dict[str, BoundingBox] = {}
    
    def _get_cell_coords(self, point: Point) -> Tuple[int, int]:
        """Get grid cell coordinates for a point"""
        return (int(point.x // self.cell_size), int(point.y // self.cell_size))
    
    def _get_cells_for_bbox(self, bbox: BoundingBox) -> List[Tuple[int, int]]:
        """Get all grid cells that intersect with bounding box"""
        min_cell = self._get_cell_coords(Point(bbox.x1, bbox.y1))
        max_cell = self._get_cell_coords(Point(bbox.x2, bbox.y2))
        
        cells = []
        for x in range(min_cell[0], max_cell[0] + 1):
            for y in range(min_cell[1], max_cell[1] + 1):
                cells.append((x, y))
        return cells
    
    def insert(self, obj_id: str, bbox: BoundingBox):
        """Insert object into spatial index"""
        self.objects[obj_id] = bbox
        for cell in self._get_cells_for_bbox(bbox):
            self.grid[cell].add(obj_id)
    
    def remove(self, obj_id: str):
        """Remove object from spatial index"""
        if obj_id in self.objects:
            bbox = self.objects[obj_id]
            for cell in self._get_cells_for_bbox(bbox):
                self.grid[cell].discard(obj_id)
            del self.objects[obj_id]
    
    def update(self, obj_id: str, bbox: BoundingBox):
        """Update object in spatial index"""
        self.remove(obj_id)
        self.insert(obj_id, bbox)
    
    def query_radius(self, center: Point, radius: float) -> List[str]:
        """Find all objects within radius of center point"""
        # Calculate grid cells to check
        min_x = int((center.x - radius) // self.cell_size)
        max_x = int((center.x + radius) // self.cell_size)
        min_y = int((center.y - radius) // self.cell_size)
        max_y = int((center.y + radius) // self.cell_size)
        
        candidates = set()
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                candidates.update(self.grid.get((x, y), set()))
        
        # Filter by actual distance
        result = []
        for obj_id in candidates:
            if obj_id in self.objects:
                bbox = self.objects[obj_id]
                if center.distance_to(bbox.center) <= radius:
                    result.append(obj_id)
        
        return result

class VehicleTracker:
    """
    Efficient vehicle tracking using Kalman filter and trajectory analysis
    """
    
    def __init__(self, vehicle_id: str, initial_bbox: BoundingBox):
        self.id = vehicle_id
        self.bbox = initial_bbox
        self.trajectory: deque = deque(maxlen=30)  # Keep last 30 positions
        self.trajectory.append(initial_bbox.center)
        self.velocity = Point(0, 0)
        self.last_seen = datetime.now()
        self.violation_count = 0
        self.is_violating = False
        
        # Kalman filter state
        self.kalman_state = np.array([initial_bbox.center.x, initial_bbox.center.y, 0, 0], dtype=np.float32)
        self.kalman_covariance = np.eye(4, dtype=np.float32) * 1000
        
    def update(self, new_bbox: BoundingBox):
        """Update vehicle position and trajectory"""
        self.bbox = new_bbox
        self.trajectory.append(new_bbox.center)
        self.last_seen = datetime.now()
        
        # Update velocity
        if len(self.trajectory) >= 2:
            prev_pos = self.trajectory[-2]
            curr_pos = self.trajectory[-1]
            self.velocity = Point(curr_pos.x - prev_pos.x, curr_pos.y - prev_pos.y)
    
    def get_direction_vector(self) -> np.ndarray:
        """Get normalized direction vector from trajectory"""
        if len(self.trajectory) < 5:
            return np.array([0, 0])
        
        # Use last 5 points for direction calculation
        points = list(self.trajectory)[-5:]
        dx = points[-1].x - points[0].x
        dy = points[-1].y - points[0].y
        
        # Normalize
        magnitude = math.sqrt(dx*dx + dy*dy)
        if magnitude > 0:
            return np.array([dx/magnitude, dy/magnitude])
        return np.array([0, 0])
    
    def is_moving_wrong_direction(self, expected_direction: np.ndarray, threshold: float = -0.7) -> bool:
        """Check if vehicle is moving in wrong direction"""
        direction = self.get_direction_vector()
        if np.linalg.norm(direction) == 0:
            return False
        
        dot_product = np.dot(direction, expected_direction)
        return dot_product < threshold

class ViolationTracker:
    """
    Efficient violation tracking with priority queue for real-time processing
    """
    
    def __init__(self):
        self.violations: Dict[str, ViolationEvent] = {}
        self.priority_queue = []  # Min heap for time-based processing
        self.violation_counts: Dict[str, int] = defaultdict(int)
        self.recent_violations: deque = deque(maxlen=1000)  # Keep last 1000 violations
    
    def add_violation(self, violation: ViolationEvent):
        """Add new violation with priority queue management"""
        self.violations[violation.id] = violation
        self.violation_counts[violation.type] += 1
        self.recent_violations.append(violation)
        
        # Add to priority queue for time-based processing
        heapq.heappush(self.priority_queue, (violation.timestamp, violation.id))
    
    def get_violations_by_type(self, violation_type: str) -> List[ViolationEvent]:
        """Get all violations of specific type"""
        return [v for v in self.violations.values() if v.type == violation_type]
    
    def get_recent_violations(self, minutes: int = 10) -> List[ViolationEvent]:
        """Get violations from last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [v for v in self.recent_violations if v.timestamp >= cutoff_time]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get violation statistics"""
        total = len(self.violations)
        return {
            "total_violations": total,
            "by_type": dict(self.violation_counts),
            "recent_violations": len(self.get_recent_violations()),
            "violation_rate": total / max(1, len(self.recent_violations))
        }

class TrafficLightState:
    """Efficient traffic light state management"""
    
    def __init__(self):
        self.is_red = False
        self.last_change = datetime.now()
        self.change_interval = 5.0  # seconds
    
    def update(self, frame_number: int, fps: int):
        """Update traffic light state based on frame number"""
        current_time = datetime.now()
        if (current_time - self.last_change).total_seconds() >= self.change_interval:
            self.is_red = not self.is_red
            self.last_change = current_time
    
    def should_check_violation(self) -> bool:
        """Check if we should check for red light violations"""
        return self.is_red


