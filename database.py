import os
import logging
from pymongo import MongoClient
from datetime import datetime, timedelta
import hashlib
import uuid
import bcrypt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # MongoDB Atlas connection string from environment
        self.mongo_uri = os.getenv('MONGODB_URI')
        self.client = None
        self.db = None
        self.is_render = os.getenv('RENDER') is not None  # Detect Render environment
        self.connect()
    
    def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            if not self.mongo_uri:
                logger.warning("No MongoDB URI found in environment variables")
                return
            
            # Different connection strategies based on environment
            if self.is_render:
                logger.info("Detected Render environment, using SSL bypass")
                self._connect_render()
            else:
                logger.info("Local/other environment, using standard connection")
                self._connect_standard()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None
    
    def _connect_standard(self):
        """Standard MongoDB connection for local/other environments"""
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.resume_generator
        self.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Atlas (standard)")
    
    def _connect_render(self):
        """Special MongoDB connection for Render environment"""
        import ssl
        
        # Try multiple connection strategies for Render
        connection_strategies = [
            # Strategy 1: TLS with invalid certificates allowed
            {
                "tls": True,
                "tlsAllowInvalidCertificates": True,
                "serverSelectionTimeoutMS": 10000,
                "connectTimeoutMS": 10000,
                "socketTimeoutMS": 10000
            },
            # Strategy 2: SSL with certificate verification disabled
            {
                "ssl": True,
                "ssl_cert_reqs": ssl.CERT_NONE,
                "ssl_match_hostname": False,
                "serverSelectionTimeoutMS": 15000,
                "connectTimeoutMS": 15000,
                "socketTimeoutMS": 15000
            },
            # Strategy 3: Basic SSL
            {
                "ssl": True,
                "serverSelectionTimeoutMS": 20000,
                "connectTimeoutMS": 20000,
                "socketTimeoutMS": 20000
            },
            # Strategy 4: No SSL (fallback)
            {
                "serverSelectionTimeoutMS": 10000,
                "connectTimeoutMS": 10000,
                "socketTimeoutMS": 10000
            }
        ]
        
        for i, strategy in enumerate(connection_strategies, 1):
            try:
                logger.info(f"Render: Trying connection strategy {i}")
                self.client = MongoClient(self.mongo_uri, **strategy)
                self.db = self.client.resume_generator
                # Test connection
                self.client.admin.command('ping')
                logger.info(f"Successfully connected to MongoDB Atlas using Render strategy {i}")
                return
            except Exception as e:
                logger.warning(f"Render strategy {i} failed: {str(e)}")
                if self.client:
                    self.client.close()
                    self.client = None
                    self.db = None
                continue
        
        # If all strategies fail
        raise Exception("All Render connection strategies failed")
    
    def create_user_account(self, name, email, password):
        """Create a new user account with authentication"""
        if self.db is None:
            logger.error("Database connection not available")
            return {"error": "Database connection failed. Please try again later."}
        
        try:
            # Check if user already exists
            existing_user = self.db.users.find_one({"email": email})
            if existing_user:
                logger.info(f"User already exists: {email}")
                return {"error": "An account with this email already exists."}
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Create user document
            user_id = str(uuid.uuid4())
            user_doc = {
                "user_id": user_id,
                "name": name,
                "email": email,
                "password_hash": password_hash,
                "created_at": datetime.utcnow(),
                "last_active": datetime.utcnow(),
                "usage_count": 0,
                "is_premium": False
            }
            
            # Insert user
            result = self.db.users.insert_one(user_doc)
            if result.inserted_id:
                logger.info(f"User created successfully: {email}")
                # Return user without password hash
                del user_doc['password_hash']
                return user_doc
            else:
                logger.error(f"Failed to insert user: {email}")
                return {"error": "Failed to create account. Please try again."}
            
        except Exception as e:
            logger.error(f"Error creating user account: {e}")
            return {"error": f"Database error: {str(e)}"}
    
    def authenticate_user(self, email, password):
        """Authenticate user with email and password"""
        if self.db is None:
            logger.error("Database connection not available")
            return {"error": "Database connection failed. Please try again later."}
        
        try:
            user = self.db.users.find_one({"email": email})
            if not user:
                logger.info(f"User not found: {email}")
                return {"error": "Invalid email or password."}
            
            # Check password
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
                # Update last active
                self.db.users.update_one(
                    {'email': email},
                    {'$set': {'last_active': datetime.utcnow()}}
                )
                # Remove password hash from returned data
                del user['password_hash']
                logger.info(f"User authenticated successfully: {email}")
                return user
            else:
                logger.info(f"Invalid password for user: {email}")
                return {"error": "Invalid email or password."}
                
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return {"error": f"Authentication error: {str(e)}"}
    
    def get_user_by_id(self, user_id):
        """Get user by user_id"""
        if self.db is None:
            logger.error("Database is None in get_user_by_id")
            return None
        
        try:
            logger.info(f"Searching for user_id: {user_id}")
            user = self.db.users.find_one({'user_id': user_id})
            logger.info(f"Query result: {user}")
            if user and 'password_hash' in user:
                del user['password_hash']
            return user
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        if self.db is None:
            return None
        
        try:
            user = self.db.users.find_one({'email': email})
            if user and 'password_hash' in user:
                del user['password_hash']
            return user
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    def get_user_by_fingerprint(self, fingerprint):
        """Get user by browser fingerprint"""
        if self.db is None:
            return None
        
        try:
            user = self.db.users.find_one({'fingerprint': fingerprint})
            return user
        except Exception as e:
            logger.error(f"Error getting user by fingerprint: {e}")
            return None
    
    def create_user(self, fingerprint, ip_address=None, user_agent=None):
        """Create a new user with fingerprint tracking"""
        if self.db is None:
            return None
        
        try:
            user_doc = {
                'user_id': str(uuid.uuid4()),
                'fingerprint': fingerprint,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'created_at': datetime.utcnow(),
                'last_active': datetime.utcnow(),
                'usage_count': 0,
                'is_premium': False,
                'generations': []
            }
            
            result = self.db.users.insert_one(user_doc)
            if result.inserted_id:
                return user_doc
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def update_user_activity(self, fingerprint):
        """Update user's last activity timestamp"""
        if self.db is None:
            return False
        
        try:
            result = self.db.users.update_one(
                {'fingerprint': fingerprint},
                {'$set': {'last_active': datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
            return False
    
    def increment_usage(self, user_id):
        """Increment user's usage count"""
        if self.db is None:
            return False
        
        try:
            result = self.db.users.update_one(
                {'user_id': user_id},
                {
                    '$inc': {'usage_count': 1},
                    '$set': {'last_active': datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error incrementing usage: {e}")
            return False
    
    def upgrade_to_premium(self, user_id):
        """Upgrade user to premium"""
        if self.db is None:
            return False
        
        try:
            result = self.db.users.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'is_premium': True,
                        'upgraded_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error upgrading to premium: {e}")
            return False
    
    def log_generation(self, user_id, data, summaries):
        """Log a resume generation"""
        if self.db is None:
            return False
        
        try:
            generation_doc = {
                'generation_id': str(uuid.uuid4()),
                'user_id': user_id,
                'timestamp': datetime.utcnow(),
                'input_data': data,
                'generated_summaries': summaries,
                'ip_address': data.get('ip_address'),
                'user_agent': data.get('user_agent')
            }
            
            # Insert generation record
            result = self.db.generations.insert_one(generation_doc)
            
            # Update user's generation list
            if result.inserted_id:
                self.db.users.update_one(
                    {'user_id': user_id},
                    {'$push': {'generations': generation_doc['generation_id']}}
                )
            
            return result.inserted_id is not None
        except Exception as e:
            logger.error(f"Error logging generation: {e}")
            return False
    
    def get_usage_stats(self):
        """Get usage statistics"""
        if self.db is None:
            return {}
        
        try:
            total_users = self.db.users.count_documents({})
            total_generations = self.db.generations.count_documents({})
            premium_users = self.db.users.count_documents({'is_premium': True})
            
            # Recent activity (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_users = self.db.users.count_documents({'last_active': {'$gte': yesterday}})
            recent_generations = self.db.generations.count_documents({'timestamp': {'$gte': yesterday}})
            
            return {
                'total_users': total_users,
                'total_generations': total_generations,
                'premium_users': premium_users,
                'recent_users': recent_users,
                'recent_generations': recent_generations
            }
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return {}

def generate_user_fingerprint(ip_address, user_agent):
    """Generate a unique fingerprint for user tracking"""
    # Combine IP and User Agent to create a unique identifier
    fingerprint_data = f"{ip_address}:{user_agent}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()

# Global database instance - will be initialized later
db = None

def initialize_database():
    """Initialize the database connection after environment variables are loaded"""
    global db
    if db is None:
        db = Database()
    return db
