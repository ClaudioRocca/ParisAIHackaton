"""
Simple Flask web interface for Gemini API
"""

from flask import Flask, render_template, request, jsonify, session
import secrets
from gemini_client import GeminiClient

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize Gemini client
try:
    gemini_client = GeminiClient()
    print("✅ Gemini client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Gemini client: {e}")
    gemini_client = None


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    if not gemini_client:
        return jsonify({
            'error': 'Gemini client not initialized. Check your API key configuration.'
        }), 500
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get chat history from session
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        # Generate response
        response = gemini_client.generate_text(message)
        
        # Update chat history
        session['chat_history'].append({
            'user': message,
            'assistant': response
        })
        
        return jsonify({
            'response': response,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error generating response: {str(e)}'
        }), 500


@app.route('/api/clear', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    session['chat_history'] = []
    return jsonify({'success': True})


@app.route('/api/status')
def status():
    """Get API status"""
    if gemini_client:
        info = gemini_client.get_model_info()
        return jsonify({
            'status': 'ready',
            'model_info': info
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Gemini client not initialized'
        }), 500


if __name__ == '__main__':
    print("🌐 Starting Gemini Web Interface...")
    print("📝 Make sure your .env file is configured with GEMINI_API_KEY")
    print("🔗 Open http://localhost:5000 in your browser")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
