import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import text_to_speech, image_to_text, pdf_converter, speech_to_text, spell_correct
from app.core.config import settings

json_file_name = settings.SERVICE_ACCOUNT_FILE
# Check if the file exists
if not os.path.isfile(json_file_name):
    raise FileNotFoundError(f"Service account file '{json_file_name}' not found.")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_file_name
os.environ["GOOGLE_CLOUD_PROJECT"] = settings.GOOGLE_CLOUD_PROJECT
os.environ["GOOGLE_CLOUD_LOCATION"] = settings.GOOGLE_CLOUD_LOCATION
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = settings.GOOGLE_GENAI_USE_VERTEXAI

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
app.include_router(
    spell_correct.router, prefix="/api", tags=["Spell Correct"]
)

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
