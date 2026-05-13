# to run, no need to run detect_web.py, run: python app.py
from flask import Flask, render_template, Response, jsonify
from src.detect_web import generate_frames, global_logs

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/logs')
def get_logs():
    return jsonify(global_logs)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)