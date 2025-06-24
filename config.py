"""
Configuration settings for AI Interview Simulator MVP
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Flask application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Google Gemini API
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-pro')
    
    # Application settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    JSON_SORT_KEYS = False
    
    # Interview settings
    DEFAULT_INTERVIEW_TYPE = 'technical'
    MAX_SESSION_TIME = 3600  # 1 hour in seconds
    
    # Code analysis settings
    MAX_CODE_LENGTH = 10000  # Maximum characters in code submission
    SUPPORTED_LANGUAGES = ['python', 'javascript', 'java', 'cpp', 'c', 'go', 'rust']
    
    @staticmethod
    def validate_config():
        """Validate required configuration"""
        errors = []
        
        if not Config.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is required")
            
        return errors

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 