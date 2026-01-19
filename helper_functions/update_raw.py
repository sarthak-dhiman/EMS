import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(url)
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN deadline TIMESTAMP WITH TIME ZONE")
        print("Added deadline")
    except Exception as e:
        print(f"Deadline error: {e}")

    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN completed_at TIMESTAMP WITH TIME ZONE")
        print("Added completed_at")
    except Exception as e:
        print(f"Completed_at error: {e}")
        
    conn.close()
    print("Done")
except Exception as e:
    print(f"Connection failed: {e}")
