import json
import os
import sys
import asyncio
import logging
from pathlib import Path
from playwright.async_api import async_playwright
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from typing import Dict, List, Any, Optional

# Fix for Windows Playwright subprocess issue
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccessibilityService:
    def __init__(self):
        self.axe_script_path = self._get_axe_script_path()
        self._load_summarization_model()
        self._playwright_context = None
    
    def _get_axe_script_path(self) -> str:
        """Get the path to axe.min.js in the project root"""
        project_root = Path(__file__).parent.parent
        axe_path = project_root / "axe.min.js"
        
        if not axe_path.exists():
            raise FileNotFoundError(f"axe.min.js not found at {axe_path}")
        
        return str(axe_path)
    
    def _load_summarization_model(self):
        """Load T5-small model for summarization"""
        try:
            self.model_name = "t5-small"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = self.model.to(self.device)
            logger.info(f"Model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    async def _get_playwright_context(self):
        """Get or create playwright context"""
        if self._playwright_context is None:
            self._playwright_context = await async_playwright().start()
        return self._playwright_context
    
    async def run_accessibility_check(self, url: str) -> Dict[str, Any]:
        """
        Run accessibility check on the given URL
        
        Args:
            url: The website URL to check
            
        Returns:
            Dictionary containing accessibility report
        """
        browser = None
        page = None
        
        try:
            # Use a new playwright instance for each request
            p = await async_playwright().start()
            
            try:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']  # Additional Windows compatibility
                )
                page = await browser.new_page()
                
                # Set user agent to avoid detection
                await page.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                
                # Set longer timeout and better error handling
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    logger.info(f"Successfully loaded page: {url}")
                except Exception as e:
                    logger.error(f"Failed to load the page {url}: {e}")
                    return {}
                
                # Wait a bit for dynamic content
                await page.wait_for_timeout(2000)
                
                # Load and inject axe script
                try:
                    with open(self.axe_script_path, "r", encoding="utf-8") as f:
                        axe_script = f.read()
                    await page.add_script_tag(content=axe_script)
                    logger.info("Axe script injected successfully")
                    
                    # Wait for axe to be ready
                    await page.wait_for_function("typeof window.axe !== 'undefined'", timeout=5000)
                except Exception as e:
                    logger.error(f"Failed to load axe script: {e}")
                    return {}
                
                # Run axe accessibility check with timeout
                try:
                    result = await asyncio.wait_for(
                        page.evaluate("""
                            async () => {
                                if (typeof window.axe === 'undefined') {
                                    return null;
                                }
                                try {
                                    return await window.axe.run();
                                } catch (error) {
                                    console.error('Axe error:', error);
                                    return null;
                                }
                            }
                        """),
                        timeout=30.0
                    )
                    logger.info("Accessibility check completed")
                    return result if result else {}
                except asyncio.TimeoutError:
                    logger.error("Axe accessibility check timed out")
                    return {}
                except Exception as e:
                    logger.error(f"Error running axe check: {e}")
                    return {}
                    
            finally:
                # Cleanup browser and playwright
                try:
                    if page:
                        await page.close()
                    if browser:
                        await browser.close()
                    await p.stop()
                    logger.info("Browser and playwright resources cleaned up")
                except Exception as e:
                    logger.error(f"Error during cleanup: {e}")
                    
        except Exception as e:
            logger.error(f"Unexpected error in accessibility check: {e}")
            return {}
    
    async def generate_summary(self, violations: List[Dict[str, Any]]) -> str:
        """
        Generate AI summary of accessibility violations
        
        Args:
            violations: List of violation dictionaries
            
        Returns:
            Summarized text of violations
        """
        if not violations:
            return "✅ No accessibility violations were found."
        
        try:
            # Prepare input chunks
            CHUNK_SIZE = 512
            input_chunks = []
            current_chunk = ""
            
            for v in violations:
                text = (
                    f"Violation ID: {v.get('id', 'unknown')}\n"
                    f"Description: {v.get('description', 'No description')}\n"
                    f"Impact: {v.get('impact', 'unknown')}\n"
                    f"Help: {v.get('help', 'No help available')}\n"
                    f"Affected Elements: {len(v.get('nodes', []))}\n\n"
                )
                
                if len(current_chunk) + len(text) > CHUNK_SIZE:
                    if current_chunk:  # Only add non-empty chunks
                        input_chunks.append(current_chunk)
                    current_chunk = text
                else:
                    current_chunk += text
            
            if current_chunk:
                input_chunks.append(current_chunk)
            
            # Generate summaries for each chunk
            summaries = []
            
            for i, chunk in enumerate(input_chunks):
                try:
                    input_text = "summarize: " + chunk.strip()
                    inputs = self.tokenizer.encode(
                        input_text, 
                        return_tensors="pt", 
                        max_length=512, 
                        truncation=True
                    ).to(self.device)
                    
                    with torch.no_grad():  # Save memory
                        summary_ids = self.model.generate(
                            inputs,
                            max_length=150,
                            min_length=30,
                            length_penalty=2.0,
                            num_beams=4,
                            early_stopping=True,
                        )
                    
                    summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                    summaries.append(summary)
                    logger.info(f"Generated summary for chunk {i+1}/{len(input_chunks)}")
                    
                except Exception as e:
                    logger.error(f"Error generating summary for chunk {i+1}: {e}")
                    summaries.append(f"Error generating summary for part {i+1}")
            
            return "\n\n".join(summaries)
            
        except Exception as e:
            logger.error(f"Error in generate_summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._playwright_context:
            await self._playwright_context.stop()