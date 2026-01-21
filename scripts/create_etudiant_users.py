"""Create user accounts for all etudiants"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import get_connection
from backend.services.auth_service import create_user

def create_etudiant_users():
    """Create user accounts for all etudiants"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        print("=" * 60)
        print("Creating User Accounts for Etudiants")
        print("=" * 60)
        print()
        
        # Get all etudiants
        cur.execute("SELECT id, nom, prenom FROM etudiant ORDER BY id;")
        etudiants = cur.fetchall()
        
        created_count = 0
        existing_count = 0
        
        for etud in etudiants:
            etudiant_id = etud['id']
            username = f"etud{etudiant_id}"
            password = "password123"
            
            success, message = create_user(username, password, "etudiant", etudiant_id)
            
            if success:
                print(f"[OK] Created user: {username} for {etud['nom']} {etud['prenom']}")
                created_count += 1
            else:
                if "existe déjà" in message or "already exists" in message.lower():
                    print(f"[INFO] User {username} already exists")
                    existing_count += 1
                else:
                    print(f"[ERROR] Failed to create {username}: {message}")
        
        print()
        print("=" * 60)
        print(f"Summary: {created_count} created, {existing_count} already existed")
        print("=" * 60)
        print()
        print("Test accounts created:")
        for etud in etudiants:
            print(f"  - etud{etud['id']} / password123")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_etudiant_users()
