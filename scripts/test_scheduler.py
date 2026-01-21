"""Test the scheduler function to verify it works correctly"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.optimization.scheduler import generate_schedule
from datetime import date, time
import inspect

print("=" * 60)
print("Testing generate_schedule function")
print("=" * 60)
print()

# Check function signature
sig = inspect.signature(generate_schedule)
print("Function signature:", sig)
print("Parameters:", list(sig.parameters.keys()))
print()

# Test with all parameters
print("Testing function call with all parameters...")
try:
    result = generate_schedule(
        start_date=date.today(),
        start_time=time(9, 0),
        duration_minutes=120,
        time_slots_per_day=4
    )
    print("[OK] Function call successful!")
    print(f"Result type: {type(result)}")
    print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
    print(f"Success: {result.get('success', 'N/A')}")
    print(f"Failed: {result.get('failed', 'N/A')}")
    print(f"Total: {result.get('total', 'N/A')}")
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("Test completed")
print("=" * 60)
