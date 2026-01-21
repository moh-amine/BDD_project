"""
Apply database constraints for exam scheduling system.
This script executes the SQL constraints file.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import get_connection

def apply_constraints():
    """Apply all constraint fixes to the database"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        print("=" * 60)
        print("Applying Database Constraints")
        print("=" * 60)
        print()
        
        # Read the SQL file
        sql_file = os.path.join(os.path.dirname(__file__), 'constraints_analysis_and_fix.sql')
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Execute the SQL
        cur.execute(sql_content)
        conn.commit()
        
        print("[OK] All constraints applied successfully!")
        print()
        print("Constraints now active:")
        print("  1. One exam per module (UNIQUE)")
        print("  2. Valid room type (CHECK)")
        print("  3. Student no overlapping exams (TRIGGER)")
        print("  4. Professor no simultaneous exams (TRIGGER)")
        print("  5. Room capacity sufficient (TRIGGER)")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Failed to apply constraints: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    apply_constraints()
