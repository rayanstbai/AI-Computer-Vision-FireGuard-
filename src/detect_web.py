import cv2
from ultralytics import YOLO
from collections import deque
import datetime


global_logs = []

def add_log(message, level="info"):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_entry = {"time": timestamp, "message": message, "level": level}
    global_logs.insert(0, log_entry)
    if len(global_logs) > 50:
        global_logs.pop()

def generate_frames():
    model = YOLO("models/fireguard_final.pt")
    
    # Connect to the camera (Update this if using webcam 0, http://127.0.0.1:4747/video for droidcam)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    history = deque(maxlen=10)
    
    add_log("System Booted. Camera Connected.", "info")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        results = model(frame, verbose=False)
        detections = []

        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                
                if conf > 0.5: 
                    label = model.names[cls]
                    detections.append(label)
                    
                    
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Temporal Logic Simulation
        if len(detections) > 0:
            history.append(1)
            add_log(f"Anomaly detected: {detections[0]}", "warning")
        else:
            history.append(0)

        # Trigger ALARM if 6 out of the last 10 frames have detections
        if sum(history) >= 6:
            add_log("🚨 ALARM: Confirmed Threat Detected!", "danger")
            # Draw a massive warning border on the frame
            cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), 10)

        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Yield the frame to the Flask server
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')