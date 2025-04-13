# main.py
import os
import cv2
import base64
import numpy as np
from fastapi import APIRouter, Request, File, UploadFile, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from insightface.app import FaceAnalysis
from numpy.linalg import norm

router = APIRouter()

# Setup directories (assumes index.html is in the same folder as main.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = BASE_DIR
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Set up template engine
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Although you originally mounted static on the FastAPI app,
# here we simply rely on the main FastAPI (in ocr_api.py) to mount the static directory.
# You may remove router.mount(...) because APIRouter does not support mount().

# Load the face analysis model (CPU-only)
face_app = FaceAnalysis(name='buffalo_l')
face_app.prepare(ctx_id=-1)

# Utility functions for the face check endpoints
def cosine_similarity(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

def draw_faces(img, faces):
    for i, face in enumerate(faces):
        x1, y1, x2, y2 = map(int, face.bbox)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, f"Face {i+1}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    return img

def image_to_base64(img):
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')

# --------------------------------------------------------------
# Endpoint to serve the index.html using a Jinja2 template.
@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --------------------------------------------------------------
# Endpoint for processing image face check requests.
@router.post("/check_faces", response_class=HTMLResponse)
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
        
        # Detect faces using the insightface model
        faces = face_app.get(img)
        face_count = len(faces)
        
        # Validate that exactly two faces are found
        if face_count == 2:
            img = draw_faces(img, faces)
            sim = cosine_similarity(faces[0].embedding, faces[1].embedding)
            result["comparisons"].append({
                "face_pair": [1, 2],
                "similarity": round(float(sim), 4),
                "same_person": sim > 0.3
            })
            result["image"] = image_to_base64(img)
        elif face_count > 2:
            result["error"] = "More than two faces detected. Please upload an image with exactly two faces."
        else:
            result["error"] = "Insufficient face detection. Please upload an image with at least two faces."
    except Exception as e:
        result["error"] = f"An error occurred: {str(e)}"
    return templates.TemplateResponse("index.html", {"request": request, "result": result})
