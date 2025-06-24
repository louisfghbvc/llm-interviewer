"""
LLM Client for AI Interview Simulator MVP
This is a placeholder implementation - will be completed in Task 2
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Simplified LLM client for interview simulation
    Full implementation will be added in Task 2
    """
    
    def __init__(self):
        """Initialize LLM client"""
        self.sessions: Dict[str, list] = {}
        logger.info("LLM Client initialized (placeholder)")
    
    def start_interview(self, interview_type: str = 'technical') -> str:
        """
        Start a new interview session
        
        Args:
            interview_type: Type of interview (technical, behavioral, system_design)
            
        Returns:
            Initial interview question
        """
        # Placeholder implementation
        questions = {
            'technical': "請先自我介紹一下，然後我們會開始技術問題。",
            'behavioral': "請談談你最具挑戰性的專案經驗。",
            'system_design': "我們將進行系統設計面試，請先自我介紹。"
        }
        
        return questions.get(interview_type, questions['technical'])
    
    def get_response(self, message: str, session_id: str) -> str:
        """
        Get response from LLM based on user message
        
        Args:
            message: User's message
            session_id: Session identifier
            
        Returns:
            LLM response
        """
        # Placeholder implementation
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append(f"User: {message}")
        
        # Simple placeholder responses
        response = f"感謝您的回答：'{message}'。這是一個很好的觀點。請繼續詳細說明。"
        
        self.sessions[session_id].append(f"Assistant: {response}")
        
        return response
    
    def analyze_code(self, code: str, language: str = 'python') -> Dict:
        """
        Analyze code submission
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Analysis results
        """
        # Placeholder implementation
        return {
            'score': 75,
            'feedback': f"程式碼看起來不錯！這是 {language} 代碼的基本分析。完整實現將在任務 6 中完成。",
            'suggestions': [
                "考慮添加更多註解",
                "檢查邊界條件處理"
            ],
            'language': language,
            'complexity': 'Medium'
        }
    
    def end_interview(self, session_id: str) -> Dict:
        """
        End interview and generate summary
        
        Args:
            session_id: Session identifier
            
        Returns:
            Interview summary
        """
        # Placeholder implementation
        conversation_length = len(self.sessions.get(session_id, []))
        
        return {
            'session_id': session_id,
            'total_exchanges': conversation_length // 2,
            'summary': "面試已結束。這是一個基本總結 - 完整功能將在後續任務中實現。",
            'score': 'B+',
            'recommendations': [
                "繼續練習技術問題",
                "加強系統設計能力"
            ]
        } 