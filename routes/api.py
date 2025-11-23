"""
Internal API routes for Worker Agent interaction.
"""
from flask import Blueprint, request, jsonify
from services.auth_service import auth_service
# Assuming a global state service exists or using a simple mock for now if not found
# I will check for a global state service, if not I'll implement a simple one here or in a service
# Based on file list, there is no explicit global state service. I'll check services/ again.
# For now I will implement the routes and use a placeholder or create a service.

api_bp = Blueprint('api', __name__)

# In-memory global state for demonstration if no DB is set up for it yet
# In a real app this should be in a database
global_state_store = {}

@api_bp.route('/internal/api/verify_user/<user_id>', methods=['GET'])
def verify_user(user_id):
    """Verify if a user exists."""
    user = auth_service.get_user_by_id(user_id)
    if user:
        return jsonify({'valid': True, 'user_id': user.user_id}), 200
    return jsonify({'valid': False, 'error': 'User not found'}), 404

@api_bp.route('/internal/api/profile/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Get user profile."""
    user = auth_service.get_user_by_id(user_id)
    if user:
        # Assuming user object has to_dict or similar, or constructing it
        # Based on auth_service usage in other files, it returns a User object
        return jsonify({
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            # Add other profile fields as needed
        }), 200
    return jsonify({'error': 'User not found'}), 404

@api_bp.route('/internal/api/global_state/<user_id>', methods=['GET'])
def get_global_state(user_id):
    """Get global state for a user."""
    # Verify user first
    user = auth_service.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    state = global_state_store.get(user_id, {})
    return jsonify(state), 200

@api_bp.route('/internal/api/global_state/<user_id>', methods=['POST'])
def update_global_state(user_id):
    """Update global state for a user."""
    # Verify user first
    user = auth_service.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    current_state = global_state_store.get(user_id, {})
    current_state.update(data)
    global_state_store[user_id] = current_state
    
    return jsonify({'status': 'success', 'state': current_state}), 200
