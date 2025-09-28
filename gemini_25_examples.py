"""
Gemini 2.5 Pro Examples
Examples demonstrating advanced features like thinking mode and Google Search
"""

from gemini_25_client import Gemini25Client
import time


def example_thinking_mode():
    """Example: Using thinking mode for complex reasoning"""
    print("🔹 Thinking Mode Example")
    print("=" * 50)
    
    client = Gemini25Client()
    
    prompt = """
    I have a 3x3 grid puzzle where I need to place numbers 1-9 such that:
    - Each row sums to 15
    - Each column sums to 15
    - Each diagonal sums to 15
    
    This is a magic square. Can you solve it step by step?
    """
    
    try:
        print("🧠 Analyzing with thinking mode...")
        result = client.analyze_with_thinking(prompt)
        
        if result['thinking']:
            print(f"\n💭 Thinking Process:\n{result['thinking']}")
        
        print(f"\n🤖 Final Answer:\n{result['response']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    print()


def example_google_search():
    """Example: Using Google Search for current information"""
    print("🔹 Google Search Integration Example")
    print("=" * 50)
    
    client = Gemini25Client()
    
    queries = [
        "What are the latest developments in quantum computing in 2024?",
        "Current stock price of NVIDIA and recent news",
        "Latest updates on SpaceX Starship missions"
    ]
    
    for query in queries:
        try:
            print(f"\n🔍 Searching: {query}")
            response = client.search_and_answer(query)
            print(f"📊 Answer: {response}")
            print("-" * 40)
            
        except Exception as e:
            print(f"❌ Error: {e}")
    print()


def example_streaming_response():
    """Example: Streaming responses for real-time interaction"""
    print("🔹 Streaming Response Example")
    print("=" * 50)
    
    client = Gemini25Client()
    
    prompt = """
    Write a creative short story about a time traveler who accidentally 
    changes a small detail in the past and discovers how it affects the future. 
    Make it engaging and include dialogue.
    """
    
    try:
        print("🌊 Streaming creative story...")
        print("📖 Story: ", end="", flush=True)
        
        for chunk in client.generate_text(prompt, stream=True):
            print(chunk, end="", flush=True)
            time.sleep(0.01)  # Small delay to show streaming effect
        
        print("\n✅ Story complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    print()


def example_multi_turn_conversation():
    """Example: Multi-turn conversation with context"""
    print("🔹 Multi-turn Conversation Example")
    print("=" * 50)
    
    client = Gemini25Client()
    
    conversation = [
        {"role": "user", "content": "I'm planning a trip to Japan. What are the must-visit places?"},
        {"role": "assistant", "content": "Japan offers incredible experiences! Here are must-visit places:\n\n🏯 **Tokyo**: Modern metropolis with Shibuya, Harajuku, and traditional temples\n🗾 **Kyoto**: Ancient capital with stunning temples like Kinkaku-ji and Fushimi Inari\n🗻 **Mount Fuji**: Iconic mountain, best viewed from Hakone or climbed in summer\n🦌 **Nara**: Historic city with friendly deer in Nara Park\n🏰 **Osaka**: Food paradise and Osaka Castle\n\nWhat type of experiences interest you most - cultural, culinary, or natural?"},
        {"role": "user", "content": "I'm most interested in cultural experiences and traditional architecture. How many days should I spend in Kyoto?"}
    ]
    
    try:
        print("💬 Multi-turn conversation about Japan travel...")
        
        # Show conversation history
        for msg in conversation[:-1]:
            role_emoji = "👤" if msg["role"] == "user" else "🤖"
            print(f"{role_emoji} {msg['role'].title()}: {msg['content'][:100]}...")
        
        print(f"\n👤 User: {conversation[-1]['content']}")
        
        # Generate response
        print("🤖 Gemini 2.5 Pro: ", end="", flush=True)
        response = client.chat_conversation(conversation, enable_thinking=True)
        print(response)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    print()


def example_code_analysis_with_thinking():
    """Example: Code analysis with thinking process"""
    print("🔹 Code Analysis with Thinking Example")
    print("=" * 50)
    
    client = Gemini25Client()
    
    code_prompt = """
    Analyze this Python code and identify potential issues, optimizations, and improvements:
    
    ```python
    def fibonacci(n):
        if n <= 1:
            return n
        else:
            return fibonacci(n-1) + fibonacci(n-2)
    
    # Calculate fibonacci for large numbers
    for i in range(40):
        print(f"fib({i}) = {fibonacci(i)}")
    ```
    
    Consider performance, best practices, and suggest better implementations.
    """
    
    try:
        print("🔍 Analyzing code with thinking mode...")
        result = client.analyze_with_thinking(code_prompt)
        
        if result['thinking']:
            print(f"\n💭 Analysis Process:\n{result['thinking']}")
        
        print(f"\n📝 Code Review:\n{result['response']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    print()


def example_research_with_search():
    """Example: Research task combining thinking and search"""
    print("🔹 Research Task Example")
    print("=" * 50)
    
    client = Gemini25Client()
    
    research_prompt = """
    I need to write a brief report on the environmental impact of electric vehicles 
    compared to traditional gasoline cars. Please research current data and provide:
    
    1. Latest statistics on EV adoption rates
    2. Comparative carbon footprint analysis
    3. Battery recycling challenges and solutions
    4. Future projections for 2030
    
    Use recent, credible sources and provide a balanced analysis.
    """
    
    try:
        print("📚 Conducting research with Google Search...")
        response = client.search_and_answer(research_prompt)
        print(f"📊 Research Report:\n{response}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    print()


def main():
    """Run all Gemini 2.5 Pro examples"""
    print("🚀 Gemini 2.5 Pro Advanced Features Examples")
    print("=" * 70)
    
    try:
        # Run examples
        example_thinking_mode()
        example_streaming_response()
        example_multi_turn_conversation()
        example_google_search()
        example_code_analysis_with_thinking()
        example_research_with_search()
        
        print("✅ All Gemini 2.5 Pro examples completed!")
        print("\n🎯 Key Features Demonstrated:")
        print("   🧠 Thinking Mode - Complex reasoning with visible thought process")
        print("   🔍 Google Search - Real-time web search integration")
        print("   🌊 Streaming - Real-time response generation")
        print("   💬 Multi-turn - Context-aware conversations")
        print("   📝 Analysis - Deep code and content analysis")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
        print("\n💡 Make sure your .env file is configured for Gemini 2.5 Pro")


if __name__ == "__main__":
    main()
