# DocuMind 📄🧠
Note: OCR_FInal folder is working folder
Automate document processing with OCR, face recognition, and form auto-filling!

---

## 🌟 Features

- OCR Text Extraction: Extract text from citizen documents (ID cards, passports) using Tesseract OCR.
- Face Detection & Comparison: Detect and compare two faces in uploaded images.
- Form Auto-Fill: Automatically populate forms using extracted citizen information.
- FastAPI Backend: Robust Python API for processing data.
- Simple HTML Frontend: User-friendly interface for uploading documents/images.

---

## 🛠 Technologies Used

- OCR: Tesseract OCR (Python wrapper: pytesseract)
- Face Recognition: OpenCV (Python library)
- Backend: FastAPI, Python 3.9+, Pydantic (data validation)
- Frontend: HTML, CSS, JavaScript
- Other Tools: uvicorn (ASGI server), python-multipart (file uploads)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Tesseract OCR installed ([Download here](https://github.com/tesseract-ocr/tesseract))
- Install dependencies:
  ```bash
  pip install fastapi uvicorn python-multipart opencv-python pytesseract face_recognition
  uvicorn main:app --reload