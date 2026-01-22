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
    try:
        if not password or not password_hash:
            print(f"[DEBUG] verify_password: Empty password or hash - password: {bool(password)}, hash: {bool(password_hash)}")
            return False
        
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        
        # Check if hash looks like a valid bcrypt hash (starts with $2a$, $2b$, or $2y$)
        if not (password_hash.startswith('$2a$') or password_hash.startswith('$2b$') or password_hash.startswith('$2y$')):
            print(f"[DEBUG] verify_password: Invalid bcrypt hash format. Hash starts with: {password_hash[:10] if len(password_hash) >= 10 else password_hash}")
            return False
        
        result = bcrypt.checkpw(password_bytes, hash_bytes)
        print(f"[DEBUG] verify_password: bcrypt.checkpw result: {result}")
        return result
    except Exception as e:
        print(f"[DEBUG] verify_password: Exception occurred: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"[DEBUG] verify_password traceback:\n{traceback.format_exc()}")
        return False


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
    # Normalize username (strip whitespace, but keep case-sensitive for now)
    username = username.strip() if username else ""
    password = password if password else ""
    
    if not username or not password:
        print(f"[DEBUG] Login: Empty username or password provided")
        return False, None, "Veuillez remplir tous les champs"
    
    try:
        # Try to establish database connection
        # This will raise an exception if connection fails (e.g., wrong credentials, network issue)
        conn = get_connection()
        cur = conn.cursor()
    except ValueError as e:
        # Configuration error (missing environment variables)
        return False, None, f"❌ Erreur de configuration: {str(e)}"
    except Exception as e:
        # Connection error (network, SSL, wrong DB credentials)
        error_msg = str(e)
        # Provide helpful error message for common connection issues
        if "password authentication failed" in error_msg.lower():
            return False, None, "❌ Erreur de connexion à la base de données: Identifiants incorrects. Vérifiez DB_USER et DB_PASSWORD dans Streamlit Cloud Secrets."
        elif "could not connect" in error_msg.lower() or "connection refused" in error_msg.lower():
            return False, None, "❌ Erreur de connexion: Impossible de se connecter à la base de données. Vérifiez DB_HOST et que la base de données est accessible."
        elif "ssl" in error_msg.lower():
            return False, None, f"❌ Erreur SSL: {error_msg}"
        else:
            return False, None, f"❌ Erreur de connexion à la base de données: {error_msg}"
    
    try:
        # Query user by username
        cur.execute("""
            SELECT id, username, password_hash, role, linked_id
            FROM users
            WHERE username = %s;
        """, (username,))
        
        user = cur.fetchone()
        
        # DEBUG: Log user fetch result
        print(f"[DEBUG] Login attempt for username: '{username}'")
        if user:
            print(f"[DEBUG] User found: id={user.get('id')}, username={user.get('username')}, role={user.get('role')}, linked_id={user.get('linked_id')}")
            print(f"[DEBUG] Password hash exists: {user.get('password_hash') is not None}")
            print(f"[DEBUG] Password hash length: {len(user.get('password_hash', '')) if user.get('password_hash') else 0}")
            print(f"[DEBUG] Password hash preview: {user.get('password_hash', '')[:20] if user.get('password_hash') else 'None'}...")
        else:
            print(f"[DEBUG] User NOT found in database for username: '{username}'")
            return False, None, "Nom d'utilisateur ou mot de passe incorrect"
        
        # Check if password_hash exists and is not empty
        password_hash = user.get('password_hash')
        if not password_hash:
            print(f"[DEBUG] ERROR: password_hash is None or empty for user '{username}'")
            return False, None, "❌ Erreur: Le mot de passe de l'utilisateur n'est pas configuré correctement dans la base de données."
        
        # Verify password
        print(f"[DEBUG] Attempting password verification...")
        print(f"[DEBUG] Input password length: {len(password)}")
        print(f"[DEBUG] Stored hash length: {len(password_hash)}")
        
        password_valid = verify_password(password, password_hash)
        print(f"[DEBUG] Password verification result: {password_valid}")
        
        if not password_valid:
            print(f"[DEBUG] Password verification FAILED for user '{username}'")
            return False, None, "Nom d'utilisateur ou mot de passe incorrect"
        
        print(f"[DEBUG] Password verification SUCCESS for user '{username}'")
        
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
        
        print(f"[DEBUG] Login SUCCESS for user '{username}' with role '{user_data['role']}'")
        return True, user_data, "Connexion réussie"
        
    except Exception as e:
        conn.rollback()
        # Database query error (table doesn't exist, etc.)
        error_msg = str(e)
        print(f"[DEBUG] Exception during login query: {type(e).__name__}: {error_msg}")
        import traceback
        print(f"[DEBUG] Traceback:\n{traceback.format_exc()}")
        if "does not exist" in error_msg.lower() or "relation" in error_msg.lower():
            return False, None, f"❌ Erreur: La table 'users' n'existe pas. Vérifiez que le schéma de la base de données est correctement initialisé."
        return False, None, f"❌ Erreur lors de la connexion: {error_msg}"
        
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
