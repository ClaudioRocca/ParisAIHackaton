"""
Gemini API Client
A simple client for interacting with Google's Gemini AI API
"""

import os
import sys
from typing import Optional, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv


class GeminiClient:
    """Client for interacting with Google's Gemini AI API"""
    
    def _extract_response_text(self, response) -> str:
        """
        Safely extract text from a Gemini response, handling complex responses
        
        Args:
            response: The response object from Gemini API
            
        Returns:
            str: Extracted text content
        """
        try:
            # Try the simple accessor first
            if hasattr(response, 'text') and response.text is not None:
                return response.text
        except Exception:
            # If simple accessor fails, use the complex accessor
            pass
        
        # Use the complex accessor for multi-part responses
        try:
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    text_parts = []
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                    return ''.join(text_parts)
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from response: {str(e)}")
        
        # If all else fails, return empty string
        return ""
    
    def __init__(self):
        """Initialize the Gemini client with environment variables"""
        # Load environment variables
        load_dotenv()
        
        # Get configuration from environment
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')
        self.temperature = float(os.getenv('GEMINI_TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('GEMINI_MAX_TOKENS', '1000'))
        
        # Validate API key
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please copy .env.example to .env and add your API key."
            )
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        try:
            self.model = genai.GenerativeModel(self.model_name)
            print(f"✅ Successfully initialized Gemini model: {self.model_name}")
        except Exception as e:
            raise ValueError(f"Failed to initialize model {self.model_name}: {str(e)}")
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the Gemini model
        
        Args:
            prompt (str): The input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            str: Generated text response
        """
        try:
            # Merge default config with any provided kwargs
            generation_config = {
                'temperature': kwargs.get('temperature', self.temperature),
                'max_output_tokens': kwargs.get('max_tokens', self.max_tokens),
            }
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return self._extract_response_text(response)
            
        except Exception as e:
            raise RuntimeError(f"Error generating text: {str(e)}")
    
    def chat(self, messages: list) -> str:
        """
        Start a chat conversation
        
        Args:
            messages (list): List of message dictionaries with 'role' and 'content'
            
        Returns:
            str: Generated response
        """
        try:
            # Convert messages to Gemini format
            chat = self.model.start_chat(history=[])
            
            # Send the last message and get response
            if messages:
                last_message = messages[-1]['content']
                response = chat.send_message(last_message)
                return self._extract_response_text(response)
            return "No messages provided"
            
        except Exception as e:
            raise RuntimeError(f"Error in chat: {str(e)}")
    
    def analyze_image(self, image_base64: str, mime_type: str, prompt: str) -> str:
        """
        Analyze an image using Gemini's vision capabilities
        
        Args:
            image_base64 (str): Base64 encoded image data
            mime_type (str): MIME type of the image (e.g., 'image/jpeg')
            prompt (str): Analysis prompt for the image
            
        Returns:
            str: Analysis result from Gemini
        """
        try:
            import google.generativeai as genai
            
            # Create image part for Gemini
            image_part = {
                "mime_type": mime_type,
                "data": image_base64
            }
            
            # Generate content with image and text
            response = self.model.generate_content([prompt, image_part])
            
            # Extract text from response
            return self._extract_response_text(response)
            
        except Exception as e:
            raise RuntimeError(f"Error analyzing image: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            'model_name': self.model_name,
            'api_key_set': bool(self.api_key),
            'temperature': self.temperature,
            'max_tokens': self.max_tokens
        }


def main():
    """Main function to demonstrate the Gemini client"""
    try:
        # Initialize client
        client = GeminiClient()
        
        # Display model info
        info = client.get_model_info()
        print(f"\n📋 Model Configuration:")
        print(f"   Model: {info['model_name']}")
        print(f"   Temperature: {info['temperature']}")
        print(f"   Max Tokens: {info['max_tokens']}")
        print(f"   API Key Set: {info['api_key_set']}")
        
        # Interactive mode
        print(f"\n🤖 Gemini AI Chat")
        print("Type 'quit' or 'exit' to end the conversation")
        print("=" * 50)
        
        while True:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Generate response
                print("🤖 Gemini: ", end="", flush=True)
                response = client.generate_text(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                
    except Exception as e:
        print(f"❌ Failed to initialize Gemini client: {str(e)}")
        print("\n💡 Make sure to:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Gemini API key to the .env file")
        print("   3. Install requirements: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
