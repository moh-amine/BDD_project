from backend.database.connection import get_connection

try:
    conn = get_connection()
    print("✅ Connexion PostgreSQL OK")
    conn.close()
except Exception as e:
    print("❌ Erreur de connexion :", e)
