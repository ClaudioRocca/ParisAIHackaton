#!/usr/bin/env python3
"""
AI Voyage Assistant - Startup Script
Easy way to start the application with different interfaces.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

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

def check_env():
    """Check environment configuration"""
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found!")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    
    print("✅ Environment configured")
    return True

def start_web_app():
    """Start the Streamlit web application"""
    print("🌍 Starting AI Voyage Assistant Web Interface...")
    print("The web app will open in your browser automatically.")
    print("Press Ctrl+C to stop the server.")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Web app stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting web app: {e}")

def start_cli():
    """Start the command line interface"""
    print("🌍 Starting AI Voyage Assistant CLI...")
    
    try:
        subprocess.run([sys.executable, "cli.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 CLI stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting CLI: {e}")

def run_tests():
    """Run the test examples"""
    print("🧪 Running AI Voyage Assistant Tests...")
    
    try:
        subprocess.run([sys.executable, "test_example.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running tests: {e}")

def install_requirements():
    """Install requirements"""
    print("📦 Installing requirements...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")

def setup_env():
    """Setup environment file"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if env_example.exists():
        # Copy example to .env
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Created .env file from .env.example")
        print("Please edit .env and add your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
    else:
        # Create basic .env file
        with open(env_file, 'w') as f:
            f.write("# OpenAI API Key for LangChain\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        
        print("✅ Created basic .env file")
        print("Please edit .env and add your OpenAI API key")

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description="AI Voyage Assistant Startup Script")
    parser.add_argument("mode", nargs="?", default="web", 
                       choices=["web", "cli", "test", "install", "setup"],
                       help="Mode to run: web (default), cli, test, install, or setup")
    
    args = parser.parse_args()
    
    print("🌍 AI VOYAGE ASSISTANT")
    print("=" * 40)
    
    # Handle setup and install modes first
    if args.mode == "setup":
        setup_env()
        return
    
    if args.mode == "install":
        install_requirements()
        return
    
    # Check requirements for other modes
    if not check_requirements():
        print("\n💡 Run: python start.py install")
        return
    
    if not check_env():
        print("\n💡 Run: python start.py setup")
        return
    
    # Run the selected mode
    if args.mode == "web":
        start_web_app()
    elif args.mode == "cli":
        start_cli()
    elif args.mode == "test":
        run_tests()

if __name__ == "__main__":
    main()
