"""Test if frontend/app.py can be imported correctly"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("Testing frontend/app.py imports...")

try:
    # This simulates what Streamlit does
    import importlib.util
    spec = importlib.util.spec_from_file_location("app", "frontend/app.py")
    app_module = importlib.util.module_from_spec(spec)
    
    # This will execute the imports
    print("Loading frontend/app.py...")
    spec.loader.exec_module(app_module)
    
    print("[OK] frontend/app.py imported successfully!")
    print("[OK] All backend modules are accessible")
    
except Exception as e:
    print(f"[ERROR] Failed to import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[SUCCESS] Frontend app is ready to run with Streamlit!")
