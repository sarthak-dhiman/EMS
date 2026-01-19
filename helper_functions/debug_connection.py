import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import engine
from sqlalchemy import text
import traceback

def test():
    print(f"URL: {engine.url}")
    try:
        with engine.connect() as conn:
            print("Connection OK")
            
            # Try read
            res = conn.execute(text("SELECT 1"))
            print(f"Read OK: {res.fetchone()}")
            
            # Try Write (Create Temp Table)
            # Use separate transaction
            trans = conn.begin()
            try:
                conn.execute(text("CREATE TABLE IF NOT EXISTS temp_test (id serial primary key)"))
                print("Create Table OK")
                trans.commit()
            except Exception as e:
                trans.rollback()
                print("Create Table FAILED")
                traceback.print_exc()
                
    except Exception as e:
        print("Connection FAILED")
        traceback.print_exc()

if __name__ == "__main__":
    test()
