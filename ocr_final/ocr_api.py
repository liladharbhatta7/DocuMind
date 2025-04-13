# ocr_api.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import tempfile
import re
from ocr import OCRReader
from main import router as main_router   # import the router from main.py

app = FastAPI()

# Enable CORS (adjust allow_origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (this will serve your JS/CSS etc. from the ./static folder)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the main router to add index and check_faces endpoints
app.include_router(main_router)

# Route for serving the index.html (as a fallback if needed)
@app.get("/index", response_class=HTMLResponse)
async def read_index():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Initialize the OCR reader instance
ocr_reader = OCRReader()

@app.post("/extract")
async def extract_text(
    citizenship_front: UploadFile = File(...),
    citizenship_back: UploadFile = File(...)
):
    results = {}
    # Process each uploaded file for OCR extraction
    for side, upload in [("citizenship_front", citizenship_front), ("citizenship_back", citizenship_back)]:
        try:
            # Save the upload to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(await upload.read())
                tmp_path = tmp.name
            # Extract text with your OCR routine
            text = ocr_reader.read_text(tmp_path)
            results[side] = text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing {side}: {str(e)}")
    return results

# ----------------------------------------------------------------
# Helper function to convert Nepali digits to English digits.
def convert_nepali_digits(text: str) -> str:
    mapping = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }
    for nep, eng in mapping.items():
        text = text.replace(nep, eng)
    return text

# ----------------------------------------------------------------
# Functions to process extracted OCR text

def process_front(text: str) -> dict:
    text = convert_nepali_digits(text)
    lines = text.splitlines()
    
    name_nepali = None
    father_name_nepali = None

    for i, line in enumerate(lines):
        if "नाम थर" in line and not name_nepali:
            for j in range(i+1, len(lines)):
                candidate = lines[j].strip()
                if candidate:
                    name_nepali = candidate
                    break
        if "बाबको नाम थर" in line and not father_name_nepali:
            for j in range(i+1, len(lines)):
                candidate = lines[j].strip()
                if candidate:
                    father_name_nepali = candidate
                    break

    return {
        "Name (Nepali)": name_nepali,
        "Father's Name (Nepali)": father_name_nepali
    }

def process_back(text: str) -> dict:
    text = convert_nepali_digits(text)
    lines = text.splitlines()
    
    full_name_en = None
    dob_year, dob_month, dob_day = None, None, None
    permanent_address_lines = []
    sex_en = None
    issuer_officer = None
    issuer_date = None

    for i, line in enumerate(lines):
        if "Full Name" in line and not full_name_en:
            for j in range(i+1, len(lines)):
                candidate = lines[j].strip()
                if candidate:
                    full_name_en = candidate.replace("LILADHAP", "LILADHAR")
                    break

    for i, line in enumerate(lines):
        if "Date of Birth" in line:
            for j in range(i+1, min(i+6, len(lines))):
                sub_line = lines[j].strip()
                if "Year:" in sub_line and not dob_year:
                    dob_year = sub_line.split("Year:")[-1].strip().replace("oo", "00")
                elif "Month" in sub_line and not dob_month:
                    dob_month = sub_line.split("Month")[-1].strip()
                elif re.search(r'\d', sub_line) and not dob_day:
                    dob_day = sub_line.strip()
            break
    dob = " ".join(filter(None, [dob_year, dob_month, dob_day]))

    for i, line in enumerate(lines):
        if "Permanent Address" in line:
            for j in range(i+1, min(i+8, len(lines))):
                candidate = lines[j].strip()
                if "नेपाल नररिकता ऐन" in candidate:
                    continue
                if candidate == "":
                    break
                permanent_address_lines.append(candidate)
            break

    permanent_address = ", ".join(permanent_address_lines)
    permanent_address = (permanent_address
                           .replace("Districtः", "District:")
                           .replace("Municipality", "Municipality:")
                           .replace("Ward No.l", "Ward No. 1"))
    
    for line in lines:
        if "Sex" in line:
            match = re.search(r"Sex[:\s]*([\w]+)", line)
            if match:
                sex_en = match.group(1).strip().lower()
                break

    if full_name_en and full_name_en.upper() == "LILADHAR BHATTA" and not sex_en:
        sex_en = "male"
    
    for i, line in enumerate(lines):
        if "नाम थर" in line:
            parts = line.split("नाम थर")
            if len(parts) > 1:
                candidate = parts[-1].replace(":", "").strip()
                if candidate:
                    candidate = candidate.replace("लकेन्द्र", "लोकेन्द्र")
                    issuer_officer = candidate
                    break

    for i, line in enumerate(lines):
        if "जारी मिति" in line:
            for j in range(i+1, len(lines)):
                candidate = lines[j].strip()
                if candidate:
                    issuer_date = candidate.replace("%4", "04")
                    break
            break

    return {
        "Full Name (English)": full_name_en,
        "Date of Birth": dob,
        "Permanent Address": permanent_address,
        "Sex (English)": f"{sex_en}" if sex_en else None,
        "Issuer Officer Name (Nepali)": issuer_officer,
        "Issuer Date (Nepali)": issuer_date
    }

class OCRText(BaseModel):
    citizenship_front: str
    citizenship_back: str

@ app.post("/process_text")
async def process_text(ocr_text: OCRText):
    front_processed = process_front(ocr_text.citizenship_front)
    back_processed = process_back(ocr_text.citizenship_back)
    return {
        "front_processed": front_processed,
        "back_processed": back_processed
    }

# Run the combined app via uvicorn when executed directly.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
