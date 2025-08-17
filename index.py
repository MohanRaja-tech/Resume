import os
import sys
import traceback
import logging

# Configure logging to capture detailed errors
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def create_error_app(error_msg, traceback_msg=None):
    """Create a minimal Flask app that shows error details"""
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def show_error():
        return jsonify({
            'status': 'error',
            'error': error_msg,
            'traceback': traceback_msg,
            'python_version': sys.version,
            'environment_vars': {
                'SECRET_KEY': 'present' if os.getenv('SECRET_KEY') else 'missing',
                'FLASK_ENV': os.getenv('FLASK_ENV', 'not_set'),
                'MONGODB_URI': 'present' if os.getenv('MONGODB_URI') else 'missing',
                'RAZORPAY_KEY_ID': 'present' if os.getenv('RAZORPAY_KEY_ID') else 'missing',
                'CUSTOM_API_KEY': os.getenv('CUSTOM_API_KEY', 'not_set'),
                'FREE_TRIAL_LIMIT': os.getenv('FREE_TRIAL_LIMIT', 'not_set')
            },
            'current_directory': os.getcwd(),
            'files_present': os.listdir('.') if os.path.exists('.') else 'unknown'
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'error_mode', 'message': 'Running in error debug mode'})
    
    return app

# Try to import and run the main application
try:
    logger.info("Attempting to import main app...")
    from app import app
    logger.info("Successfully imported main app")
    application = app
    
except ImportError as e:
    logger.error(f"ImportError when importing app: {e}")
    traceback_str = traceback.format_exc()
    logger.error(f"Traceback: {traceback_str}")
    
    # Try minimal app as fallback
    try:
        logger.info("Trying minimal app as fallback...")
        from minimal_app import app as minimal_app
        logger.info("Successfully imported minimal app")
        application = minimal_app
    except Exception as minimal_error:
        logger.error(f"Error importing minimal app: {minimal_error}")
        application = create_error_app(f"ImportError: {str(e)}", traceback_str)
    
except Exception as e:
    logger.error(f"Unexpected error when importing app: {e}")
    traceback_str = traceback.format_exc()
    logger.error(f"Traceback: {traceback_str}")
    
    # Try minimal app as fallback
    try:
        logger.info("Trying minimal app as fallback...")
        from minimal_app import app as minimal_app
        logger.info("Successfully imported minimal app")
        application = minimal_app
    except Exception as minimal_error:
        logger.error(f"Error importing minimal app: {minimal_error}")
        application = create_error_app(f"Unexpected error: {str(e)}", traceback_str)

# For local testing
if __name__ == "__main__":
    application.run(debug=True, host='0.0.0.0', port=5000)
