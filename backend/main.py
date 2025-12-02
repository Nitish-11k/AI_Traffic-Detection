import os
import cv2
import shutil
import tempfile
import base64  # <--- Added for Image Proof
import asyncio
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from supabase import create_client, Client
from datetime import datetime
from typing import List
from dotenv import load_dotenv

from models.violation_detector import TrafficViolationDetector

# --- 1. CONFIGURATION ---
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    SUPABASE_URL = "https://your-project.supabase.co"
    SUPABASE_KEY = "your-anon-key"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase!")
except Exception as e:
    print(f"❌ Supabase Connection Failed: {e}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = TrafficViolationDetector()


# --- 2. HELPERS (UPDATED FOR IMAGE PROOF) ---
def push_to_supabase(violation, frame):
    """
    Violation data + Image Proof save karta hai
    """
    try:
        # 1. Convert Frame to Base64 String
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        image_data = f"data:image/jpeg;base64,{jpg_as_text}"

        # 2. Prepare Data
        data = {
            "type": violation.type,
            "vehicle_id": violation.vehicle_id,
            "confidence": float(violation.confidence),
            "created_at": datetime.now().isoformat(),
            "violation_image": image_data  # <--- Saving Proof
        }

        # 3. Insert into DB
        supabase.table("violations").insert(data).execute()
        print(f"🚀 Saved with PROOF: {violation.type}")
    except Exception as e:
        print(f"❌ DB Error: {e}")


# --- 3. ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "Online", "message": "AI Traffic System Ready"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# --- A. LIVE VIDEO STREAMING ---
def generate_frames():
    video_path = "Traffic.mp4"
    if not os.path.exists(video_path):
        video_path = 0

    cap = cv2.VideoCapture(video_path)
    frame_num = 0

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame_num += 1

        if frame_num % 3 == 0:
            violations = detector.process_frame(frame, frame_num)
            for v in violations:
                # Draw box BEFORE saving so proof has the box
                x, y = int(v.location.x), int(v.location.y)
                # Clone frame for clean upload or draw on it
                proof_frame = frame.copy()
                cv2.rectangle(proof_frame, (x - 50, y - 50), (x + 50, y + 50), (0, 0, 255), 2)
                cv2.putText(proof_frame, v.type, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

                # Pass frame to save function
                push_to_supabase(v, proof_frame)

                # Draw on display frame as well
                cv2.rectangle(frame, (x - 50, y - 50), (x + 50, y + 50), (0, 0, 255), 2)
                cv2.putText(frame, v.type, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


# --- B. VIDEO UPLOAD LOGIC ---
@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    print(f"📥 Received file: {file.filename}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        shutil.copyfileobj(file.file, tmp)
        temp_path = tmp.name

    cap = cv2.VideoCapture(temp_path)
    frame_count = 0
    all_violations = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 10 == 0:
            violations = detector.process_frame(frame, frame_count)
            for v in violations:
                # Draw details on proof
                x, y = int(v.location.x), int(v.location.y)
                cv2.rectangle(frame, (x - 50, y - 50), (x + 50, y + 50), (0, 0, 255), 2)

                # Save with Proof
                push_to_supabase(v, frame)

                all_violations.append({
                    "id": v.id,
                    "type": v.type,
                    "timestamp": v.timestamp.isoformat(),
                    "confidence": v.confidence,
                    "vehicle_id": v.vehicle_id,
                    "frame_number": v.frame_number,
                    "location": {"x": v.location.x, "y": v.location.y}
                })

    cap.release()
    os.unlink(temp_path)

    return {
        "status": "success",
        "filename": file.filename,
        "violations": all_violations,
        "total_violations": len(all_violations)
    }


# --- C. REPORTS DATA ---
@app.get("/violations")
def get_violations_history():
    default_response = {
        "violations": [],
        "statistics": {"total_violations": 0, "by_type": {}, "recent_violations": 0, "violation_rate": 0.0}
    }

    try:
        # Fetch data WITH image column
        response = supabase.table("violations").select("*").order("created_at", desc=True).limit(50).execute()
        data = response.data

        if not data:
            return default_response

        stats = {
            "total_violations": len(data),
            "by_type": {
                "red_light": len([v for v in data if v.get('type') == 'red_light']),
                "wrong_side": len([v for v in data if v.get('type') == 'wrong_side']),
                "no_helmet": len([v for v in data if v.get('type') == 'no_helmet'])
            },
            "recent_violations": len(data),
            "violation_rate": 0.0
        }

        formatted_violations = []
        for v in data:
            formatted_violations.append({
                "id": v.get('id'),
                "type": v.get('type'),
                "timestamp": v.get('created_at'),
                "confidence": v.get('confidence', 0.0),
                "vehicle_id": v.get('vehicle_id', 'Unknown'),
                "violation_image": v.get('violation_image', ''),  # <--- Sending Image to Frontend
                "location": {"x": 0, "y": 0}
            })

        return {
            "violations": formatted_violations,
            "statistics": stats
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        return default_response


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True: await websocket.receive_text()
    except:
        pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)