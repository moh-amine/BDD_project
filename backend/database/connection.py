"""
Database Connection Module
==========================
This module provides database connection functionality for PostgreSQL.
All database operations use this centralized connection function.

The connection uses RealDictCursor which returns results as dictionaries
instead of tuples, making data access more readable.

Author: Exam Scheduling System
"""

import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    """
    Create and return a PostgreSQL database connection.
    
    Returns:
        psycopg2.connection: Database connection object
        
    Note:
        Connection parameters are hardcoded. In production, consider using
        environment variables or a configuration file.
        
    Example:
        >>> conn = get_connection()
        >>> cur = conn.cursor()
        >>> cur.execute("SELECT * FROM users;")
        >>> results = cur.fetchall()
        >>> cur.close()
        >>> conn.close()
    """
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="exam_scheduler",
        user="postgres",
        password="1234",
        cursor_factory=RealDictCursor
    )
