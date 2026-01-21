"""Create users table in the database"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import get_connection

SQL_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'professeur', 'etudiant')),
    linked_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    CONSTRAINT chk_linked_id CHECK (
        (role = 'admin' AND linked_id IS NULL) OR
        (role IN ('professeur', 'etudiant') AND linked_id IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
"""

def create_users_table():
    """Create the users table if it doesn't exist"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(SQL_CREATE_TABLE)
        conn.commit()
        print("[OK] Users table created successfully")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Failed to create users table: {e}")
        return False
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("Creating users table...")
    create_users_table()
