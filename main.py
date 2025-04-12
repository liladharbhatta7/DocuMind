import os
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse

app = FastAPI()

# Serve the HTML form on the root endpoint.
@app.get("/", response_class=HTMLResponse)
async def get_form():
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Endpoint to handle form submission.
@app.post("/submit")
async def submit_form(
    name: str = Form(...),
    dob: str = Form(...),
    father_name: str = Form(...),
    address: str = Form(...),
    citizenship_number: str = Form(...),
    sex: str = Form(...),
    citizenship_front: UploadFile = File(...),
    citizenship_back: UploadFile = File(...),
    pan_card: UploadFile = File(...)
):
    # Create a directory to store the uploads.
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    # Save the uploaded Citizenship Front image.
    front_path = os.path.join(upload_dir, citizenship_front.filename)
    with open(front_path, "wb") as f:
        f.write(await citizenship_front.read())

    # Save the uploaded Citizenship Back image.
    back_path = os.path.join(upload_dir, citizenship_back.filename)
    with open(back_path, "wb") as f:
        f.write(await citizenship_back.read())

    # Save the uploaded PAN Card image.
    pan_path = os.path.join(upload_dir, pan_card.filename)
    with open(pan_path, "wb") as f:
        f.write(await pan_card.read())

    # You can integrate your ML components and further processing here.
    # For now, return a simple JSON response with the submitted data.
    return {
        "message": "Form submitted successfully",
        "data": {
            "name": name,
            "dob": dob,
            "father_name": father_name,
            "address": address,
            "citizenship_number": citizenship_number,
            "sex": sex,
            "citizenship_front_file": front_path,
            "citizenship_back_file": back_path,
            "pan_card_file": pan_path
        }
    }
