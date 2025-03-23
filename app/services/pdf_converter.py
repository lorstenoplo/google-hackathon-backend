from io import BytesIO
import json
import markdown

from mistralai import Mistral
from mistralai.models import OCRResponse
from mistralai import DocumentURLChunk

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

class PdfConverterService:
    """
    Service for converting between PDF and Markdown using Mistral's OCR API
    """
    
    def __init__(self, api_key: str):
        self.client = Mistral(api_key=api_key)
    
    def pdf_to_markdown(self, pdf_data: bytes) -> str:
        """
        Convert PDF to Markdown using Mistral's OCR service
        """
        try:
            uploaded_file = self.client.files.upload(
                file={
                    "file_name": "uploaded.pdf",
                    "content": pdf_data,
                },
                purpose="ocr",
            )
            
            if not uploaded_file or not uploaded_file.id:
                raise ValueError("File upload failed. No valid file ID received.")
            
            signed_url = self.client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
            if not signed_url or not signed_url.url:
                raise ValueError("Failed to obtain signed URL for OCR processing.")
            
            pdf_response = self.client.ocr.process(
                document=DocumentURLChunk(document_url=signed_url.url),
                model="mistral-ocr-latest",
                include_image_base64=True
            )
            
            # Debugging: Log response
            response_dict = json.loads(pdf_response.model_dump_json())
            print(json.dumps(response_dict, indent=4)[:1000])  # First 1000 chars
            
            return self._get_combined_markdown(pdf_response)
        
        except Exception as e:
            print(f"Error in PDF-to-Markdown conversion: {str(e)}")
            raise Exception(f"Failed to convert PDF to Markdown: {str(e)}")
    
    def _replace_images_in_markdown(self, markdown_str: str, images_dict: dict) -> str:
        """
        Replace image placeholders in markdown with base64-encoded images.
        """
        for img_name, base64_str in images_dict.items():
            markdown_str = markdown_str.replace(
                f"![{img_name}]({img_name})", f"![{img_name}](data:image/png;base64,{base64_str})"
            )
        return markdown_str
    
    def _get_combined_markdown(self, ocr_response: OCRResponse) -> str:
        """
        Combine OCR text and images into a single markdown document.
        """
        markdowns = []
        for page in ocr_response.pages:
            image_data = {img.id: img.image_base64 for img in page.images}
            markdowns.append(self._replace_images_in_markdown(page.markdown, image_data))
        return "\n\n".join(markdowns)
    
    def markdown_to_pdf(self, markdown_text: str) -> bytes:
        """
        Convert Markdown to PDF while preserving formatting.

        Args:
            markdown_text (str): Markdown content

        Returns:
            bytes: Generated PDF content
        """
        try:
            html_content = markdown.markdown(markdown_text)  # Convert Markdown to HTML

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = [Paragraph(html_content, styles["Normal"])]  # Convert HTML to Paragraph
            
            doc.build(story)  # Build PDF with proper formatting
            buffer.seek(0)
            return buffer.getvalue()

        except Exception as e:
            print(f"Error in Markdown-to-PDF conversion: {str(e)}")
            raise Exception(f"Failed to convert Markdown to PDF: {str(e)}")
