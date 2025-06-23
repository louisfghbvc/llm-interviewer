"""
LLM processing API endpoints
Handles Gemini LLM interactions and interview logic
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from core.llm.gemini_client import GeminiClient
from core.llm.interviewer import InterviewerAgent
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
gemini_client = GeminiClient()
interviewer = InterviewerAgent()

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    interview_type: str = "technical"
    context: Optional[Dict[str, Any]] = None
    history: Optional[List[ChatMessage]] = None

class CodeAnalysisRequest(BaseModel):
    code: str
    language: str = "python"
    interview_type: str = "technical"

class InterviewStartRequest(BaseModel):
    interview_type: str = "technical"
    candidate_name: Optional[str] = None
    position: Optional[str] = None

@router.post("/chat")
async def chat_with_interviewer(request: ChatRequest):
    """
    Chat with the AI interviewer
    """
    try:
        # Generate response using interviewer agent
        response = await interviewer.generate_response(
            message=request.message,
            interview_type=request.interview_type,
            context=request.context or {},
            history=request.history or []
        )
        
        return {
            "success": True,
            "response": response["content"],
            "interview_type": request.interview_type,
            "metadata": response.get("metadata", {}),
            "suggestions": response.get("suggestions", [])
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.post("/analyze-code")
async def analyze_code(request: CodeAnalysisRequest):
    """
    Analyze code and provide feedback
    """
    try:
        # Analyze code using interviewer
        analysis = await interviewer.analyze_code(
            code=request.code,
            language=request.language,
            interview_type=request.interview_type
        )
        
        return {
            "success": True,
            "analysis": analysis["content"],
            "score": analysis.get("score", 0),
            "suggestions": analysis.get("suggestions", []),
            "complexity": analysis.get("complexity", {}),
            "issues": analysis.get("issues", [])
        }
        
    except Exception as e:
        logger.error(f"Code analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Code analysis failed: {str(e)}")

@router.post("/start-interview")
async def start_interview(request: InterviewStartRequest):
    """
    Start a new interview session
    """
    try:
        # Initialize interview session
        session = await interviewer.start_interview(
            interview_type=request.interview_type,
            candidate_name=request.candidate_name,
            position=request.position
        )
        
        return {
            "success": True,
            "session_id": session["session_id"],
            "welcome_message": session["welcome_message"],
            "interview_type": request.interview_type,
            "estimated_duration": session.get("estimated_duration", "30-60 minutes")
        }
        
    except Exception as e:
        logger.error(f"Start interview error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")

@router.post("/end-interview/{session_id}")
async def end_interview(session_id: str):
    """
    End interview session and provide summary
    """
    try:
        # Generate interview summary
        summary = await interviewer.end_interview(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "summary": summary["content"],
            "score": summary.get("overall_score", 0),
            "strengths": summary.get("strengths", []),
            "areas_for_improvement": summary.get("areas_for_improvement", []),
            "recommendations": summary.get("recommendations", [])
        }
        
    except Exception as e:
        logger.error(f"End interview error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to end interview: {str(e)}")

@router.get("/interview-types")
async def get_interview_types():
    """Get available interview types"""
    return {
        "types": [
            {
                "id": "technical",
                "name": "技術面試",
                "description": "評估程式設計能力和技術知識",
                "duration": "45-60 minutes"
            },
            {
                "id": "behavioral",
                "name": "行為面試",
                "description": "評估軟技能和文化契合度",
                "duration": "30-45 minutes"
            },
            {
                "id": "system_design",
                "name": "系統設計",
                "description": "評估系統架構和設計能力",
                "duration": "60-90 minutes"
            }
        ]
    }

@router.get("/status")
async def get_llm_status():
    """Get LLM service status"""
    try:
        status = await gemini_client.check_status()
        return {
            "model": settings.gemini_model,
            "available": status,
            "max_tokens": gemini_client.max_tokens,
            "temperature": gemini_client.temperature
        }
    except Exception as e:
        logger.error(f"LLM status error: {e}")
        return {
            "model": settings.gemini_model,
            "available": False,
            "error": str(e)
        }

@router.post("/generate-question")
async def generate_question(interview_type: str, difficulty: str = "medium"):
    """
    Generate a new interview question
    """
    try:
        question = await interviewer.generate_question(
            interview_type=interview_type,
            difficulty=difficulty
        )
        
        return {
            "success": True,
            "question": question["content"],
            "type": interview_type,
            "difficulty": difficulty,
            "expected_duration": question.get("expected_duration", "5-10 minutes"),
            "hints": question.get("hints", [])
        }
        
    except Exception as e:
        logger.error(f"Generate question error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate question: {str(e)}") 