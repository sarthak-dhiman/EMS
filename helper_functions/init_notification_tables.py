from app.core.database import engine, Base
# Import all models so Base.metadata is populated
from app.models.user import User
from app.models.team import Team
from app.models.task import Task
from app.models.subtask import SubTask
from app.models.comment import Comment
from app.models.history import TaskHistory
from app.models.notification import NotificationLog
from app.models.password_reset import PasswordReset
from sqlalchemy import text
import traceback

def migrate_notifications():
    print("--- Migrating Notifications Schema ---")
    try:
        with engine.begin() as conn:
            # Check and add columns
            print("Checking User/Team columns...")
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS email_notifications BOOLEAN DEFAULT TRUE"))
                conn.execute(text("ALTER TABLE teams ADD COLUMN IF NOT EXISTS webhook_url VARCHAR"))
            except Exception as e:
                print(f"Column add warning: {e}")

            # Create NotificationLog table
            print("Creating notification_logs table...")
            NotificationLog.__table__.create(conn, checkfirst=True)
            
            print("Migration success.")
    except Exception as e:
        print(f"Migration failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    migrate_notifications()
