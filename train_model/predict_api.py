from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import joblib
from app.ocr import OCRReader  # assuming ocr.py is inside train_model/app

# Define BASE_DIR as this file’s directory
BASE_DIR = os.path.dirname(__file__)

# Correct paths for model and vectorizer
MODEL_PATH = os.path.join(BASE_DIR, "text_classifier_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")

# Load model and vectorizer
model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

# Init FastAPI
app = FastAPI()

# Enable CORS (for frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this more restrictively
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Serve the HTML page
@app.get("/", response_class=FileResponse)
async def serve_html():
    return FileResponse(os.path.join(STATIC_DIR, "predict.html"))

# Init OCR Reader
ocr_instance = OCRReader(languages=['en', 'ne'])

# Predict endpoint
@app.post("/predict")
async def predict_document(file: UploadFile = File(...)):
    try:
        # Save uploaded image temporarily
        temp_path = os.path.join(STATIC_DIR, file.filename)
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # OCR
        extracted_text = ocr_instance.read_text(temp_path)
        os.remove(temp_path)  # Clean up temp file

        if not extracted_text or not extracted_text.strip():
            return JSONResponse(status_code=400, content={"message": "No text found."})

        # Prediction
        features = vectorizer.transform([extracted_text])
        prediction = model.predict(features)[0]

        return {"prediction": prediction, "extracted_text": extracted_text}

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Prediction failed: {str(e)}"})
