"""
AI Interview Simulator - MVP Flask Application
簡化版的 AI 面試模擬工具
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import os
from config import Config
from llm_client import LLMClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for API endpoints
CORS(app)

# Initialize LLM client
llm_client = None

def init_llm():
    """Initialize LLM client"""
    global llm_client
    try:
        llm_client = LLMClient()
        logger.info("LLM client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}")
        llm_client = None

# Routes
@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'AI Interview Simulator',
        'version': '1.0.0-mvp',
        'llm_ready': llm_client is not None
    })

@app.route('/api/start_interview', methods=['POST'])
def start_interview():
    """Start a new interview session"""
    try:
        data = request.get_json() or {}
        interview_type = data.get('type', 'technical')
        
        if not llm_client:
            return jsonify({
                'success': False, 
                'error': 'LLM service not available'
            }), 503
        
        # Generate initial interview question
        initial_question = llm_client.start_interview(interview_type)
        
        return jsonify({
            'success': True,
            'session_id': 'mvp_session_1',  # Simplified session management
            'interview_type': interview_type,
            'question': initial_question
        })
        
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        return jsonify({
            'success': False, 
            'error': 'Failed to start interview'
        }), 500

@app.route('/api/send_message', methods=['POST'])
def send_message():
    """Send message to interview bot"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False, 
                'error': 'Message is required'
            }), 400
        
        message = data['message']
        session_id = data.get('session_id', 'mvp_session_1')
        
        if not llm_client:
            return jsonify({
                'success': False, 
                'error': 'LLM service not available'
            }), 503
        
        # Get response from LLM
        response = llm_client.get_response(message, session_id)
        
        return jsonify({
            'success': True,
            'response': response,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return jsonify({
            'success': False, 
            'error': 'Failed to process message'
        }), 500

@app.route('/api/analyze_code', methods=['POST'])
def analyze_code():
    """Analyze submitted code"""
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({
                'success': False, 
                'error': 'Code is required'
            }), 400
        
        code = data['code']
        language = data.get('language', 'python')
        
        if not llm_client:
            return jsonify({
                'success': False, 
                'error': 'LLM service not available'
            }), 503
        
        # Analyze code using LLM
        analysis = llm_client.analyze_code(code, language)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error analyzing code: {e}")
        return jsonify({
            'success': False, 
            'error': 'Failed to analyze code'
        }), 500

@app.route('/api/end_interview', methods=['POST'])
def end_interview():
    """End interview session"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id', 'mvp_session_1')
        
        if not llm_client:
            return jsonify({
                'success': False, 
                'error': 'LLM service not available'
            }), 503
        
        # Generate interview summary
        summary = llm_client.end_interview(session_id)
        
        return jsonify({
            'success': True,
            'summary': summary,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error ending interview: {e}")
        return jsonify({
            'success': False, 
            'error': 'Failed to end interview'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize LLM client
    init_llm()
    
    # Run Flask application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting AI Interview Simulator on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug) 