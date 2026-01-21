"""Test etudiant exam query to debug the issue"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import get_connection
from backend.database.queries import get_examens_by_etudiant_formation

def test_etudiant_query():
    """Test the etudiant query to see what's happening"""
    conn = get_connection()
    cur = conn.cursor()
    
    print("=" * 60)
    print("Testing Etudiant Exam Query")
    print("=" * 60)
    print()
    
    # Get all etudiants
    cur.execute("SELECT id, nom, prenom, formation_id FROM etudiant;")
    etudiants = cur.fetchall()
    
    print("ETUDIANTS:")
    for etud in etudiants:
        print(f"  [{etud['id']}] {etud['nom']} {etud['prenom']} - Formation ID: {etud['formation_id']}")
    print()
    
    # Get all exams
    cur.execute("""
        SELECT 
            e.id,
            e.date,
            m.nom as module,
            m.formation_id,
            f.nom as formation
        FROM examen e
        JOIN module m ON m.id = e.module_id
        JOIN formation f ON f.id = m.formation_id
        ORDER BY e.date;
    """)
    exams = cur.fetchall()
    
    print("ALL EXAMS:")
    for exam in exams:
        print(f"  [{exam['id']}] {exam['module']} ({exam['formation']}) - Formation ID: {exam['formation_id']} - Date: {exam['date']}")
    print()
    
    # Test the query for each etudiant
    print("TESTING QUERY FOR EACH ETUDIANT:")
    print("-" * 60)
    for etud in etudiants:
        etudiant_id = etud['id']
        formation_id = etud['formation_id']
        
        print(f"\nEtudiant [{etudiant_id}]: {etud['nom']} {etud['prenom']}")
        print(f"  Formation ID: {formation_id}")
        
        # Test the current query
        result = get_examens_by_etudiant_formation(etudiant_id)
        print(f"  Exams found by query: {len(result)}")
        
        if result:
            for exam in result:
                print(f"    - {exam['module']} on {exam['date']}")
        else:
            print("    (No exams found)")
            
            # Debug: Check what the subquery returns
            cur.execute("""
                SELECT COALESCE(
                    (SELECT formation_id FROM etudiant WHERE id = %s),
                    (SELECT formation_id FROM inscription WHERE etudiant_id = %s LIMIT 1)
                ) as formation_id;
            """, (etudiant_id, etudiant_id))
            debug_result = cur.fetchone()
            print(f"  Debug - COALESCE returns: {debug_result['formation_id'] if debug_result else 'NULL'}")
            
            # Check if there are exams for this formation
            cur.execute("""
                SELECT COUNT(*) as count
                FROM examen e
                JOIN module m ON m.id = e.module_id
                WHERE m.formation_id = %s;
            """, (formation_id,))
            exam_count = cur.fetchone()
            print(f"  Debug - Exams in formation {formation_id}: {exam_count['count']}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    test_etudiant_query()
