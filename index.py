import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app import app
    
    # This is the WSGI application that Vercel will use
    application = app
    
    # For local testing
    if __name__ == "__main__":
        app.run(debug=False)
        
except Exception as e:
    print(f"Error importing app: {e}")
    # Create a minimal error app
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return f"Import Error: {str(e)}", 500
    
    application = app
