from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash
import sys

# Ensure tables exist
Base.metadata.create_all(bind=engine)

def seed_db():
    db: Session = SessionLocal()
    try:
        users = [
            {"username": "admin", "email": "admin@example.com", "password": "adminpassword", "role": "admin"},
            {"username": "manager", "email": "manager@example.com", "password": "managerpassword", "role": "manager"},
            {"username": "user1", "email": "user1@example.com", "password": "password123", "role": "employee"},
            {"username": "user2", "email": "user2@example.com", "password": "password123", "role": "employee"},
            {"username": "emp3", "email": "emp3@example.com", "password": "password123", "role": "employee"},
        ]

        created_users = []
        for u_data in users:
            existing = db.query(User).filter(User.email == u_data["email"]).first()
            if not existing:
                user = User(
                    username=u_data["username"],
                    email=u_data["email"],
                    hashed_password=get_password_hash(u_data["password"]),
                    role=u_data["role"],
                    is_active=True
                )
                db.add(user)
                created_users.append(u_data)
                print(f"Created {u_data['role']}: {u_data['email']}")
            else:
                print(f"Skipped existing: {u_data['email']}")
        
        db.commit()
        return created_users
        
    except Exception as e:
        print(f"Error seeding DB: {e}")
        db.rollback()
        return []
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
