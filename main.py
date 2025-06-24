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
from interview_manager import InterviewManager

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

# Initialize LLM client and Interview Manager
llm_client = None
interview_manager = None

def init_services():
    """Initialize LLM client and Interview Manager"""
    global llm_client, interview_manager
    try:
        llm_client = LLMClient()
        interview_manager = InterviewManager(llm_client)
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        llm_client = None
        interview_manager = None

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
        'llm_ready': llm_client is not None,
        'interview_manager_ready': interview_manager is not None,
        'active_sessions': interview_manager.get_active_sessions_count() if interview_manager else 0
    })

@app.route('/api/start_interview', methods=['POST'])
def start_interview():
    """Start a new interview session"""
    try:
        data = request.get_json() or {}
        interview_type = data.get('type', 'technical')
        candidate_name = data.get('candidate_name', '')
        position = data.get('position', '')
        difficulty_level = data.get('difficulty_level', 'medium')
        
        if not interview_manager:
            return jsonify({
                'success': False, 
                'error': 'Interview service not available'
            }), 503
        
        # Create new interview session
        session_id = interview_manager.create_session(
            interview_type=interview_type,
            candidate_name=candidate_name,
            position=position,
            difficulty_level=difficulty_level
        )
        
        # Start the interview
        result = interview_manager.start_interview(session_id)
        
        return jsonify(result)
        
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
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False, 
                'error': 'Session ID is required'
            }), 400
        
        if not interview_manager:
            return jsonify({
                'success': False, 
                'error': 'Interview service not available'
            }), 503
        
        # Process answer through interview manager
        result = interview_manager.process_answer(session_id, message)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return jsonify({
            'success': False, 
            'error': 'Failed to process message'
        }), 500

@app.route('/api/analyze_code', methods=['POST'])
def analyze_code():
    """Analyze submitted code during interview"""
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({
                'success': False, 
                'error': 'Code is required'
            }), 400
        
        code = data['code']
        language = data.get('language', 'python')
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False, 
                'error': 'Session ID is required'
            }), 400
        
        if not interview_manager:
            return jsonify({
                'success': False, 
                'error': 'Interview service not available'
            }), 503
        
        # Submit code through interview manager
        result = interview_manager.submit_code(session_id, code, language)
        
        return jsonify(result)
        
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
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False, 
                'error': 'Session ID is required'
            }), 400
        
        if not interview_manager:
            return jsonify({
                'success': False, 
                'error': 'Interview service not available'
            }), 503
        
        # End interview through interview manager
        result = interview_manager.end_interview(session_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error ending interview: {e}")
        return jsonify({
            'success': False, 
            'error': 'Failed to end interview'
        }), 500

@app.route('/api/session_status/<session_id>')
def get_session_status(session_id):
    """Get current session status and progress"""
    try:
        if not interview_manager:
            return jsonify({
                'success': False, 
                'error': 'Interview service not available'
            }), 503
        
        # Get session status
        result = interview_manager.get_session_status(session_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        return jsonify({
            'success': False, 
            'error': 'Failed to get session status'
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
    # Initialize services
    init_services()
    
    # Run Flask application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting AI Interview Simulator on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug) 