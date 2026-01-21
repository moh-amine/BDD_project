"""
Authentication Service Module
=============================
This module handles user authentication, password hashing, and role verification.
It provides secure login functionality compatible with Streamlit session management.

Author: Exam Scheduling System
"""

import bcrypt
from typing import Optional, Tuple
from ..database.connection import get_connection


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    
    Args:
        password (str): Plain-text password to hash
        
    Returns:
        str: Bcrypt hash of the password
        
    Example:
        >>> hash = hash_password("mypassword")
        >>> verify_password("mypassword", hash)
        True
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password (str): Plain-text password to verify
        password_hash (str): Stored password hash
        
    Returns:
        bool: True if password matches, False otherwise
    """
    password_bytes = password.encode('utf-8')
    hash_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)


def login(username: str, password: str) -> Tuple[bool, Optional[dict], str]:
    """
    Authenticate a user with username and password.
    
    Args:
        username (str): Username for login
        password (str): Plain-text password
        
    Returns:
        tuple: (success: bool, user_data: dict | None, message: str)
            - success: True if authentication successful
            - user_data: Dictionary containing user info (id, username, role, linked_id) or None
            - message: Success or error message
            
    Example:
        >>> success, user, msg = login("admin", "password123")
        >>> if success:
        ...     print(f"Logged in as {user['role']}")
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Query user by username
        cur.execute("""
            SELECT id, username, password_hash, role, linked_id
            FROM users
            WHERE username = %s;
        """, (username,))
        
        user = cur.fetchone()
        
        if not user:
            return False, None, "Nom d'utilisateur ou mot de passe incorrect"
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return False, None, "Nom d'utilisateur ou mot de passe incorrect"
        
        # Update last login timestamp
        cur.execute("""
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE id = %s;
        """, (user['id'],))
        conn.commit()
        
        # Return user data (without password hash)
        user_data = {
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'linked_id': user['linked_id']
        }
        
        return True, user_data, "Connexion réussie"
        
    except Exception as e:
        conn.rollback()
        return False, None, f"Erreur lors de la connexion: {str(e)}"
        
    finally:
        cur.close()
        conn.close()


def get_user_by_id(user_id: int) -> Optional[dict]:
    """
    Retrieve user information by user ID.
    
    Args:
        user_id (int): User ID
        
    Returns:
        dict | None: User data dictionary or None if not found
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, username, role, linked_id
            FROM users
            WHERE id = %s;
        """, (user_id,))
        
        user = cur.fetchone()
        return dict(user) if user else None
        
    except Exception as e:
        return None
        
    finally:
        cur.close()
        conn.close()


def create_user(username: str, password: str, role: str, linked_id: Optional[int] = None) -> Tuple[bool, str]:
    """
    Create a new user account (admin function).
    
    Args:
        username (str): Username
        password (str): Plain-text password
        role (str): User role ('admin', 'professeur', or 'etudiant')
        linked_id (int | None): ID of linked professeur or etudiant (required for non-admin roles)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Validate role
        if role not in ['admin', 'professeur', 'etudiant']:
            return False, "Rôle invalide"
        
        # Validate linked_id for non-admin roles
        if role != 'admin' and linked_id is None:
            return False, "linked_id requis pour les rôles professeur et etudiant"
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert user
        cur.execute("""
            INSERT INTO users (username, password_hash, role, linked_id)
            VALUES (%s, %s, %s, %s);
        """, (username, password_hash, role, linked_id))
        
        conn.commit()
        return True, "Utilisateur créé avec succès"
        
    except Exception as e:
        conn.rollback()
        error_msg = str(e)
        if "unique constraint" in error_msg.lower() or "duplicate" in error_msg.lower():
            return False, "Ce nom d'utilisateur existe déjà"
        return False, f"Erreur lors de la création: {error_msg}"
        
    finally:
        cur.close()
        conn.close()


def is_admin(user_data: Optional[dict]) -> bool:
    """
    Check if user has admin role.
    
    Args:
        user_data (dict | None): User data dictionary from login
        
    Returns:
        bool: True if user is admin
    """
    return user_data is not None and user_data.get('role') == 'admin'


def is_professeur(user_data: Optional[dict]) -> bool:
    """
    Check if user has professeur role.
    
    Args:
        user_data (dict | None): User data dictionary from login
        
    Returns:
        bool: True if user is professeur
    """
    return user_data is not None and user_data.get('role') == 'professeur'


def is_etudiant(user_data: Optional[dict]) -> bool:
    """
    Check if user has etudiant role.
    
    Args:
        user_data (dict | None): User data dictionary from login
        
    Returns:
        bool: True if user is etudiant
    """
    return user_data is not None and user_data.get('role') == 'etudiant'
