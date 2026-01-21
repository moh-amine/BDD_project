"""Test the fixed etudiant query"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.queries import get_examens_by_etudiant_formation

def test_fixed_query():
    """Test the fixed query"""
    print("=" * 60)
    print("Testing Fixed Etudiant Query")
    print("=" * 60)
    print()
    
    # Test with etudiants that should have exams
    test_etudiants = [11, 13, 10]  # These should see exams based on formation_id
    
    for etudiant_id in test_etudiants:
        print(f"Testing Etudiant ID: {etudiant_id}")
        exams = get_examens_by_etudiant_formation(etudiant_id)
        print(f"  Exams found: {len(exams)}")
        
        if exams:
            for exam in exams:
                print(f"    - {exam['module']} on {exam['date']} at {exam['heure_debut']}")
        else:
            print("    (No exams found)")
        print()

if __name__ == "__main__":
    test_fixed_query()
