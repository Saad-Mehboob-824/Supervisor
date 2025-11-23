"""
Main Flask application for Sleep Optimizer Supervisor Agent.
"""
from flask import Flask, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS

try:
    from config import Config
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.memory import memory_bp
    from routes.worker import worker_bp
    from utils.logger import logger, setup_logger
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config import Config
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.memory import memory_bp
    from routes.worker import worker_bp
    from utils.logger import logger, setup_logger

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)
    
    # Configure CORS
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(memory_bp)
    app.register_blueprint(worker_bp)
    
    # Register internal API blueprint
    try:
        from routes.api import api_bp
        app.register_blueprint(api_bp)
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from routes.api import api_bp
        app.register_blueprint(api_bp)
    
    # Import and register profile blueprint
    try:
        from routes.profile import profile_bp
        app.register_blueprint(profile_bp)
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from routes.profile import profile_bp
        app.register_blueprint(profile_bp)
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint - redirect to login or dashboard."""
        if session.get('user_id'):
            return redirect(url_for('dashboard.dashboard'))
        return redirect('/login')
    
    @app.route('/login', methods=['GET'])
    def login_page():
        """Login page."""
        if session.get('user_id'):
            return redirect('/dashboard')
        return render_template('login.html')
    
    @app.route('/register', methods=['GET'])
    def register_page():
        """Registration page."""
        if session.get('user_id'):
            return redirect('/dashboard')
        return render_template('register.html')
    
    # Root endpoint with agent information
    @app.route('/api', methods=['GET'])
    def api_info():
        """API information endpoint."""
        return jsonify({
            'agent': Config.AGENT_NAME,
            'agent_id': Config.AGENT_ID,
            'version': Config.AGENT_VERSION,
            'status': 'running',
            'endpoints': {
                'register': '/register',
                'login': '/login',
                'logout': '/logout',
                'current_user': '/current-user',
                'dashboard': '/dashboard',
                'recommendations': '/api/recommendations',
                'analyze': '/api/analyze',
                'memory': '/api/memory',
                'worker_health': '/api/worker/health'
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint not found',
            'code': 'NOT_FOUND',
            'details': {}
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'Method not allowed',
            'code': 'METHOD_NOT_ALLOWED',
            'details': {}
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal server error: {str(error)}')
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': {}
        }), 500
    
    logger.info(f'{Config.AGENT_NAME} initialized')
    logger.info(f'Agent ID: {Config.AGENT_ID}')
    logger.info(f'Version: {Config.AGENT_VERSION}')
    logger.info(f'Worker Agent URL: {Config.WORKER_AGENT_URL}')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )

