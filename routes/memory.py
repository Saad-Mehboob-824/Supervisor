"""
Memory management routes for Supervisor Agent.
"""
from flask import Blueprint, request, jsonify, session

try:
    from services.worker_client import worker_client
    from services.auth_service import auth_service
    from utils.logger import logger
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from services.worker_client import worker_client
    from services.auth_service import auth_service
    from utils.logger import logger

memory_bp = Blueprint('memory', __name__)

def require_auth():
    """Check if user is authenticated."""
    user_id = session.get('user_id')
    if not user_id:
        return None, jsonify({
            'error': 'Not authenticated',
            'code': 'NOT_AUTHENTICATED'
        }), 401
    
    user = auth_service.get_user_by_id(user_id)
    if not user:
        session.clear()
        return None, jsonify({
            'error': 'User not found',
            'code': 'USER_NOT_FOUND'
        }), 404
    
    return user, None, None

@memory_bp.route('/api/memory', methods=['GET'])
def get_memory():
    """Get user's memory from worker agent."""
    try:
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        memory = worker_client.get_memory(user.user_id)
        
        if memory is None:
            return jsonify({
                'error': 'Failed to fetch memory from worker agent',
                'code': 'WORKER_AGENT_ERROR',
                'memory': {
                    'stm': {'sessions': [], 'count': 0},
                    'ltm': {'trends': {}, 'patterns': [], 'preferences': {}, 'available': False}
                }
            }), 200
        
        return jsonify({
            'user_id': user.user_id,
            'memory': memory
        }), 200
        
    except Exception as e:
        logger.error(f'Memory endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

