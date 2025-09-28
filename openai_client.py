"""
OpenAI Client - Fallback for when Gemini fails
"""

import os
import openai
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class OpenAIClient:
    """OpenAI client as fallback for Gemini"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        load_dotenv()
        
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize OpenAI client
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        print(f"✅ OpenAI client initialized with model: {self.model}")
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI"""
        try:
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 1000)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise RuntimeError(f"OpenAI error: {str(e)}")
    
    def analyze_image_urls(self, image_urls: list, analysis_prompt: str) -> str:
        """Analyze multiple image URLs with OpenAI Vision"""
        try:
            # Create content with text and images
            content = [{"type": "text", "text": analysis_prompt}]
            
            # Add up to 4 images (OpenAI limit)
            for url in image_urls[:4]:
                if url and not url.startswith('https://via.placeholder.com'):
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": url}
                    })
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Vision model
                messages=[{"role": "user", "content": content}],
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Image analysis failed: {str(e)}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model info"""
        return {
            'model_name': self.model,
            'api_key_set': bool(self.api_key),
            'provider': 'OpenAI'
        }
