"""
Alternative MongoDB connection approach for Render deployment issues
This uses a simpler connection method that bypasses SSL completely
"""
import os
import logging
from pymongo import MongoClient
import ssl

logger = logging.getLogger(__name__)

def create_render_compatible_connection():
    """Create a MongoDB connection that works specifically with Render"""
    mongo_uri = os.getenv('MONGODB_URI')
    
    if not mongo_uri:
        logger.error("No MONGODB_URI found")
        return None, None
    
    try:
        # Method 1: Force non-SSL connection by modifying the URI
        logger.info("Attempting Render-compatible connection...")
        
        # Replace mongodb+srv with mongodb and modify parameters
        if 'mongodb+srv://' in mongo_uri:
            # Extract credentials and host
            import re
            import urllib.parse
            
            # Parse the SRV URI
            pattern = r'mongodb\+srv://([^:]+):([^@]+)@([^/]+)/([^?]*)'
            match = re.match(pattern, mongo_uri)
            
            if match:
                username, password, host, database = match.groups()
                password = urllib.parse.unquote(password)
                
                # Create direct connection without SRV
                cluster_host = host.replace('.mongodb.net', '.mongodb.net')
                
                # Try multiple port combinations
                ports = [27017, 27016, 27015]
                
                for port in ports:
                    try:
                        # Build direct connection string
                        direct_uri = f"mongodb://{username}:{urllib.parse.quote(password)}@{cluster_host}:{port}/{database}?authSource=admin&retryWrites=true&w=majority"
                        
                        logger.info(f"Trying direct connection on port {port}")
                        client = MongoClient(
                            direct_uri,
                            serverSelectionTimeoutMS=10000,
                            connectTimeoutMS=10000,
                            socketTimeoutMS=10000
                        )
                        
                        # Test connection
                        client.admin.command('ping')
                        db = client[database or 'resume_generator']
                        
                        logger.info(f"✅ Connected successfully using direct connection on port {port}")
                        return client, db
                        
                    except Exception as e:
                        logger.warning(f"Port {port} failed: {str(e)}")
                        continue
        
        logger.error("All Render connection attempts failed")
        return None, None
        
    except Exception as e:
        logger.error(f"Render connection error: {e}")
        return None, None

if __name__ == "__main__":
    # Test the connection
    os.environ['MONGODB_URI'] = 'mongodb+srv://mohantwo3:Mohan%402006@cluster0.gs12h0u.mongodb.net/resume_generator?retryWrites=true&w=majority'
    
    client, db = create_render_compatible_connection()
    if db:
        try:
            count = db.users.count_documents({})
            print(f"✅ Render connection test successful! Users: {count}")
        except Exception as e:
            print(f"❌ Database query failed: {e}")
    else:
        print("❌ Render connection test failed")
