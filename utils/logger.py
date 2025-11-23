"""
Logging utility for Supervisor Agent.
"""
import logging
import os
from datetime import datetime
from config import Config

def setup_logger():
    """Setup and configure logger."""
    logger = logging.getLogger('supervisor_agent')
    logger.setLevel(getattr(logging, Config.LOG_LEVEL, logging.INFO))
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(Config.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # File handler
    if Config.LOG_FILE:
        file_handler = logging.FileHandler(Config.LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

def log_with_context(logger, level, message, **context):
    """Log message with additional context."""
    context_str = ' '.join([f'{k}={v}' for k, v in context.items()])
    full_message = f'{message} {context_str}' if context_str else message
    getattr(logger, level.lower())(full_message)

