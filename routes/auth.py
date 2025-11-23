"""
Authentication routes for Supervisor Agent.
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

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'code': 'INVALID_REQUEST'
            }), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        profile = data.get('profile', {})
        
        user, error = auth_service.register_user(username, password, profile)
        
        if error:
            return jsonify({
                'error': error,
                'code': 'REGISTRATION_ERROR'
            }), 400
        
        # Set session
        session['user_id'] = user.user_id
        session['username'] = user.username
        session.permanent = True
        
        logger.info(f'User registered and logged in: {username}')
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'Registration endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'code': 'INVALID_REQUEST'
            }), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        user, error = auth_service.authenticate_user(username, password)
        
        if error:
            return jsonify({
                'error': error,
                'code': 'AUTHENTICATION_ERROR'
            }), 401
        
        # Set session
        session['user_id'] = user.user_id
        session['username'] = user.username
        session.permanent = True
        
        logger.info(f'User logged in: {username}')
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'Login endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user."""
    try:
        username = session.get('username', 'Unknown')
        session.clear()
        logger.info(f'User logged out: {username}')
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        logger.error(f'Logout endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

@auth_bp.route('/current-user', methods=['GET'])
def get_current_user():
    """Get current logged-in user."""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'error': 'Not authenticated',
                'code': 'NOT_AUTHENTICATED'
            }), 401
        
        user = auth_service.get_user_by_id(user_id)
        if not user:
            session.clear()
            return jsonify({
                'error': 'User not found',
                'code': 'USER_NOT_FOUND'
            }), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'Current user endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

