"""
User Creation Helper Script
============================
This script helps create user accounts for the Exam Scheduling System.

Usage:
    python scripts/create_users.py

You can modify this script to create users programmatically.
"""

import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.auth_service import create_user


def create_admin_user(username: str, password: str):
    """Create an admin user account."""
    success, message = create_user(username, password, "admin", None)
    if success:
        print(f"[OK] Admin user '{username}' created successfully")
    else:
        print(f"[ERROR] Error creating admin user '{username}': {message}")
    return success


def create_professeur_user(username: str, password: str, professeur_id: int):
    """Create a professeur user account."""
    success, message = create_user(username, password, "professeur", professeur_id)
    if success:
        print(f"[OK] Professeur user '{username}' created successfully (linked to professeur ID: {professeur_id})")
    else:
        print(f"[ERROR] Error creating professeur user '{username}': {message}")
    return success


def create_etudiant_user(username: str, password: str, etudiant_id: int):
    """Create an etudiant user account."""
    success, message = create_user(username, password, "etudiant", etudiant_id)
    if success:
        print(f"[OK] Etudiant user '{username}' created successfully (linked to etudiant ID: {etudiant_id})")
    else:
        print(f"[ERROR] Error creating etudiant user '{username}': {message}")
    return success


if __name__ == "__main__":
    print("=" * 60)
    print("User Creation Script - Exam Scheduling System")
    print("=" * 60)
    print()
    
    # Example: Create admin user
    print("Creating admin user...")
    create_admin_user("admin", "password123")
    print()
    
    # Example: Create professeur user
    # Replace 1 with actual professeur.id from your database
    print("Creating professeur user...")
    print("[NOTE] Replace '1' with actual professeur.id from your database")
    # create_professeur_user("prof1", "password123", 1)
    print()
    
    # Example: Create etudiant user
    # Replace 1 with actual etudiant.id from your database
    print("Creating etudiant user...")
    print("[NOTE] Replace '1' with actual etudiant.id from your database")
    # create_etudiant_user("etud1", "password123", 1)
    print()
    
    print("=" * 60)
    print("To create more users, modify this script and uncomment the lines above.")
    print("Or call the functions directly:")
    print("  create_admin_user('username', 'password')")
    print("  create_professeur_user('username', 'password', professeur_id)")
    print("  create_etudiant_user('username', 'password', etudiant_id)")
    print("=" * 60)
