from typing import Optional
from google.cloud import texttospeech, storage

class TextToSpeechService:
    """
    Service for converting text to speech using Google Cloud Text-to-Speech
    """
    
    def __init__(self, bucket_name="ttsfile"):
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
        voice: str = "en-US",
        rate: float = 1.0,
        output_filename: Optional[str] = "output.mp3"
    ) -> str:
        """
        Convert text to speech using Google Cloud Text-to-Speech.
        """
        try:
            # Ensure a valid voice ID
            if not voice or voice == "default":
                voice = "en-US-Wavenet-D"  # Change to a valid Google Cloud voice ID

            # Create synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)

            print("Converting text to speech...", text, synthesis_input)
            
            # Configure voice
            voice_params = texttospeech.VoiceSelectionParams(
                language_code="en-US",  # Use appropriate language code
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
            
            # Otherwise, save and upload the file
            with open(output_filename, "wb") as out:
                out.write(response.audio_content)
                
            print(f"Audio saved as {output_filename}")
            
            # Upload to Google Cloud Storage
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(output_filename)
            blob.upload_from_filename(output_filename)
            
            # Make the file public
            blob.make_public()
            
            # Return the public URL
            public_url = blob.public_url
            print(f"Public URL: {public_url}")
            
            return public_url
            
        except Exception as e:
            # Log the error
            print(f"Error in text-to-speech conversion: {str(e)}")
            raise Exception(f"Failed to convert text to speech: {str(e)}")
