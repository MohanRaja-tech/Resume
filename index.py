import os
import sys
import traceback

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Try to import main app, fallback to debug app
try:
    from app import app
    print("Successfully imported main app")
    application = app
except Exception as e:
    print(f"Error importing main app: {e}")
    print("Full traceback:")
    traceback.print_exc()
    
    # Fallback to debug app
    try:
        from debug import app as debug_app
        print("Using debug app as fallback")
        application = debug_app
    except Exception as debug_error:
        print(f"Error importing debug app: {debug_error}")
        
        # Last resort - minimal Flask app
        from flask import Flask, jsonify
        app = Flask(__name__)
        
        @app.route('/')
        def error():
            return jsonify({
                'error': f"Import Error: {str(e)}",
                'debug_error': f"Debug Error: {str(debug_error)}",
                'status': 'critical_error'
            }), 500
        
        application = app

# For local testing
if __name__ == "__main__":
    application.run(debug=False)
