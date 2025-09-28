"""
Example usage of the Gemini API client
"""

from gemini_client import GeminiClient


def example_basic_generation():
    """Example of basic text generation"""
    print("🔹 Basic Text Generation Example")
    print("=" * 40)
    
    client = GeminiClient()
    
    prompt = "Explain quantum computing in simple terms"
    response = client.generate_text(prompt)
    
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    print()


def example_creative_writing():
    """Example of creative writing with custom parameters"""
    print("🔹 Creative Writing Example")
    print("=" * 40)
    
    client = GeminiClient()
    
    prompt = "Write a short story about a robot learning to paint"
    response = client.generate_text(
        prompt,
        temperature=0.9,  # Higher creativity
        max_tokens=500
    )
    
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    print()


def example_code_generation():
    """Example of code generation"""
    print("🔹 Code Generation Example")
    print("=" * 40)
    
    client = GeminiClient()
    
    prompt = """
    Write a Python function that:
    1. Takes a list of numbers as input
    2. Returns the sum of all even numbers in the list
    3. Include proper error handling and docstring
    """
    
    response = client.generate_text(
        prompt,
        temperature=0.3  # Lower temperature for more precise code
    )
    
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    print()


def example_chat_conversation():
    """Example of a chat conversation"""
    print("🔹 Chat Conversation Example")
    print("=" * 40)
    
    client = GeminiClient()
    
    messages = [
        {"role": "user", "content": "What are the benefits of renewable energy?"}
    ]
    
    response = client.chat(messages)
    
    print(f"User: {messages[0]['content']}")
    print(f"Gemini: {response}")
    print()


def example_analysis_task():
    """Example of text analysis"""
    print("🔹 Text Analysis Example")
    print("=" * 40)
    
    client = GeminiClient()
    
    text_to_analyze = """
    The quick brown fox jumps over the lazy dog. This sentence contains 
    every letter of the alphabet at least once, making it a pangram.
    """
    
    prompt = f"""
    Analyze the following text and provide:
    1. Word count
    2. Character count (excluding spaces)
    3. Most common words
    4. Any interesting linguistic features
    
    Text: {text_to_analyze}
    """
    
    response = client.generate_text(prompt)
    
    print(f"Text to analyze: {text_to_analyze.strip()}")
    print(f"Analysis: {response}")
    print()


def main():
    """Run all examples"""
    print("🚀 Gemini API Examples")
    print("=" * 50)
    
    try:
        example_basic_generation()
        example_creative_writing()
        example_code_generation()
        example_chat_conversation()
        example_analysis_task()
        
        print("✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
        print("\n💡 Make sure your .env file is properly configured")


if __name__ == "__main__":
    main()
