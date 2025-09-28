#!/usr/bin/env python3
"""
Test script for AI fallback system
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_client():
    """Test Gemini client"""
    try:
        from gemini_client import GeminiClient
        client = GeminiClient()
        
        print("🤖 Testing Gemini client...")
        response = client.generate_text("Say hello in one sentence")
        print(f"✅ Gemini response: '{response}' ({len(response)} chars)")
        return len(response.strip()) > 0
        
    except Exception as e:
        print(f"❌ Gemini failed: {e}")
        return False

def test_openai_client():
    """Test OpenAI client"""
    try:
        from openai_client import OpenAIClient
        client = OpenAIClient()
        
        print("🤖 Testing OpenAI client...")
        response = client.generate_text("Say hello in one sentence")
        print(f"✅ OpenAI response: '{response}' ({len(response)} chars)")
        return len(response.strip()) > 0
        
    except Exception as e:
        print(f"❌ OpenAI failed: {e}")
        return False

def test_smart_fallback():
    """Test smart fallback system"""
    try:
        # Import the smart function from the web app
        sys.path.append('.')
        from multimedia_web_app import smart_generate_text
        
        print("🧠 Testing smart fallback system...")
        response = smart_generate_text("Write a short sentence about Paris")
        print(f"✅ Smart fallback response: '{response}' ({len(response)} chars)")
        return len(response.strip()) > 0
        
    except Exception as e:
        print(f"❌ Smart fallback failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AI Fallback System Test")
    print("=" * 50)
    
    # Check environment variables
    gemini_key = os.getenv('GEMINI_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"🔑 GEMINI_API_KEY: {'✅ Set' if gemini_key else '❌ Missing'}")
    print(f"🔑 OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Missing'}")
    print()
    
    # Test individual clients
    gemini_works = test_gemini_client()
    openai_works = test_openai_client()
    
    print()
    print("📊 Client Status:")
    print(f"   Gemini: {'✅ Working' if gemini_works else '❌ Failed'}")
    print(f"   OpenAI: {'✅ Working' if openai_works else '❌ Failed'}")
    
    # Test smart fallback
    print()
    smart_works = test_smart_fallback()
    
    print()
    print("🎯 Final Results:")
    if smart_works:
        print("✅ Smart fallback system is working!")
        if gemini_works and openai_works:
            print("🚀 Both AI providers available - maximum reliability!")
        elif gemini_works:
            print("🤖 Gemini primary, no OpenAI fallback")
        elif openai_works:
            print("🔄 OpenAI fallback active (Gemini issues)")
        else:
            print("⚠️ Fallback working but both clients have issues")
    else:
        print("❌ Smart fallback system failed!")
        print("💡 Check your API keys and network connection")

if __name__ == "__main__":
    main()
