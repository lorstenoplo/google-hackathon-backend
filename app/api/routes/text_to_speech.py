from fastapi import APIRouter, Depends, status, Response
from app.models.schemas import TextToSpeechRequest, TextToSpeechResponse
from app.services.text_to_speech import TextToSpeechService

router = APIRouter()

@router.post(
    "/text-to-speech",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"content": {"audio/mpeg": {}}}
    }
)
async def convert_text_to_speech(
    request: TextToSpeechRequest
):
    """
    Convert text to speech and return an audio file
    """
    service = TextToSpeechService()
    audio_data = service.convert_text_to_speech(
        text=request.text,
        voice=request.voice,
        rate=request.rate
    )
    
    return Response(
        content=audio_data,
        media_type="audio/mpeg"
    )