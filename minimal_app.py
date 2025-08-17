from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        'status': 'minimal_app_working',
        'message': 'This is a minimal test app',
        'environment_check': {
            'SECRET_KEY': 'present' if os.getenv('SECRET_KEY') else 'missing',
            'FLASK_ENV': os.getenv('FLASK_ENV', 'not_set'),
            'MONGODB_URI': 'present' if os.getenv('MONGODB_URI') else 'missing',
            'RAZORPAY_KEY_ID': 'present' if os.getenv('RAZORPAY_KEY_ID') else 'missing',
            'CUSTOM_API_KEY': os.getenv('CUSTOM_API_KEY', 'not_set'),
            'FREE_TRIAL_LIMIT': os.getenv('FREE_TRIAL_LIMIT', 'not_set')
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Minimal app is healthy'})

# For Vercel
application = app

if __name__ == "__main__":
    app.run(debug=True)
