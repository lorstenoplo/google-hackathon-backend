from app.models.schemas import TextCorrectionResponse, TextCorrectionRequest
from app.services.spell_correct import GeminiSpellCorrectService
from fastapi import APIRouter

router = APIRouter()

gemini_service = GeminiSpellCorrectService()

@router.post("/spell-correct", response_model=TextCorrectionResponse)
async def correct_text(request: TextCorrectionRequest):
    """
    Endpoint to correct spelling and grammatical errors in text.
    """
    corrected = await gemini_service.correct_text(request.text)
    return TextCorrectionResponse(
        corrected_text=corrected,
        original_text=request.text
    )
