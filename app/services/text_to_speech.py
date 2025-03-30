from typing import Optional
import uuid
from google.cloud import texttospeech, storage

class TextToSpeechService:
    """
    Service for converting text to speech using Google Cloud Text-to-Speech
    """
    
    def __init__(self, bucket_name="read-ease"):
        """
        Initialize the service with Google Cloud clients
        
        Args:
            bucket_name: The name of the Google Cloud Storage bucket to use
        """
        self.tts_client = texttospeech.TextToSpeechClient()
        self.storage_client = storage.Client()
        self.bucket_name = bucket_name
    
    def convert_text_to_speech(
        self, 
        text: str, 
        voice: str = "default",
        rate: float = 1.0,
        output_filename: Optional[str] = None,
        language_code:str = "en-IN"
    ) -> str:
        """
        Convert text to speech using Google Cloud Text-to-Speech and upload directly to Cloud Storage.
        
        Args:
            text: The text to convert to speech
            voice: The voice ID to use
            rate: The speaking rate
            output_filename: Optional filename for the output file. If not provided, a random UUID will be used.
            
        Returns:
            The public URL of the uploaded audio file
        """
        try:
            # Ensure a valid voice ID
            if not voice or voice == "default":
                voice = "en-IN-Chirp-HD-F"  # Default to a specific voice ID if none is provided

            # Create synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)

            print("Converting text to speech...", text, synthesis_input)
            
            # Configure voice
            voice_params = texttospeech.VoiceSelectionParams(
                language_code=language_code, 
                name=voice,  # Use the corrected voice ID
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            
            # Configure audio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=rate
            )
            
            # Generate speech
            response = self.tts_client.synthesize_speech(
                input=synthesis_input, 
                voice=voice_params, 
                audio_config=audio_config
            )
            
            # Generate random filename if not provided
            if not output_filename:
                output_filename = f"{uuid.uuid4()}.mp3"
            
            # Ensure path includes the required folder structure
            storage_path = f"generated/audio/{output_filename}"
            
            # Upload directly to Google Cloud Storage without saving locally
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(storage_path)
            
            # Upload the audio content directly from memory
            blob.upload_from_string(
                response.audio_content,
                content_type="audio/mp3"
            )
            
            # Make the file public
            blob.make_public()
            
            # Return the public URL
            public_url = blob.public_url
            print(f"Audio uploaded to: {storage_path}")
            print(f"Public URL: {public_url}")
            
            return public_url
            
        except Exception as e:
            # Log the error
            print(f"Error in text-to-speech conversion: {str(e)}")
            raise Exception(f"Failed to convert text to speech: {str(e)}")