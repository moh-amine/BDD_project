from ..database.connection import get_connection
from datetime import time

def generate_schedule():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT m.id
        FROM module m
        WHERE m.id NOT IN (SELECT module_id FROM examen);
    """)
    modules = cur.fetchall()

    heure_debut = time(9, 0)

    for m in modules:
        try:
            cur.execute("""
                INSERT INTO examen (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
                SELECT
                    CURRENT_DATE + INTERVAL '1 day',
                    %s,
                    120,
                    %s,
                    p.id,
                    s.id
                FROM professeur p, salle s
                LIMIT 1;
            """, (heure_debut, m["id"]))

            heure_debut = time(heure_debut.hour + 2, 0)

        except:
            continue

    conn.commit()
    cur.close()
    conn.close()
