"""
Enhanced Flask web interface for Gemini 2.5 Pro with thinking mode and Google Search
"""

from flask import Flask, render_template, request, jsonify, session, Response
import secrets
import json
from gemini_25_client import Gemini25Client

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize Gemini 2.5 Pro client
try:
    gemini_client = Gemini25Client()
    print("✅ Gemini 2.5 Pro client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Gemini 2.5 Pro client: {e}")
    gemini_client = None


@app.route('/')
def index():
    """Main page"""
    return render_template('gemini_25_index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle regular chat requests"""
    if not gemini_client:
        return jsonify({
            'error': 'Gemini 2.5 Pro client not initialized. Check your API key configuration.'
        }), 500
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        enable_thinking = data.get('enable_thinking', True)
        enable_search = data.get('enable_search', False)
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get chat history from session
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        # Add user message to history
        session['chat_history'].append({
            'role': 'user',
            'content': message
        })
        
        # Generate response
        response = gemini_client.generate_text(
            message, 
            enable_thinking=enable_thinking,
            enable_search=enable_search
        )
        
        # Add assistant response to history
        session['chat_history'].append({
            'role': 'assistant',
            'content': response
        })
        
        return jsonify({
            'response': response,
            'success': True,
            'features_used': {
                'thinking': enable_thinking,
                'search': enable_search
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error generating response: {str(e)}'
        }), 500


@app.route('/api/chat-stream', methods=['POST'])
def chat_stream():
    """Handle streaming chat requests"""
    if not gemini_client:
        return jsonify({
            'error': 'Gemini 2.5 Pro client not initialized.'
        }), 500
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        enable_thinking = data.get('enable_thinking', True)
        enable_search = data.get('enable_search', False)
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        def generate():
            try:
                for chunk in gemini_client.generate_text(
                    message,
                    enable_thinking=enable_thinking,
                    enable_search=enable_search,
                    stream=True
                ):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(generate(), mimetype='text/plain')
        
    except Exception as e:
        return jsonify({
            'error': f'Error setting up stream: {str(e)}'
        }), 500


@app.route('/api/thinking-analysis', methods=['POST'])
def thinking_analysis():
    """Handle requests with explicit thinking mode"""
    if not gemini_client:
        return jsonify({
            'error': 'Gemini 2.5 Pro client not initialized.'
        }), 500
    
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        thinking_budget = data.get('thinking_budget', -1)
        
        if not prompt:
            return jsonify({'error': 'Prompt cannot be empty'}), 400
        
        # Generate response with thinking
        result = gemini_client.analyze_with_thinking(prompt, thinking_budget)
        
        return jsonify({
            'thinking': result.get('thinking', ''),
            'response': result.get('response', ''),
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error in thinking analysis: {str(e)}'
        }), 500


@app.route('/api/search-answer', methods=['POST'])
def search_answer():
    """Handle search and answer requests"""
    if not gemini_client:
        return jsonify({
            'error': 'Gemini 2.5 Pro client not initialized.'
        }), 500
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Search and generate answer
        response = gemini_client.search_and_answer(query)
        
        return jsonify({
            'response': response,
            'success': True,
            'search_used': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error in search and answer: {str(e)}'
        }), 500


@app.route('/api/multi-turn-chat', methods=['POST'])
def multi_turn_chat():
    """Handle multi-turn conversation"""
    if not gemini_client:
        return jsonify({
            'error': 'Gemini 2.5 Pro client not initialized.'
        }), 500
    
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        enable_thinking = data.get('enable_thinking', True)
        enable_search = data.get('enable_search', False)
        
        if not messages:
            return jsonify({'error': 'No messages provided'}), 400
        
        # Generate response using conversation history
        response = gemini_client.chat_conversation(
            messages,
            enable_thinking=enable_thinking,
            enable_search=enable_search
        )
        
        return jsonify({
            'response': response,
            'success': True,
            'context_length': len(messages)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error in multi-turn chat: {str(e)}'
        }), 500


@app.route('/api/clear', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    session['chat_history'] = []
    return jsonify({'success': True})


@app.route('/api/status')
def status():
    """Get API status and client information"""
    if gemini_client:
        info = gemini_client.get_client_info()
        return jsonify({
            'status': 'ready',
            'client_info': info
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Gemini 2.5 Pro client not initialized'
        }), 500


if __name__ == '__main__':
    print("🌐 Starting Gemini 2.5 Pro Web Interface...")
    print("📝 Make sure your .env file is configured with GEMINI_API_KEY")
    print("🧠 Features: Thinking Mode, Google Search, Streaming, Multi-turn Chat")
    print("🔗 Open http://localhost:5002 in your browser")
    
    app.run(debug=True, host='0.0.0.0', port=5002)
