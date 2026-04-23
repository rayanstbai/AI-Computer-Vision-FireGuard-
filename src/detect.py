# to run, ACTIVATE YOUR VIRTUAL ENVIRONMENT (command: .venv\Scripts\activate ), THEN:
# python src/detect.py
# but first, make sure the phone settings have dev mode on, allowing usb debugging, and the droidcam app to detect and add the usb camera, activate it once then desactivate. then run the above command.

import cv2
import time
from collections import deque
from ultralytics import YOLO

# 1. Load the Champion Model
model = YOLO('models/fireguard_final.pt')

# 2. Temporal Smoothing Configuration
WINDOW_SIZE = 10
CONFIRMATION_THRESHOLD = 6

fire_history = deque([0]*WINDOW_SIZE, maxlen=WINDOW_SIZE)
smoke_history = deque([0]*WINDOW_SIZE, maxlen=WINDOW_SIZE)


# 1. Use the WiFi IP shown on your phone screen (Replace with your actual IP)
cap = cv2.VideoCapture('http://127.0.0.1:4747/video')

# Force OpenCV to hold a maximum of 1 frame in memory to prevent lag
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

'''
if it doesn't fix the latency for the camera live feed moving with a delay of 1-2 seconds, try the following:
Open the DroidCam app on your phone.

Go to Settings (the three dots).

Find the "FPS Limit" or "Camera Framerate" setting.

If it's set to 60, drop it to 30. Your model runs around 21 FPS anyway, so forcing the phone to send 60 FPS just creates unnecessary network heat.
'''

# --- UPGRADE 1: Request HD Resolution ---
# This asks your webcam to output in 720p for a larger, crisper UI.
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

prev_time = 0
print("Booting FireGuard Edge Inference...")

# --- UPGRADE 1b: Make the window resizable ---
cv2.namedWindow("FireGuard Edge UI", cv2.WINDOW_NORMAL)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Failed to grab frame from camera.")
        break

    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time

    # --- UPGRADE 2: Bumped confidence to 0.55 to fight white-wall glare ---
    results = model(frame, stream=True, conf=0.55) 

    fire_in_current_frame = 0
    smoke_in_current_frame = 0
    current_detections = []

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            class_name = model.names[cls]

            current_detections.append((x1, y1, x2, y2, class_name, conf))

            if class_name == 'fire':
                fire_in_current_frame = 1
            elif class_name == 'smoke':
                smoke_in_current_frame = 1

    fire_history.append(fire_in_current_frame)
    smoke_history.append(smoke_in_current_frame)

    fire_confirmed = sum(fire_history) >= CONFIRMATION_THRESHOLD
    smoke_confirmed = sum(smoke_history) >= CONFIRMATION_THRESHOLD

    for (x1, y1, x2, y2, class_name, conf) in current_detections:
        if class_name == 'fire':
            if fire_confirmed:
                color = (0, 0, 255) 
                thickness = 3
                label = f"FIRE ALARM: {conf:.2f}"
            else:
                color = (0, 255, 255) 
                thickness = 1
                label = f"Detecting heat... {conf:.2f}"
        else: 
            if smoke_confirmed:
                color = (0, 165, 255) # Changed to Orange for confirmed smoke visibility
                thickness = 3
                label = f"SMOKE ALARM: {conf:.2f}"
            else:
                color = (200, 200, 200) 
                thickness = 1
                label = f"Detecting haze... {conf:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, thickness)

    cv2.putText(frame, f"FPS: {int(fps)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # --- UPGRADE 3: Dynamic Status Text ---
    if fire_confirmed and smoke_confirmed:
        cv2.putText(frame, "STATUS: FIRE & SMOKE DETECTED", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    elif fire_confirmed:
        cv2.putText(frame, "STATUS: FIRE DETECTED", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    elif smoke_confirmed:
        cv2.putText(frame, "STATUS: SMOKE DETECTED", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
    else:
        cv2.putText(frame, "STATUS: CLEAR", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("FireGuard Edge UI", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()