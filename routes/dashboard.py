"""
Dashboard routes for Supervisor Agent.
"""
import json
from flask import Blueprint, request, jsonify, session, render_template

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

dashboard_bp = Blueprint('dashboard', __name__)

def require_auth():
    """Check if user is authenticated."""
    user_id = session.get('user_id')
    if not user_id:
        return None, None
    
    user = auth_service.get_user_by_id(user_id)
    if not user:
        session.clear()
        return None, None
    
    return user, None

@dashboard_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Main dashboard page."""
    try:
        user, _ = require_auth()
        if not user:
            return render_template('login.html'), 200
        
        return render_template('dashboard.html', user=user.to_dict())
        
    except Exception as e:
        logger.error(f'Dashboard endpoint error: {str(e)}')
        return render_template('login.html'), 200

@dashboard_bp.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """
    Get recommendations for current user.
    Triggers a fresh analysis using existing user data from worker agent's storage.
    """
    try:
        user, _ = require_auth()
        if not user:
            return jsonify({
                'error': 'Not authenticated',
                'code': 'NOT_AUTHENTICATED'
            }), 401
        
        logger.info(f'\n{"="*80}\nRECOMMENDATIONS ENDPOINT - REQUEST\n{"="*80}')
        logger.info(f'User ID: {user.user_id}')
        logger.info('Triggering fresh analysis to generate recommendations...')
        
        # Trigger fresh analysis with existing data (no new sessions)
        # Backend will fetch all existing STM/LTM data for this user
        analysis_result = worker_client.send_task(
            user_id=user.user_id,
            profile=user.profile,
            sleep_sessions=[]  # Empty list - backend will use existing stored sessions
        )
        
        if analysis_result is None:
            logger.warning('Analysis failed - worker agent may be unavailable')
            # Return empty recommendations if worker agent is unavailable
            response = {
                'sleep_score': None,
                'confidence': None,
                'issues': [],
                'recommendations': {},
                'personalized_tips': [],
                'available': False
            }
        elif analysis_result.get('status') == 'error':
            logger.error(f'Analysis error: {analysis_result.get("error")}')
            response = {
                'sleep_score': None,
                'confidence': None,
                'issues': [],
                'recommendations': {},
                'personalized_tips': [],
                'available': False,
                'error': analysis_result.get('error', 'Analysis failed')
            }
        else:
            # Extract recommendations from analysis result
            result_data = analysis_result.get('result', {})
            
            response = {
                'sleep_score': result_data.get('sleep_score'),
                'confidence': result_data.get('confidence'),
                'issues': result_data.get('issues', []),
                'recommendations': result_data.get('recommendations', {}),
                'personalized_tips': result_data.get('personalized_tips', []),
                'available': True
            }
            
            logger.info(f'Fresh analysis completed successfully')
        
        # Log response being sent to client
        logger.info(f'\n{"="*80}\nRECOMMENDATIONS ENDPOINT - RESPONSE TO CLIENT\n{"="*80}')
        try:
            response_str = json.dumps(response, indent=2)
            logger.info(f'Response Data:\n{response_str}')
        except Exception:
            logger.info(f'Response Data: {response}')
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f'Recommendations endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

@dashboard_bp.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Trigger analysis via worker agent.
    Only sends new sleep sessions. Backend will automatically fetch
    all existing STM/LTM data for the user from its storage.
    """
    try:
        user, _ = require_auth()
        if not user:
            return jsonify({
                'error': 'Not authenticated',
                'code': 'NOT_AUTHENTICATED'
            }), 401
        
        data = request.get_json()
        profile = data.get('profile', user.profile)
        
        # Only send NEW sleep sessions (not all sessions)
        # Backend will fetch existing sessions from its STM/LTM storage
        sleep_sessions = data.get('sleep_sessions', [])
        
        # Log incoming request data
        logger.info(f'\n{"="*80}\nANALYZE ENDPOINT - INCOMING REQUEST\n{"="*80}')
        logger.info(f'User ID: {user.user_id}')
        logger.info(f'New Sessions Count: {len(sleep_sessions)}')
        try:
            request_data = {
                'profile': profile,
                'sleep_sessions': sleep_sessions
            }
            request_str = json.dumps(request_data, indent=2)
            logger.info(f'Request Data:\n{request_str}')
        except Exception:
            logger.info(f'Request Data: profile={profile}, sessions_count={len(sleep_sessions)}')
        
        # Send task to worker agent
        # Backend will automatically map and retrieve all existing STM/LTM data
        result = worker_client.send_task(
            user_id=user.user_id,
            profile=profile,
            sleep_sessions=sleep_sessions  # Only new sessions
        )
        
        if result is None:
            logger.error('Worker agent returned None - agent may be unavailable')
            return jsonify({
                'error': 'Failed to analyze data. Worker agent may be unavailable.',
                'code': 'WORKER_AGENT_ERROR'
            }), 503
        
        if result.get('status') == 'error':
            logger.error(f'Worker agent returned error: {result.get("error")}')
            return jsonify({
                'error': result.get('error', 'Analysis failed'),
                'code': 'ANALYSIS_ERROR'
            }), 500
        
        # Extract result data
        analysis_result = result.get('result', {})
        
        # Log response being sent to client
        logger.info(f'\n{"="*80}\nANALYZE ENDPOINT - RESPONSE TO CLIENT\n{"="*80}')
        try:
            response_data = {
                'success': True,
                'result': analysis_result
            }
            response_str = json.dumps(response_data, indent=2)
            logger.info(f'Response Data:\n{response_str}')
        except Exception:
            logger.info(f'Response Data: success=True, result_keys={list(analysis_result.keys()) if analysis_result else []}')
        
        return jsonify({
            'success': True,
            'result': analysis_result
        }), 200
        
    except Exception as e:
        logger.error(f'Analyze endpoint error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

