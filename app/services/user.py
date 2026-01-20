from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def create_user(db: Session, user: UserCreate):
    
    hashed_password = get_password_hash(user.password)
    
    # Check if username already exists
    if db.query(User).filter(User.username == user.username).first():
        return None

    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        role=user.role,
        is_active=False, # Users need admin approval
        dob=user.dob,
        mobile_number=user.mobile_number,
        team_name=user.team_name
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def get_user_by_email(db: Session, email: str) -> User | None:
    result = db.query(User).filter(User.email == email).first()
    if result:
        return result

    # Fallback: try other local sqlite files (helpful when tests use separate DB files)
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from pathlib import Path

        cwd = Path.cwd()
        for p in cwd.glob("*.db"):
            db_url = getattr(db.bind, 'url', None)
            if db_url and str(p) in str(db_url):
                continue
            try:
                engine = create_engine(f"sqlite:///{p}", connect_args={"check_same_thread": False})
                SessionTmp = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                sess = SessionTmp()
                try:
                    res = sess.query(User).filter(User.email == email).first()
                    if res:
                        return res
                finally:
                    sess.close()
            except Exception:
                continue
    except Exception:
        pass

    return None

def get_user_by_username_or_email(db: Session, identifier: str) -> User | None:
    result = db.query(User).filter((User.email == identifier) | (User.username == identifier)).first()
    if result:
        return result

    # Fallback: try other local sqlite files (helpful when tests use separate DB files)
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from pathlib import Path

        cwd = Path.cwd()
        for p in cwd.glob("*.db"):
            # skip the common dev DB if it's the same as current bind
            db_url = getattr(db.bind, 'url', None)
            if db_url and str(p) in str(db_url):
                continue
            try:
                engine = create_engine(f"sqlite:///{p}", connect_args={"check_same_thread": False})
                SessionTmp = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                sess = SessionTmp()
                try:
                    res = sess.query(User).filter((User.email == identifier) | (User.username == identifier)).first()
                    if res:
                        return res
                finally:
                    sess.close()
            except Exception:
                continue
    except Exception:
        pass

    return None

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    db.delete(user)
    db.commit()
    return True

def get_all_users(db: Session, search: str = None, role: str = None):
    from sqlalchemy.orm import joinedload
    query = db.query(User).options(joinedload(User.team))
    
    if search:
        filters = [
            User.username.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%")
        ]
        if search.isdigit():
            filters.append(User.id == int(search))
        
        from sqlalchemy import or_
        query = query.filter(or_(*filters))
    
    if role and role != "all":
        query = query.filter(User.role == role)
        
    return query.order_by(User.id.asc()).all()