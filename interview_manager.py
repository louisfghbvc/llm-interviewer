"""
Interview Manager - Core interview logic and state management
核心面試邏輯實現，包含狀態機和會話管理
"""

import logging
import time
import uuid
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from llm_client import LLMClient
from config import Config

logger = logging.getLogger(__name__)

class InterviewState(Enum):
    """Interview session states"""
    INIT = "init"                    # 初始化
    INTRODUCTION = "introduction"    # 自我介紹階段
    QUESTIONING = "questioning"      # 提問階段
    CODE_REVIEW = "code_review"     # 程式碼審查階段
    EVALUATION = "evaluation"        # 評估階段
    COMPLETED = "completed"          # 完成
    FAILED = "failed"               # 失敗

class InterviewType(Enum):
    """Interview types"""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"

@dataclass
class InterviewMetrics:
    """Interview performance metrics"""
    technical_score: int = 0          # 技術得分 (0-100)
    communication_score: int = 0      # 溝通得分 (0-100)
    problem_solving_score: int = 0    # 問題解決得分 (0-100)
    overall_score: int = 0           # 總體得分 (0-100)
    total_questions: int = 0         # 總問題數
    correct_answers: int = 0         # 正確回答數
    response_quality: str = "B"      # 回答品質等級

@dataclass
class InterviewSession:
    """Interview session data structure"""
    session_id: str
    interview_type: InterviewType
    state: InterviewState = InterviewState.INIT
    start_time: float = None
    end_time: float = None
    duration_minutes: float = 0
    
    # Conversation data
    conversation_history: List[Dict] = None
    current_question: str = ""
    question_count: int = 0
    
    # Performance tracking
    metrics: InterviewMetrics = None
    feedback_history: List[str] = None
    
    # Metadata
    candidate_name: str = ""
    position: str = ""
    difficulty_level: str = "medium"  # easy, medium, hard
    
    def __post_init__(self):
        """Initialize default values"""
        if self.conversation_history is None:
            self.conversation_history = []
        if self.metrics is None:
            self.metrics = InterviewMetrics()
        if self.feedback_history is None:
            self.feedback_history = []
        if self.start_time is None:
            self.start_time = time.time()

class InterviewManager:
    """
    Core interview management system
    Handles interview flow, state transitions, and logic
    """
    
    def __init__(self, llm_client: LLMClient = None):
        """Initialize interview manager"""
        self.llm_client = llm_client or LLMClient()
        self.active_sessions: Dict[str, InterviewSession] = {}
        self.completed_sessions: List[InterviewSession] = []
        
        # Interview configuration
        self.max_questions_per_type = {
            InterviewType.TECHNICAL: 8,
            InterviewType.BEHAVIORAL: 6,
            InterviewType.SYSTEM_DESIGN: 4
        }
        
        self.time_limits = {
            InterviewType.TECHNICAL: 45,      # minutes
            InterviewType.BEHAVIORAL: 30,
            InterviewType.SYSTEM_DESIGN: 60
        }
        
        logger.info("Interview Manager initialized")
    
    def create_session(self, 
                      interview_type: str, 
                      candidate_name: str = "",
                      position: str = "",
                      difficulty_level: str = "medium") -> str:
        """
        Create a new interview session
        
        Args:
            interview_type: Type of interview
            candidate_name: Name of the candidate
            position: Position being interviewed for
            difficulty_level: Difficulty level (easy, medium, hard)
            
        Returns:
            Session ID
        """
        try:
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            
            # Convert string to enum
            interview_type_enum = InterviewType(interview_type.lower())
            
            # Create session
            session = InterviewSession(
                session_id=session_id,
                interview_type=interview_type_enum,
                candidate_name=candidate_name,
                position=position,
                difficulty_level=difficulty_level
            )
            
            # Store session
            self.active_sessions[session_id] = session
            
            logger.info(f"Created interview session {session_id} for {interview_type}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating interview session: {e}")
            raise
    
    def start_interview(self, session_id: str) -> Dict[str, Any]:
        """
        Start the interview process
        
        Args:
            session_id: Session identifier
            
        Returns:
            Initial response with question
        """
        try:
            session = self._get_session(session_id)
            
            # Transition to introduction state
            session.state = InterviewState.INTRODUCTION
            
            # Generate initial question based on interview type
            initial_prompt = self._get_initial_prompt(session)
            
            # Get response from LLM
            initial_question = self.llm_client.start_interview(session.interview_type.value)
            
            # Store initial interaction
            session.current_question = initial_question
            session.conversation_history.append({
                'role': 'interviewer',
                'content': initial_question,
                'timestamp': time.time(),
                'state': session.state.value
            })
            
            session.question_count += 1
            
            logger.info(f"Started interview for session {session_id}")
            
            return {
                'success': True,
                'session_id': session_id,
                'question': initial_question,
                'state': session.state.value,
                'interview_type': session.interview_type.value,
                'question_number': session.question_count,
                'max_questions': self.max_questions_per_type[session.interview_type],
                'time_limit_minutes': self.time_limits[session.interview_type]
            }
            
        except Exception as e:
            logger.error(f"Error starting interview: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_answer(self, session_id: str, answer: str) -> Dict[str, Any]:
        """
        Process candidate's answer and generate next question
        
        Args:
            session_id: Session identifier
            answer: Candidate's answer
            
        Returns:
            Response with feedback and next question
        """
        try:
            session = self._get_session(session_id)
            
            # Store candidate's answer
            session.conversation_history.append({
                'role': 'candidate',
                'content': answer,
                'timestamp': time.time(),
                'state': session.state.value
            })
            
            # Check if interview should continue
            should_continue = self._should_continue_interview(session)
            
            if not should_continue:
                return self._end_interview(session_id)
            
            # Get response from LLM
            response = self.llm_client.get_response(answer, session_id)
            
            # Extract feedback and next question
            feedback, next_question = self._parse_llm_response(response)
            
            # Update session
            session.current_question = next_question
            session.conversation_history.append({
                'role': 'interviewer',
                'content': response,
                'timestamp': time.time(),
                'state': session.state.value
            })
            
            session.question_count += 1
            session.feedback_history.append(feedback)
            
            # Update state if needed
            self._update_interview_state(session)
            
            # Calculate progress
            progress = self._calculate_progress(session)
            
            return {
                'success': True,
                'session_id': session_id,
                'feedback': feedback,
                'next_question': next_question,
                'state': session.state.value,
                'question_number': session.question_count,
                'progress_percentage': progress,
                'continuing': True
            }
            
        except Exception as e:
            logger.error(f"Error processing answer: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def submit_code(self, session_id: str, code: str, language: str = 'python') -> Dict[str, Any]:
        """
        Submit code for analysis during interview
        
        Args:
            session_id: Session identifier
            code: Code to analyze
            language: Programming language
            
        Returns:
            Code analysis results
        """
        try:
            session = self._get_session(session_id)
            
            # Transition to code review state
            session.state = InterviewState.CODE_REVIEW
            
            # Analyze code using LLM
            analysis_result = self.llm_client.analyze_code(code, language)
            
            # Store code submission
            session.conversation_history.append({
                'role': 'candidate',
                'content': f"Code submission ({language}):\n{code}",
                'timestamp': time.time(),
                'state': session.state.value,
                'metadata': {
                    'type': 'code_submission',
                    'language': language,
                    'analysis': analysis_result
                }
            })
            
            # Update metrics based on code analysis
            self._update_metrics_from_code_analysis(session, analysis_result)
            
            # Generate follow-up question about the code
            code_feedback = f"程式碼分析完成。{analysis_result['feedback'][:200]}... 請解釋你的實現思路。"
            
            session.conversation_history.append({
                'role': 'interviewer',
                'content': code_feedback,
                'timestamp': time.time(),
                'state': session.state.value
            })
            
            return {
                'success': True,
                'session_id': session_id,
                'analysis': analysis_result,
                'feedback_question': code_feedback,
                'state': session.state.value
            }
            
        except Exception as e:
            logger.error(f"Error submitting code: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def end_interview(self, session_id: str) -> Dict[str, Any]:
        """
        End the interview and generate final summary
        
        Args:
            session_id: Session identifier
            
        Returns:
            Final interview summary
        """
        return self._end_interview(session_id)
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get current session status and progress
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session status information
        """
        try:
            session = self._get_session(session_id)
            
            # Calculate current metrics
            duration = time.time() - session.start_time
            progress = self._calculate_progress(session)
            
            return {
                'success': True,
                'session_id': session_id,
                'state': session.state.value,
                'interview_type': session.interview_type.value,
                'candidate_name': session.candidate_name,
                'position': session.position,
                'duration_minutes': round(duration / 60, 1),
                'question_count': session.question_count,
                'max_questions': self.max_questions_per_type[session.interview_type],
                'progress_percentage': progress,
                'current_metrics': asdict(session.metrics),
                'is_active': session.state not in [InterviewState.COMPLETED, InterviewState.FAILED]
            }
            
        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_session(self, session_id: str) -> InterviewSession:
        """Get session by ID with validation"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        return self.active_sessions[session_id]
    
    def _get_initial_prompt(self, session: InterviewSession) -> str:
        """Generate initial prompt based on interview type and difficulty"""
        base_prompts = {
            InterviewType.TECHNICAL: f"歡迎參加{session.position or '軟體工程師'}的技術面試",
            InterviewType.BEHAVIORAL: f"歡迎參加{session.position or '職位'}的行為面試",
            InterviewType.SYSTEM_DESIGN: f"歡迎參加{session.position or '系統設計師'}的系統設計面試"
        }
        
        return base_prompts.get(session.interview_type, "歡迎參加面試")
    
    def _should_continue_interview(self, session: InterviewSession) -> bool:
        """Determine if interview should continue"""
        # Check question limit
        max_questions = self.max_questions_per_type[session.interview_type]
        if session.question_count >= max_questions:
            return False
        
        # Check time limit
        duration_minutes = (time.time() - session.start_time) / 60
        time_limit = self.time_limits[session.interview_type]
        if duration_minutes >= time_limit:
            return False
        
        # Check if in failed state
        if session.state == InterviewState.FAILED:
            return False
        
        return True
    
    def _parse_llm_response(self, response: str) -> Tuple[str, str]:
        """Parse LLM response into feedback and next question"""
        # Simple parsing - in a real implementation, this would be more sophisticated
        lines = response.split('\n')
        
        # Try to separate feedback from question
        feedback_lines = []
        question_lines = []
        
        in_question = False
        for line in lines:
            if any(keyword in line for keyword in ['問題', '請問', '能否', '如何', '什麼', '為什麼']):
                in_question = True
            
            if in_question:
                question_lines.append(line)
            else:
                feedback_lines.append(line)
        
        feedback = '\n'.join(feedback_lines).strip()
        next_question = '\n'.join(question_lines).strip()
        
        # Fallback if parsing fails
        if not next_question:
            next_question = response
            feedback = "感謝您的回答。"
        
        return feedback, next_question
    
    def _update_interview_state(self, session: InterviewSession):
        """Update interview state based on progress"""
        if session.question_count >= 2 and session.state == InterviewState.INTRODUCTION:
            session.state = InterviewState.QUESTIONING
        elif session.question_count >= 6 and session.state == InterviewState.QUESTIONING:
            session.state = InterviewState.EVALUATION
    
    def _calculate_progress(self, session: InterviewSession) -> int:
        """Calculate interview progress percentage"""
        max_questions = self.max_questions_per_type[session.interview_type]
        progress = min(100, int((session.question_count / max_questions) * 100))
        return progress
    
    def _update_metrics_from_code_analysis(self, session: InterviewSession, analysis: Dict):
        """Update session metrics based on code analysis"""
        if 'score' in analysis:
            session.metrics.technical_score = max(session.metrics.technical_score, analysis['score'])
        
        # Update overall score (weighted average)
        session.metrics.overall_score = int(
            (session.metrics.technical_score * 0.4 +
             session.metrics.communication_score * 0.3 +
             session.metrics.problem_solving_score * 0.3)
        )
    
    def _end_interview(self, session_id: str) -> Dict[str, Any]:
        """Internal method to end interview and generate summary"""
        try:
            session = self._get_session(session_id)
            
            # Update session state
            session.state = InterviewState.COMPLETED
            session.end_time = time.time()
            session.duration_minutes = (session.end_time - session.start_time) / 60
            
            # Generate final summary using LLM
            summary_result = self.llm_client.end_interview(session_id)
            
            # Calculate final metrics
            final_metrics = self._calculate_final_metrics(session)
            session.metrics = final_metrics
            
            # Move to completed sessions
            self.completed_sessions.append(session)
            del self.active_sessions[session_id]
            
            logger.info(f"Interview completed for session {session_id}")
            
            return {
                'success': True,
                'session_id': session_id,
                'summary': summary_result.get('summary', '面試已完成'),
                'final_score': final_metrics.overall_score,
                'grade': summary_result.get('score', 'B'),
                'duration_minutes': round(session.duration_minutes, 1),
                'total_questions': session.question_count,
                'metrics': asdict(final_metrics),
                'recommendations': summary_result.get('recommendations', []),
                'interview_completed': True
            }
            
        except Exception as e:
            logger.error(f"Error ending interview: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_final_metrics(self, session: InterviewSession) -> InterviewMetrics:
        """Calculate final interview metrics"""
        # This is a simplified calculation - in practice, this would be more sophisticated
        
        # Base scores from conversation quality
        communication_score = min(100, max(50, 60 + session.question_count * 5))
        problem_solving_score = min(100, max(40, 55 + len(session.feedback_history) * 8))
        
        # Technical score already updated from code analysis
        technical_score = session.metrics.technical_score or 70
        
        # Calculate overall score
        overall_score = int(
            (technical_score * 0.4 +
             communication_score * 0.3 +
             problem_solving_score * 0.3)
        )
        
        # Determine response quality grade
        if overall_score >= 90:
            quality = "A+"
        elif overall_score >= 85:
            quality = "A"
        elif overall_score >= 80:
            quality = "B+"
        elif overall_score >= 75:
            quality = "B"
        elif overall_score >= 70:
            quality = "B-"
        elif overall_score >= 65:
            quality = "C+"
        elif overall_score >= 60:
            quality = "C"
        else:
            quality = "D"
        
        return InterviewMetrics(
            technical_score=technical_score,
            communication_score=communication_score,
            problem_solving_score=problem_solving_score,
            overall_score=overall_score,
            total_questions=session.question_count,
            correct_answers=max(1, session.question_count - 1),  # Simplified
            response_quality=quality
        )
    
    def get_active_sessions_count(self) -> int:
        """Get number of active sessions"""
        return len(self.active_sessions)
    
    def get_completed_sessions_count(self) -> int:
        """Get number of completed sessions"""
        return len(self.completed_sessions) 