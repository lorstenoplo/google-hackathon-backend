import os
from datetime import datetime
from typing import Dict
from google.cloud import vision, storage
from app.services.text_to_speech import TextToSpeechService
import vertexai
from vertexai.generative_models import GenerativeModel, Part

class GeminiVisionService:
    """
    Service for processing images using Google's Gemini API and Cloud Vision
    with Google Cloud Storage integration
    """
    
    def __init__(self, project_id: str = None, location: str = "us-central1", 
                 bucket_name: str = "read-ease"):
        """
        Initialize the Gemini and Vision service
        
        Args:
            project_id: Google Cloud project ID
            location: Google Cloud location
            bucket_name: GCS bucket name
        """
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT')
        self.location = location
        self.bucket_name = bucket_name
        
        # Initialize Vision client
        self.vision_client = vision.ImageAnnotatorClient()
        
        # Initialize Storage client
        self.storage_client = storage.Client()
        
        # Initialize Vertex AI for Gemini
        if self.project_id:
            vertexai.init(project=self.project_id, location=self.location)
        else:
            print("Warning: Project ID not provided. Some functionality may be limited.")
            
        # Ensure bucket exists
        try:
            self._ensure_bucket_exists()
        except Exception as e:
            print(f"Warning: Could not create/verify bucket: {str(e)}")
    
    def _ensure_bucket_exists(self):
        """Ensure the GCS bucket exists, create it if it doesn't"""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            if not bucket.exists():
                bucket = self.storage_client.create_bucket(
                    self.bucket_name, 
                    location=self.location
                )
                print(f"Bucket {self.bucket_name} created.")
            return bucket
        except Exception as e:
            print(f"Error ensuring bucket exists: {str(e)}")
            raise
    
    def upload_to_gcs(self, image_data: bytes, filename: str = None) -> str:
        """
        Upload an image to Google Cloud Storage
        
        Args:
            image_data: Raw bytes of the image file
            filename: Optional filename, if None a timestamp will be used
            
        Returns:
            str: Public URL of the uploaded file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"image_{timestamp}.jpg"
                
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(filename)
            blob.upload_from_string(image_data, content_type="image/jpeg")
            
            # Make the blob publicly readable
            blob.make_public()
            
            return blob.public_url
        except Exception as e:
            print(f"Error uploading to GCS: {str(e)}")
            raise Exception(f"Failed to upload image to GCS: {str(e)}")
    
    def process_image(self, image_data: bytes, text_to_speech_service: TextToSpeechService=None) -> Dict:
        """
        Process an image with both Gemini and Vision API
        
        Args:
            image_data: Raw bytes of the image file
            text_to_speech_service: Optional service for text-to-speech conversion
            
        Returns:
            Dict containing extracted text with formatting, explanation, and URLs
        """
        try:
            # Upload image to GCS
            gcs_url = self.upload_to_gcs(image_data)
            
            # Process with Vision API for OCR
            ocr_result = self._extract_text_with_vision(image_data)
            
            # Process with Gemini for explanation
            gemini_result = self._analyze_with_gemini(image_data, ocr_result['full_text'])
            
            # Generate audio URL if text_to_speech_service is provided
            audio_url = ""
            if text_to_speech_service and 'explanation' in gemini_result:
                audio_url = text_to_speech_service.convert_text_to_speech(text=gemini_result['explanation'], voice="en-IN-Chirp-HD-F", language_code="en-IN")
            
            # Combine results
            result = {
                'image_url': gcs_url,
                'audio_path': audio_url,
                'confidence_score': ocr_result.get('confidence_score', 0.9),
                'extracted_text': ocr_result.get('full_text', ''),
                'gemini_response': gemini_result.get('gemini_response', ''),
                'explanation': gemini_result.get('explanation', ''),
            }
            
            return result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to process image: {str(e)}")
    
    def _extract_text_with_vision(self, image_data: bytes) -> Dict:
        """
        Extract text from image using Vision API
        
        Args:
            image_data: Raw bytes of the image file
            
        Returns:
            Dict containing extracted text with formatting
        """
        try:
            # Create image object
            image = vision.Image(content=image_data)
            
            # Perform OCR using document_text_detection for better results
            response = self.vision_client.document_text_detection(image=image)
            
            if response.error.message:
                raise Exception(f"Error from Vision API: {response.error.message}")
            
            # Extract the full text
            full_text = response.full_text_annotation.text
            
            # Extract text blocks with positions
            text_blocks = []
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    block_text = ""
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            word_text = ''.join([symbol.text for symbol in word.symbols])
                            block_text += word_text + " "
                    
                    if block_text.strip():
                        text_blocks.append({
                            'text': block_text.strip(),
                            'bounding_box': [(vertex.x, vertex.y) for vertex in block.bounding_box.vertices],
                            'confidence': block.confidence
                        })
            
            return {
                'full_text': full_text,
                'text_blocks': text_blocks,
                'confidence_score': response.full_text_annotation.pages[0].blocks[0].confidence if response.full_text_annotation.pages and response.full_text_annotation.pages[0].blocks else 0.9
            }
            
        except Exception as e:
            print(f"Error in Vision API text extraction: {str(e)}")
            return {
                'full_text': '',
                'text_blocks': [],
                'confidence_score': 0
            }
    
    def _analyze_with_gemini(self, image_data: bytes, extracted_text: str = "") -> Dict:
        """
        Analyze image with Gemini for explanation and context
        
        Args:
            image_data: Raw bytes of the image file
            extracted_text: Text already extracted by Vision API
            
        Returns:
            Dict containing Gemini's analysis
        """
        try:
            # Initialize the Gemini model
            model = GenerativeModel("gemini-pro-vision")
            
            # Create prompt with extracted text if available
            context = f"The OCR system extracted the following text:\n{extracted_text}\n\n" if extracted_text else ""
            
            prompt = (
                f"{context}Please analyze this image and provide the following:\n"
                "1. A brief explanation of what the image shows\n"
                "2. Any additional context that might be relevant\n"
                "3. Any formatting or layout observations\n\n"
                "Format your response like this:\n"
                "EXPLANATION: [your explanation]\n"
                "CONTEXT: [additional context]\n"
                "LAYOUT: [layout observations]"
            )

            # Convert image to multipart
            image_part = Part.from_data(
                data=image_data,
                mime_type="image/jpeg"
            )
            
            # Generate response
            response = model.generate_content([prompt, image_part])
            
            # Parse response
            full_response = response.text if hasattr(response, 'text') else str(response)
            
            # Extract sections
            explanation = "No explanation provided."
            context = "No additional context provided."
            layout = "No layout information provided."
            
            if "EXPLANATION:" in full_response:
                parts = full_response.split("EXPLANATION:")[1].split("CONTEXT:") if "CONTEXT:" in full_response else [full_response.split("EXPLANATION:")[1]]
                explanation = parts[0].strip()
            
            if "CONTEXT:" in full_response:
                parts = full_response.split("CONTEXT:")[1].split("LAYOUT:") if "LAYOUT:" in full_response else [full_response.split("CONTEXT:")[1]]
                context = parts[0].strip()
            
            if "LAYOUT:" in full_response:
                layout = full_response.split("LAYOUT:")[1].strip()
            
            return {
                'explanation': explanation,
                'context': context,
                'layout': layout,
                'gemini_response': full_response
            }
            
        except Exception as e:
            print(f"Error in Gemini analysis: {str(e)}")
            return {
                'explanation': f"Error analyzing image: {str(e)}",
                'context': '',
                'layout': '',
                'gemini_response': ''
            }