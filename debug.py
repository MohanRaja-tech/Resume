from flask import Flask, jsonify
import os
import sys

app = Flask(__name__)

@app.route('/')
def debug_info():
    try:
        return jsonify({
            'status': 'debug_working',
            'python_version': sys.version,
            'environment_vars': {
                'SECRET_KEY': 'present' if os.getenv('SECRET_KEY') else 'missing',
                'FLASK_ENV': os.getenv('FLASK_ENV'),
                'MONGODB_URI': 'present' if os.getenv('MONGODB_URI') else 'missing',
                'RAZORPAY_KEY_ID': 'present' if os.getenv('RAZORPAY_KEY_ID') else 'missing',
                'CUSTOM_API_KEY': os.getenv('CUSTOM_API_KEY'),
                'FREE_TRIAL_LIMIT': os.getenv('FREE_TRIAL_LIMIT')
            }
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__
        }), 500

@app.route('/test-db')
def test_db():
    try:
        from database import initialize_database
        db = initialize_database()
        return jsonify({
            'database': 'connected' if db else 'failed',
            'message': 'Database test successful'
        })
    except Exception as e:
        return jsonify({
            'database': 'error',
            'error': str(e),
            'type': type(e).__name__
        }), 500

# For Vercel
application = app

if __name__ == "__main__":
    app.run(debug=True)
