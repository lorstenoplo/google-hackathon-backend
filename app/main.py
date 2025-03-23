from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import text_to_speech, image_to_text, pdf_converter, speech_to_text
from app.core.config import settings
import os

# Replace with your actual JSON file name
json_file_name = r"D:\Nishanth\dyslexia-reader\backend\app\keys\tts.json"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_file_name
os.environ["GOOGLE_CLOUD_PROJECT"] = "flowing-elf-454116-m4"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

print("Authentication setup complete!")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(text_to_speech.router, prefix="/api", tags=["Text to Speech"])
app.include_router(image_to_text.router, prefix="/api", tags=["Image to Text"])
app.include_router(pdf_converter.router, prefix="/api", tags=["PDF Converter"])
app.include_router(speech_to_text.router, prefix="/api", tags=["Speech to Text"])

@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint to verify API is running
    """
    return {
        "message": "Welcome to the ReadEase API",
        "version": settings.PROJECT_VERSION,
        "documentation": "/docs",
    }
