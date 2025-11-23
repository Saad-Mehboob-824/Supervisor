"""
Worker agent integration routes.
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

worker_bp = Blueprint('worker', __name__)

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

@worker_bp.route('/api/worker/health', methods=['GET'])
def check_worker_health():
    """Check worker agent health."""
    try:
        health = worker_client.check_health()
        
        if health is None:
            return jsonify({
                'status': 'unavailable',
                'message': 'Worker agent is not responding'
            }), 503
        
        return jsonify(health), 200
        
    except Exception as e:
        logger.error(f'Worker health check error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

@worker_bp.route('/api/worker/register', methods=['POST'])
def register_worker():
    """Register with worker agent."""
    try:
        result = worker_client.register_worker()
        
        if result is None:
            return jsonify({
                'error': 'Failed to register with worker agent',
                'code': 'WORKER_AGENT_ERROR'
            }), 503
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'Worker registration error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

