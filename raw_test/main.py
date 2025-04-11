import os
import cv2
import base64
import uuid
import numpy as np
from io import BytesIO
from fastapi import FastAPI, Request, File, UploadFile
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

# Cosine similarity
def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

# Draw boxes and labels on faces
def draw_faces(img, faces):
    for i, face in enumerate(faces):
        x1, y1, x2, y2 = map(int, face.bbox)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, f"Face {i+1}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    return img

# Convert annotated image to base64 for HTML display
def image_to_base64(img):
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')

# Homepage
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Face comparison endpoint
@app.post("/check_faces", response_class=HTMLResponse)
async def check_faces(request: Request, image: UploadFile = File(...)):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    faces = face_app.get(img)
    result = {
        "image": "",
        "comparisons": []
    }

    if len(faces) >= 2:
        img = draw_faces(img, faces)

        for i in range(len(faces)):
            for j in range(i + 1, len(faces)):
                sim = cosine_similarity(faces[i].embedding, faces[j].embedding)
                result["comparisons"].append({
                    "face_pair": [i + 1, j + 1],
                    "similarity": round(float(sim), 4),
                    "same_person": sim > 0.3
                })

        result["image"] = image_to_base64(img)

    elif len(faces) == 1:
        result["comparisons"].append({"note": "Only one face found. No comparisons made."})
    else:
        result["comparisons"].append({"note": "No faces detected."})

    return templates.TemplateResponse("index.html", {"request": request, "result": result})
