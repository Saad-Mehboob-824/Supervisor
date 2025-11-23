"""
Configuration settings for the Supervisor Agent.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the Supervisor Flask application"""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supervisor-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 3002))
    
    # CORS configuration
    CORS_ORIGINS = [
        'http://localhost:3002',
        'http://127.0.0.1:3002',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://localhost:5500',
        'http://127.0.0.1:5500',
        '*'  # Allow all for development
    ]
    
    # Worker Agent configuration
    WORKER_AGENT_URL = os.environ.get('WORKER_AGENT_URL', 'http://localhost:8000')
    WORKER_AGENT_TIMEOUT = int(os.environ.get('WORKER_AGENT_TIMEOUT', 30))
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # MongoDB configuration
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME', 'supervisor_db')
    
    # Session configuration
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('PERMANENT_SESSION_LIFETIME', 86400))  # 24 hours
    
    # Agent configuration
    AGENT_ID = os.environ.get('AGENT_ID') or 'supervisor-agent-001'
    AGENT_VERSION = os.environ.get('AGENT_VERSION') or '1.0.0'
    AGENT_NAME = 'Sleep Optimizer Supervisor Agent'
    AGENT_DESCRIPTION = 'Supervisor agent for managing users and coordinating sleep analysis'
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', os.path.join(BASE_DIR, 'instance', 'logs', 'supervisor.log'))
    
    # API configuration
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False

