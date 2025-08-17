import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

logger.info("Starting index.py...")

# Test with ultra-minimal app first
try:
    logger.info("Trying ultra-minimal test app...")
    from test_app import app as test_app
    logger.info("Successfully imported test app")
    application = test_app
    
except Exception as test_error:
    logger.error(f"Error importing test app: {test_error}")
    
    # Create the most basic Flask app possible
    try:
        from flask import Flask, jsonify
        app = Flask(__name__)
        
        @app.route('/')
        def basic():
            return jsonify({
                'status': 'basic_flask_working',
                'error': f"Test app failed: {str(test_error)}",
                'python_version': sys.version
            })
        
        application = app
        logger.info("Created basic Flask app")
        
    except Exception as basic_error:
        logger.error(f"Even basic Flask app failed: {basic_error}")
        # Last resort
        def application(environ, start_response):
            status = '200 OK'
            headers = [('Content-type', 'text/plain')]
            start_response(status, headers)
            return [b'Raw WSGI app working - Flask import failed']

logger.info("Index.py setup complete")

# For local testing
if __name__ == "__main__":
    if hasattr(application, 'run'):
        application.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("WSGI application ready")
