import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

env_path = Path(__file__).resolve().parent.parent.parent / ".env"

print(f"Loading .env from: {env_path}") 
load_dotenv(dotenv_path=env_path)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

print(f"DATABASE_URL found: {SQLALCHEMY_DATABASE_URL}")


if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(f"DATABASE_URL is not set. Please check your .env file at {env_path}")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()