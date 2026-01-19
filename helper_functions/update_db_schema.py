import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal, engine
from sqlalchemy import text
import traceback

def add_columns():
    # Use engine.begin() for auto-commit transaction
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN deadline DATETIME"))
            print("Added deadline column")
        except Exception as e:
            print(f"Error adding deadline (might exist): {e}")
            
        try:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN completed_at TIMESTAMP"))
            print("Added completed_at column")
        except Exception as e:
            print(f"Error adding completed_at (might exist): {e}")

if __name__ == "__main__":
    add_columns()
