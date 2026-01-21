"""Test database connection and check if users table exists"""
from backend.database.connection import get_connection

try:
    conn = get_connection()
    cur = conn.cursor()
    
    # Check if users table exists
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'users';
    """)
    result = cur.fetchone()
    
    if result:
        print("[OK] Users table exists")
    else:
        print("[ERROR] Users table does NOT exist")
        print("Please run: psql -U postgres -d exam_scheduler -f docs/create_users_table.sql")
    
    cur.close()
    conn.close()
    print("[OK] Database connection successful")
    
except Exception as e:
    print(f"[ERROR] Database connection error: {e}")
