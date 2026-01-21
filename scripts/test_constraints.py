"""
Test database constraints for exam scheduling system.
This script executes the test cases SQL file.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import get_connection

def test_constraints():
    """Run all constraint test cases"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        print("=" * 60)
        print("Testing Database Constraints")
        print("=" * 60)
        print()
        
        # Read the SQL file
        sql_file = os.path.join(os.path.dirname(__file__), 'constraints_test_cases.sql')
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Execute the SQL (it will print NOTICE messages)
        cur.execute(sql_content)
        conn.commit()
        
        print()
        print("[OK] All test cases completed!")
        print("Review the output above to verify constraints are working.")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    test_constraints()
