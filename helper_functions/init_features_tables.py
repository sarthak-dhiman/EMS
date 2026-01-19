import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import engine, Base
from app.models.comment import Comment
from app.models.history import TaskHistory
from app.models.task import Task
from app.models.user import User

def init_db():
    print("Creating tables for Comments and TaskHistory...")
    try:
        # This will create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    init_db()
