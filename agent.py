"""
AI Voyage Assistant - LangChain Agent
Main agent that orchestrates travel planning using web scraping tools.
"""

import os
from typing import List, Dict, Any
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage
from langchain.memory import ConversationBufferWindowMemory
from dotenv import load_dotenv
import logging

# Import our custom tools
from tools import search_hotels, search_flights

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoyageAssistant:
    """
    AI Voyage Assistant that helps users plan trips with hotel and flight recommendations
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Initialize the Voyage Assistant
        
        Args:
            model_name: OpenAI model to use
            temperature: Temperature for response generation
        """
        self.model_name = model_name
        self.temperature = temperature
        
        # Check for OpenAI API key
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize the language model
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Define available tools
        self.tools = [search_hotels, search_flights]
        
        # Create the agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessage(content="{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create memory for conversation history
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10  # Keep last 10 exchanges
        )
        
        # Create the agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the voyage assistant
        """
        return """You are an AI Voyage Assistant, a helpful and knowledgeable travel planning expert. 
        Your goal is to help users plan amazing trips by providing personalized recommendations for:
        
        🏨 **Hotels**: Find accommodations that match their budget, location, and preferences
        ✈️ **Flights**: Search for flight options with good prices and convenient schedules  
        🌍 **Travel Information**: Provide insights about destinations, attractions, restaurants, and travel tips
        
        **Your Capabilities:**
        - search_hotels: Search for hotel recommendations from Booking.com and Airbnb
        - search_flights: Find flight options from Skyscanner only
        
        **Guidelines:**
        1. **Be Helpful**: Always try to understand what the user is looking for and provide relevant suggestions
        2. **Be Specific**: Ask clarifying questions if the user's request is vague (dates, budget, preferences)
        3. **Be Comprehensive**: Use multiple tools when appropriate to give complete travel advice
        4. **Be Honest**: If you can't find information or if scraping fails, explain the limitations
        5. **Be Conversational**: Maintain a friendly, enthusiastic tone about travel
        
        **Example Interactions:**
        - User: "I want to go to Paris" → Ask about dates, budget, hotel preferences, then search hotels and flights
        - User: "Find cheap flights to Tokyo" → Ask about departure city and dates, then search flights
        - User: "Hotels in Rome" → Search for accommodations on Booking.com and Airbnb
        
        **Important Notes:**
        - Web scraping results may vary in quality and availability
        - Always recommend users verify prices and availability on official booking sites
        - Suggest booking soon for good deals, especially for flights
        - Be aware that some searches might not return results due to technical limitations
        
        Start each conversation by greeting the user and asking how you can help them plan their next adventure!"""
    
    def chat(self, message: str) -> str:
        """
        Process a user message and return the assistant's response
        
        Args:
            message: User's input message
            
        Returns:
            Assistant's response
        """
        try:
            logger.info(f"Processing user message: {message}")
            
            # Execute the agent
            response = self.agent_executor.invoke({
                "input": message,
                "chat_history": self.memory.chat_memory.messages
            })
            
            return response["output"]
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try again or rephrase your question."
    
    def reset_conversation(self):
        """
        Reset the conversation memory
        """
        self.memory.clear()
        logger.info("Conversation memory cleared")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history
        
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        history = []
        for message in self.memory.chat_memory.messages:
            if hasattr(message, 'content'):
                role = "user" if isinstance(message, HumanMessage) else "assistant"
                history.append({
                    "role": role,
                    "content": message.content
                })
        return history

def create_voyage_assistant(**kwargs) -> VoyageAssistant:
    """
    Factory function to create a VoyageAssistant instance
    
    Args:
        **kwargs: Arguments to pass to VoyageAssistant constructor
        
    Returns:
        VoyageAssistant instance
    """
    return VoyageAssistant(**kwargs)

# Example usage
if __name__ == "__main__":
    # Create the assistant
    assistant = create_voyage_assistant()
    
    print("🌍 AI Voyage Assistant initialized!")
    print("Ask me about hotels, flights, or travel destinations.")
    print("Type 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Assistant: Safe travels! 👋")
                break
            
            if not user_input:
                continue
            
            # Get response from assistant
            response = assistant.chat(user_input)
            print(f"\nAssistant: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nAssistant: Safe travels! 👋")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
