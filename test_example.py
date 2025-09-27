#!/usr/bin/env python3
"""
AI Voyage Assistant - Test Examples
Demonstrates the functionality of the voyage assistant.
"""

import os
from dotenv import load_dotenv
from agent import create_voyage_assistant

def check_requirements():
    """Check if requirements are installed"""
    try:
        import streamlit
        import langchain
        import requests
        import bs4
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def test_basic_functionality():
    """Test basic functionality without API calls"""
    print("🧪 Testing AI Voyage Assistant Basic Functionality")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment")
        print("Please create a .env file with your OpenAI API key")
        return False
    
    try:
        # Create assistant
        print("1. Creating assistant...")
        assistant = create_voyage_assistant()
        print("✅ Assistant created successfully")
        
        # Test conversation history
        print("\n2. Testing conversation history...")
        history = assistant.get_conversation_history()
        print(f"✅ Initial history length: {len(history)}")
        
        # Test memory reset
        print("\n3. Testing memory reset...")
        assistant.reset_conversation()
        print("✅ Memory reset successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_with_sample_queries():
    """Test with sample queries (requires API key and internet)"""
    print("\n🌍 Testing with Sample Queries")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Skipping API tests - no OpenAI API key")
        return
    
    try:
        # Create assistant
        assistant = create_voyage_assistant()
        
        # Sample queries to test
        sample_queries = [
            "Hello! I'm planning a trip to Paris. Can you help?",
            "What are some good hotels in Tokyo under $150?",
            "I need flights from New York to London"
        ]
        
        for i, query in enumerate(sample_queries, 1):
            print(f"\n{i}. Testing query: '{query}'")
            try:
                response = assistant.chat(query)
                print(f"✅ Response received ({len(response)} characters)")
                print(f"Preview: {response[:100]}...")
            except Exception as e:
                print(f"❌ Query failed: {e}")
        
        # Test conversation history
        history = assistant.get_conversation_history()
        print(f"\n✅ Final conversation history: {len(history)} messages")
        
    except Exception as e:
        print(f"❌ Error in API tests: {e}")

def test_individual_tools():
    """Test individual tools without the agent"""
    print("\n🔧 Testing Individual Tools")
    print("=" * 50)
    
    try:
        from tools import search_hotels, search_flights, search_travel_info
        
        print("1. Testing hotel search tool...")
        # This will test the tool structure but may not return results without proper setup
        try:
            result = search_hotels("test query")
            print(f"✅ Hotel search tool callable (returned {len(result)} characters)")
        except Exception as e:
            print(f"⚠️ Hotel search tool error: {e}")
        
        print("\n2. Testing flight search tool...")
        try:
            result = search_flights("test query")
            print(f"✅ Flight search tool callable (returned {len(result)} characters)")
        except Exception as e:
            print(f"⚠️ Flight search tool error: {e}")
        
        print("\n3. Testing travel info tool...")
        try:
            result = search_travel_info("test query")
            print(f"✅ Travel info tool callable (returned {len(result)} characters)")
        except Exception as e:
            print(f"⚠️ Travel info tool error: {e}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")

def main():
    """Run all tests"""
    print("🧪 AI VOYAGE ASSISTANT - TEST SUITE")
    print("=" * 60)
    
    # Check requirements first
    if not check_requirements():
        print("\n💡 Run: python start.py install")
        return
    
    # Basic functionality test
    basic_success = test_basic_functionality()
    
    # Individual tools test
    test_individual_tools()
    
    # API tests (only if basic tests pass)
    if basic_success:
        test_with_sample_queries()
    
    print("\n" + "=" * 60)
    print("🏁 Test suite completed!")
    print("\nNext steps:")
    print("1. Run 'streamlit run app.py' for the web interface")
    print("2. Run 'python cli.py' for the command line interface")
    print("3. Check README.md for detailed usage instructions")

if __name__ == "__main__":
    main()
