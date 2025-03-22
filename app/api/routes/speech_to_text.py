from fastapi import APIRouter, UploadFile, File, status
from app.models.schemas import SpeechToTextResponse
from app.services.speech_to_text import SpeechToTextService

router = APIRouter()

@router.post(
    "/speech-to-text",
    response_model=SpeechToTextResponse,
    status_code=status.HTTP_200_OK
)
async def convert_speech_to_text(
    file: UploadFile = File(...)
):
    """
    Convert speech to text
    """
    service = SpeechToTextService()
    
    # Read file content
    contents = await file.read()
    
    # Process audio
    text, confidence = service.convert_speech_to_text(contents)
    
    return SpeechToTextResponse(
        text=text,
        confidence=confidence
    )
