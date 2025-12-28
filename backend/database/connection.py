import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="exam_scheduler",
        user="postgres",
        password="1234",
        cursor_factory=RealDictCursor
    )
