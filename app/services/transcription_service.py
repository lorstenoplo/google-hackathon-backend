import os
from typing import Dict, Any, Optional
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import mimetypes

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
            self.gemini_model = GenerativeModel("gemini-2.0-flash-exp")  # Use latest model with video support
        else:
            self.gemini_model = None
            print("Warning: No project_id provided. Direct video processing will be disabled.")
    
    def _is_supported_file(self, file_path: str) -> bool:
        """Check if file is supported by Gemini for processing."""
        # Gemini supports these formats
        supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.m4v',
                           '.mp3', '.wav', '.aac', '.ogg', '.flac', '.m4a']
        return os.path.splitext(file_path)[1].lower() in supported_formats
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type for the file."""
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            return mime_type
        
        # Fallback for common audio/video formats
        ext = os.path.splitext(file_path)[1].lower()
        mime_map = {
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.mkv': 'video/x-matroska',
            '.webm': 'video/webm',
            '.flv': 'video/x-flv',
            '.m4v': 'video/x-m4v',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.aac': 'audio/aac',
            '.ogg': 'audio/ogg',
            '.flac': 'audio/flac',
            '.m4a': 'audio/mp4'
        }
        return mime_map.get(ext, 'application/octet-stream')
    
    def _process_with_gemini_direct(self, file_path: str, prompt: str, **options) -> str:
        """
        Process audio/video directly with Gemini.
        
        Args:
            file_path: Path to the audio/video file
            prompt: Prompt for Gemini
            **options: Additional options
            
        Returns:
            Generated response text
        """
        if not self.gemini_model:
            raise Exception("Gemini model not initialized. Please provide project_id during initialization.")
        
        try:
            # Read the media file
            with open(file_path, 'rb') as f:
                media_data = f.read()
            
            # Get MIME type
            mime_type = self._get_mime_type(file_path)
            
            # Create media part
            media_part = Part.from_data(media_data, mime_type=mime_type)
            
            # Generate content with media and prompt
            response = self.gemini_model.generate_content([media_part, prompt])
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Gemini direct media processing error: {str(e)}")

    
    def transcribe(self, file_path: str, model_size: str = "base", **options) -> Dict[str, Any]:
        """
        Transcribe audio or video file using Gemini directly.
        
        Args:
            file_path: Path to the file to transcribe
            model_size: Ignored (kept for API compatibility)
            **options: Additional options for transcription
            
        Returns:
            Dictionary containing transcription results
        """
        if not self.gemini_model:
            raise Exception("Gemini model not initialized. Please provide project_id during initialization.")
        
        if not self._is_supported_file(file_path):
            supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.m4v',
                               '.mp3', '.wav', '.aac', '.ogg', '.flac', '.m4a']
            return {"error": f"Unsupported file format. Supported formats: {', '.join(supported_formats)}"}
        
        try:
            # Use Gemini directly for transcription
            prompt = """Please provide a complete and accurate transcription of all spoken content in this audio/video file. 
            
            Format the response as follows:
            - Include all dialogue and speech
            - Use proper punctuation and paragraph breaks
            - Indicate speaker changes if multiple speakers are present (e.g., Speaker 1:, Speaker 2:)
            - Do not include descriptions of visual elements or background sounds, only transcribe the spoken words
            - If there are multiple languages, transcribe each in their original language
            
            Transcription:"""
            
            transcript_text = self._process_with_gemini_direct(file_path, prompt, **options)
            
            # Format response to match expected output structure
            response = {
                "transcript": transcript_text.strip(),
                "segments": [],  # Gemini doesn't provide timing segments
                "language": options.get("language", "auto-detected"),
                "method": "gemini_direct"
            }
            
            # Optionally save transcript to file
            if options.get("save_transcript", False):
                transcript_path = os.path.splitext(file_path)[0] + "_transcript.txt"
                with open(transcript_path, "w", encoding="utf-8") as f:
                    f.write(transcript_text)
                response["transcript_path"] = transcript_path
            
            return response
            
        except Exception as e:
            raise Exception(f"Gemini transcription error: {str(e)}")
    
    def translate(self, file_path: str, model_size: str = "base", **options) -> Dict[str, Any]:
        """
        Translate audio or video file using Gemini directly.
        
        Args:
            file_path: Path to the file to translate
            model_size: Ignored (kept for API compatibility)
            **options: Additional options like target language
            
        Returns:
            Dictionary containing translation results
        """
        if not self.gemini_model:
            raise Exception("Gemini model not initialized. Please provide project_id during initialization.")
        
        if not self._is_supported_file(file_path):
            supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.m4v',
                               '.mp3', '.wav', '.aac', '.ogg', '.flac', '.m4a']
            return {"error": f"Unsupported file format. Supported formats: {', '.join(supported_formats)}"}
        
        target_language = options.get("target_language", "English")
        
        try:
            prompt = f"""Please provide a complete translation of all spoken content in this audio/video file to {target_language}.
            
            Requirements:
            - Translate all dialogue and speech accurately
            - Maintain the meaning and context
            - Use natural, fluent {target_language}
            - Use proper punctuation and paragraph breaks
            - Indicate speaker changes if multiple speakers are present (e.g., Speaker 1:, Speaker 2:)
            - Do not translate background sounds or visual descriptions, only spoken words
            
            Translation:"""
            
            translation_text = self._process_with_gemini_direct(file_path, prompt, **options)
            
            return {
                "transcript": translation_text.strip(),
                "translation": translation_text.strip(),
                "target_language": target_language,
                "segments": [],
                "method": "gemini_direct"
            }
            
        except Exception as e:
            raise Exception(f"Gemini translation error: {str(e)}")
    
    def _generate_summary_with_gemini(self, transcript: str, summary_type: str = "general", **options) -> str:
        """
        Generate summary using Gemini model from transcript text.
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
        Transcribe and summarize content using Gemini directly for videos.
        
        Args:
            file_path: Path to the file to summarize
            model_size: Size of the Whisper model to use (for fallback)
            **options: Additional options for summarization
                - summary_type: "general", "bullet_points", "key_insights", "executive", "detailed", "action_items"
                - use_gemini_direct: Use Gemini directly for video processing (default: True)
                - max_length: Maximum length in words
                - focus_areas: List of areas to focus on
                - target_audience: Target audience for the summary
                - save_summary: Boolean to save summary to file
            
        Returns:
            Dictionary containing transcription and summarization results
        """
        use_gemini_direct = options.get("use_gemini_direct", True)
        summary_type = options.get("summary_type", "general")
        
        # Check if file is video and we should use Gemini directly
        if use_gemini_direct and self.gemini_model:
            try:
                # Build comprehensive prompt for direct video processing
                summary_prompts = {
                    "general": "Please watch this video and provide both a complete transcription and a concise comprehensive summary.",
                    "bullet_points": "Please watch this video and provide both a complete transcription and a bullet-point summary highlighting the main topics.",
                    "key_insights": "Please watch this video and provide both a complete transcription and extract the key insights and important conclusions.",
                    "executive": "Please watch this video and provide both a complete transcription and an executive summary for decision-makers.",
                    "detailed": "Please watch this video and provide both a complete transcription and a detailed summary preserving important context.",
                    "action_items": "Please watch this video and provide both a complete transcription and identify any action items or next steps."
                }
                
                base_prompt = summary_prompts.get(summary_type, summary_prompts["general"])
                
                # Add additional instructions
                additional_instructions = []
                if options.get("max_length"):
                    additional_instructions.append(f"Keep the summary under {options['max_length']} words.")
                if options.get("focus_areas"):
                    focus_list = ", ".join(options["focus_areas"])
                    additional_instructions.append(f"Focus particularly on these areas: {focus_list}")
                if options.get("target_audience"):
                    additional_instructions.append(f"Tailor the summary for: {options['target_audience']}")
                
                full_prompt = base_prompt
                if additional_instructions:
                    full_prompt += " " + " ".join(additional_instructions)
                
                full_prompt += """

Please format your response as follows:
TRANSCRIPTION:
[Complete transcription here]

SUMMARY:
[Summary here]"""
                
                # Process with Gemini directly
                result_text = self._process_with_gemini_direct(file_path, full_prompt, **options)
                
                # Parse the response to extract transcription and summary
                parts = result_text.split("SUMMARY:")
                if len(parts) == 2:
                    transcript_part = parts[0].replace("TRANSCRIPTION:", "").strip()
                    summary_part = parts[1].strip()
                else:
                    # Fallback parsing
                    lines = result_text.split('\n')
                    transcript_lines = []
                    summary_lines = []
                    current_section = "transcript"
                    
                    for line in lines:
                        if "SUMMARY" in line.upper():
                            current_section = "summary"
                            continue
                        elif "TRANSCRIPTION" in line.upper():
                            current_section = "transcript"
                            continue
                        
                        if current_section == "transcript":
                            transcript_lines.append(line)
                        else:
                            summary_lines.append(line)
                    
                    transcript_part = '\n'.join(transcript_lines).strip()
                    summary_part = '\n'.join(summary_lines).strip()
                
                response = {
                    "transcript": transcript_part,
                    "summary": summary_part,
                    "summary_type": summary_type,
                    "language": "auto-detected",
                    "segments": [],
                    "method": "gemini_direct"
                }
                
                # Optionally save summary to file
                if options.get("save_summary", False):
                    summary_path = os.path.splitext(file_path)[0] + f"_summary_{summary_type}.txt"
                    with open(summary_path, "w", encoding="utf-8") as f:
                        f.write(f"Summary Type: {summary_type}\n")
                        f.write("="*50 + "\n\n")
                        f.write(summary_part)
                        f.write(f"\n\n{'='*50}\n")
                        f.write("Original Transcript:\n")
                        f.write(transcript_part)
                    response["summary_path"] = summary_path
                
                return response
                
            except Exception as e:
                print(f"Gemini direct summarization failed: {e}")
                print("Falling back to traditional transcription + summarization...")
                # Fall back to traditional method
                pass
        
        # Traditional method: First transcribe, then summarize
        transcription_result = self.transcribe(file_path, model_size, **options)
        
        if "error" in transcription_result:
            return transcription_result
        
        try:
            # Generate summary using Gemini
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
                "segments": transcription_result.get("segments", []),
                "method": transcription_result.get("method", "whisper") + "_+_gemini_summary"
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
                "segments": transcription_result.get("segments", []),
                "method": transcription_result.get("method", "whisper")
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
        if os.path.exists(self.temp_dir):
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")