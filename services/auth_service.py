"""
Authentication service for Supervisor Agent.
"""
from datetime import datetime
from typing import Optional
from datetime import datetime
from typing import Optional

try:
    from models.user import User, user_storage
    from utils.logger import logger
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models.user import User, user_storage
    from utils.logger import logger

class AuthService:
    """Handles authentication operations."""
    
    @staticmethod
    def register_user(username: str, password: str, profile: dict = None) -> tuple[Optional[User], Optional[str]]:
        """
        Register a new user.
        
        Returns:
            (User, None) on success, (None, error_message) on failure
        """
        if not username or not password:
            return None, "Username and password are required"
        
        if len(username) < 3:
            return None, "Username must be at least 3 characters"
        
        if len(password) < 6:
            return None, "Password must be at least 6 characters"
        
        if user_storage.user_exists(username):
            return None, "Username already exists"
        
        try:
            user = User(username=username, password=password, profile=profile or {})
            if user_storage.save_user(user):
                logger.info(f'User registered: {username}')
                return user, None
            else:
                return None, "Failed to save user"
        except Exception as e:
            logger.error(f'Registration error: {str(e)}')
            return None, f"Registration failed: {str(e)}"
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> tuple[Optional[User], Optional[str]]:
        """
        Authenticate a user.
        
        Returns:
            (User, None) on success, (None, error_message) on failure
        """
        if not username or not password:
            return None, "Username and password are required"
        
        user = user_storage.get_user_by_username(username)
        if not user:
            return None, "Invalid username or password"
        
        if not user.check_password(password):
            return None, "Invalid username or password"
        
        # Update last login
        user.last_login = datetime.now().isoformat()
        user_storage.update_user(user)
        
        logger.info(f'User authenticated: {username}')
        return user, None
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by user_id."""
        return user_storage.get_user_by_id(user_id)

auth_service = AuthService()

