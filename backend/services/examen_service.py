from ..database.connection import get_connection

def create_examen(date, heure_debut, duree, module_id, professeur_id, salle_id):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO examen
            (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (date, heure_debut, duree, module_id, professeur_id, salle_id))

        conn.commit()
        return True, "Examen créé avec succès"

    except Exception as e:
        conn.rollback()
        return False, str(e)

    finally:
        cur.close()
        conn.close()

def delete_examen(examen_id):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM examen WHERE id = %s;", (examen_id,))
        conn.commit()
        return True, "Examen supprimé avec succès"

    except Exception as e:
        conn.rollback()
        return False, str(e)

    finally:
        cur.close()
        conn.close()


def update_examen(examen_id, date, heure_debut, duree, module_id, professeur_id, salle_id):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE examen
            SET date = %s,
                heure_debut = %s,
                duree_minutes = %s,
                module_id = %s,
                professeur_id = %s,
                salle_id = %s
            WHERE id = %s;
        """, (date, heure_debut, duree, module_id, professeur_id, salle_id, examen_id))

        conn.commit()
        return True, "Examen modifié avec succès"

    except Exception as e:
        conn.rollback()
        return False, str(e)

    finally:
        cur.close()
        conn.close()
