"""
Database Connection Module
==========================
This module provides database connection functionality for PostgreSQL.
All database operations use this centralized connection function.

The connection uses RealDictCursor which returns results as dictionaries
instead of tuples, making data access more readable.

Connection parameters are read from environment variables for cloud deployment:
- DB_HOST: Database host (default: localhost)
- DB_PORT: Database port (default: 5432)
- DB_NAME: Database name (default: exam_scheduler)
- DB_USER: Database user (default: postgres)
- DB_PASSWORD: Database password (required)

For local development, if environment variables are not set, the module will
attempt to load them from a .env file in the project root.

Author: Exam Scheduling System
"""

import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor


def _load_env_file_if_needed():
    """
    Attempt to load .env file for local development.
    Only loads if DB_PASSWORD is not already set in environment.
    This is safe because:
    - Cloud deployments set environment variables directly
    - Local development can use .env file
    - No credentials are hardcoded
    """
    # Only load .env if DB_PASSWORD is not set (local development scenario)
    if os.getenv("DB_PASSWORD") is None:
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
            # Silently fail - will raise clear error later if password still missing
            pass


def get_connection():
    """
    Create and return a PostgreSQL database connection.
    
    Reads connection parameters from environment variables:
    - DB_HOST: Database host (default: localhost)
    - DB_PORT: Database port (default: 5432)
    - DB_NAME: Database name (default: exam_scheduler)
    - DB_USER: Database user (default: postgres)
    - DB_PASSWORD: Database password (required, no default)
    
    For local development:
    - If DB_PASSWORD is not set, attempts to load from .env file
    - .env file should be in the project root directory
    - See .env.example for template
    
    Returns:
        psycopg2.connection: Database connection object
        
    Raises:
        ValueError: If DB_PASSWORD is not set (with helpful error message)
        psycopg2.OperationalError: If connection fails
        
    Example:
        >>> conn = get_connection()
        >>> cur = conn.cursor()
        >>> cur.execute("SELECT * FROM users;")
        >>> results = cur.fetchall()
        >>> cur.close()
        >>> conn.close()
    """
    # Try to load .env file for local development (if password not set)
    _load_env_file_if_needed()
    
    # Read connection parameters from environment variables
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "exam_scheduler")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD")
    
    # Password is required (no default for security)
    if password is None:
        # Provide helpful error message for both local and cloud scenarios
        error_msg = (
            "❌ Database connection error: DB_PASSWORD environment variable is required.\n\n"
            "📋 For LOCAL development:\n"
            "   1. Create a .env file in the project root (see .env.example)\n"
            "   2. Add: DB_PASSWORD=your_password\n"
            "   3. Install python-dotenv: pip install python-dotenv\n\n"
            "☁️  For CLOUD deployment:\n"
            "   1. Set DB_PASSWORD in Streamlit Cloud Secrets\n"
            "   2. Ensure all DB_* variables are configured\n\n"
            "⚠️  Security: Never hardcode passwords in source code!"
        )
        raise ValueError(error_msg)
    
    # Convert port to integer
    try:
        port = int(port)
    except ValueError:
        raise ValueError(f"Invalid DB_PORT value: {port}. Must be an integer.")
    
    return psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        cursor_factory=RealDictCursor
    )
