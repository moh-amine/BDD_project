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

Author: Exam Scheduling System
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    """
    Create and return a PostgreSQL database connection.
    
    Reads connection parameters from environment variables:
    - DB_HOST: Database host (default: localhost)
    - DB_PORT: Database port (default: 5432)
    - DB_NAME: Database name (default: exam_scheduler)
    - DB_USER: Database user (default: postgres)
    - DB_PASSWORD: Database password (required, no default)
    
    Returns:
        psycopg2.connection: Database connection object
        
    Raises:
        ValueError: If DB_PASSWORD is not set
        psycopg2.OperationalError: If connection fails
        
    Example:
        >>> conn = get_connection()
        >>> cur = conn.cursor()
        >>> cur.execute("SELECT * FROM users;")
        >>> results = cur.fetchall()
        >>> cur.close()
        >>> conn.close()
    """
    # Read connection parameters from environment variables
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "exam_scheduler")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD")
    
    # Password is required (no default for security)
    if password is None:
        raise ValueError(
            "DB_PASSWORD environment variable is required. "
            "Please set it in your environment or .env file."
        )
    
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
