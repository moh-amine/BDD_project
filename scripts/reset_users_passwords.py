"""
Reset Users Passwords Script
============================
This script resets all user passwords to "1234" using proper bcrypt hashing.

It will:
1. Delete existing users (or update their password_hash)
2. Recreate users with correct bcrypt-hashed passwords
3. Create: admin, prof1-3, etud1-3

All users will have password: "1234"

Usage:
    python scripts/reset_users_passwords.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import get_connection
from backend.services.auth_service import create_user


def get_professeur_ids(limit=3):
    """Get the first N professeur IDs from database."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id FROM professeur ORDER BY id LIMIT %s;", (limit,))
        results = cur.fetchall()
        return [r['id'] for r in results] if results else []
    except Exception as e:
        print(f"[ERROR] Failed to get professeur IDs: {e}")
        return []
    finally:
        cur.close()
        conn.close()


def get_etudiant_ids(limit=3):
    """Get the first N etudiant IDs from database."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id FROM etudiant ORDER BY id LIMIT %s;", (limit,))
        results = cur.fetchall()
        return [r['id'] for r in results] if results else []
    except Exception as e:
        print(f"[ERROR] Failed to get etudiant IDs: {e}")
        return []
    finally:
        cur.close()
        conn.close()


def delete_existing_users():
    """Delete all existing users from the database."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Get count before deletion
        cur.execute("SELECT COUNT(*) as count FROM users;")
        count_before = cur.fetchone()['count']
        
        # Delete all users
        cur.execute("DELETE FROM users;")
        conn.commit()
        
        print(f"[OK] Deleted {count_before} existing user(s)")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Failed to delete existing users: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def reset_users_passwords():
    """
    Reset all user passwords by deleting and recreating users.
    All users will have password "1234" with proper bcrypt hashing.
    """
    print("=" * 70)
    print("RESET USERS PASSWORDS - Exam Scheduling System")
    print("=" * 70)
    print()
    print("This script will:")
    print("  1. Delete all existing users")
    print("  2. Recreate users with password '1234' (properly bcrypt-hashed)")
    print("  3. Create: admin, prof1-3, etud1-3")
    print()
    
    # Step 1: Delete existing users
    print("Step 1: Deleting existing users...")
    if not delete_existing_users():
        print("[ERROR] Failed to delete existing users. Aborting.")
        return False
    print()
    
    # Step 2: Get professeur and etudiant IDs
    print("Step 2: Getting professeur IDs...")
    professeur_ids = get_professeur_ids(limit=3)
    if len(professeur_ids) < 3:
        print(f"[WARNING] Only found {len(professeur_ids)} professeur(s). Need at least 3.")
        if len(professeur_ids) == 0:
            print("[ERROR] No professeurs found in database. Cannot create professeur users.")
            return False
    else:
        print(f"[OK] Found {len(professeur_ids)} professeur IDs: {professeur_ids}")
    print()
    
    print("Step 3: Getting etudiant IDs...")
    etudiant_ids = get_etudiant_ids(limit=3)
    if len(etudiant_ids) < 3:
        print(f"[WARNING] Only found {len(etudiant_ids)} etudiant(s). Need at least 3.")
        if len(etudiant_ids) == 0:
            print("[ERROR] No etudiants found in database. Cannot create etudiant users.")
            return False
    else:
        print(f"[OK] Found {len(etudiant_ids)} etudiant IDs: {etudiant_ids}")
    print()
    
    # Step 3: Create admin user
    print("Step 4: Creating admin user...")
    password = "1234"
    success, message = create_user("admin", password, "admin", None)
    if success:
        print(f"[OK] Admin user created: admin / {password}")
    else:
        print(f"[ERROR] Failed to create admin user: {message}")
        return False
    print()
    
    # Step 4: Create professeur users
    print("Step 5: Creating professeur users...")
    for i, professeur_id in enumerate(professeur_ids[:3], 1):
        username = f"prof{i}"
        success, message = create_user(username, password, "professeur", professeur_id)
        if success:
            print(f"[OK] Professeur user created: {username} / {password} (linked to professeur ID: {professeur_id})")
        else:
            print(f"[ERROR] Failed to create {username}: {message}")
            return False
    print()
    
    # Step 5: Create etudiant users
    print("Step 6: Creating etudiant users...")
    for i, etudiant_id in enumerate(etudiant_ids[:3], 1):
        username = f"etud{i}"
        success, message = create_user(username, password, "etudiant", etudiant_id)
        if success:
            print(f"[OK] Etudiant user created: {username} / {password} (linked to etudiant ID: {etudiant_id})")
        else:
            print(f"[ERROR] Failed to create {username}: {message}")
            return False
    print()
    
    # Summary
    print("=" * 70)
    print("✅ PASSWORD RESET COMPLETE")
    print("=" * 70)
    print()
    print("All users have been recreated with password: 1234")
    print()
    print("Created users:")
    print("  - admin / 1234 (Admin)")
    for i in range(1, min(4, len(professeur_ids) + 1)):
        print(f"  - prof{i} / 1234 (Professeur)")
    for i in range(1, min(4, len(etudiant_ids) + 1)):
        print(f"  - etud{i} / 1234 (Etudiant)")
    print()
    print("⚠️  IMPORTANT: All passwords are now properly bcrypt-hashed.")
    print("   Authentication should now work correctly.")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    try:
        success = reset_users_passwords()
        if success:
            print("\n[SUCCESS] Password reset completed successfully!")
            sys.exit(0)
        else:
            print("\n[FAILED] Password reset encountered errors.")
            sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
