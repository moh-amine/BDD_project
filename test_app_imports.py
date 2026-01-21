"""Test if all imports work correctly"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

try:
    print("1. Testing backend imports...")
    from backend.database.connection import get_connection
    from backend.database.queries import get_all_examens
    from backend.services.auth_service import login, hash_password
    from backend.services.examen_service import create_examen
    from backend.optimization.scheduler import generate_schedule
    print("   [OK] Backend imports successful")
except Exception as e:
    print(f"   [ERROR] Backend import failed: {e}")
    sys.exit(1)

try:
    print("2. Testing frontend imports...")
    # This will show warnings but should work
    import streamlit as st
    # Don't actually import app.py as it needs Streamlit context
    print("   [OK] Streamlit available")
except Exception as e:
    print(f"   [ERROR] Streamlit import failed: {e}")
    sys.exit(1)

try:
    print("3. Testing database connection...")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1")
    cur.close()
    conn.close()
    print("   [OK] Database connection successful")
except Exception as e:
    print(f"   [ERROR] Database connection failed: {e}")
    sys.exit(1)

try:
    print("4. Testing users table...")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as count FROM users")
    result = cur.fetchone()
    count = result['count'] if result else 0
    cur.close()
    conn.close()
    print(f"   [OK] Users table accessible (current users: {count})")
except Exception as e:
    print(f"   [ERROR] Users table check failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[SUCCESS] All tests passed! The application should work correctly.")
print("\nTo run the application:")
print("  streamlit run frontend/app.py")
