import sys
import os
import logging

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from launchpad_api.main import get_main_app
    
    # Get Connexion app
    logger.info("Initializing application...")
    connexion_app = get_main_app()
    
    # Extract actual Flask app from it
    app = connexion_app.app
    logger.info("Application initialized successfully")
    
except Exception as e:
    logger.error(f"Failed to initialize application: {str(e)}", exc_info=True)
    # Create a minimal app that at least binds to port
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return {'status': 'error', 'message': f'Application failed to start: {str(e)}'}, 500
    
    logger.error("Created minimal error app")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting application on port {port}")
    app.run(port=port, debug=False, host='0.0.0.0')
