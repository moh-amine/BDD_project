"""
Create test users: prof1 and etud1
This script finds the first available professeur and etudiant IDs
and creates user accounts for them.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import get_connection
from backend.services.auth_service import create_user


def get_first_professeur_id():
    """Get the first professeur ID from database."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id FROM professeur ORDER BY id LIMIT 1;")
        result = cur.fetchone()
        return result['id'] if result else None
    except Exception as e:
        print(f"[ERROR] Failed to get professeur ID: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def get_first_etudiant_id():
    """Get the first etudiant ID from database."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id FROM etudiant ORDER BY id LIMIT 1;")
        result = cur.fetchone()
        return result['id'] if result else None
    except Exception as e:
        print(f"[ERROR] Failed to get etudiant ID: {e}")
        return None
    finally:
        cur.close()
        conn.close()


def main():
    print("=" * 60)
    print("Creating Test Users: prof1 and etud1")
    print("=" * 60)
    print()
    
    # Get IDs from database
    print("1. Finding professeur ID...")
    professeur_id = get_first_professeur_id()
    if professeur_id:
        print(f"   [OK] Found professeur ID: {professeur_id}")
    else:
        print("   [ERROR] No professeur found in database!")
        print("   Please ensure there is at least one professeur in the database.")
        return
    
    print()
    print("2. Finding etudiant ID...")
    etudiant_id = get_first_etudiant_id()
    if etudiant_id:
        print(f"   [OK] Found etudiant ID: {etudiant_id}")
    else:
        print("   [ERROR] No etudiant found in database!")
        print("   Please ensure there is at least one etudiant in the database.")
        return
    
    print()
    print("3. Creating professeur user (prof1)...")
    success, message = create_user("prof1", "password123", "professeur", professeur_id)
    if success:
        print(f"   [OK] {message}")
    else:
        if "existe déjà" in message or "already exists" in message.lower():
            print(f"   [INFO] User prof1 already exists: {message}")
        else:
            print(f"   [ERROR] {message}")
    
    print()
    print("4. Creating etudiant user (etud1)...")
    success, message = create_user("etud1", "password123", "etudiant", etudiant_id)
    if success:
        print(f"   [OK] {message}")
    else:
        if "existe déjà" in message or "already exists" in message.lower():
            print(f"   [INFO] User etud1 already exists: {message}")
        else:
            print(f"   [ERROR] {message}")
    
    print()
    print("=" * 60)
    print("Test Users Created:")
    print("  - prof1 / password123 (Professeur)")
    print("  - etud1 / password123 (Etudiant)")
    print("=" * 60)


if __name__ == "__main__":
    main()
