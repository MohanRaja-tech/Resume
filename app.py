from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import os
from datetime import datetime
import logging
import uuid
from dotenv import load_dotenv
from functools import wraps
import razorpay
import hmac
import hashlib
import requests

# Load environment variables from .env file
load_dotenv()

# Initialize database after environment variables are loaded
from database import initialize_database
db = initialize_database()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
CORS(app, supports_credentials=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Free trial configuration
FREE_TRIAL_LIMIT = int(os.getenv('FREE_TRIAL_LIMIT', 3))

# Custom Resume Summary API Configuration
RESUME_API_URL = "https://ufc6ri782h.execute-api.ap-south-1.amazonaws.com/StageOneResumeSummaryText/ProdEasyJobsResumeSummary"
CUSTOM_API_KEY = os.getenv('CUSTOM_API_KEY')

if not CUSTOM_API_KEY:
    logger.warning("No custom API key found in environment variables")
else:
    logger.info("Custom API key loaded successfully from environment")

logger.info("Resume Summary API endpoint configured")

# Initialize Razorpay client
razorpay_key_id = os.getenv('RAZORPAY_KEY_ID')
razorpay_key_secret = os.getenv('RAZORPAY_KEY_SECRET')

if not razorpay_key_id or not razorpay_key_secret:
    logger.warning("Razorpay credentials not found in environment variables")
    razorpay_client = None
else:
    razorpay_client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
    logger.info("Razorpay client initialized successfully")

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"Login required check - Session contents: {dict(session)}")
        if 'user_id' not in session:
            logger.info(f"No user_id in session, redirecting to auth")
            return redirect(url_for('auth_page'))
        logger.info(f"User authenticated, proceeding to {f.__name__}")
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged-in user"""
    if 'user_id' not in session:
        logger.info("No user_id in session")
        return None
    
    user_id = session['user_id']
    logger.info(f"Looking for user_id: {user_id}")
    user = db.get_user_by_id(user_id)
    logger.info(f"Database returned user: {user}")
    
    # If user not found in database, clear the invalid session
    if user is None:
        logger.warning(f"User {user_id} not found in database, clearing session")
        session.clear()
        return None
    
    return user

@app.route('/')
def index():
    """Redirect to auth page if not logged in, else redirect to dashboard"""
    logger.info(f"Index route - Session contents: {dict(session)}")
    if 'user_id' in session:
        logger.info(f"User logged in, redirecting to dashboard")
        return redirect(url_for('dashboard'))
    logger.info(f"No user logged in, redirecting to auth")
    return redirect(url_for('auth_page'))

@app.route('/auth')
def auth_page():
    """Serve the authentication page"""
    logger.info(f"Auth route - Session contents: {dict(session)}")
    if 'user_id' in session:
        logger.info(f"User already logged in from auth page, redirecting to dashboard")
        return redirect(url_for('dashboard'))
    return render_template('auth.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Serve the main dashboard page for logged-in users"""
    return render_template('dashboard.html')

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Handle user signup"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create user account
        result = db.create_user_account(
            data['name'],
            data['email'],
            data['password']
        )
        
        if result and 'error' in result:
            return jsonify({
                'success': False,
                'message': result['error']
            }), 400
        
        if result:
            # Set session
            session['user_id'] = result['user_id']
            session['user_name'] = result['name']
            session['user_email'] = result['email']
            
            logger.info(f"New user registered: {result['email']}")
            
            return jsonify({
                'success': True,
                'message': 'Account created successfully!',
                'user': {
                    'name': result['name'],
                    'email': result['email']
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create account. Please try again.'
            }), 500
            
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        # Authenticate user
        user = db.authenticate_user(data['email'], data['password'])
        
        if user:
            # Set session
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            
            logger.info(f"User logged in: {user['email']}")
            
            return jsonify({
                'success': True,
                'message': 'Login successful!',
                'user': {
                    'name': user['name'],
                    'email': user['email']
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/logout')
def logout():
    """Log out user"""
    session.clear()
    return redirect(url_for('auth_page'))

@app.route('/clear-session')
def clear_session():
    """Clear session for debugging"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/usage-status', methods=['GET'])
@login_required
def get_usage_status():
    """Get current usage status for the logged-in user"""
    try:
        logger.info("get_usage_status called")
        user = get_current_user()
        logger.info(f"get_current_user returned: {user}")
        
        if not user:
            logger.error("User not found in get_usage_status, session cleared")
            # Return unauthorized to trigger frontend redirect to login
            return jsonify({'success': False, 'error': 'Session invalid, please login again'}), 401
        
        result = {
            'success': True,
            'data': {
                'usage_count': user.get('usage_count', 0),
                'limit': FREE_TRIAL_LIMIT,
                'remaining': max(0, FREE_TRIAL_LIMIT - user.get('usage_count', 0)),
                'is_premium': user.get('is_premium', False),
                'is_limited': user.get('usage_count', 0) >= FREE_TRIAL_LIMIT and not user.get('is_premium', False),
                'user_name': user.get('name', ''),
                'user_email': user.get('email', '')
            }
        }
        logger.info(f"Returning usage status: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in get_usage_status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-summary', methods=['POST'])
@login_required
def generate_summary():
    """
    Generate resume summaries based on user input
    Expected input format matches the requirements.txt structure
    """
    try:
        # Get current user and check usage limits
        user = get_current_user()
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
            
        # Check if user has exceeded free trial limit
        if not user.get('is_premium', False) and user.get('usage_count', 0) >= FREE_TRIAL_LIMIT:
            return jsonify({
                'success': False,
                'error': 'free_trial_exceeded',
                'message': 'You have reached your free trial limit of 3 generations. Upgrade to Premium for unlimited access!',
                'usage_count': user.get('usage_count', 0),
                'limit': FREE_TRIAL_LIMIT
            }), 429  # Too Many Requests
        
        # Get data from request
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['current_job_title', 'job_description', 'years_experience', 
                          'achievements', 'technical_skills', 'education']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Log the request
        logger.info(f"Generating summary for user {user.get('user_id')}, job title: {data['current_job_title']}")
        
        # Generate three different versions of resume summaries
        summaries = generate_resume_summaries(data)
        
        # Increment usage count for non-premium users
        if not user.get('is_premium', False):
            db.increment_usage(user['user_id'])
            # Log the generation
            db.log_generation(user['user_id'], data, summaries)
            # Get updated user data
            user = db.get_user_by_id(user['user_id'])
        
        # Response format matching requirements.txt
        response = {
            "success": True,
            "data": {
                "v1": summaries[0],
                "v2": summaries[1], 
                "v3": summaries[2]
            },
            "usage_info": {
                "usage_count": user.get('usage_count', 0),
                "remaining": max(0, FREE_TRIAL_LIMIT - user.get('usage_count', 0)) if not user.get('is_premium', False) else "unlimited",
                "is_premium": user.get('is_premium', False)
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

def generate_resume_summaries(data):
    """
    Generate three different versions of resume summaries using custom API
    """
    
    job_title = data['current_job_title']
    job_description = data['job_description'] 
    years_experience = data['years_experience']
    achievements = data['achievements']
    technical_skills = data['technical_skills']
    education = data['education']
    
    # Try to use custom API first, fallback to templates
    try:
        return generate_custom_api_summaries(data)
    except Exception as e:
        logger.error(f"Custom API error: {str(e)}, falling back to templates")
        return generate_template_summaries(data)

def generate_custom_api_summaries(data):
    """
    Generate AI-powered resume summaries using custom AWS API
    """
    try:
        # Prepare payload for the custom API
        payload = {
            "current_job_title": data['current_job_title'],
            "job_description": data['job_description'],
            "years_experience": data['years_experience'],
            "achievements": data['achievements'],
            "technical_skills": data['technical_skills'],
            "education": data['education']
        }
        
        # Prepare headers for the custom API
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Add API key to headers if available
        if CUSTOM_API_KEY:
            headers['Authorization'] = f'Bearer {CUSTOM_API_KEY}'
            # Alternative header formats you might need:
            # headers['X-API-Key'] = CUSTOM_API_KEY
            # headers['api-key'] = CUSTOM_API_KEY
        
        # Make request to custom API
        response = requests.post(
            RESUME_API_URL,
            json=payload,
            headers=headers,
            timeout=30  # 30 second timeout
        )
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            
            # Assuming the API returns summaries in a specific format
            # Adjust this based on your actual API response structure
            if 'summaries' in result:
                summaries = result['summaries']
                if len(summaries) >= 3:
                    return [
                        clean_summary(summaries[0]),
                        clean_summary(summaries[1]),
                        clean_summary(summaries[2])
                    ]
            elif 'data' in result:
                # If API returns data similar to OpenAI format
                data_result = result['data']
                if isinstance(data_result, dict):
                    return [
                        clean_summary(data_result.get('v1', '')),
                        clean_summary(data_result.get('v2', '')),
                        clean_summary(data_result.get('v3', ''))
                    ]
                elif isinstance(data_result, list) and len(data_result) >= 3:
                    return [
                        clean_summary(data_result[0]),
                        clean_summary(data_result[1]),
                        clean_summary(data_result[2])
                    ]
            elif isinstance(result, list) and len(result) >= 3:
                # If API directly returns an array of summaries
                return [
                    clean_summary(result[0]),
                    clean_summary(result[1]),
                    clean_summary(result[2])
                ]
            
            # If we can't parse the response properly, log it and fallback
            logger.warning(f"Unexpected API response format: {result}")
            return generate_template_summaries(data)
        else:
            logger.error(f"Custom API returned status code: {response.status_code}")
            return generate_template_summaries(data)
            
    except requests.exceptions.Timeout:
        logger.error("Custom API request timed out")
        return generate_template_summaries(data)
    except requests.exceptions.RequestException as e:
        logger.error(f"Custom API request error: {str(e)}")
        return generate_template_summaries(data)
    except Exception as e:
        logger.error(f"Unexpected error calling custom API: {str(e)}")
        return generate_template_summaries(data)

def generate_template_summaries(data):
    """
    Generate template-based summaries (fallback method)
    """
    job_title = data['current_job_title']
    job_description = data['job_description'] 
    years_experience = data['years_experience']
    achievements = data['achievements']
    technical_skills = data['technical_skills']
    education = data['education']
    
    # Template summaries with better structure
    summary_v1 = f"Detail-oriented {job_title} with {years_experience} years of experience in {job_description.lower()}. Skilled in {technical_skills}, with a track record of {achievements.lower()}. Proven ability to deliver results through strategic analysis and implementation, supported by {education}."
    
    summary_v2 = f"Accomplished {job_title} possessing {years_experience} years of expertise in {job_description.lower()}. Proficient in {technical_skills}, contributing to {achievements.lower()}. Holds {education}, demonstrating a strong foundation in professional excellence and innovative problem-solving."
    
    summary_v3 = f"Results-driven {job_title} with {years_experience} years of experience leveraging {job_description.lower()}. Expert in using {technical_skills} for comprehensive solutions, leading to {achievements.lower()}. {education} graduate, committed to enabling success through strategic initiatives and data-driven strategies."
    
    return [
        clean_summary(summary_v1),
        clean_summary(summary_v2), 
        clean_summary(summary_v3)
    ]

def clean_summary(summary):
    """Clean and format the summary text"""
    # Remove extra spaces and ensure proper formatting
    summary = ' '.join(summary.split())
    
    # Ensure it starts with capital letter
    if summary and summary[0].islower():
        summary = summary[0].upper() + summary[1:]
    
    # Ensure it ends with a period
    if summary and not summary.endswith('.'):
        summary += '.'
    
    return summary

@app.route('/api/upgrade-premium', methods=['POST'])
@login_required
def upgrade_premium():
    """
    Simulate premium upgrade (in real app, integrate with payment processor)
    """
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # In a real application, you would:
        # 1. Validate payment information
        # 2. Process payment through Stripe/PayPal/etc
        # 3. Update user's premium status in database
        
        # Update premium status
        success = db.upgrade_to_premium(user['user_id'])
        if not success:
            return jsonify({'success': False, 'error': 'Failed to upgrade to premium'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Successfully upgraded to Premium! You now have unlimited generations.',
            'is_premium': True
        })
        
    except Exception as e:
        logger.error(f"Error upgrading to premium: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to upgrade to premium'
        }), 500

@app.route('/api/create-razorpay-order', methods=['POST'])
@login_required
def create_razorpay_order():
    """Create Razorpay order for premium subscription"""
    try:
        if not razorpay_client:
            return jsonify({
                'success': False, 
                'error': 'Payment system not configured'
            }), 500
        
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get request data
        data = request.get_json()
        amount = data.get('amount', 100000)  # ₹1000 in paise
        currency = data.get('currency', 'INR')
        
        # Create Razorpay order
        # Generate short receipt (max 40 chars for Razorpay)
        timestamp = str(int(datetime.now().timestamp()))[-8:]  # Last 8 digits of timestamp
        receipt = f"prem_{user['user_id']}_{timestamp}"[:40]  # Ensure max 40 chars
        
        order_data = {
            'amount': amount,
            'currency': currency,
            'receipt': receipt,
            'notes': {
                'user_id': user['user_id'],
                'username': user.get('username', user.get('name', '')),
                'subscription_type': 'premium_monthly'
            }
        }
        
        order = razorpay_client.order.create(data=order_data)
        
        return jsonify({
            'success': True,
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'razorpay_key': razorpay_key_id
        })
        
    except Exception as e:
        logger.error(f"Error creating Razorpay order: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create payment order'
        }), 500

@app.route('/api/verify-razorpay-payment', methods=['POST'])
@login_required
def verify_razorpay_payment():
    """Verify Razorpay payment and upgrade user to premium"""
    try:
        if not razorpay_client:
            return jsonify({
                'success': False, 
                'error': 'Payment system not configured'
            }), 500
        
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get payment data
        data = request.get_json()
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return jsonify({
                'success': False,
                'error': 'Missing payment verification data'
            }), 400
        
        # Verify signature
        try:
            # Create expected signature
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            expected_signature = hmac.new(
                razorpay_key_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if expected_signature != razorpay_signature:
                logger.warning(f"Payment signature verification failed for user {user['user_id']}")
                return jsonify({
                    'success': False,
                    'error': 'Payment verification failed'
                }), 400
            
        except Exception as e:
            logger.error(f"Error verifying payment signature: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Payment verification failed'
            }), 400
        
        # Payment verified successfully, upgrade user to premium
        try:
            success = db.upgrade_to_premium(user['user_id'])
            if not success:
                logger.error(f"Failed to upgrade user {user['user_id']} to premium after successful payment")
                return jsonify({
                    'success': False,
                    'error': 'Failed to activate premium subscription'
                }), 500
            
            # Log successful payment
            logger.info(f"User {user['user_id']} successfully upgraded to premium. Payment ID: {razorpay_payment_id}")
            
            return jsonify({
                'success': True,
                'message': 'Payment verified and premium activated successfully!',
                'is_premium': True,
                'payment_id': razorpay_payment_id
            })
            
        except Exception as e:
            logger.error(f"Error upgrading user to premium: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to activate premium subscription'
            }), 500
        
    except Exception as e:
        logger.error(f"Error verifying Razorpay payment: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Payment verification failed'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """Get usage statistics for admin (protected endpoint)"""
    # In production, add proper authentication
    admin_key = request.headers.get('X-Admin-Key')
    if admin_key != os.getenv('ADMIN_KEY', 'admin123'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    stats = db.get_usage_stats()
    return jsonify({
        'success': True,
        'data': stats
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Vercel serverless function entry point
# The app is imported by index.py for Vercel deployment
