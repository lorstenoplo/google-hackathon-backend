import os
import subprocess
import whisper
from typing import Dict, Any, Optional
import vertexai
from vertexai.generative_models import GenerativeModel

class ProcessingService:
    """Service for processing different types of media files."""
    
    def __init__(self, project_id: str = "", location: str = "us-central1"):
        """Initialize processing service."""
        self.temp_dir = "temp_files"
        os.makedirs(self.temp_dir, exist_ok=True)

        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT')
        self.location = location
        
        # Initialize Vertex AI
        if self.project_id:
            vertexai.init(project=self.project_id, location=self.location)
            self.gemini_model = GenerativeModel("gemini-2.5-flash-preview-05-20")
        else:
            self.gemini_model = None
            print("Warning: No project_id provided. Summarization will be disabled.")
    
    def extract_audio(self, file_path: str, audio_format: str = "wav") -> Optional[str]:
        """
        Extract audio from video file.
        
        Args:
            file_path: Path to the video file
            audio_format: Output audio format (default: wav)
            
        Returns:
            Path to the extracted audio file, or None if extraction failed
        """
        # Create unique temp filename
        filename = os.path.basename(file_path)
        base_name = os.path.splitext(filename)[0]
        audio_path = f"{self.temp_dir}/{base_name}_audio.{audio_format}"
        
        try:
            subprocess.run([
                "ffmpeg", "-y", "-i", file_path,
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return audio_path
        except subprocess.CalledProcessError as e:
            print(f"Error extracting audio: {e}")
            return None
    
    def transcribe(self, file_path: str, model_size: str = "base", **options) -> Dict[str, Any]:
        """
        Transcribe audio or video file.
        
        Args:
            file_path: Path to the file to transcribe
            model_size: Size of the Whisper model to use (tiny, base, small, medium, large)
            **options: Additional options for transcription
            
        Returns:
            Dictionary containing transcription results
        """
        # Check if file is video or audio
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Video formats that need audio extraction
        video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        
        if file_ext in video_formats:
            # Extract audio first
            audio_path = self.extract_audio(file_path)
            if not audio_path:
                return {"error": "Failed to extract audio from video"}
        else:
            # Assume file is already audio
            audio_path = file_path
        
        try:
            # Load whisper model
            model = whisper.load_model(model_size)
            
            # Process transcription
            transcription_options = {
                "language": options.get("language", None),
                "task": options.get("task", "transcribe"),
            }
            
            # Filter None values
            transcription_options = {k: v for k, v in transcription_options.items() if v is not None}
            
            # Run transcription
            result = model.transcribe(audio_path, **transcription_options)
            
            # Clean up temp file if it was created
            if audio_path != file_path and os.path.exists(audio_path):
                os.remove(audio_path)
            
            # Format response
            response = {
                "transcript": result["text"],
                "segments": result.get("segments", []),
                "language": result.get("language", None),
            }
            
            # Optionally save transcript to file
            if options.get("save_transcript", False):
                transcript_path = os.path.splitext(file_path)[0] + "_transcript.txt"
                with open(transcript_path, "w", encoding="utf-8") as f:
                    f.write(result["text"])
                response["transcript_path"] = transcript_path
            
            return response
        
        except Exception as e:
            # Ensure cleanup even on error
            if audio_path != file_path and os.path.exists(audio_path):
                os.remove(audio_path)
            raise Exception(f"Transcription error: {str(e)}")
    
    def translate(self, file_path: str, model_size: str = "base", **options) -> Dict[str, Any]:
        """
        Translate audio or video file.
        
        Args:
            file_path: Path to the file to translate
            model_size: Size of the Whisper model to use
            **options: Additional options like target language
            
        Returns:
            Dictionary containing translation results
        """
        # Set task to translate
        options["task"] = "translate"
        
        # Reuse transcription logic but with translate task
        return self.transcribe(file_path, model_size, **options)
    
    def _generate_summary_with_gemini(self, transcript: str, summary_type: str = "general", **options) -> str:
        """
        Generate summary using Gemini model.
        
        Args:
            transcript: Text to summarize
            summary_type: Type of summary (general, bullet_points, key_insights, etc.)
            **options: Additional options like max_length, focus_areas
            
        Returns:
            Generated summary text
        """
        if not self.gemini_model:
            raise Exception("Gemini model not initialized. Please provide project_id during initialization.")
        
        # Build prompt based on summary type
        prompts = {
            "general": "Please provide a concise and comprehensive summary of the following transcript:",
            "bullet_points": "Please summarize the following transcript in bullet points, highlighting the main topics and key information:",
            "key_insights": "Please extract the key insights, main arguments, and important conclusions from the following transcript:",
            "executive": "Please provide an executive summary of the following transcript, focusing on the main points that would be relevant for decision-makers:",
            "detailed": "Please provide a detailed summary of the following transcript, preserving important context and nuances:",
            "action_items": "Please identify and summarize any action items, decisions, or next steps mentioned in the following transcript:"
        }
        
        base_prompt = prompts.get(summary_type, prompts["general"])
        
        # Add additional instructions based on options
        additional_instructions = []
        
        if options.get("max_length"):
            additional_instructions.append(f"Keep the summary under {options['max_length']} words.")
        
        if options.get("focus_areas"):
            focus_list = ", ".join(options["focus_areas"])
            additional_instructions.append(f"Focus particularly on these areas: {focus_list}")
        
        if options.get("target_audience"):
            additional_instructions.append(f"Tailor the summary for: {options['target_audience']}")
        
        # Construct final prompt
        full_prompt = base_prompt
        if additional_instructions:
            full_prompt += " " + " ".join(additional_instructions)
        
        full_prompt += f"\n\nTranscript:\n{transcript}"
        
        try:
            response = self.gemini_model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini summarization error: {str(e)}")
    
    def summarize(self, file_path: str, model_size: str = "base", **options) -> Dict[str, Any]:
        """
        Transcribe and then summarize content using Gemini.
        
        Args:
            file_path: Path to the file to summarize
            model_size: Size of the Whisper model to use
            **options: Additional options for summarization
                - summary_type: "general", "bullet_points", "key_insights", "executive", "detailed", "action_items"
                - max_length: Maximum length in words
                - focus_areas: List of areas to focus on
                - target_audience: Target audience for the summary
                - save_summary: Boolean to save summary to file
            
        Returns:
            Dictionary containing transcription and summarization results
        """
        # First transcribe the content
        transcription_result = self.transcribe(file_path, model_size, **options)
        
        if "error" in transcription_result:
            return transcription_result
        
        try:
            # Generate summary using Gemini
            summary_type = options.get("summary_type", "general")
            summary = self._generate_summary_with_gemini(
                transcription_result["transcript"], 
                summary_type, 
                **options
            )
            
            response = {
                "transcript": transcription_result["transcript"],
                "summary": summary,
                "summary_type": summary_type,
                "language": transcription_result.get("language"),
                "segments": transcription_result.get("segments", [])
            }
            
            # Optionally save summary to file
            if options.get("save_summary", False):
                summary_path = os.path.splitext(file_path)[0] + f"_summary_{summary_type}.txt"
                with open(summary_path, "w", encoding="utf-8") as f:
                    f.write(f"Summary Type: {summary_type}\n")
                    f.write("="*50 + "\n\n")
                    f.write(summary)
                    f.write(f"\n\n{'='*50}\n")
                    f.write("Original Transcript:\n")
                    f.write(transcription_result["transcript"])
                response["summary_path"] = summary_path
            
            return response
            
        except Exception as e:
            return {
                "transcript": transcription_result["transcript"],
                "error": f"Summarization failed: {str(e)}",
                "language": transcription_result.get("language"),
                "segments": transcription_result.get("segments", [])
            }
    
    def batch_summarize(self, file_paths: list, model_size: str = "base", **options) -> Dict[str, Any]:
        """
        Summarize multiple files.
        
        Args:
            file_paths: List of file paths to process
            model_size: Whisper model size
            **options: Summarization options
            
        Returns:
            Dictionary with results for each file
        """
        results = {}
        for file_path in file_paths:
            try:
                result = self.summarize(file_path, model_size, **options)
                results[file_path] = result
            except Exception as e:
                results[file_path] = {"error": str(e)}
        
        return results
    
    def cleanup(self):
        """Clean up temporary files."""
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")