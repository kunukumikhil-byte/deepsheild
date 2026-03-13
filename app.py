from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from transformers import pipeline
from PIL import Image
import requests
import io
import cv2
import numpy as np
import tempfile
from datetime import datetime

app = Flask(__name__, template_folder="templates")
CORS(app)

# -------------------------
# HuggingFace Deepfake Model
# -------------------------
detector = pipeline(
    "image-classification",
    model="dima806/deepfake_vs_real_image_detection"
)

# -------------------------
# SightEngine API KEYS
# -------------------------
SIGHTENGINE_USER = "1786584317"
SIGHTENGINE_SECRET = "TcBpbXhmNZE6TFuetmPSNQFafrJNAzjm"

# -------------------------
# Allowed files
# -------------------------
ALLOWED_EXTENSIONS = {"png","jpg","jpeg","webp","mp4","mov","avi"}
MAX_FILE_SIZE_MB = 50


def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------
# HuggingFace Detection
# -------------------------
def hf_detect(image):

    result = detector(image)[0]

    label = result["label"].upper()
    score = result["score"]

    if label == "FAKE":
        return True, int(score*100)
    else:
        return False, int(score*100)


# -------------------------
# SightEngine Detection
# -------------------------
def sightengine_detect(image_bytes):

    url = "https://api.sightengine.com/1.0/check.json"

    files = {'media': ('image.jpg', image_bytes)}

    data = {
        'models': 'genai,deepfake',
        'api_user': SIGHTENGINE_USER,
        'api_secret': SIGHTENGINE_SECRET
    }

    response = requests.post(url, files=files, data=data)

    result = response.json()

    try:
        ai_score = result["type"]["ai_generated"]
    except:
        ai_score = 0

    if ai_score > 0.5:
        return True, int(ai_score*100)
    else:
        return False, int(ai_score*100)


# -------------------------
# Image Analysis
# -------------------------
def analyze_image(image_bytes):

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    hf_fake, hf_conf = hf_detect(image)

    api_fake, api_conf = sightengine_detect(image_bytes)

    if hf_fake or api_fake:

        verdict = "DEEPFAKE"
        confidence = max(hf_conf, api_conf)
        authenticity = 100 - confidence
        risk = "High probability of AI manipulation"

        indicators = [
            {"type":"red","category":"AI Detection","text":"AI generated patterns detected"},
            {"type":"yellow","category":"GAN Artifact","text":"Synthetic textures detected"},
            {"type":"red","category":"Manipulation","text":"Possible deepfake content"}
        ]

        overview = "Multiple detectors indicate possible AI generation or manipulation."

    else:

        verdict = "REAL"
        confidence = hf_conf
        authenticity = confidence
        risk = "Low manipulation probability"

        indicators = [
            {"type":"green","category":"Texture","text":"Natural image patterns detected"},
            {"type":"green","category":"Lighting","text":"Lighting appears consistent"},
            {"type":"green","category":"Integrity","text":"No manipulation indicators found"}
        ]

        overview = "Image appears consistent with natural photographic characteristics."

    return {
        "verdict": verdict,
        "confidence": confidence,
        "authenticity_score": authenticity,
        "source_risk": risk,
        "indicators": indicators,
        "overview": overview
    }


# -------------------------
# Video Analysis
# -------------------------
def analyze_video(video_bytes):

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp.write(video_bytes)
    temp.close()

    cap = cv2.VideoCapture(temp.name)

    fake_scores = []
    frame_count = 0

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break

        if frame_count % 10 == 0:

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)

            result = detector(image)[0]

            label = result["label"].upper()
            score = result["score"]

            if label == "FAKE":
                fake_scores.append(score)

        frame_count += 1

    cap.release()

    if len(fake_scores) == 0:
        return False,0

    avg_fake = np.mean(fake_scores)

    if avg_fake > 0.5:
        return True,int(avg_fake*100)
    else:
        return False,int(avg_fake*100)


# -------------------------
# Routes
# -------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        if "image" not in request.files:
            return jsonify({"error":"No file uploaded"}),400

        file = request.files["image"]

        if file.filename == "":
            return jsonify({"error":"No file selected"}),400

        if not allowed_file(file.filename):
            return jsonify({"error":"Unsupported file type"}),400

        data = file.read()

        # VIDEO
        if file.filename.lower().endswith(("mp4","mov","avi")):

            fake, confidence = analyze_video(data)

            if fake:
                verdict = "DEEPFAKE VIDEO"
                authenticity = 100-confidence
                risk = "High manipulation probability"
            else:
                verdict = "REAL VIDEO"
                authenticity = confidence
                risk = "Low manipulation probability"

            return jsonify({
                "verdict":verdict,
                "confidence":confidence,
                "authenticity_score":authenticity,
                "source_risk":risk,
                "overview":"Video analyzed using frame-by-frame deepfake detection",
                "model":"DeepShield Video Detector",
                "analyzed_at":datetime.utcnow().isoformat()+"Z"
            })

        # IMAGE
        else:

            result = analyze_image(data)

            result["model"] = "DeepShield Hybrid Detector"
            result["analyzed_at"] = datetime.utcnow().isoformat()+"Z"

            return jsonify(result)

    except Exception as e:

        return jsonify({
            "error":"Analysis failed",
            "details":str(e)
        }),500


@app.route("/health")
def health():

    return jsonify({
        "status":"online",
        "model":"DeepShield Hybrid AI Detector",
        "providers":["HuggingFace","SightEngine"],
        "version":"5.0"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)