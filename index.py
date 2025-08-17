import os
import sys
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Store the main error for the error app
main_app_error = None

try:
    # Import the main Flask application
    from app import app
    logger.info("Successfully imported main app")
    application = app
    
except Exception as e:
    main_app_error = e
    logger.error(f"Error importing main app: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Create a minimal error app
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return jsonify({
            'error': 'Application failed to start',
            'details': str(main_app_error),
            'message': 'Check server logs for more details'
        }), 500
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'error', 'message': 'Application not healthy'})
    
    application = app

# For local development
if __name__ == "__main__":
    application.run(debug=True, host='0.0.0.0', port=5000)
