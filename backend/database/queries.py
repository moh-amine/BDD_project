"""
Database Queries Module
=======================
This module contains all database query functions for retrieving data.
Functions are organized by entity type (examens, modules, professeurs, etc.)
and include role-based filtering functions for authentication.

All functions follow a consistent pattern:
1. Get database connection
2. Execute query
3. Fetch results
4. Close connection
5. Return data

Author: Exam Scheduling System
"""

from .connection import get_connection


def get_all_examens():
    """
    Retrieve all exams with related information (module, professor, room).
    
    Returns:
        list: List of dictionaries containing exam data
            Each dictionary contains: id, module, date, heure_debut, 
            duree_minutes, professeur, salle
            
    Note:
        Used by ADMIN role to display all exams.
        Results are ordered by date and start time.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            e.id,
            m.nom AS module,
            e.date,
            e.heure_debut,
            e.duree_minutes,
            p.nom AS professeur,
            d.nom AS departement,
            s.nom AS salle,
            f.nom AS formation
        FROM examen e
        JOIN module m ON m.id = e.module_id
        JOIN formation f ON f.id = m.formation_id
        JOIN departement d ON d.id = f.departement_id
        JOIN professeur p ON p.id = e.professeur_id
        JOIN salle s ON s.id = e.salle_id
        ORDER BY e.date, e.heure_debut;
    """)

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def get_modules():
    """
    Retrieve all modules.
    
    Returns:
        list: List of dictionaries with id and nom (name) for each module
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nom FROM module ORDER BY nom;")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def get_professeurs():
    """
    Retrieve all professors.
    
    Returns:
        list: List of dictionaries with id and nom (name) for each professor
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nom FROM professeur ORDER BY nom;")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def get_salles():
    """
    Retrieve all rooms (salles).
    
    Returns:
        list: List of dictionaries with id and nom (name) for each room
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nom FROM salle ORDER BY nom;")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_examens_simple():
    """
    Retrieve simplified exam list for selection dropdowns.
    
    Returns:
        list: List of dictionaries with id and label (formatted string)
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            e.id,
            m.nom || ' | ' || e.date || ' ' || e.heure_debut AS label
        FROM examen e
        JOIN module m ON m.id = e.module_id
        ORDER BY e.date, e.heure_debut;
    """)

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def get_examen_details(examen_id):
    """
    Retrieve detailed information about a specific exam including module, formation, and department.
    
    Args:
        examen_id (int): Exam ID
        
    Returns:
        dict: Dictionary containing exam details including module_id, formation_id, departement_id
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            e.id,
            e.date,
            e.heure_debut,
            e.duree_minutes,
            e.module_id,
            e.professeur_id,
            e.salle_id,
            m.formation_id,
            f.departement_id
        FROM examen e
        JOIN module m ON m.id = e.module_id
        JOIN formation f ON f.id = m.formation_id
        WHERE e.id = %s;
    """, (examen_id,))

    data = cur.fetchone()
    cur.close()
    conn.close()
    return dict(data) if data else None

def get_departements():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nom FROM departement ORDER BY nom;")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def get_formations_by_departement(dept_id):
    """
    Retrieve all formations for a specific department.
    
    Args:
        dept_id (int): Department ID
        
    Returns:
        list: List of dictionaries with id and nom (name) for each formation
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nom
        FROM formation
        WHERE departement_id = %s
        ORDER BY nom;
    """, (dept_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def get_modules_by_formation(formation_id):
    """
    Retrieve all modules for a specific formation.
    
    Args:
        formation_id (int): Formation ID
        
    Returns:
        list: List of dictionaries with id and nom (name) for each module
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nom
        FROM module
        WHERE formation_id = %s
        ORDER BY nom;
    """, (formation_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def get_examens_filtered(dept_id=None, formation_id=None, professeur_id=None):
    """
    Retrieve exams with optional filters for department, formation, or professor.
    
    This function builds a dynamic SQL query based on provided filters.
    Used by ADMIN role for analytical filtering.
    
    Args:
        dept_id (int, optional): Filter by department ID
        formation_id (int, optional): Filter by formation ID
        professeur_id (int, optional): Filter by professor ID
        
    Returns:
        list: List of dictionaries containing filtered exam data
        
    Example:
        >>> exams = get_examens_filtered(dept_id=1, professeur_id=2)
        >>> # Returns exams in department 1 assigned to professor 2
    """
    conn = get_connection()
    cur = conn.cursor()

    # Base query with joins
    query = """
        SELECT
            e.id,
            m.nom AS module,
            e.date,
            e.heure_debut,
            p.nom AS professeur,
            d.nom AS departement,
            s.nom AS salle,
            f.nom AS formation
        FROM examen e
        JOIN module m ON m.id = e.module_id
        JOIN formation f ON f.id = m.formation_id
        JOIN departement d ON d.id = f.departement_id
        JOIN professeur p ON p.id = e.professeur_id
        JOIN salle s ON s.id = e.salle_id
        WHERE 1=1
    """

    # Build dynamic WHERE clause based on provided filters
    params = []

    if dept_id:
        query += " AND f.departement_id = %s"
        params.append(dept_id)

    if formation_id:
        query += " AND f.id = %s"
        params.append(formation_id)

    if professeur_id:
        query += " AND p.id = %s"
        params.append(professeur_id)

    query += " ORDER BY e.date, e.heure_debut;"

    cur.execute(query, params)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def kpi_occupation_salles():
    """
    Calculate KPI: Room occupation statistics.
    
    Returns the number of exams per room, ordered by exam count (descending).
    Used for dashboard analytics (ADMIN only).
    
    Returns:
        list: List of dictionaries with salle (room name) and nb_examens (count)
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            s.nom AS salle,
            COUNT(e.id) AS nb_examens
        FROM salle s
        LEFT JOIN examen e ON e.salle_id = s.id
        GROUP BY s.nom
        ORDER BY nb_examens DESC;
    """)

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def kpi_examens_par_prof():
    """
    Calculate KPI: Exams per professor statistics.
    
    Returns the number of exams per professor, ordered by exam count (descending).
    Used for dashboard analytics (ADMIN only).
    
    Returns:
        list: List of dictionaries with professeur (professor name) and nb_examens (count)
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.nom AS professeur,
            COUNT(e.id) AS nb_examens
        FROM professeur p
        LEFT JOIN examen e ON e.professeur_id = p.id
        GROUP BY p.nom
        ORDER BY nb_examens DESC;
    """)

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


# ============================================================
# ROLE-BASED QUERY FUNCTIONS
# ============================================================
# These functions filter exams based on user roles:
# - Professeur: Only see exams they are assigned to
# - Etudiant: Only see exams for their formation
# ============================================================


def get_examens_by_professeur(professeur_id: int):
    """
    Get all exams assigned to a specific professor.
    Used for PROFESSEUR role to show only their exams.
    
    Args:
        professeur_id (int): ID of the professor
        
    Returns:
        list: List of exam dictionaries
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            e.id,
            m.nom AS module,
            e.date,
            e.heure_debut,
            e.duree_minutes,
            p.nom AS professeur,
            d.nom AS departement,
            s.nom AS salle
        FROM examen e
        JOIN module m ON m.id = e.module_id
        JOIN professeur p ON p.id = e.professeur_id
        JOIN departement d ON d.id = p.departement_id
        JOIN salle s ON s.id = e.salle_id
        WHERE e.professeur_id = %s
        ORDER BY e.date, e.heure_debut;
    """, (professeur_id,))

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def get_examens_by_etudiant_formation(etudiant_id: int):
    """
    Get all exams for formations that a student is enrolled in.
    Used for ETUDIANT role to show only exams relevant to their formation.
    
    This function:
    1. Gets the student's formation_id from etudiant table
    2. Finds all exams for modules in that formation
    
    Args:
        etudiant_id (int): ID of the student
        
    Returns:
        list: List of exam dictionaries
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Step 1: Get the student's formation_id
        cur.execute("SELECT formation_id FROM etudiant WHERE id = %s;", (etudiant_id,))
        etudiant_result = cur.fetchone()
        
        if not etudiant_result or not etudiant_result.get('formation_id'):
            # Fallback: try to get formation_id from inscription table
            cur.execute("""
                SELECT DISTINCT m.formation_id
                FROM inscription i
                JOIN module m ON m.id = i.module_id
                WHERE i.etudiant_id = %s
                LIMIT 1;
            """, (etudiant_id,))
            inscription_result = cur.fetchone()
            
            if not inscription_result or not inscription_result.get('formation_id'):
                # No formation found for this student
                return []
            
            formation_id = inscription_result['formation_id']
        else:
            formation_id = etudiant_result['formation_id']
        
        # Step 2: Get all exams for modules in this formation
        # Include department and formation info
        cur.execute("""
            SELECT
                e.id,
                m.nom AS module,
                e.date,
                e.heure_debut,
                e.duree_minutes,
                p.nom AS professeur,
                d.nom AS departement,
                s.nom AS salle,
                f.nom AS formation
            FROM examen e
            JOIN module m ON m.id = e.module_id
            JOIN formation f ON f.id = m.formation_id
            JOIN departement d ON d.id = f.departement_id
            JOIN professeur p ON p.id = e.professeur_id
            JOIN salle s ON s.id = e.salle_id
            WHERE m.formation_id = %s
            ORDER BY e.date, e.heure_debut;
        """, (formation_id,))

        data = cur.fetchall()
        return data
        
    except Exception as e:
        # Log error but return empty list to prevent crashes
        print(f"Error in get_examens_by_etudiant_formation: {e}")
        return []
        
    finally:
        cur.close()
        conn.close()


def get_etudiant_formation_id(etudiant_id: int):
    """
    Get the formation_id for a given student.
    Checks both etudiant table and inscription table.
    
    Args:
        etudiant_id (int): ID of the student
        
    Returns:
        int | None: Formation ID or None if not found
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Try direct link from etudiant table
        cur.execute("SELECT formation_id FROM etudiant WHERE id = %s;", (etudiant_id,))
        result = cur.fetchone()
        
        if result and result.get('formation_id'):
            return result['formation_id']
        
        # Fallback to inscription table
        cur.execute("""
            SELECT formation_id 
            FROM inscription 
            WHERE etudiant_id = %s 
            LIMIT 1;
        """, (etudiant_id,))
        result = cur.fetchone()
        
        return result['formation_id'] if result else None
        
    except Exception:
        return None
        
    finally:
        cur.close()
        conn.close()


def get_etudiant_info(etudiant_id: int):
    """
    Get complete student information including full name and department.
    
    Args:
        etudiant_id (int): ID of the student
        
    Returns:
        dict: Dictionary containing student info with nom, prenom, full_name, formation, departement
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                et.id,
                et.nom,
                et.prenom,
                et.nom || ' ' || et.prenom AS full_name,
                f.nom AS formation,
                d.nom AS departement,
                et.formation_id,
                et.promotion
            FROM etudiant et
            JOIN formation f ON f.id = et.formation_id
            JOIN departement d ON d.id = f.departement_id
            WHERE et.id = %s;
        """, (etudiant_id,))
        
        result = cur.fetchone()
        return dict(result) if result else None
        
    except Exception:
        return None
        
    finally:
        cur.close()
        conn.close()