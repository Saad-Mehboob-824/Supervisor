"""
Profile management routes for Supervisor Agent.
"""
from flask import Blueprint, request, jsonify, session

try:
    from services.auth_service import auth_service
    from utils.logger import logger
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from services.auth_service import auth_service
    from utils.logger import logger

profile_bp = Blueprint('profile', __name__)

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

@profile_bp.route('/api/profile', methods=['GET'])
def get_profile():
    """Get current user's profile."""
    try:
        # Check if user_id is provided as query parameter (for cross-origin access from worker agent)
        user_id_param = request.args.get('user_id')
        
        if user_id_param:
            # Validate user_id from parameter
            user = auth_service.get_user_by_id(user_id_param)
            if not user:
                return jsonify({
                    'error': 'User not found',
                    'code': 'USER_NOT_FOUND'
                }), 404
            
            return jsonify({
                'profile': user.profile,
                'user_id': user.user_id
            }), 200
        
        # Otherwise, use session-based authentication
        user, error_response, status_code = require_auth()
        if error_response:
            return error_response, status_code
        
        return jsonify({
            'profile': user.profile,
            'user_id': user.user_id
        }), 200
        
    except Exception as e:
        logger.error(f'Get profile endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

@profile_bp.route('/api/profile', methods=['PUT'])
def update_profile():
    """Update current user's profile."""
    try:
        # Check if user_id is provided as query parameter (for cross-origin access from worker agent)
        user_id_param = request.args.get('user_id')
        
        if user_id_param:
            # Validate user_id from parameter
            user = auth_service.get_user_by_id(user_id_param)
            if not user:
                return jsonify({
                    'error': 'User not found',
                    'code': 'USER_NOT_FOUND'
                }), 404
        else:
            # Otherwise, use session-based authentication
            user, error_response, status_code = require_auth()
            if error_response:
                return error_response, status_code
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'code': 'INVALID_REQUEST'
            }), 400
        
        # Update profile with new data
        profile = data.get('profile', {})
        if profile:
            # Merge with existing profile
            user.profile.update(profile)
            
            # Save updated user
            from models.user import user_storage
            if user_storage.update_user(user):
                logger.info(f'Profile updated for user {user.user_id}')
                return jsonify({
                    'success': True,
                    'profile': user.profile,
                    'user_id': user.user_id,
                    'message': 'Profile updated successfully'
                }), 200
            else:
                return jsonify({
                    'error': 'Failed to update profile',
                    'code': 'UPDATE_ERROR'
                }), 500
        
        return jsonify({
            'error': 'No profile data provided',
            'code': 'MISSING_DATA'
        }), 400
        
    except Exception as e:
        logger.error(f'Update profile endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

