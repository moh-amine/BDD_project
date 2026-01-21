"""
Execute SQL script to populate database with sample data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import get_connection

SQL_SCRIPT = """
BEGIN;

-- ===============================
-- 1️⃣ DEPARTEMENTS
-- ===============================
INSERT INTO departement (nom)
VALUES
('Informatique'),
('Physique'),
('Mathématiques')
ON CONFLICT (nom) DO NOTHING;

-- ===============================
-- 2️⃣ FORMATIONS (ALL REQUIRED COLUMNS)
-- ===============================

-- Informatique
INSERT INTO formation (nom, niveau, nb_modules, departement_id)
SELECT 'Licence Informatique', 'Licence', 6, id
FROM departement WHERE nom = 'Informatique'
ON CONFLICT DO NOTHING;

INSERT INTO formation (nom, niveau, nb_modules, departement_id)
SELECT 'Master Informatique', 'Master', 4, id
FROM departement WHERE nom = 'Informatique'
ON CONFLICT DO NOTHING;

-- Physique
INSERT INTO formation (nom, niveau, nb_modules, departement_id)
SELECT 'Licence Physique', 'Licence', 6, id
FROM departement WHERE nom = 'Physique'
ON CONFLICT DO NOTHING;

INSERT INTO formation (nom, niveau, nb_modules, departement_id)
SELECT 'Master Physique', 'Master', 4, id
FROM departement WHERE nom = 'Physique'
ON CONFLICT DO NOTHING;

-- Mathématiques
INSERT INTO formation (nom, niveau, nb_modules, departement_id)
SELECT 'Licence Mathématiques', 'Licence', 6, id
FROM departement WHERE nom = 'Mathématiques'
ON CONFLICT DO NOTHING;

INSERT INTO formation (nom, niveau, nb_modules, departement_id)
SELECT 'Master Mathématiques', 'Master', 4, id
FROM departement WHERE nom = 'Mathématiques'
ON CONFLICT DO NOTHING;

-- ===============================
-- 3️⃣ MODULES
-- ===============================

-- Informatique
INSERT INTO module (nom, credits, formation_id)
SELECT 'Bases de Données', 6, id FROM formation WHERE nom = 'Licence Informatique'
ON CONFLICT DO NOTHING;

INSERT INTO module (nom, credits, formation_id)
SELECT 'Programmation Python', 6, id FROM formation WHERE nom = 'Licence Informatique'
ON CONFLICT DO NOTHING;

INSERT INTO module (nom, credits, formation_id)
SELECT 'Systèmes d''exploitation', 6, id FROM formation WHERE nom = 'Master Informatique'
ON CONFLICT DO NOTHING;

-- Physique
INSERT INTO module (nom, credits, formation_id)
SELECT 'Mécanique Générale', 6, id FROM formation WHERE nom = 'Licence Physique'
ON CONFLICT DO NOTHING;

INSERT INTO module (nom, credits, formation_id)
SELECT 'Électromagnétisme', 6, id FROM formation WHERE nom = 'Licence Physique'
ON CONFLICT DO NOTHING;

INSERT INTO module (nom, credits, formation_id)
SELECT 'Physique Quantique', 6, id FROM formation WHERE nom = 'Master Physique'
ON CONFLICT DO NOTHING;

-- Mathématiques
INSERT INTO module (nom, credits, formation_id)
SELECT 'Analyse Mathématique', 6, id FROM formation WHERE nom = 'Licence Mathématiques'
ON CONFLICT DO NOTHING;

INSERT INTO module (nom, credits, formation_id)
SELECT 'Algèbre Linéaire', 6, id FROM formation WHERE nom = 'Licence Mathématiques'
ON CONFLICT DO NOTHING;

INSERT INTO module (nom, credits, formation_id)
SELECT 'Probabilités', 6, id FROM formation WHERE nom = 'Master Mathématiques'
ON CONFLICT DO NOTHING;

COMMIT;
"""

def populate_database():
    """Execute SQL script to populate database with sample data"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        print("Populating database with sample data...")
        print("-" * 60)
        
        # Execute the SQL script
        cur.execute(SQL_SCRIPT)
        conn.commit()
        
        print("[OK] Sample data inserted successfully!")
        print()
        
        # Verify data was inserted
        print("Verifying inserted data...")
        
        # Count departments
        cur.execute("SELECT COUNT(*) as count FROM departement;")
        dept_count = cur.fetchone()['count']
        print(f"  - Departements: {dept_count}")
        
        # Count formations
        cur.execute("SELECT COUNT(*) as count FROM formation;")
        form_count = cur.fetchone()['count']
        print(f"  - Formations: {form_count}")
        
        # Count modules
        cur.execute("SELECT COUNT(*) as count FROM module;")
        module_count = cur.fetchone()['count']
        print(f"  - Modules: {module_count}")
        
        print()
        print("-" * 60)
        print("[SUCCESS] Database populated successfully!")
        print()
        print("You can now test the exam creation cascade:")
        print("  1. Login as admin")
        print("  2. Go to 'Gérer les examens'")
        print("  3. Try creating exams for different departments")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Failed to populate database: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    populate_database()
