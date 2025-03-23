import os
import io
import base64
from typing import Dict, Tuple, Optional
from gtts import gTTS
from google import genai
from datetime import datetime

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
            
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

            image = Image.open(io.BytesIO(image_data))
            text = pytesseract.image_to_string(image)
            return text, 0.95
            
        except Exception as e:
            # Log the error
            print(f"Error in image-to-text conversion: {str(e)}")
            raise Exception(f"Failed to extract text from image: {str(e)}")
        
class GeminiImageService:
    """
    Service for processing images using Google's Gemini API
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Gemini service
        
        Args:
            api_key: Google API key for Gemini. If None, will try to get from environment variable.
        """
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key is required. Either pass it directly or set GEMINI_API_KEY environment variable.")

    def process_image(self, image_data: bytes) -> Dict:
        """
        Process an image with Gemini to extract text and get an explanation
        """
        try:    
            # Initialize the Gemini API client
            client = genai.Client(api_key=self.api_key)

            # Initialize the Gemini Vision model
            model = genai.GenerativeModel("gemini-pro-vision")

            # Encode image to Base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Create input prompt
            prompt = (
                "Please analyze this image and provide the following:\n"
                "1. Extract all text visible in the image (OCR)\n"
                "2. Provide a brief explanation of what the image shows\n\n"
                "Format your response like this:\n"
                "TEXT CONTENT:\n[extracted text]\n\n"
                "EXPLANATION:\n[your explanation]"
            )

            print("Sending request to Gemini API...")
            # Call Gemini API
            response = model.generate_content(
                contents=[prompt, {"mime_type": "image/jpeg", "data": image_base64}]
            )

            # Extract response text safely
            full_response = response.text if response else "No valid response from Gemini."

            print(f"Parsed response: {full_response[:100]}...")  # Print just the beginning to avoid huge logs

            # Parse extracted text and explanation
            extracted_text = ""
            explanation = "No explanation provided."
            
            if "TEXT CONTENT:" in full_response and "EXPLANATION:" in full_response:
                parts = full_response.split("EXPLANATION:")
                extracted_text = parts[0].replace("TEXT CONTENT:", "").strip()
                explanation = parts[1].strip()
            else:
                extracted_text = full_response

            # Generate audio for the explanation
            print("Generating audio...")
            audio_path = self._generate_audio(explanation)
            print(f"Audio generated: {audio_path}")

            return {
                'extracted_text': extracted_text,
                'explanation': explanation,
                'audio_path': audio_path,
                'confidence_score': 0.9  # Placeholder score
            }

        except Exception as e:
            print(f"Error in Gemini image processing: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to process image with Gemini: {str(e)}")

    def _generate_audio(self, text: str, filename: str = None) -> str:
        """
        Generate an audio file from text using gTTS
        
        Args:
            text: The text to convert to speech
            filename: Optional custom filename, if None, a timestamp will be used
            
        Returns:
            str: Path to the generated audio file
        """
        try:
            # Ensure output directory exists
            output_dir = "audio_outputs"
            os.makedirs(output_dir, exist_ok=True)

            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"explanation_{timestamp}.mp3"

            filepath = os.path.join(output_dir, filename)

            # Generate speech and save to file
            if text.strip():
                tts = gTTS(text=text, lang='en', slow=False)
                tts.save(filepath)
                return filepath
            else:
                print("Skipping audio generation: Empty text")
                return ""

        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            return ""