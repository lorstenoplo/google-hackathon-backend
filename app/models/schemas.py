from pydantic import BaseModel, Field
from typing import Optional, List


class TextToSpeechRequest(BaseModel):
    """
    Schema for text-to-speech request
    """
    text: str = Field(..., description="The text to convert to speech")
    voice: Optional[str] = Field("default", description="Voice ID to use")
    rate: Optional[float] = Field(1.0, description="Speech rate (0.5 to 2.0)")
    
    class Config:
        schema_extra = {
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


class ImageToTextRequest(BaseModel):
    """
    Schema for image-to-text request
    Note: This is for documentation, actual file upload uses multipart/form-data
    """
    class Config:
        schema_extra = {
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


class PdfToMarkdownRequest(BaseModel):
    """
    Schema for PDF to Markdown request
    Note: This is for documentation, actual file upload uses multipart/form-data
    """
    class Config:
        schema_extra = {
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
        schema_extra = {
            "example": {
                "markdown": "# Title\n\nThis is a paragraph with **bold** and *italic* text."
            }
        }


class PdfToMarkdownResponse(BaseModel):
    """
    Schema for PDF to Markdown response
    """
    markdown: str


class SpeechToTextRequest(BaseModel):
    """
    Schema for speech-to-text request
    Note: This is for documentation, actual file upload uses multipart/form-data
    """
    class Config:
        schema_extra = {
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