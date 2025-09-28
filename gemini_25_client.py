"""
Gemini 2.5 Pro Client
Enhanced client for Gemini 2.5 Pro with thinking mode, Google Search, and streaming
"""

import os
import base64
from typing import Optional, Dict, Any, List, Generator, Union
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv


class Gemini25Client:
    """Enhanced client for Gemini 2.5 Pro with advanced features"""
    
    def __init__(self):
        """Initialize the Gemini 2.5 Pro client"""
        # Load environment variables
        load_dotenv()
        
        # Get configuration from environment
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-pro')
        self.thinking_budget = int(os.getenv('GEMINI_THINKING_BUDGET', '-1'))
        self.enable_search = os.getenv('GEMINI_ENABLE_SEARCH', 'true').lower() == 'true'
        
        # Validate API key
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please copy .env.example to .env and add your API key."
            )
        
        # Initialize the client
        try:
            self.client = genai.Client(api_key=self.api_key)
            print(f"✅ Successfully initialized Gemini 2.5 Pro client")
            print(f"   Model: {self.model_name}")
            print(f"   Thinking Mode: {'Enabled' if self.thinking_budget != 0 else 'Disabled'}")
            print(f"   Google Search: {'Enabled' if self.enable_search else 'Disabled'}")
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini 2.5 Pro client: {str(e)}")
    
    def _create_content(self, message: str, role: str = "user") -> types.Content:
        """Create a Content object from a message"""
        return types.Content(
            role=role,
            parts=[types.Part.from_text(text=message)]
        )
    
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
    
    def _create_config(self, enable_thinking: bool = True, enable_search: bool = None) -> types.GenerateContentConfig:
        """Create generation configuration with optional thinking and search"""
        config_params = {}
        
        # Add thinking configuration
        if enable_thinking and self.thinking_budget != 0:
            config_params['thinking_config'] = types.ThinkingConfig(
                thinking_budget=self.thinking_budget
            )
        
        # Add tools configuration
        tools = []
        search_enabled = enable_search if enable_search is not None else self.enable_search
        if search_enabled:
            tools.append(types.Tool(googleSearch=types.GoogleSearch()))
        
        if tools:
            config_params['tools'] = tools
        
        return types.GenerateContentConfig(**config_params)
    
    def generate_text(self, prompt: str, enable_thinking: bool = True, 
                     enable_search: bool = None, stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """
        Generate text using Gemini 2.5 Pro
        
        Args:
            prompt (str): The input prompt
            enable_thinking (bool): Enable thinking mode
            enable_search (bool): Enable Google Search (uses default if None)
            stream (bool): Return streaming generator instead of complete text
            
        Returns:
            Union[str, Generator]: Generated text or streaming generator
        """
        try:
            contents = [self._create_content(prompt)]
            config = self._create_config(enable_thinking, enable_search)
            
            if stream:
                return self._generate_stream(contents, config)
            else:
                return self._generate_complete(contents, config)
                
        except Exception as e:
            raise RuntimeError(f"Error generating text: {str(e)}")
    
    def _generate_stream(self, contents: List[types.Content], 
                        config: types.GenerateContentConfig) -> Generator[str, None, None]:
        """Generate streaming response"""
        for chunk in self.client.models.generate_content_stream(
            model=self.model_name,
            contents=contents,
            config=config
        ):
            # Try to extract text from chunk safely
            chunk_text = self._extract_chunk_text(chunk)
            if chunk_text:
                yield chunk_text
    
    def _extract_chunk_text(self, chunk) -> str:
        """
        Safely extract text from a streaming chunk
        
        Args:
            chunk: The streaming chunk from Gemini API
            
        Returns:
            str: Extracted text content
        """
        try:
            # Try the simple accessor first
            if hasattr(chunk, 'text') and chunk.text is not None:
                return chunk.text
        except Exception:
            # If simple accessor fails, use the complex accessor
            pass
        
        # Use the complex accessor for multi-part chunks
        try:
            if hasattr(chunk, 'candidates') and chunk.candidates:
                candidate = chunk.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    text_parts = []
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                    return ''.join(text_parts)
        except Exception:
            # Silently handle streaming chunk extraction errors
            pass
        
        return ""
    
    def _generate_complete(self, contents: List[types.Content], 
                          config: types.GenerateContentConfig) -> str:
        """Generate complete response"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config
        )
        return self._extract_response_text(response)
    
    def chat_conversation(self, messages: List[Dict[str, str]], 
                         enable_thinking: bool = True, enable_search: bool = None,
                         stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """
        Handle multi-turn conversation
        
        Args:
            messages (List[Dict]): List of messages with 'role' and 'content'
            enable_thinking (bool): Enable thinking mode
            enable_search (bool): Enable Google Search
            stream (bool): Return streaming generator
            
        Returns:
            Union[str, Generator]: Response or streaming generator
        """
        try:
            contents = []
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                contents.append(self._create_content(content, role))
            
            config = self._create_config(enable_thinking, enable_search)
            
            if stream:
                return self._generate_stream(contents, config)
            else:
                return self._generate_complete(contents, config)
                
        except Exception as e:
            raise RuntimeError(f"Error in chat conversation: {str(e)}")
    
    def analyze_with_thinking(self, prompt: str, thinking_budget: int = -1) -> Dict[str, str]:
        """
        Generate response with explicit thinking mode and return both thinking and final answer
        
        Args:
            prompt (str): The input prompt
            thinking_budget (int): Thinking budget (-1 for unlimited)
            
        Returns:
            Dict[str, str]: Dictionary with 'thinking' and 'response' keys
        """
        try:
            contents = [self._create_content(prompt)]
            config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=thinking_budget)
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            
            # Extract thinking and final response
            result = {
                'thinking': '',
                'response': self._extract_response_text(response)
            }
            
            # Try to extract thinking process if available
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'thought') and part.thought:
                            result['thinking'] = part.thought
                            break
                        # Also check for thinking in text format
                        elif hasattr(part, 'text') and part.text and '<thinking>' in part.text:
                            # Extract thinking content between <thinking> tags
                            import re
                            thinking_match = re.search(r'<thinking>(.*?)</thinking>', part.text, re.DOTALL)
                            if thinking_match:
                                result['thinking'] = thinking_match.group(1).strip()
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Error in thinking analysis: {str(e)}")
    
    def search_and_answer(self, query: str, stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """
        Search the web and provide an answer based on search results
        
        Args:
            query (str): Search query
            stream (bool): Return streaming generator
            
        Returns:
            Union[str, Generator]: Answer based on search results
        """
        enhanced_prompt = f"""
        Please search for information about: {query}
        
        Provide a comprehensive answer based on the most recent and reliable information you find.
        Include relevant details and cite sources when possible.
        """
        
        return self.generate_text(
            enhanced_prompt, 
            enable_thinking=True, 
            enable_search=True, 
            stream=stream
        )
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get information about the client configuration"""
        return {
            'model_name': self.model_name,
            'thinking_budget': self.thinking_budget,
            'search_enabled': self.enable_search,
            'api_key_set': bool(self.api_key),
            'features': {
                'thinking_mode': self.thinking_budget != 0,
                'google_search': self.enable_search,
                'streaming': True,
                'multi_turn_chat': True
            }
        }


def main():
    """Main function to demonstrate Gemini 2.5 Pro features"""
    try:
        # Initialize client
        client = Gemini25Client()
        
        # Display client info
        info = client.get_client_info()
        print(f"\n📋 Gemini 2.5 Pro Configuration:")
        print(f"   Model: {info['model_name']}")
        print(f"   Thinking Budget: {info['thinking_budget']}")
        print(f"   Google Search: {info['search_enabled']}")
        print(f"   Features: {', '.join([k for k, v in info['features'].items() if v])}")
        
        # Interactive mode
        print(f"\n🤖 Gemini 2.5 Pro Interactive Mode")
        print("Commands:")
        print("  /think <prompt>  - Use thinking mode")
        print("  /search <query>  - Search and answer")
        print("  /stream <prompt> - Streaming response")
        print("  /quit           - Exit")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['/quit', 'quit', 'exit']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.startswith('/think '):
                    prompt = user_input[7:]
                    print("🧠 Thinking and responding...")
                    result = client.analyze_with_thinking(prompt)
                    if result['thinking']:
                        print(f"\n💭 Thinking: {result['thinking']}")
                    print(f"🤖 Response: {result['response']}")
                
                elif user_input.startswith('/search '):
                    query = user_input[8:]
                    print("🔍 Searching and analyzing...")
                    response = client.search_and_answer(query)
                    print(f"🤖 Answer: {response}")
                
                elif user_input.startswith('/stream '):
                    prompt = user_input[8:]
                    print("🌊 Streaming response:")
                    print("🤖 ", end="", flush=True)
                    for chunk in client.generate_text(prompt, stream=True):
                        print(chunk, end="", flush=True)
                    print()  # New line after streaming
                
                else:
                    # Regular generation
                    print("🤖 Gemini 2.5 Pro: ", end="", flush=True)
                    response = client.generate_text(user_input)
                    print(response)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                
    except Exception as e:
        print(f"❌ Failed to initialize Gemini 2.5 Pro client: {str(e)}")
        print("\n💡 Make sure to:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Gemini API key to the .env file")
        print("   3. Install requirements: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
