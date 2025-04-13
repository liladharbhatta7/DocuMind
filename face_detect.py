import os
import cv2
import base64
import uuid
import numpy as np
from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from insightface.app import FaceAnalysis
from numpy.linalg import norm

# Setup FastAPI
app = FastAPI()

# Directory setup (relative to this file)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Load model (CPU only)
face_app = FaceAnalysis(name='buffalo_l')
face_app.prepare(ctx_id=-1)

# Cosine similarity function
def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

# Draw boxes and labels on detected faces
def draw_faces(img, faces):
    for i, face in enumerate(faces):
        x1, y1, x2, y2 = map(int, face.bbox)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, f"Face {i+1}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    return img

# Convert image to base64 for inline HTML display
def image_to_base64(img):
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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

        # Detect faces
        faces = face_app.get(img)
        face_count = len(faces)

        # Check exactly two faces are detected
        if face_count == 2:
            # Draw bounding boxes and labels
            img = draw_faces(img, faces)
            sim = cosine_similarity(faces[0].embedding, faces[1].embedding)
            result["comparisons"].append({
                "face_pair": [1, 2],
                "similarity": round(float(sim), 4),
                "same_person": sim > 0.3
            })
            result["image"] = image_to_base64(img)

        elif face_count > 2:
            result["error"] = "More than two faces detected. Please upload another document with exactly two faces."
        else:
            result["error"] = "Insufficient face detection. Please upload another document with at least two faces."

    except Exception as e:
        result["error"] = f"An error occurred: {str(e)}"
        
    return templates.TemplateResponse("index.html", {"request": request, "result": result})
