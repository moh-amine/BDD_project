"""
Scheduler Optimization Module
==============================
This module provides automatic exam scheduling functionality.
It generates exam schedules for modules that don't have exams yet.

The scheduler intelligently assigns exams to:
- Available professors (preferably from same department)
- Available rooms (with sufficient capacity)
- Non-overlapping time slots
- Multiple days if needed

All database constraints are respected:
- No student overlapping exams
- No professor simultaneous exams
- Room capacity sufficient
- One exam per module

Author: Exam Scheduling System
"""

from ..database.connection import get_connection
from datetime import time, date, timedelta, datetime


def generate_schedule(start_date=None, start_time=time(9, 0), duration_minutes=120, time_slots_per_day=4):
    """
    Automatically generate exam schedule for modules without exams.
    
    This function:
    1. Finds all modules that don't have exams scheduled
    2. For each module, finds:
       - A professor from the same department (or any available professor)
       - A room with sufficient capacity for the formation
       - An available time slot (no conflicts)
    3. Distributes exams across multiple days if needed
    4. Respects all database constraints
    
    Args:
        start_date (date, optional): Starting date for exams. Defaults to tomorrow.
        start_time (time, optional): Starting time for first exam. Defaults to 09:00.
        duration_minutes (int, optional): Exam duration in minutes. Defaults to 120.
        time_slots_per_day (int, optional): Maximum exams per day. Defaults to 4.
    
    Returns:
        dict: {
            'success': int,      # Number of exams successfully scheduled
            'failed': int,        # Number of modules that couldn't be scheduled
            'total': int,         # Total modules without exams
            'details': list       # List of (module_id, status, message) tuples
        }
    """
    conn = get_connection()
    cur = conn.cursor()

    results = {
        'success': 0,
        'failed': 0,
        'total': 0,
        'details': []
    }

    try:
        # Find modules without scheduled exams with their formation info
        cur.execute("""
            SELECT 
                m.id AS module_id,
                m.nom AS module_nom,
                m.formation_id,
                f.departement_id,
                COUNT(e.id) AS student_count
            FROM module m
            JOIN formation f ON f.id = m.formation_id
            LEFT JOIN etudiant e ON e.formation_id = f.id
            WHERE m.id NOT IN (SELECT module_id FROM examen WHERE module_id IS NOT NULL)
            GROUP BY m.id, m.nom, m.formation_id, f.departement_id
            ORDER BY m.id;
        """)
        modules = cur.fetchall()
        results['total'] = len(modules)

        if not modules:
            return results

        # Set default start date to tomorrow if not provided
        if start_date is None:
            start_date = date.today() + timedelta(days=1)

        current_date = start_date
        current_time = start_time
        exams_today = 0

        # Schedule each module
        for module in modules:
            module_id = module['module_id']
            module_nom = module['module_nom']
            formation_id = module['formation_id']
            departement_id = module['departement_id']
            student_count = module['student_count'] or 0

            scheduled = False
            error_message = None

            # Try to find a valid slot (try multiple days if needed)
            max_attempts = 10  # Try up to 10 days
            attempt = 0

            while not scheduled and attempt < max_attempts:
                # Reset to start of day if we've exceeded slots per day
                if exams_today >= time_slots_per_day:
                    current_date += timedelta(days=1)
                    current_time = start_time
                    exams_today = 0
                    attempt += 1
                    continue

                # Calculate end time
                time_delta = timedelta(minutes=duration_minutes)
                start_datetime = current_date
                end_time = (datetime.combine(current_date, current_time) + time_delta).time()

                # Find available professor (prefer same department)
                cur.execute("""
                    SELECT p.id, p.nom, p.departement_id
                    FROM professeur p
                    WHERE p.id NOT IN (
                        SELECT DISTINCT e.professeur_id
                        FROM examen e
                        WHERE e.date = %s
                          AND e.professeur_id IS NOT NULL
                          AND (
                              %s < (e.heure_debut + (e.duree_minutes || ' minutes')::interval)
                              AND
                              e.heure_debut < (%s + (%s || ' minutes')::interval)
                          )
                    )
                    ORDER BY 
                        CASE WHEN p.departement_id = %s THEN 0 ELSE 1 END,
                        p.id
                    LIMIT 1;
                """, (current_date, current_time, current_time, duration_minutes, departement_id))

                prof = cur.fetchone()

                if not prof:
                    # No available professor at this time, try next time slot
                    current_time = (datetime.combine(current_date, current_time) + timedelta(hours=2)).time()
                    if current_time.hour >= 18:  # After 6 PM, move to next day
                        current_date += timedelta(days=1)
                        current_time = start_time
                        exams_today = 0
                    attempt += 1
                    continue

                # Find available room with sufficient capacity
                cur.execute("""
                    SELECT s.id, s.nom, s.capacite
                    FROM salle s
                    WHERE s.capacite >= %s
                      AND s.id NOT IN (
                          SELECT DISTINCT e.salle_id
                          FROM examen e
                          WHERE e.date = %s
                            AND e.salle_id IS NOT NULL
                            AND (
                                %s < (e.heure_debut + (e.duree_minutes || ' minutes')::interval)
                                AND
                                e.heure_debut < (%s + (%s || ' minutes')::interval)
                            )
                      )
                    ORDER BY s.capacite ASC  -- Prefer smaller rooms first
                    LIMIT 1;
                """, (student_count, current_date, current_time, current_time, duration_minutes))

                salle = cur.fetchone()

                if not salle:
                    # No available room at this time, try next time slot
                    current_time = (datetime.combine(current_date, current_time) + timedelta(hours=2)).time()
                    if current_time.hour >= 18:  # After 6 PM, move to next day
                        current_date += timedelta(days=1)
                        current_time = start_time
                        exams_today = 0
                    attempt += 1
                    continue

                # Try to insert the exam
                try:
                    cur.execute("""
                        INSERT INTO examen 
                        (date, heure_debut, duree_minutes, module_id, professeur_id, salle_id)
                        VALUES (%s, %s, %s, %s, %s, %s);
                    """, (current_date, current_time, duration_minutes, module_id, prof['id'], salle['id']))

                    # Success!
                    scheduled = True
                    results['success'] += 1
                    results['details'].append((
                        module_id,
                        'success',
                        f"Module '{module_nom}' programmé le {current_date} à {current_time.strftime('%H:%M')} avec {prof['nom']} en {salle['nom']}"
                    ))

                    # Move to next time slot
                    current_time = (datetime.combine(current_date, current_time) + timedelta(hours=2)).time()
                    if current_time.hour >= 18:  # After 6 PM, move to next day
                        current_date += timedelta(days=1)
                        current_time = start_time
                        exams_today = 0
                    else:
                        exams_today += 1

                except Exception as e:
                    # Constraint violation or other error
                    error_message = str(e)
                    # Try next time slot
                    current_time = (datetime.combine(current_date, current_time) + timedelta(hours=2)).time()
                    if current_time.hour >= 18:
                        current_date += timedelta(days=1)
                        current_time = start_time
                        exams_today = 0
                    attempt += 1

            # If we couldn't schedule this module
            if not scheduled:
                results['failed'] += 1
                results['details'].append((
                    module_id,
                    'failed',
                    f"Module '{module_nom}' n'a pas pu être programmé: {error_message or 'Aucun créneau disponible après plusieurs tentatives'}"
                ))

        conn.commit()
        return results

    except Exception as e:
        conn.rollback()
        raise Exception(f"Erreur lors de la génération du planning: {str(e)}")

    finally:
        cur.close()
        conn.close()


