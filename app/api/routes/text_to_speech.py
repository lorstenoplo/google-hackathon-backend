from fastapi import APIRouter, Depends, status, Response
from app.models.schemas import TextToSpeechRequest, TextToSpeechResponse
from app.services.text_to_speech import TextToSpeechService

router = APIRouter()

@router.post(
    "/text-to-speech",
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
    audio_url = service.convert_text_to_speech(
        text=request.text,
        voice=request.voice,
        rate=request.rate,
        output_filename= request.output_filename
    )

    return TextToSpeechResponse(
        success=True,
        message="Text converted to speech",
        audio_url=audio_url
    )
