from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import routers from the refactored modules
from main import router as main_router
from ocr_api import router as ocr_router

app = FastAPI()

# Optionally enable CORS globally if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (if you haven't mounted it in individual modules)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the routers
app.include_router(main_router)
app.include_router(ocr_router)
