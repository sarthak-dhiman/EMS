import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import engine, Base
from app.models.password_reset import PasswordReset
from app.models.user import User
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    try:
        logger.info("Creating password_resets table...")
        Base.metadata.create_all(bind=engine)
        logger.info("Table created successfully.")
    except Exception as e:
        logger.error("Error creating table:")
        traceback.print_exc()

if __name__ == "__main__":
    init_db()
