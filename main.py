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
from code_handler import CodeHandler
import time

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

# Initialize services
llm_client = None
interview_manager = None
code_handler = None

def init_services():
    """Initialize all services"""
    global llm_client, interview_manager, code_handler
    try:
        llm_client = LLMClient()
        interview_manager = InterviewManager(llm_client)
        code_handler = CodeHandler()
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        llm_client = None
        interview_manager = None
        code_handler = None

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
        'code_handler_ready': code_handler is not None,
        'active_sessions': interview_manager.get_active_sessions_count() if interview_manager else 0,
        'supported_languages': code_handler.get_supported_languages() if code_handler else []
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

# Code Input and Management API Endpoints
@app.route('/api/validate_code', methods=['POST'])
def validate_code():
    """Validate code syntax and format"""
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({
                'success': False,
                'error': 'Code is required'
            }), 400
        
        code = data['code']
        language = data.get('language', 'python')
        
        if not code_handler:
            return jsonify({
                'success': False,
                'error': 'Code validation service not available'
            }), 503
        
        # Validate code
        validation_result = code_handler.validate_code(code, language)
        
        return jsonify({
            'success': True,
            'validation': {
                'is_valid': validation_result.is_valid,
                'language': validation_result.language,
                'errors': validation_result.errors,
                'warnings': validation_result.warnings,
                'line_count': validation_result.line_count,
                'char_count': validation_result.char_count,
                'complexity_score': validation_result.complexity_score,
                'security_issues': validation_result.security_issues,
                'suggestions': validation_result.suggestions
            }
        })
        
    except Exception as e:
        logger.error(f"Error validating code: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to validate code'
        }), 500

@app.route('/api/store_code', methods=['POST'])
def store_code():
    """Store code snippet for a session"""
    try:
        data = request.get_json()
        if not data or 'code' not in data or 'session_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Code and session_id are required'
            }), 400
        
        code = data['code']
        session_id = data['session_id']
        language = data.get('language', 'python')
        problem_description = data.get('problem_description', '')
        is_solution = data.get('is_solution', False)
        
        if not code_handler:
            return jsonify({
                'success': False,
                'error': 'Code storage service not available'
            }), 503
        
        # Store code snippet
        snippet_id = code_handler.store_code_snippet(
            session_id=session_id,
            code=code,
            language=language,
            problem_description=problem_description,
            is_solution=is_solution
        )
        
        # Get the stored snippet for validation info
        snippet = code_handler.get_code_snippet(snippet_id)
        
        return jsonify({
            'success': True,
            'snippet_id': snippet_id,
            'validation': {
                'is_valid': snippet.validation_result.is_valid,
                'errors': snippet.validation_result.errors,
                'warnings': snippet.validation_result.warnings,
                'security_issues': snippet.validation_result.security_issues
            }
        })
        
    except Exception as e:
        logger.error(f"Error storing code: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to store code'
        }), 500

@app.route('/api/get_code/<snippet_id>')
def get_code(snippet_id):
    """Retrieve code snippet by ID"""
    try:
        if not code_handler:
            return jsonify({
                'success': False,
                'error': 'Code retrieval service not available'
            }), 503
        
        snippet = code_handler.get_code_snippet(snippet_id)
        
        if not snippet:
            return jsonify({
                'success': False,
                'error': 'Code snippet not found'
            }), 404
        
        return jsonify({
            'success': True,
            'snippet': {
                'snippet_id': snippet.snippet_id,
                'session_id': snippet.session_id,
                'code': snippet.code,
                'language': snippet.language,
                'timestamp': snippet.timestamp,
                'is_solution': snippet.is_solution,
                'problem_description': snippet.problem_description,
                'validation': {
                    'is_valid': snippet.validation_result.is_valid,
                    'errors': snippet.validation_result.errors,
                    'warnings': snippet.validation_result.warnings,
                    'line_count': snippet.validation_result.line_count,
                    'char_count': snippet.validation_result.char_count,
                    'complexity_score': snippet.validation_result.complexity_score,
                    'security_issues': snippet.validation_result.security_issues,
                    'suggestions': snippet.validation_result.suggestions
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving code: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve code'
        }), 500

@app.route('/api/session_code/<session_id>')
def get_session_code(session_id):
    """Get all code snippets for a session"""
    try:
        if not code_handler:
            return jsonify({
                'success': False,
                'error': 'Code retrieval service not available'
            }), 503
        
        snippets = code_handler.get_session_snippets(session_id)
        
        snippets_data = []
        for snippet in snippets:
            snippets_data.append({
                'snippet_id': snippet.snippet_id,
                'code': snippet.code,
                'language': snippet.language,
                'timestamp': snippet.timestamp,
                'is_solution': snippet.is_solution,
                'problem_description': snippet.problem_description,
                'validation': {
                    'is_valid': snippet.validation_result.is_valid,
                    'errors': snippet.validation_result.errors,
                    'warnings': snippet.validation_result.warnings,
                    'complexity_score': snippet.validation_result.complexity_score
                }
            })
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'snippets': snippets_data,
            'total_snippets': len(snippets_data)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving session code: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve session code'
        }), 500

@app.route('/api/supported_languages')
def get_supported_languages():
    """Get list of supported programming languages"""
    try:
        if not code_handler:
            return jsonify({
                'success': False,
                'error': 'Code handler service not available'
            }), 503
        
        return jsonify({
            'success': True,
            'languages': code_handler.get_supported_languages()
        })
        
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get supported languages'
        }), 500

# Enhanced LLM Code Analysis API Endpoints
@app.route('/api/llm_analyze_code', methods=['POST'])
def llm_analyze_code():
    """Direct LLM code analysis without interview context"""
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
        
        # Perform LLM analysis
        analysis_result = llm_client.analyze_code(code, language)
        
        return jsonify({
            'success': True,
            'analysis': analysis_result
        })
        
    except Exception as e:
        logger.error(f"Error in LLM code analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze code with LLM'
        }), 500

@app.route('/api/generate_coding_problem', methods=['POST'])
def generate_coding_problem():
    """Generate a coding problem using LLM"""
    try:
        data = request.get_json() or {}
        difficulty = data.get('difficulty', 'medium')
        topic = data.get('topic', 'algorithms')
        language = data.get('language', 'python')
        
        if not llm_client:
            return jsonify({
                'success': False,
                'error': 'LLM service not available'
            }), 503
        
        # Generate coding problem prompt
        problem_prompt = f"""
請生成一個 {difficulty} 難度的 {topic} 程式設計問題，適合 {language} 語言：

要求：
1. 清楚的問題描述
2. 輸入輸出範例
3. 約束條件
4. 預期時間複雜度
5. 提示（可選）

請用繁體中文描述，格式化為結構化的程式設計問題。
        """
        
        # Get problem from LLM
        problem_response = llm_client._call_gemini(problem_prompt)
        
        return jsonify({
            'success': True,
            'problem': {
                'difficulty': difficulty,
                'topic': topic,
                'language': language,
                'description': problem_response,
                'generated_at': time.time()
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating coding problem: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate coding problem'
        }), 500

@app.route('/api/evaluate_code_solution', methods=['POST'])
def evaluate_code_solution():
    """Evaluate code solution against a specific problem"""
    try:
        data = request.get_json()
        if not data or 'code' not in data or 'problem' not in data:
            return jsonify({
                'success': False,
                'error': 'Code and problem description are required'
            }), 400
        
        code = data['code']
        problem = data['problem']
        language = data.get('language', 'python')
        
        if not llm_client:
            return jsonify({
                'success': False,
                'error': 'LLM service not available'
            }), 503
        
        # Enhanced evaluation prompt
        evaluation_prompt = f"""
請評估以下程式碼解答：

問題描述：
{problem}

解答程式碼 ({language}):
```{language}
{code}
```

請提供：
1. 正確性評估（是否解決了問題）
2. 程式碼品質評分（0-100分）
3. 時間和空間複雜度分析
4. 具體的優點和缺點
5. 改進建議
6. 替代解法提示
7. 綜合評級（A-F）

請用繁體中文提供詳細的評估報告。
        """
        
        # Get evaluation from LLM
        evaluation_response = llm_client._call_gemini(evaluation_prompt)
        
        # Also run basic code validation
        validation_result = None
        if code_handler:
            validation_result = code_handler.validate_code(code, language)
        
        return jsonify({
            'success': True,
            'evaluation': {
                'llm_analysis': evaluation_response,
                'basic_validation': {
                    'is_valid': validation_result.is_valid if validation_result else None,
                    'errors': validation_result.errors if validation_result else [],
                    'warnings': validation_result.warnings if validation_result else [],
                    'complexity_score': validation_result.complexity_score if validation_result else None
                } if validation_result else None,
                'language': language,
                'evaluated_at': time.time()
            }
        })
        
    except Exception as e:
        logger.error(f"Error evaluating code solution: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to evaluate code solution'
        }), 500

@app.route('/api/interview_code_feedback', methods=['POST'])
def interview_code_feedback():
    """Get interview-style feedback on code submission"""
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
        
        if not llm_client:
            return jsonify({
                'success': False,
                'error': 'LLM service not available'
            }), 503
        
        # Generate interview-style feedback
        feedback_prompt = f"""
你是一位經驗豐富的技術面試官。請對以下程式碼提供面試風格的反饋：

程式碼 ({language}):
```{language}
{code}
```

請以面試官的語調提供：
1. 程式碼的優點認可
2. 需要改進的地方（以問題形式引導）
3. 後續技術問題（測試深度理解）
4. 建設性的改進建議
5. 鼓勵性的總結

保持友善但專業的面試官語調，用繁體中文回應。
        """
        
        # Get feedback from LLM
        feedback_response = llm_client._call_gemini(feedback_prompt)
        
        return jsonify({
            'success': True,
            'feedback': {
                'interviewer_response': feedback_response,
                'language': language,
                'session_id': session_id,
                'timestamp': time.time()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting interview code feedback: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get interview feedback'
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