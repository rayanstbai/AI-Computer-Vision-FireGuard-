# FireGuard: Real-Time Fire and Smoke Detection

1. Project Description
FireGuard is a highly optimized, edge-capable Computer Vision system designed to detect fire and smoke in real-time CCTV or IP camera feeds. 

Built using the **YOLOv8 Nano** architecture, the model was trained on a stacked dataset of over 30,000 images, 
specifically introducing an "Other" class to actively filter out environmental noise like sunsets and artificial lighting. To ensure stability for local edge deployment,
the inference pipeline features a custom **Temporal Smoothing** algorithm. By evaluating a rolling history of the last 10 frames, 
the system mathematically suppresses false positives and UI flickering, only triggering an alarm when a threat is temporally consistent.

**Enterprise Web Dashboard Deployment:**
To bridge the gap between edge inference and end-user accessibility, a lightweight web dashboard was engineered using Flask. The Python backend operates as a generator, 
encoding processed frames into a network stream and decoupling the YOLOv8 engine from heavy local GUI libraries. 
The dashboard features a live video feed alongside a real-time, asynchronous telemetry log terminal for comprehensive situational awareness.

2. Repository Structure
```text
FireGuard/
├── models/
│   ├── fireguard_final.pt                       # The final trained champion model
│   ├── fireguard_v1_dfire.pt                    # Phase 1 baseline model (D-Fire only)
│   └── yolov8n.pt                               # Base YOLO weights
├── notebooks used to cloud train the YOLOv8n model/
│   ├── FireGuard_2nd_dataset.ipynb              # Phase 2 training (Stacked dataset)
│   └── FireGuard_Cloud_Base_Training_DFire.ipynb # Phase 1 training (Baseline)
├── src/
│   └── detect_web.py                            # AI inference engine & video frame generator
├── templates/
│   └── index.html                               # Enterprise SOC web dashboard UI
├── app.py                                       # Flask web server and routing logic
├── README.md
└── requirements.txt
```

3. Setup Instructions
Prerequisites:

Python 3.9+ installed.
A local webcam or a mobile device running DroidCam for IP network streaming.

Installation:

Clone this repository to your local machine:
git clone [https://github.com/RayanSalmanUSJ/FireGuard.git](https://github.com/RayanSalmanUSJ/FireGuard.git)
cd FireGuard

Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

Install the core inference dependencies:
pip install -r requirements.txt

4. How to Run Inference

The system is designed to run locally, pulling a video stream and processing it through the YOLOv8 model while applying the temporal buffer.
Ensure your camera is active. By default, the script is configured to pull a raw HTTP video stream from a local network device (e.g., DroidCam).
Execute the detection script from the root directory:

python app.py

to view, CTRL + click on the link to view the live feed with detections fromt the terminal output right after executing the command python app.py

CTRL + C on terminal to safely shut down.

Configuring the Camera Feed:
If you need to change the video source, open src/detect.py and modify the cv2.VideoCapture() initialization:

For IP Camera / DroidCam (Default):
cap = cv2.VideoCapture('http://[DeviceIP]:[DroidCamPort]/video')
Replace DeviceIP with your device IP. Ensure the port matches your DroidCam configuration.
For a built-in laptop webcam:
cap = cv2.VideoCapture(0)

Viewing the Output:
Once running, a UI window will appear displaying the real-time feed, the current FPS, and the dynamic temporal bounding boxes (Yellow for unconfirmed anomalies, 
Red/Orange for confirmed threats). Press q in the terminal or on the active window to safely shut down the system.