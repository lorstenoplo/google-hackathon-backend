from fastapi import APIRouter, UploadFile, File, status, Response
from app.models.schemas import PdfToMarkdownResponse, MarkdownToPdfRequest
from app.services.pdf_converter import PdfConverterService

router = APIRouter()

@router.post(
    "/pdf-to-markdown",
    response_model=PdfToMarkdownResponse,
    status_code=status.HTTP_200_OK
)
async def convert_pdf_to_markdown(
    file: UploadFile = File(...)
):
    """
    Convert PDF to Markdown
    """
    service = PdfConverterService()
    
    # Read file content
    contents = await file.read()
    
    # Convert PDF to Markdown
    markdown_text = service.pdf_to_markdown(contents)
    
    return PdfToMarkdownResponse(
        markdown=markdown_text
    )

@router.post(
    "/markdown-to-pdf",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"content": {"application/pdf": {}}}
    }
)
async def convert_markdown_to_pdf(
    request: MarkdownToPdfRequest
):
    """
    Convert Markdown to PDF
    """
    service = PdfConverterService()
    
    # Convert Markdown to PDF
    pdf_data = service.markdown_to_pdf(request.markdown)
    
    return Response(
        content=pdf_data,
        media_type="application/pdf"
    )