# app/ocr_api.py

import os
import csv
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.ocr import OCRReader

# Initialize FastAPI app
app = FastAPI()

# Absolute path for the static directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Pre-load the OCR model so that it isn’t reloaded for every request.
print("Initializing OCRReader globally...")
ocr_instance = OCRReader(languages=['en', 'ne'])
print("OCRReader initialized.")

# Endpoint to serve the HTML page.
@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join(static_dir, "index.html")
    with open(index_path, encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)

# Endpoint for performing OCR on an image file.
@app.post("/ocr")
async def extract_text(file: UploadFile = File(...)):
    try:
        print("Endpoint /ocr called.")
        # Save the uploaded file to the static directory.
        temp_file_path = os.path.join(static_dir, file.filename)
        print(f"Saving uploaded file to: {temp_file_path}")
        with open(temp_file_path, "wb") as f:
            f.write(await file.read())
        
        print("File saved. Performing OCR using pre-loaded model...")
        extracted_text = ocr_instance.read_text(temp_file_path)
        print("OCR completed. Extracted text:")
        print(extracted_text)
        
        # Remove temporary file after processing.
        os.remove(temp_file_path)
        print("Temporary file removed. Returning response.")
        return {"extracted_text": extracted_text}
    except Exception as e:
        print("Error in /ocr endpoint:", e)
        return {"extracted_text": f"Error during OCR: {str(e)}"}

# New endpoint to save extracted text along with a label to a CSV file.
@app.post("/save")
async def save_document(payload: dict):
    import re

    # Retrieve text and label from the JSON payload.
    raw_text = payload.get("text", "").strip()
    label = payload.get("label", "").strip()

    if not raw_text or not label:
        return JSONResponse(
            status_code=400,
            content={"message": "Both text and label are required."}
        )

    # Clean the text: remove newlines and extra whitespace
    cleaned_text = re.sub(r'\s+', ' ', raw_text).strip()

    # Define path for CSV file (create the 'data' folder if not exists).
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "document_data.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    write_header = not os.path.exists(csv_path)

    try:
        with open(csv_path, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if write_header:
                writer.writerow(["text", "label"])
            writer.writerow([cleaned_text, label])
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Failed to write to CSV file: {str(e)}"}
        )

    return {"message": "Document saved successfully."}
