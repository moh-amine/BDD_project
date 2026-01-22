"""
Database Connection Module
==========================
This module provides database connection functionality for PostgreSQL.
All database operations use this centralized connection function.

The connection uses RealDictCursor which returns results as dictionaries
instead of tuples, making data access more readable.

Connection parameters are read ONLY from environment variables (no fallbacks):
- DB_HOST: Database host (required)
- DB_PORT: Database port (required)
- DB_NAME: Database name (required)
- DB_USER: Database user (required)
- DB_PASSWORD: Database password (required)

For local development:
- If environment variables are not set, the module will attempt to load them
  from a .env file in the project root using python-dotenv

For Streamlit Cloud deployment:
- All variables must be set in Streamlit Cloud Secrets (TOML format)
- SSL mode is automatically set to "require" (mandatory for Neon PostgreSQL)

Author: Exam Scheduling System
"""

import os
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor


def _load_env_file_if_needed():
    """
    Attempt to load .env file for local development.
    Only loads if any required DB variable is not already set in environment.
    This is safe because:
    - Cloud deployments set environment variables directly
    - Local development can use .env file
    - No credentials are hardcoded
    """
    # Check if any required variable is missing (local development scenario)
    required_vars = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    if any(os.getenv(var) is None for var in required_vars):
        try:
            from dotenv import load_dotenv
            
            # Find project root (where .env should be located)
            # This works whether running from frontend/ or project root
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent  # backend/database/connection.py -> project root
            env_file = project_root / ".env"
            
            # Try to load .env file if it exists
            if env_file.exists():
                load_dotenv(dotenv_path=env_file, override=False)
        except ImportError:
            # python-dotenv not installed - that's OK, will use environment variables only
            pass
        except Exception:
            # Silently fail - will raise clear error later if variables still missing
            pass


def _validate_connection_params():
    """
    Validate that all required database connection parameters are set.
    
    Returns:
        tuple: (host, port, database, user, password) if all are valid
        
    Raises:
        ValueError: If any required environment variable is missing
    """
    # Try to load .env file for local development (if any variable missing)
    _load_env_file_if_needed()
    
    # Read connection parameters from environment variables (NO DEFAULTS)
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    
    # Collect all missing variables for a comprehensive error message
    missing_vars = []
    if host is None:
        missing_vars.append("DB_HOST")
    if port is None:
        missing_vars.append("DB_PORT")
    if database is None:
        missing_vars.append("DB_NAME")
    if user is None:
        missing_vars.append("DB_USER")
    if password is None:
        missing_vars.append("DB_PASSWORD")
    
    # Raise error if any variable is missing
    if missing_vars:
        error_msg = (
            f"❌ Database connection error: Missing required environment variable(s): {', '.join(missing_vars)}\n\n"
            "📋 For LOCAL development:\n"
            "   1. Create a .env file in the project root\n"
            "   2. Add all required variables:\n"
            "      DB_HOST=your_host\n"
            "      DB_PORT=5432\n"
            "      DB_NAME=your_database\n"
            "      DB_USER=your_user\n"
            "      DB_PASSWORD=your_password\n"
            "   3. Install python-dotenv: pip install python-dotenv\n\n"
            "☁️  For CLOUD deployment (Streamlit Cloud):\n"
            "   1. Go to your app settings in Streamlit Cloud\n"
            "   2. Open 'Secrets' tab\n"
            "   3. Add all required variables in TOML format:\n"
            "      [database]\n"
            "      DB_HOST = \"your_host\"\n"
            "      DB_PORT = \"5432\"\n"
            "      DB_NAME = \"your_database\"\n"
            "      DB_USER = \"your_user\"\n"
            "      DB_PASSWORD = \"your_password\"\n"
            "   4. Or use top-level format:\n"
            "      DB_HOST = \"your_host\"\n"
            "      DB_PORT = \"5432\"\n"
            "      DB_NAME = \"your_database\"\n"
            "      DB_USER = \"your_user\"\n"
            "      DB_PASSWORD = \"your_password\"\n\n"
            "⚠️  Security: Never hardcode credentials in source code!"
        )
        raise ValueError(error_msg)
    
    # Validate port is a valid integer
    try:
        port = int(port)
    except ValueError:
        raise ValueError(f"Invalid DB_PORT value: '{port}'. Must be an integer.")
    
    return host, port, database, user, password


def get_connection():
    """
    Create and return a PostgreSQL database connection.
    
    Reads connection parameters ONLY from environment variables (no fallbacks):
    - DB_HOST: Database host (required)
    - DB_PORT: Database port (required, must be integer)
    - DB_NAME: Database name (required)
    - DB_USER: Database user (required)
    - DB_PASSWORD: Database password (required)
    
    SSL mode is automatically set to "require" (mandatory for Neon PostgreSQL).
    
    For local development:
    - If environment variables are not set, attempts to load from .env file
    - .env file should be in the project root directory
    
    For Streamlit Cloud deployment:
    - All variables must be set in Streamlit Cloud Secrets (TOML format)
    - See error message for exact format requirements
    
    Returns:
        psycopg2.connection: Database connection object with RealDictCursor
        
    Raises:
        ValueError: If any required environment variable is missing or invalid
        psycopg2.OperationalError: If connection fails (e.g., wrong credentials, network issue)
        
    Example:
        >>> conn = get_connection()
        >>> cur = conn.cursor()
        >>> cur.execute("SELECT * FROM users;")
        >>> results = cur.fetchall()
        >>> cur.close()
        >>> conn.close()
    """
    # Validate and get all connection parameters
    host, port, database, user, password = _validate_connection_params()
    
    # Create connection with SSL mode "require" (mandatory for Neon PostgreSQL)
    # This ensures secure connection to cloud-hosted databases
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        sslmode="require",  # Mandatory for Neon PostgreSQL
        cursor_factory=RealDictCursor
    )
    
    # Optional: Verify connection is working (for debugging/confirmation)
    # This helps catch connection issues early
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 as connection_test")
            cur.fetchone()
    except Exception as e:
        conn.close()
        raise psycopg2.OperationalError(
            f"Database connection established but test query failed: {e}"
        ) from e
    
    return conn
