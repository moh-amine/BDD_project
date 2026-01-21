"""
Populate database with complete sample data:
- Professeurs (10 teachers)
- Salles (10 rooms)
- Etudiants (10 students across different formations)
- Link students to formations properly
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import get_connection

def populate_full_data():
    """Populate database with complete sample data"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        print("=" * 60)
        print("Populating Database with Complete Sample Data")
        print("=" * 60)
        print()
        
        # ======================
        # 1. PROFESSEURS (10 teachers)
        # ======================
        print("1. Creating Professeurs...")
        professeurs_data = [
            ('Dr. Ait Ahmed', 'Bases de données', 1),  # Informatique
            ('Dr. Benali', 'Intelligence Artificielle', 1),
            ('Dr. Cherif', 'Algorithmes', 1),
            ('Dr. Amrani', 'Réseaux', 1),
            ('Dr. El Fassi', 'Sécurité', 1),
            ('Dr. Martin', 'Mécanique', 3),  # Physique
            ('Dr. Dubois', 'Électromagnétisme', 3),
            ('Dr. Laurent', 'Optique', 3),
            ('Dr. Moreau', 'Analyse', 2),  # Mathématiques
            ('Dr. Bernard', 'Algèbre', 2),
        ]
        
        for nom, specialite, dept_id in professeurs_data:
            cur.execute("""
                INSERT INTO professeur (nom, specialite, departement_id)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (nom, specialite, dept_id))
        
        print(f"   [OK] {len(professeurs_data)} professeurs created")
        print()
        
        # ======================
        # 2. SALLES (10 rooms)
        # ======================
        print("2. Creating Salles...")
        salles_data = [
            ('Amphi A', 300, 'amphi', 'Bloc A'),
            ('Amphi B', 250, 'amphi', 'Bloc A'),
            ('Salle 101', 50, 'salle', 'Bloc B'),
            ('Salle 102', 50, 'salle', 'Bloc B'),
            ('Salle 201', 30, 'salle', 'Bloc C'),
            ('Salle 202', 30, 'salle', 'Bloc C'),
            ('Salle Info 1', 25, 'salle', 'Bloc D'),
            ('Salle Info 2', 25, 'salle', 'Bloc D'),
            ('Salle 301', 40, 'salle', 'Bloc E'),
            ('Salle 302', 40, 'salle', 'Bloc E'),
        ]
        
        for nom, capacite, type_salle, batiment in salles_data:
            cur.execute("""
                INSERT INTO salle (nom, capacite, type, batiment)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (nom, capacite, type_salle, batiment))
        
        print(f"   [OK] {len(salles_data)} salles created")
        print()
        
        # ======================
        # 3. ETUDIANTS (10 students)
        # ======================
        print("3. Creating Etudiants...")
        
        # Get formation IDs
        cur.execute("SELECT id, nom FROM formation ORDER BY id;")
        formations = cur.fetchall()
        formation_map = {f['nom']: f['id'] for f in formations}
        
        etudiants_data = [
            ('Kaci', 'Amine', 2023, 'Licence Informatique'),
            ('Benali', 'Sara', 2023, 'Licence Informatique'),
            ('Toumi', 'Yanis', 2023, 'Master Informatique'),
            ('Alaoui', 'Fatima', 2024, 'Master Informatique'),
            ('Idrissi', 'Mehdi', 2023, 'Licence Physique'),
            ('Bennani', 'Layla', 2023, 'Licence Physique'),
            ('Fassi', 'Omar', 2024, 'Master Physique'),
            ('Zahiri', 'Aicha', 2023, 'Licence Mathématiques'),
            ('Rachidi', 'Karim', 2023, 'Licence Mathématiques'),
            ('El Amrani', 'Nadia', 2024, 'Master Mathématiques'),
        ]
        
        for nom, prenom, promotion, formation_nom in etudiants_data:
            formation_id = formation_map.get(formation_nom)
            if formation_id:
                cur.execute("""
                    INSERT INTO etudiant (nom, prenom, promotion, formation_id)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (nom, prenom, promotion, formation_id))
        
        print(f"   [OK] {len(etudiants_data)} etudiants created")
        print()
        
        conn.commit()
        
        # ======================
        # VERIFICATION
        # ======================
        print("=" * 60)
        print("Verification:")
        print("=" * 60)
        
        cur.execute("SELECT COUNT(*) as count FROM professeur;")
        prof_count = cur.fetchone()['count']
        print(f"  Professeurs: {prof_count}")
        
        cur.execute("SELECT COUNT(*) as count FROM salle;")
        salle_count = cur.fetchone()['count']
        print(f"  Salles: {salle_count}")
        
        cur.execute("SELECT COUNT(*) as count FROM etudiant;")
        etud_count = cur.fetchone()['count']
        print(f"  Etudiants: {etud_count}")
        
        print()
        print("=" * 60)
        print("[SUCCESS] Database populated successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Create exam user accounts for etudiants")
        print("  2. Create exams as admin")
        print("  3. Login as etudiant to see their exams")
        
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
    populate_full_data()
