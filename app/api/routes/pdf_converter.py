from fastapi import APIRouter, UploadFile, File, status, HTTPException
from app.models.schemas import PdfToMarkdownResponse
from app.services.pdf_converter import PdfConverterService
from app.core.config import settings

router = APIRouter()

@router.post(
    "/pdf-to-markdown",
    response_model=PdfToMarkdownResponse,
    status_code=status.HTTP_200_OK
)
async def convert_pdf_to_markdown(file: UploadFile = File(...)):
    """
    Convert uploaded PDF file to Markdown using Mistral's OCR service.
    """
    try:
        service = PdfConverterService(api_key=settings.MISTRAL_API_KEY)

        # Read file content
        pdf_data = await file.read()

        if not pdf_data:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # Convert PDF to Markdown
        response_dict = service.pdf_to_markdown(pdf_data)

        return PdfToMarkdownResponse(response_dict=response_dict)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
