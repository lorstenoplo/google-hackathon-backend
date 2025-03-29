import os
import io
from typing import Tuple, Optional

from app.core.config import settings

class ImageToTextService:
    """
    Service for extracting text from images
    """
    
    def extract_text_from_image(self, image_data: bytes) -> Tuple[str, Optional[float]]:
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
            return text, 0.95
            
        except Exception as e:
            # Log the error
            print(f"Error in image-to-text conversion: {str(e)}")
            raise Exception(f"Failed to extract text from image: {str(e)}")