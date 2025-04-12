import os
import cv2
import base64
import numpy as np
import urllib.request
from pathlib import Path
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from insightface.app import FaceAnalysis
from numpy.linalg import norm
from deepface import DeepFace

# Setup FastAPI
app = FastAPI()

# Directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
MODELS_DIR = os.path.join(BASE_DIR, "models")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Create necessary directories
Path(MODELS_DIR).mkdir(parents=True, exist_ok=True)

# Load face analysis model
face_app = FaceAnalysis(name='buffalo_l')
face_app.prepare(ctx_id=-1)

# Emotion detection setup
EMOTION_LABELS = ['neutral', 'happy', 'sad', 'surprise', 'fear', 'disgust', 'anger']
EMOTION_MODEL_URL = "https://github.com/onnx/models/raw/main/vision/body_analysis/emotion_ferplus/model/emotion-ferplus-8.onnx"
EMOTION_MODEL_PATH = Path(MODELS_DIR) / "emotion-ferplus-8.onnx"

# Download emotion model if missing
if not EMOTION_MODEL_PATH.exists():
    try:
        print("Downloading emotion model...")
        urllib.request.urlretrieve(EMOTION_MODEL_URL, EMOTION_MODEL_PATH)
        print("Emotion model downloaded successfully")
    except Exception as e:
        print(f"Failed to download emotion model: {str(e)}")
        EMOTION_MODEL_PATH = None

# Load emotion recognition model if available
emotion_net = None
if EMOTION_MODEL_PATH and EMOTION_MODEL_PATH.exists():
    try:
        emotion_net = cv2.dnn.readNetFromONNX(str(EMOTION_MODEL_PATH))
        print("Emotion model loaded successfully")
    except Exception as e:
        print(f"Failed to load emotion model: {str(e)}")

def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

# Replace the emotion detection section with this:


def detect_emotion(face_region):
    try:
        if face_region.size == 0:
            return "invalid_face"
            
        # Convert BGR to RGB
        rgb_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB)
        
        # Analyze using DeepFace
        result = DeepFace.analyze(rgb_face, actions=['emotion'], enforce_detection=False)
        return result[0]['dominant_emotion'].lower()
        
    except Exception as e:
        print(f"Emotion detection error: {str(e)}")
        return "analysis_error"

def draw_faces(img, faces, emotions):
    for i, (face, emotion) in enumerate(zip(faces, emotions)):
        x1, y1, x2, y2 = map(int, face.bbox)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"Face {i+1}"
        if emotion not in ["model_unavailable", "error"]:
            label += f": {emotion}"
        cv2.putText(img, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    return img

def image_to_base64(img):
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    result = {
        "image": "",
        "comparisons": [],
        "error": ""
    }
    return templates.TemplateResponse("index.html", {"request": request, "result": result})

@app.post("/check_faces", response_class=HTMLResponse)
async def check_faces(request: Request, image: UploadFile = File(...)):
    result = {
        "image": "",
        "comparisons": [],
        "error": ""
    }
    
    try:
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            result["error"] = "Unable to decode the image. Please upload a valid image file."
            return templates.TemplateResponse("index.html", {"request": request, "result": result})

        faces = face_app.get(img)
        face_count = len(faces)

        emotions = []
        for face in faces:
            x1, y1, x2, y2 = map(int, face.bbox)
            face_region = img[y1:y2, x1:x2]
            if face_region.size == 0:
                emotions.append("no_face")
                continue
            emotions.append(detect_emotion(face_region))

        if face_count == 2:
            img = draw_faces(img, faces, emotions)
            sim = cosine_similarity(faces[0].embedding, faces[1].embedding)
            result["comparisons"].append({
                "face_pair": [1, 2],
                "similarity": round(float(sim), 4),
                "same_person": sim > 0.3,
                "emotions": emotions
            })
            result["image"] = image_to_base64(img)
            
        elif face_count > 2:
            result["error"] = "More than two faces detected. Please upload an image with exactly two faces."
        else:
            result["error"] = "Insufficient faces detected. Please upload an image with two faces."

    except Exception as e:
        result["error"] = f"Processing error: {str(e)}"
        
    return templates.TemplateResponse("index.html", {"request": request, "result": result})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
