from pydantic import BaseModel, Field
from typing import Optional, List


class TextToSpeechRequest(BaseModel):
    """
    Schema for text-to-speech request
    """
    text: str = Field(..., description="The text to convert to speech")
    voice: Optional[str] = Field("en-US-Wavenet-D", description="Voice ID to use")  # Set a valid default
    rate: Optional[float] = Field(1.0, description="Speech rate (0.5 to 2.0)")
    output_filename: Optional[str] = Field(None, description="Output filename")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This is a sample text to convert to speech.",
                "voice": "default",
                "rate": 1.0
            }
        }


class TextToSpeechResponse(BaseModel):
    """
    Schema for text-to-speech response
    """
    success: bool
    message: str
    audio_url: Optional[str] = None


class ImageToTextRequest(BaseModel):
    """
    Schema for image-to-text request
    Note: This is for documentation, actual file upload uses multipart/form-data
    """
    class Config:
        json_schema_extra = {
            "example": {
                "file": "binary_image_data"
            }
        }


class ImageToTextResponse(BaseModel):
    """
    Schema for image-to-text response
    """
    text: str
    confidence: Optional[float] = None
    explanation: Optional[str] = None
    audio_path: Optional[str] = None


class PdfToMarkdownRequest(BaseModel):
    """
    Schema for PDF to Markdown request
    Note: This is for documentation, actual file upload uses multipart/form-data
    """
    class Config:
        json_schema_extra = {
            "example": {
                "file": "binary_pdf_data"
            }
        }


class MarkdownToPdfRequest(BaseModel):
    """
    Schema for Markdown to PDF request
    """
    markdown: str = Field(..., description="Markdown text to convert to PDF")
    
    class Config:
        json_schema_extra = {
            "example": {
                "markdown": "# Title\n\nThis is a paragraph with **bold** and *italic* text."
            }
        }


class PdfToMarkdownResponse(BaseModel):
    """
    Schema for PDF to Markdown response
    """
    response_dict: dict = Field(..., description="Response dictionary from Mistral OCR API")


class SpeechToTextRequest(BaseModel):
    """
    Schema for speech-to-text request
    Note: This is for documentation, actual file upload uses multipart/form-data
    """
    class Config:
        json_schema_extra = {
            "example": {
                "file": "binary_audio_data"
            }
        }


class SpeechToTextResponse(BaseModel):
    """
    Schema for speech-to-text response
    """
    text: str
    confidence: Optional[float] = None


class TextCorrectionRequest(BaseModel):
    text: str

class TextCorrectionResponse(BaseModel):
    corrected_text: str
    original_text: str