#!/usr/bin/env python3
"""
Test the new Database class with environment detection
"""
import os
import sys
from database import Database

# Set up environment for testing
os.environ['MONGODB_URI'] = 'mongodb+srv://mohantwo3:Mohan%402006@cluster0.gs12h0u.mongodb.net/resume_generator?retryWrites=true&w=majority'

print("🧪 Testing Database class...")
print("=" * 50)

# Test without RENDER environment
print("\n1. Testing LOCAL environment:")
if 'RENDER' in os.environ:
    del os.environ['RENDER']

db = Database()
if db.db is not None:
    print("✅ Local connection successful!")
    user_count = db.db.users.count_documents({})
    print(f"✅ User count: {user_count}")
else:
    print("❌ Local connection failed!")

# Test with RENDER environment
print("\n2. Testing RENDER environment simulation:")
os.environ['RENDER'] = 'true'

db2 = Database()
if db2.db is not None:
    print("✅ Render simulation connection successful!")
    user_count = db2.db.users.count_documents({})
    print(f"✅ User count: {user_count}")
else:
    print("❌ Render simulation connection failed!")

print("\n🎉 Database testing complete!")
