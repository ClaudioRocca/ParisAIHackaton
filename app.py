"""
AI Voyage Assistant - Streamlit Web Interface
Beautiful web interface for the AI travel planning assistant.
"""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

# Import our agent
from agent import create_voyage_assistant

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Voyage Assistant",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #667eea;
    }
    
    .assistant-message {
        background-color: #e8f4f8;
        border-left-color: #00d4aa;
    }
    
    .sidebar-info {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    
    .feature-box {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'assistant' not in st.session_state:
        st.session_state.assistant = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False

def create_assistant():
    """Create or get the voyage assistant"""
    if st.session_state.assistant is None:
        try:
            st.session_state.assistant = create_voyage_assistant()
            st.session_state.initialized = True
            return True
        except Exception as e:
            st.error(f"Failed to initialize assistant: {str(e)}")
            return False
    return True

def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌍 AI Voyage Assistant</h1>
        <p>Your intelligent travel planning companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🛠️ Assistant Settings")
        
        # API Key status
        api_key_status = "✅ Configured" if os.getenv('OPENAI_API_KEY') else "❌ Missing"
        st.markdown(f"**OpenAI API Key:** {api_key_status}")
        
        if not os.getenv('OPENAI_API_KEY'):
            st.warning("Please set your OPENAI_API_KEY in the .env file")
            st.stop()
        
        # Model selection
        model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
        selected_model = st.selectbox("Model", model_options, index=0)
        
        # Temperature setting
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        
        # Initialize assistant button
        if st.button("🚀 Initialize Assistant", type="primary"):
            with st.spinner("Initializing AI Voyage Assistant..."):
                if create_assistant():
                    st.success("Assistant ready!")
                    st.rerun()
        
        # Clear conversation
        if st.button("🗑️ Clear Conversation"):
            if st.session_state.assistant:
                st.session_state.assistant.reset_conversation()
            st.session_state.messages = []
            st.success("Conversation cleared!")
            st.rerun()
        
        st.markdown("---")
        
        # Features info
        st.markdown("""
        <div class="sidebar-info">
            <h4>🎯 What I Can Help With:</h4>
            <ul>
                <li>🏨 Find hotels worldwide</li>
                <li>✈️ Search for flights</li>
                <li>🌍 Travel information & tips</li>
                <li>🍽️ Restaurant recommendations</li>
                <li>🗺️ Destination guides</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Example queries
        st.markdown("### 💡 Example Queries")
        example_queries = [
            "Find hotels in Paris under $200",
            "Flights from NYC to Tokyo",
            "Best restaurants in Rome",
            "Things to do in Bali",
            "Plan a 3-day trip to London"
        ]
        
        for query in example_queries:
            if st.button(f"💬 {query}", key=f"example_{query}"):
                st.session_state.example_query = query
                st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat interface
        st.markdown("### 💬 Chat with Your Travel Assistant")
        
        # Display conversation history
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {content}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>Assistant:</strong> {content}
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        user_input = st.chat_input("Ask me about hotels, flights, or travel destinations...")
        
        # Handle example query
        if hasattr(st.session_state, 'example_query'):
            user_input = st.session_state.example_query
            delattr(st.session_state, 'example_query')
        
        # Process user input
        if user_input:
            if not st.session_state.initialized:
                st.warning("Please initialize the assistant first using the sidebar.")
            else:
                # Add user message
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Get assistant response
                with st.spinner("🤔 Thinking and searching..."):
                    try:
                        response = st.session_state.assistant.chat(user_input)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"Sorry, I encountered an error: {str(e)}"
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
                st.rerun()
    
    with col2:
        # Features showcase
        st.markdown("### ✨ Features")
        
        features = [
            {
                "icon": "🏨",
                "title": "Smart Hotel Search",
                "description": "Find accommodations that match your budget, location, and preferences using advanced web scraping."
            },
            {
                "icon": "✈️",
                "title": "Flight Discovery",
                "description": "Search multiple airlines and booking sites to find the best flight deals and schedules."
            },
            {
                "icon": "🌍",
                "title": "Travel Intelligence",
                "description": "Get insider tips, restaurant recommendations, and destination guides from trusted sources."
            },
            {
                "icon": "🤖",
                "title": "AI-Powered",
                "description": "Powered by advanced language models and real-time web scraping for up-to-date information."
            }
        ]
        
        for feature in features:
            st.markdown(f"""
            <div class="feature-box">
                <h4>{feature['icon']} {feature['title']}</h4>
                <p>{feature['description']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Status indicators
        st.markdown("### 📊 System Status")
        
        status_items = [
            ("Web Scraping", "🟢 Active"),
            ("AI Model", f"🟢 {selected_model}"),
            ("Memory", f"🟢 {len(st.session_state.messages)} messages"),
            ("Tools", "🟢 3 tools loaded")
        ]
        
        for item, status in status_items:
            st.markdown(f"**{item}:** {status}")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🌍 AI Voyage Assistant - Your intelligent travel planning companion</p>
        <p>Built with Streamlit, LangChain, and advanced web scraping</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
