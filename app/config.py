"""
Application configuration settings
"""
import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    gemini_api_key: str
    openai_api_key: Optional[str] = None
    
    # LLM Configuration
    gemini_model: str = "gemini-pro"
    
    # Speech Configuration
    stt_service: str = "whisper"  # whisper, google
    stt_language: str = "zh-TW"
    tts_service: str = "edge"     # edge, gtts, openai
    tts_voice: str = "zh-TW-HsiaoChenNeural"
    tts_speed: float = 1.0
    
    # Web Scraping Configuration
    scraping_interval: int = 10   # seconds
    selenium_driver: str = "chrome"
    headless_mode: bool = True
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Security
    secret_key: str
    
    # LeetCode Configuration
    leetcode_session_cookie: Optional[str] = None
    leetcode_csrf_token: Optional[str] = None
    
    # Interview Configuration
    default_interview_type: str = "technical"
    max_conversation_history: int = 50
    interview_timeout: int = 3600  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Audio configuration
AUDIO_CONFIG = {
    "sample_rate": 16000,
    "channels": 1,
    "chunk_size": 1024,
    "format": "wav"
}

# LeetCode URLs and selectors
LEETCODE_CONFIG = {
    "base_url": "https://leetcode.com",
    "playground_selector": "#app > div > div > div.h-full.flex-1.flex.overflow-hidden > div.flex.h-full > div.h-full.flex.flex-col.flex-1 > div > div.flex.flex-col.h-full.overflow-hidden > div.h-full.overflow-hidden > div > div > div > div.flex.h-full > div.h-full.w-full.overflow-hidden > div > div.h-full.w-full.flex.flex-col.overflow-hidden > div.flex-1.overflow-hidden > div > div",
    "result_selector": "#qd-content > div.h-full.flex-1.flex.overflow-hidden > div.flex.h-full > div.h-full.flex.flex-col.flex-1 > div > div.flex.flex-col.h-full.overflow-hidden > div.h-full.overflow-hidden > div > div > div > div.flex.h-full > div.h-full.flex.flex-col.overflow-hidden.relative > div.relative.h-full.flex.flex-col.overflow-hidden > div.flex-1.overflow-hidden > div"
}

# Interview prompts and templates
INTERVIEW_PROMPTS = {
    "technical": {
        "system": """你是一位專業的技術面試官，專門負責軟體工程師的技術面試。
        你的任務是：
        1. 評估候選人的程式設計能力
        2. 分析他們的程式碼品質和邏輯思維
        3. 提供建設性的回饋和建議
        4. 引導候選人思考更好的解決方案
        
        請用繁體中文進行對話，但程式碼註解請用英文。""",
        
        "code_analysis": """請分析以下程式碼：
        
        {code}
        
        請評估：
        1. 邏輯正確性
        2. 程式碼品質
        3. 時間/空間複雜度
        4. 可能的改進建議"""
    },
    
    "behavioral": {
        "system": """你是一位經驗豐富的HR面試官，專門負責行為面試。
        你的任務是：
        1. 評估候選人的軟技能
        2. 了解他們的工作經驗和團隊合作能力
        3. 評估文化契合度
        4. 提供職涯發展建議
        
        請用繁體中文進行友善且專業的對話。"""
    },
    
    "system_design": {
        "system": """你是一位資深的系統架構師，負責系統設計面試。
        你的任務是：
        1. 評估候選人的系統設計能力
        2. 引導他們思考擴展性、可靠性等問題
        3. 討論技術選型和權衡考量
        4. 提供架構設計的建議
        
        請用繁體中文進行技術討論。"""
    }
} 