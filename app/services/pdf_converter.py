import json
from mistralai import Mistral
from mistralai.models import OCRResponse, DocumentURLChunk

class PdfConverterService:
    """
    Service for converting between PDF and Markdown using Mistral's OCR API.
    """

    def __init__(self, api_key: str):
        self.client = Mistral(api_key=api_key)

    def pdf_to_markdown(self, pdf_data: bytes) -> dict:
        """
        Convert a PDF file (as bytes) to Markdown using Mistral's OCR service.
        """
        try:
            if not pdf_data:
                raise ValueError("Empty PDF data provided.")

            # Upload PDF to Mistral
            uploaded_file = self.client.files.upload(
                file={
                    "file_name": "uploaded.pdf",  # Placeholder name
                    "content": pdf_data,
                },
                purpose="ocr",
            )

            if not uploaded_file or not uploaded_file.id:
                raise ValueError("File upload failed. No valid file ID received.")

            # Obtain signed URL for OCR processing
            signed_url = self.client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
            if not signed_url or not signed_url.url:
                raise ValueError("Failed to obtain signed URL for OCR processing.")

            # Process PDF with OCR
            pdf_response = self.client.ocr.process(
                document=DocumentURLChunk(document_url=signed_url.url),
                model="mistral-ocr-latest",
                include_image_base64=True
            )

            # Debug: Print first 1000 characters of response
            response_dict = json.loads(pdf_response.model_dump_json())
            print(json.dumps(response_dict, indent=4)[:1000])  # Debugging output

            return response_dict

        except Exception as e:
            print(f"Error in PDF-to-Markdown conversion: {str(e)}")
            raise Exception(f"Failed to convert PDF to Markdown: {str(e)}")