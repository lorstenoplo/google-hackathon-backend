import os
import io
from typing import Tuple, Optional

from app.core.config import settings
from app.services.text_to_speech import TextToSpeechService

class ImageToTextService:
    """
    Service for extracting text from images
    """
    
    def extract_text_from_image(self, image_data: bytes) -> Tuple[str, Optional[float], Optional[str]]:
        """
        Extract text from an image
        
        Args:
            image_data: The image data as bytes
            
        Returns:
            tuple: (extracted_text, confidence_score)
        """
        try:
            import pytesseract
            from PIL import Image
            
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH

            image = Image.open(io.BytesIO(image_data))

            text = pytesseract.image_to_string(image)

            text_to_speech_service = TextToSpeechService()
            audio_url = text_to_speech_service.convert_text_to_speech(text=text, voice="en-IN-Chirp-HD-F", language_code="en-IN")

            return text, 0.95, audio_url  # Assuming a default confidence score of 0.95 for simplicity
        except Exception as e:
            # Log the error
            print(f"Error in image-to-text conversion: {str(e)}")
            raise Exception(f"Failed to extract text from image: {str(e)}")