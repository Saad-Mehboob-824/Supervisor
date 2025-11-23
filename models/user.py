"""
User model and MongoDB storage for Supervisor Agent.
"""
from datetime import datetime
import uuid
from typing import Optional, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from config import Config
from utils.logger import logger

class User:
    """User model for authentication and profile management."""
    
    def __init__(self, username: str, password: str = None, user_id: str = None, 
                 profile: Dict[str, Any] = None):
        self.username = username
        self.user_id = user_id or f"U_{uuid.uuid4().hex[:8]}"
        self.password_hash = generate_password_hash(password) if password else None
        self.profile = profile or {}
        self.created_at = None
        self.last_login = None
    
    def set_password(self, password: str):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if password matches."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            'username': self.username,
            'user_id': self.user_id,
            'profile': self.profile,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary."""
        user = cls(
            username=data['username'],
            user_id=data.get('user_id'),
            profile=data.get('profile', {})
        )
        user.password_hash = data.get('password_hash')
        user.created_at = data.get('created_at')
        user.last_login = data.get('last_login')
        return user

class MongoUserStorage:
    """MongoDB-based user storage."""
    
    def __init__(self):
        try:
            self.client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client[Config.MONGODB_DB_NAME]
            self.collection = self.db['users']
            
            # Create indexes
            self.collection.create_index('username', unique=True)
            self.collection.create_index('user_id', unique=True)
            self.collection.create_index('created_at')
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"MongoDB user storage initialized: {Config.MONGODB_DB_NAME}")
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"MongoDB initialization error: {str(e)}")
            raise
    
    def save_user(self, user: User) -> bool:
        """Save user to MongoDB."""
        try:
            if not user.created_at:
                user.created_at = datetime.now().isoformat()
            
            user_doc = {
                'username': user.username,
                'user_id': user.user_id,
                'password_hash': user.password_hash,
                'profile': user.profile,
                'created_at': user.created_at,
                'last_login': user.last_login
            }
            
            # Try to insert
            self.collection.insert_one(user_doc)
            logger.info(f'User saved: {user.username} ({user.user_id})')
            return True
            
        except DuplicateKeyError:
            logger.error(f'User already exists: {user.username}')
            return False
        except Exception as e:
            logger.error(f'Error saving user {user.username}: {str(e)}')
            return False
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        try:
            user_doc = self.collection.find_one({'username': username})
            if user_doc:
                return User.from_dict(user_doc)
            return None
        except Exception as e:
            logger.error(f'Error loading user {username}: {str(e)}')
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by user_id."""
        try:
            user_doc = self.collection.find_one({'user_id': user_id})
            if user_doc:
                return User.from_dict(user_doc)
            return None
        except Exception as e:
            logger.error(f'Error loading user by ID {user_id}: {str(e)}')
            return None
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists."""
        try:
            return self.collection.count_documents({'username': username}) > 0
        except Exception as e:
            logger.error(f'Error checking user existence: {str(e)}')
            return False
    
    def update_user(self, user: User) -> bool:
        """Update existing user."""
        try:
            result = self.collection.update_one(
                {'user_id': user.user_id},
                {'$set': {
                    'username': user.username,
                    'password_hash': user.password_hash,
                    'profile': user.profile,
                    'last_login': user.last_login
                }}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f'Error updating user {user.username}: {str(e)}')
            return False
    
    def close(self):
        """Close MongoDB connection."""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("MongoDB connection closed")

# Global user storage instance
user_storage = MongoUserStorage()
