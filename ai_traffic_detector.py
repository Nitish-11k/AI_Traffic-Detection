import cv2
import numpy as np
from ultralytics import YOLO
import random

VIDEO_FILE = "/home/nickx/PycharmProjects/AITrafficVoilationSystem/Traffic.mp4" # IMPORTANT: Replace with your video file path

model = YOLO('yolov8n.pt')

STOP_LINE = [(500, 650), (1300, 650)]
# A dictionary to keep track of vehicles that have already crossed the stop line
vehicles_crossed = {}
# Simulate traffic light state (we'll cycle it for demonstration)
traffic_light_is_red = False
frame_counter = 0

# 2. Wrong-Side Driving Violation
# Define a region of interest (ROI) for one side of the road
# Format: [ (x1, y1), (x2, y2), (x3, y3), (x4, y4) ]
LANE_ROI = np.array([[1000, 350], [1800, 350], [1800, 1000], [1000, 1000]], np.int32)
# The expected direction of traffic flow in this lane (e.g., downwards and slightly to the left)
# This is a unit vector representing the general direction
EXPECTED_DIRECTION_VECTOR = np.array([-0.2, 1])
# A dictionary to store the trajectory of each vehicle
vehicle_trajectories = {}

def detect_no_helmet(person_roi):
    return random.random() < 0.3

cap = cv2.VideoCapture(VIDEO_FILE)
if not cap.isOpened():
    print(f"Error: Could not open video file {VIDEO_FILE}")
    exit()

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # --- Simulate Traffic Light ---
    frame_counter += 1
    if (frame_counter // (fps * 5)) % 2 == 0: # Light changes every 5 seconds
        traffic_light_is_red = True
        light_color = (0, 0, 255) # Red
        light_text = "RED"
    else:
        traffic_light_is_red = False
        light_color = (0, 255, 0) # Green
        light_text = "GREEN"

    # --- Object Detection and Tracking ---
    # Use the YOLO model to detect and track objects in the frame
    # The `persist=True` flag tells the tracker to remember objects between frames
    results = model.track(frame, persist=True)

    # Get bounding boxes, track IDs, and class names
    try:
        boxes = results[0].boxes.xywh.cpu().numpy()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        class_ids = results[0].boxes.cls.int().cpu().tolist()
        class_names = results[0].names
    except AttributeError:
        # If no objects are tracked in the current frame, skip to the next
        cv2.imshow("Traffic Violation Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue


    # --- Violation Detection Logic ---

    for box, track_id, cls_id in zip(boxes, track_ids, class_ids):
        x_center, y_center, w, h = box
        x1, y1 = int(x_center - w / 2), int(y_center - h / 2)
        x2, y2 = int(x_center + w / 2), int(y_center + h / 2)
        class_name = class_names[cls_id]

        # Common drawing color
        color = (255, 0, 0) # Blue for general tracking

        # --- 1. Red Light Violation Detection ---
        # We only care about 'car', 'motorcycle', 'bus', 'truck'
        if class_name in ['car', 'motorcycle', 'bus', 'truck']:
            # Check if the vehicle's center crosses the stop line
            vehicle_center_y = y_center
            if STOP_LINE[0][1] - 5 < vehicle_center_y < STOP_LINE[0][1] + 5:
                if traffic_light_is_red and track_id not in vehicles_crossed:
                    vehicles_crossed[track_id] = True # Mark as crossed
                    color = (0, 0, 255) # Red for violation
                    cv2.putText(frame, "VIOLATION: Red Light", (x1, y1 - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            # If a vehicle has been marked, keep its color red for a while
            if track_id in vehicles_crossed:
                 color = (0, 0, 255) # Red for violation

        # --- 2. Wrong-Side Driving Detection ---
        if class_name in ['car', 'motorcycle', 'bus', 'truck']:
             # Check if the vehicle center is inside the defined lane ROI
            if cv2.pointPolygonTest(LANE_ROI, (x_center, y_center), False) > 0:
                # Store trajectory
                if track_id not in vehicle_trajectories:
                    vehicle_trajectories[track_id] = []
                vehicle_trajectories[track_id].append((x_center, y_center))

                # Analyze trajectory if we have enough points
                if len(vehicle_trajectories[track_id]) > 5: # Use last 5 points
                    # Get the last 5 points
                    last_points = vehicle_trajectories[track_id][-5:]
                    # Calculate the movement vector
                    dx = last_points[-1][0] - last_points[0][0]
                    dy = last_points[-1][1] - last_points[0][1]
                    movement_vector = np.array([dx, dy])




                    # Normalize the movement vector
                    norm = np.linalg.norm(movement_vector)
                    if norm > 0:
                        movement_vector = movement_vector / norm
                        # Calculate the dot product with the expected direction
                        dot_product = np.dot(movement_vector, EXPECTED_DIRECTION_VECTOR)

                        # If dot product is strongly negative, it's going the wrong way
                        if dot_product < -0.7:
                            color = (0, 255, 255) # Yellow for violation
                            cv2.putText(frame, "VIOLATION: Wrong Side", (x1, y1 - 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # --- 3. No Helmet Detection ---
        if class_name == 'person':
            # This is a simplified logic. A real system would need to associate
            # the person with a motorcycle.
            # We will assume any person detected might be a rider for this example.
            person_roi = frame[y1:y2, x1:x2]
            if person_roi.size > 0:
                if detect_no_helmet(person_roi):
                    color = (255, 0, 255) # Magenta for violation
                    cv2.putText(frame, "VIOLATION: No Helmet", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)


        # --- Draw Bounding Boxes and Labels ---
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"ID:{track_id} {class_name}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


    # --- Draw Visual Aids on the Frame ---
    # 1. Stop Line for Red Light
    cv2.line(frame, STOP_LINE[0], STOP_LINE[1], (0, 255, 255), 3)
    # 2. Traffic Light Status
    cv2.putText(frame, f"Light: {light_text}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, light_color, 3)
    # 3. Lane ROI for Wrong Way
    cv2.polylines(frame, [LANE_ROI], isClosed=True, color=(0, 255, 0), thickness=2)


    # --- Display and Save Frame ---
    cv2.imshow("Traffic Violation Detection", frame)
    # output_video.write(frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup ---
cap.release()
# output_video.release()
cv2.destroyAllWindows()
