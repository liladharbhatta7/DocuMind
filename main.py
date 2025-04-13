import os
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

# Import the face detection function from the separate module.
from face_detect import process_face_image

app = FastAPI()

# Serve the HTML form on the root endpoint.
@app.get("/", response_class=HTMLResponse)
async def get_form():
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# Endpoint to handle overall form submission.
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
    pan_card: UploadFile = File(...),
    face_photo: UploadFile = File(...)
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

    # Process the facial verification photo using face_detect.py.
    face_contents = await face_photo.read()
    face_result, face_error = process_face_image(face_contents)

    response_data = {
        "name": name,
        "dob": dob,
        "father_name": father_name,
        "address": address,
        "citizenship_number": citizenship_number,
        "sex": sex,
        "citizenship_front_file": front_path,
        "citizenship_back_file": back_path,
        "pan_card_file": pan_path,
    }

    if face_error:
        response_data["face_verification"] = {"error": face_error}
    else:
        response_data["face_verification"] = {"processed_image": face_result}

    return JSONResponse({
        "message": "Form submitted successfully",
        "data": response_data
    })

# New endpoint to check facial detection separately.
@app.post("/check_face")
async def check_face(face_photo: UploadFile = File(...)):
    face_contents = await face_photo.read()
    face_result, face_error = process_face_image(face_contents)
    if face_error:
        return JSONResponse(status_code=400, content={"error": face_error})
    return JSONResponse({"result": face_result})
