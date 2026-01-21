"""
Examen Service Module
=====================
This module provides business logic for exam management operations:
- Create new exams
- Update existing exams
- Delete exams

All operations include proper transaction handling and error management.
Database constraints and triggers ensure data integrity (room conflicts, 
professor conflicts, overlapping exams).

Author: Exam Scheduling System
"""

from ..database.connection import get_connection


def create_examen(date, heure_debut, duree, module_id, professeur_id, salle_id):
    """
    Create a new exam entry in the database.
    
    This function inserts a new exam with the provided parameters.
    Database triggers will automatically check for:
    - Room conflicts (same room, overlapping time)
    - Professor conflicts (same professor, overlapping time)
    - Invalid schedules
    
    Args:
        date: Exam date (date object)
        heure_debut: Start time (time object)
        duree: Duration in minutes (int)
        module_id: ID of the module (int)
        professeur_id: ID of the assigned professor (int)
        salle_id: ID of the assigned room (int)
        
    Returns:
        tuple: (success: bool, message: str)
            - success: True if exam created successfully
            - message: Success message or error description
            
    Example:
        >>> success, msg = create_examen(date(2024, 1, 15), time(9, 0), 120, 1, 2, 3)
        >>> if success:
        ...     print("Exam created!")
    """
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
    """
    Delete an exam from the database.
    
    Args:
        examen_id: ID of the exam to delete (int)
        
    Returns:
        tuple: (success: bool, message: str)
            - success: True if exam deleted successfully
            - message: Success message or error description
            
    Note:
        Foreign key constraints may prevent deletion if the exam
        is referenced by other tables (e.g., inscription).
    """
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
    """
    Update an existing exam in the database.
    
    This function updates all exam fields. Database triggers will validate
    the new schedule to prevent conflicts.
    
    Args:
        examen_id: ID of the exam to update (int)
        date: New exam date (date object)
        heure_debut: New start time (time object)
        duree: New duration in minutes (int)
        module_id: New module ID (int)
        professeur_id: New professor ID (int)
        salle_id: New room ID (int)
        
    Returns:
        tuple: (success: bool, message: str)
            - success: True if exam updated successfully
            - message: Success message or error description
    """
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
