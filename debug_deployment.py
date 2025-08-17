#!/usr/bin/env python3

# Simple deployment test script
import sys
import os

print("=== DEPLOYMENT DEBUG INFO ===")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")

print("\n=== ENVIRONMENT VARIABLES ===")
env_vars = ['SECRET_KEY', 'FLASK_ENV', 'MONGODB_URI', 'RAZORPAY_KEY_ID', 'RAZORPAY_KEY_SECRET', 'CUSTOM_API_KEY', 'FREE_TRIAL_LIMIT']
for var in env_vars:
    value = os.getenv(var)
    if var in ['SECRET_KEY', 'MONGODB_URI', 'RAZORPAY_KEY_SECRET']:
        print(f"{var}: {'present' if value else 'missing'}")
    else:
        print(f"{var}: {value}")

print("\n=== IMPORT TESTS ===")
try:
    import flask
    print(f"Flask version: {flask.__version__}")
except Exception as e:
    print(f"Flask import error: {e}")

try:
    import pymongo
    print(f"PyMongo version: {pymongo.__version__}")
except Exception as e:
    print(f"PyMongo import error: {e}")

try:
    from database import initialize_database
    print("Database module imported successfully")
except Exception as e:
    print(f"Database import error: {e}")

try:
    from app import app
    print("Main app imported successfully")
except Exception as e:
    print(f"Main app import error: {e}")

print("=== END DEBUG INFO ===")
