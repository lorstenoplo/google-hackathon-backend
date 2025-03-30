from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
from typing import Optional

class GeminiSpellCorrectService:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini Service for grammar and spelling correction.
        
        Args:
            api_key: The Google API key for Gemini access. If None, tries to get from environment.
        """
        # Get API key from parameters or environment variables
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("Gemini API key is required. Provide it as a parameter or set GEMINI_API_KEY environment variable.")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-1.5-flash')  
          
    async def correct_text(self, text: str) -> str:
        """
        Correct only spelling and grammatical errors in the given text.
        
        Args:
            text: The text to be corrected.
            
        Returns:
            The corrected text with only spelling and grammar fixes.
        """
        if not text.strip():
            return text
        
        # Create a prompt that specifically asks to only fix spelling and grammar
        prompt = f"""
        Please correct ONLY spelling and grammatical errors in the following text. 
        Do not change the meaning, style, tone, vocabulary level, or any other aspects of the text.
        Do not add or remove information.
        Do not rewrite sentences for clarity or any other reason unless they contain grammatical errors.
        Only fix objective spelling mistakes and grammatical errors.
        The end-user is dyslexic and needs the text to be corrected without changing the meaning, style, tone, or vocabulary level.
        The model should not rewrite sentences for clarity or any other reason unless they contain grammatical errors.
        
        Here is the text to correct:
        
        {text}
        
        Return ONLY the corrected text with no explanations, comments, or other additions.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            corrected_text = response.text.strip()
            return corrected_text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
