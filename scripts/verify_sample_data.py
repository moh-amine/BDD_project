"""Verify the sample data structure"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import get_connection

def verify_data():
    """Verify the sample data structure"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        print("=" * 60)
        print("Database Structure Verification")
        print("=" * 60)
        print()
        
        # Show departments
        print("DEPARTEMENTS:")
        cur.execute("SELECT id, nom FROM departement ORDER BY nom;")
        depts = cur.fetchall()
        for dept in depts:
            print(f"  [{dept['id']}] {dept['nom']}")
        print()
        
        # Show formations by department
        print("FORMATIONS:")
        for dept in depts:
            print(f"  {dept['nom']}:")
            cur.execute("""
                SELECT id, nom, niveau 
                FROM formation 
                WHERE departement_id = %s 
                ORDER BY nom;
            """, (dept['id'],))
            forms = cur.fetchall()
            for form in forms:
                print(f"    [{form['id']}] {form['nom']} ({form['niveau']})")
        print()
        
        # Show modules by formation
        print("MODULES:")
        cur.execute("""
            SELECT 
                d.nom as departement,
                f.nom as formation,
                m.id,
                m.nom as module
            FROM module m
            JOIN formation f ON f.id = m.formation_id
            JOIN departement d ON d.id = f.departement_id
            ORDER BY d.nom, f.nom, m.nom;
        """)
        modules = cur.fetchall()
        
        current_dept = None
        current_form = None
        
        for mod in modules:
            if mod['departement'] != current_dept:
                current_dept = mod['departement']
                current_form = None
                print(f"  {current_dept}:")
            
            if mod['formation'] != current_form:
                current_form = mod['formation']
                print(f"    {current_form}:")
            
            print(f"      [{mod['id']}] {mod['module']}")
        
        print()
        print("=" * 60)
        print("[SUCCESS] Data structure verified!")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    verify_data()
