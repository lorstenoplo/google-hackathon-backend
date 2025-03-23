from fastapi import APIRouter, UploadFile, File, status, Form
from app.models.schemas import ImageToTextResponse
from app.services.image_to_text import GeminiImageService, ImageToTextService
from app.core.config import settings

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
            text, confidence = service.extract_text_from_image(contents)
            
            return ImageToTextResponse(
                text=text,
                confidence=confidence
            )
        elif method == "gemini":
            try:
                print("Initializing Gemini service...")
                service = GeminiImageService(api_key=settings.GEMINI_API_KEY)
                
                print("Processing image with Gemini...")
                result = service.process_image(contents)
                
                print("Gemini processing complete, returning response...")
                return ImageToTextResponse(
                    text=result['extracted_text'],
                    confidence=result['confidence_score'],
                    explanation=result['explanation'],
                    audio_path=result['audio_path']
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
