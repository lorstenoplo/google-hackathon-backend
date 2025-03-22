from fastapi import APIRouter, UploadFile, File, status
from app.models.schemas import ImageToTextResponse
from app.services.image_to_text import ImageToTextService

router = APIRouter()

@router.post(
    "/image-to-text",
    response_model=ImageToTextResponse,
    status_code=status.HTTP_200_OK
)
async def convert_image_to_text(
    file: UploadFile = File(...)
):
    """
    Extract text from an image file
    """
    service = ImageToTextService()
    
    # Read file content
    contents = await file.read()
    
    # Process image
    text, confidence = service.extract_text_from_image(contents)
    
    return ImageToTextResponse(
        text=text,
        confidence=confidence
    )
