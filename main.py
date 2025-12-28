import streamlit.web.bootstrap as bootstrap
import os
import sys

# Ensure project root is visible
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    bootstrap.run(
        "frontend/app.py",
        "",
        [],
        {}
    )
