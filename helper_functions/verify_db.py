import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import inspect
from app.core.database import engine

def check_structure():
    print(f"Connecting with: {engine.url}")
    try:
        with engine.connect() as conn:
            print("Connection successful")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns('tasks')]
    print(f"Columns in tasks: {columns}")
    
    if "deadline" in columns and "completed_at" in columns:
        print("SUCCESS: Columns present")
    else:
        print("FAILURE: Columns missing")

if __name__ == "__main__":
    check_structure()
