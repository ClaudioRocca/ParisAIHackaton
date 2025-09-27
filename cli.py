#!/usr/bin/env python3
"""
AI Voyage Assistant - Command Line Interface
Simple CLI for interacting with the travel assistant.
"""

import os
import sys
from dotenv import load_dotenv
import argparse
from agent import create_voyage_assistant

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="AI Voyage Assistant - Your travel planning companion")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="OpenAI model to use")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for response generation")
    parser.add_argument("--query", help="Single query mode - ask one question and exit")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    try:
        # Create the assistant
        print("🌍 Initializing AI Voyage Assistant...")
        assistant = create_voyage_assistant(model_name=args.model, temperature=args.temperature)
        print("✅ Assistant ready!")
        
        # Single query mode
        if args.query:
            print(f"\nYou: {args.query}")
            response = assistant.chat(args.query)
            print(f"\nAssistant: {response}")
            return
        
        # Interactive mode
        print("\n" + "="*60)
        print("🌍 AI VOYAGE ASSISTANT")
        print("="*60)
        print("Ask me about hotels, flights, or travel destinations!")
        print("Commands: 'help', 'clear', 'history', 'quit'")
        print("="*60 + "\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() == 'quit' or user_input.lower() == 'exit':
                    print("Assistant: Safe travels! 👋")
                    break
                
                elif user_input.lower() == 'help':
                    print_help()
                    continue
                
                elif user_input.lower() == 'clear':
                    assistant.reset_conversation()
                    print("Assistant: Conversation cleared! 🗑️")
                    continue
                
                elif user_input.lower() == 'history':
                    print_history(assistant)
                    continue
                
                # Get response from assistant
                print("Assistant: ", end="", flush=True)
                response = assistant.chat(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n\nAssistant: Safe travels! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
    
    except Exception as e:
        print(f"❌ Failed to initialize assistant: {e}")
        sys.exit(1)

def print_help():
    """Print help information"""
    help_text = """
🌍 AI VOYAGE ASSISTANT - HELP

WHAT I CAN DO:
🏨 Hotel Search: "Find hotels in Paris under $200"
✈️ Flight Search: "Flights from NYC to Tokyo"  
🌍 Travel Info: "Best restaurants in Rome"
🗺️ Trip Planning: "Plan a 3-day trip to London"

COMMANDS:
help     - Show this help message
clear    - Clear conversation history
history  - Show conversation history
quit     - Exit the assistant

EXAMPLES:
• "I want to visit Japan next month"
• "Find luxury hotels in Dubai"
• "Cheap flights from London to Barcelona"
• "What should I do in New York City?"
• "Best time to visit Thailand"

TIP: Be specific about dates, budget, and preferences for better results!
"""
    print(help_text)

def print_history(assistant):
    """Print conversation history"""
    history = assistant.get_conversation_history()
    
    if not history:
        print("Assistant: No conversation history yet.")
        return
    
    print("\n📜 CONVERSATION HISTORY:")
    print("-" * 40)
    
    for i, message in enumerate(history, 1):
        role = "You" if message["role"] == "user" else "Assistant"
        content = message["content"][:100] + "..." if len(message["content"]) > 100 else message["content"]
        print(f"{i}. {role}: {content}")
    
    print("-" * 40)

if __name__ == "__main__":
    main()
