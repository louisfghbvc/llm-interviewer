"""
Gemini LLM Client for AI Interview Simulator
Complete implementation with Google Gemini API integration
"""
import logging
import time
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai
from config import Config

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Complete LLM client for interview simulation using Google Gemini API
    """
    
    def __init__(self):
        """Initialize Gemini LLM client"""
        self.sessions: Dict[str, Dict] = {}
        self.model = None
        
        # Validate configuration
        if not Config.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not found in configuration")
            raise ValueError("GEMINI_API_KEY is required")
        
        try:
            # Configure Gemini API
            genai.configure(api_key=Config.GEMINI_API_KEY)
            
            # Initialize model
            self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
            
            logger.info(f"Gemini LLM client initialized successfully with model: {Config.GEMINI_MODEL}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def _get_interview_prompt(self, interview_type: str) -> str:
        """
        Get system prompt for different interview types
        
        Args:
            interview_type: Type of interview
            
        Returns:
            System prompt string
        """
        prompts = {
            'technical': """
你是一位經驗豐富的技術面試官。你的任務是：

1. 進行專業的技術面試，評估候選人的程式設計能力
2. 問題應該涵蓋：資料結構、演算法、系統設計、程式語言特性
3. 根據候選人回答調整問題難度
4. 提供建設性的回饋和追問
5. 保持友善但專業的語調
6. 每次只問一個問題，等待候選人回答

請開始面試並自我介紹。
            """,
            
            'behavioral': """
你是一位資深的人力資源面試官。你的任務是：

1. 評估候選人的軟技能和工作經驗
2. 使用 STAR 方法（Situation, Task, Action, Result）引導回答
3. 關注領導力、團隊合作、問題解決能力
4. 了解候選人的職涯規劃和動機
5. 保持同理心並營造舒適的面試環境
6. 深入挖掘具體的工作經驗和成就

請開始面試並自我介紹。
            """,
            
            'system_design': """
你是一位系統架構師，專門進行系統設計面試。你的任務是：

1. 評估候選人的系統設計和架構能力
2. 從高層設計開始，逐步深入技術細節
3. 關注可擴展性、可靠性、效能考量
4. 討論權衡取捨和技術選擇
5. 鼓勵候選人畫圖和說明架構
6. 模擬真實的業務需求場景

請開始面試並介紹今天的系統設計題目。
            """
        }
        
        return prompts.get(interview_type, prompts['technical'])
    
    def _call_gemini(self, prompt: str, conversation_history: List[str] = None) -> str:
        """
        Call Gemini API with error handling and retry logic
        
        Args:
            prompt: User prompt
            conversation_history: Previous conversation context
            
        Returns:
            Generated response
        """
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Prepare context with conversation history
                full_prompt = prompt
                if conversation_history:
                    context = "\n".join(conversation_history[-10:])  # Last 10 exchanges
                    full_prompt = f"對話歷史：\n{context}\n\n當前問題：{prompt}"
                
                # Generate response
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        candidate_count=1,
                        max_output_tokens=2048,
                        temperature=0.7,
                    )
                )
                
                if response.text:
                    return response.text.strip()
                else:
                    logger.warning("Empty response from Gemini API")
                    return "抱歉，我需要一點時間思考。請重新描述你的問題。"
                    
            except Exception as e:
                logger.warning(f"Gemini API call failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"All Gemini API attempts failed: {e}")
                    return "抱歉，目前遇到技術問題。請稍後再試。"
        
        return "系統暫時無法回應，請重試。"
    
    def start_interview(self, interview_type: str = 'technical') -> str:
        """
        Start a new interview session with Gemini
        
        Args:
            interview_type: Type of interview (technical, behavioral, system_design)
            
        Returns:
            Initial interview question from Gemini
        """
        try:
            # Generate unique session ID
            session_id = f"session_{int(time.time())}"
            
            # Initialize session data
            self.sessions[session_id] = {
                'type': interview_type,
                'history': [],
                'start_time': time.time(),
                'question_count': 0
            }
            
            # Get system prompt
            system_prompt = self._get_interview_prompt(interview_type)
            
            # Generate initial question
            initial_response = self._call_gemini(system_prompt)
            
            # Store in session history
            self.sessions[session_id]['history'].append(f"System: {system_prompt}")
            self.sessions[session_id]['history'].append(f"Interviewer: {initial_response}")
            self.sessions[session_id]['question_count'] += 1
            
            logger.info(f"Started {interview_type} interview session: {session_id}")
            
            return initial_response
            
        except Exception as e:
            logger.error(f"Error starting interview: {e}")
            return "歡迎參加面試！請先簡單自我介紹，然後我們開始今天的技術討論。"
    
    def get_response(self, message: str, session_id: str) -> str:
        """
        Get response from Gemini based on user message
        
        Args:
            message: User's message
            session_id: Session identifier
            
        Returns:
            Gemini response
        """
        try:
            # Check if session exists
            if session_id not in self.sessions:
                logger.warning(f"Session {session_id} not found, creating new one")
                self.sessions[session_id] = {
                    'type': 'technical',
                    'history': [],
                    'start_time': time.time(),
                    'question_count': 0
                }
            
            session = self.sessions[session_id]
            
            # Add user message to history
            session['history'].append(f"Candidate: {message}")
            
            # Prepare prompt for follow-up question
            interview_context = self._get_interview_prompt(session['type'])
            follow_up_prompt = f"""
基於以下面試背景：
{interview_context}

候選人剛才回答：{message}

請根據候選人的回答：
1. 給予簡短但建設性的回饋
2. 提出相關的追問或下一個問題
3. 保持面試的連續性和深度
4. 如果回答不夠詳細，請要求更多細節

回應應該專業且友善。
            """
            
            # Get response from Gemini
            response = self._call_gemini(follow_up_prompt, session['history'])
            
            # Store response in history
            session['history'].append(f"Interviewer: {response}")
            session['question_count'] += 1
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "感謝你的回答。能否請你詳細說明一下你的思考過程？"
    
    def analyze_code(self, code: str, language: str = 'python') -> Dict:
        """
        Analyze code submission using Gemini
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Analysis results
        """
        try:
            # Validate code length
            if len(code) > Config.MAX_CODE_LENGTH:
                return {
                    'score': 0,
                    'feedback': f"程式碼過長（{len(code)} 字符）。請提供較短的程式碼片段（最多 {Config.MAX_CODE_LENGTH} 字符）。",
                    'suggestions': ['減少程式碼長度'],
                    'language': language,
                    'complexity': 'Unknown'
                }
            
            # Prepare code analysis prompt
            analysis_prompt = f"""
請分析以下 {language} 程式碼：

```{language}
{code}
```

請提供：
1. 程式碼品質評分（0-100分）
2. 詳細的技術回饋
3. 具體的改進建議
4. 時間和空間複雜度分析
5. 潛在的 bug 或問題
6. 程式碼風格評估

請用繁體中文回應，格式化為結構化的分析報告。
            """
            
            # Get analysis from Gemini
            analysis_response = self._call_gemini(analysis_prompt)
            
            # Parse response (simplified scoring)
            score = self._extract_score_from_response(analysis_response)
            complexity = self._extract_complexity_from_response(analysis_response)
            
            return {
                'score': score,
                'feedback': analysis_response,
                'suggestions': self._extract_suggestions_from_response(analysis_response),
                'language': language,
                'complexity': complexity
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return {
                'score': 50,
                'feedback': f"程式碼分析遇到技術問題。基本觀察：這是一段 {language} 程式碼，建議檢查語法和邏輯。",
                'suggestions': ['檢查語法正確性', '確認邏輯流程', '添加適當註解'],
                'language': language,
                'complexity': 'Medium'
            }
    
    def end_interview(self, session_id: str) -> Dict:
        """
        End interview and generate summary using Gemini
        
        Args:
            session_id: Session identifier
            
        Returns:
            Interview summary
        """
        try:
            if session_id not in self.sessions:
                return {
                    'session_id': session_id,
                    'total_exchanges': 0,
                    'summary': "找不到面試會話記錄。",
                    'score': 'N/A',
                    'recommendations': ['請確認會話 ID 正確']
                }
            
            session = self.sessions[session_id]
            conversation_text = "\n".join(session['history'])
            
            # Generate summary prompt
            summary_prompt = f"""
以下是完整的面試對話記錄：

{conversation_text}

請提供完整的面試總結：
1. 候選人表現總評（A-F等級）
2. 技術能力評估
3. 回答品質分析
4. 具體的改進建議
5. 整體印象和建議

請用繁體中文提供專業的面試總結。
            """
            
            # Get summary from Gemini
            summary_response = self._call_gemini(summary_prompt)
            
            # Extract score
            score = self._extract_grade_from_response(summary_response)
            
            # Calculate session stats
            duration = time.time() - session['start_time']
            
            result = {
                'session_id': session_id,
                'total_exchanges': session['question_count'],
                'duration_minutes': round(duration / 60, 1),
                'interview_type': session['type'],
                'summary': summary_response,
                'score': score,
                'recommendations': self._extract_recommendations_from_response(summary_response)
            }
            
            # Clean up session
            del self.sessions[session_id]
            
            return result
            
        except Exception as e:
            logger.error(f"Error ending interview: {e}")
            return {
                'session_id': session_id,
                'total_exchanges': 0,
                'summary': "面試總結產生遇到技術問題。建議重新檢視面試過程。",
                'score': 'B',
                'recommendations': ['持續練習技術問題', '加強表達能力']
            }
    
    def _extract_score_from_response(self, response: str) -> int:
        """Extract numeric score from response"""
        import re
        
        # Look for patterns like "評分：85分" or "分數：85"
        patterns = [
            r'評分[：:]\s*(\d+)',
            r'分數[：:]\s*(\d+)',
            r'得分[：:]\s*(\d+)',
            r'(\d+)\s*分'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                score = int(match.group(1))
                return min(max(score, 0), 100)  # Ensure 0-100 range
        
        return 75  # Default score
    
    def _extract_complexity_from_response(self, response: str) -> str:
        """Extract complexity assessment from response"""
        complexity_keywords = {
            'O(1)': 'Low',
            'O(log n)': 'Low',
            'O(n)': 'Medium',
            'O(n log n)': 'Medium',
            'O(n²)': 'High',
            'O(2^n)': 'Very High'
        }
        
        for keyword, level in complexity_keywords.items():
            if keyword in response:
                return level
        
        return 'Medium'  # Default
    
    def _extract_suggestions_from_response(self, response: str) -> List[str]:
        """Extract suggestions from response"""
        import re
        
        # Look for numbered lists or bullet points
        suggestions = []
        
        # Pattern for numbered items
        numbered_items = re.findall(r'\d+[\.、]\s*([^。\n]+)', response)
        suggestions.extend(numbered_items[:5])  # Max 5 suggestions
        
        # Pattern for bullet points
        if not suggestions:
            bullet_items = re.findall(r'[•\-\*]\s*([^。\n]+)', response)
            suggestions.extend(bullet_items[:5])
        
        # Default suggestions if none found
        if not suggestions:
            suggestions = ['檢查程式碼邏輯', '改善變數命名', '添加適當註解']
        
        return suggestions
    
    def _extract_grade_from_response(self, response: str) -> str:
        """Extract grade from response"""
        import re
        
        # Look for grade patterns
        grade_pattern = r'[等級評分][：:]\s*([A-F][+\-]?)'
        match = re.search(grade_pattern, response)
        
        if match:
            return match.group(1)
        
        # Look for direct grade mentions
        grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F']
        for grade in grades:
            if grade in response:
                return grade
        
        return 'B'  # Default grade
    
    def _extract_recommendations_from_response(self, response: str) -> List[str]:
        """Extract recommendations from response"""
        import re
        
        recommendations = []
        
        # Look for recommendation sections
        rec_patterns = [
            r'建議[：:]([^。\n]+)',
            r'改進方向[：:]([^。\n]+)',
            r'下一步[：:]([^。\n]+)'
        ]
        
        for pattern in rec_patterns:
            matches = re.findall(pattern, response)
            recommendations.extend(matches)
        
        if not recommendations:
            recommendations = ['持續練習', '加強基礎知識', '提升表達能力']
        
        return recommendations[:3]  # Max 3 recommendations 