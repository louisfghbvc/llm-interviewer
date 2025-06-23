"""
Speech processing API endpoints
Handles speech-to-text and text-to-speech functionality
"""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io

from core.speech.stt import SpeechToTextService
from core.speech.tts import TextToSpeechService
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
stt_service = SpeechToTextService()
tts_service = TextToSpeechService()

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    speed: Optional[float] = None

@router.post("/stt")
async def speech_to_text(audio_file: UploadFile = File(...)):
    """
    Convert speech audio to text
    """
    try:
        # Validate file type
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Read audio data
        audio_data = await audio_file.read()
        
        # Convert to text
        text = await stt_service.transcribe(audio_data)
        
        return {
            "success": True,
            "text": text,
            "language": settings.stt_language
        }
        
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=f"Speech recognition failed: {str(e)}")

@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech audio
    """
    try:
        # Generate speech audio
        audio_data = await tts_service.synthesize(
            text=request.text,
            voice=request.voice or settings.tts_voice,
            speed=request.speed or settings.tts_speed
        )
        
        # Return audio stream
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")

@router.get("/stt/status")
async def get_stt_status():
    """Get STT service status"""
    return {
        "service": settings.stt_service,
        "language": settings.stt_language,
        "available": await stt_service.is_available()
    }

@router.get("/tts/status")
async def get_tts_status():
    """Get TTS service status"""
    return {
        "service": settings.tts_service,
        "voice": settings.tts_voice,
        "speed": settings.tts_speed,
        "available": await tts_service.is_available()
    }

@router.get("/tts/voices")
async def get_available_voices():
    """Get list of available TTS voices"""
    try:
        voices = await tts_service.get_available_voices()
        return {"voices": voices}
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available voices") 