from fastapi import APIRouter, UploadFile, File, status, Form
from app.models.schemas import ImageToTextResponse
from app.services.image_to_text import ImageToTextService
from app.services.gemini_image_service import GeminiVisionService
from app.core.config import settings
from app.services.text_to_speech import TextToSpeechService

router = APIRouter()

@router.post(
    "/image-to-text",
    response_model=ImageToTextResponse,
    status_code=status.HTTP_200_OK
)   
async def convert_image_to_text(
    file: UploadFile = File(...),
    method: str = Form("tesseract")
):
    """
    Extract text from an image file
    """
    try:
        # Read file content
        contents = await file.read()
        print(f"File read successfully, size: {len(contents)} bytes, method: {method}")

        if method == "tesseract":
            service = ImageToTextService()
            
            # Process image
            text, confidence, audio_url = service.extract_text_from_image(contents)
            
            return ImageToTextResponse(
                text=text,
                confidence=confidence,
                explanation="Text extracted using Tesseract OCR.",
                audio_path=audio_url
            )
        elif method == "gemini":
            try:
                print("Initializing Gemini service...")
                service = GeminiVisionService(project_id=settings.GOOGLE_CLOUD_PROJECT)
                
                print("Processing image with Gemini...")
                local_text_to_speech_service = TextToSpeechService()
                result = service.process_image(contents, text_to_speech_service=local_text_to_speech_service)
                
                print("Gemini processing complete, returning response...")
                return ImageToTextResponse(
                    text=result['extracted_text'],
                    confidence=result['confidence_score'],
                    explanation=result['explanation'],
                    audio_path=result['audio_path'],
                )
            except Exception as e:
                print(f"Error in Gemini processing: {str(e)}")
                raise
        else:
            return {"error": "Invalid method. Please choose 'tesseract' or 'gemini'."}
    except Exception as e:
        print(f"Unhandled exception in endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
