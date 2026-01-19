from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserCreate
from app.dependencies import get_current_user
from app.models.password_reset import PasswordReset
from app.schemas.password_reset import PasswordResetResponse
from app.core.security import get_password_hash
import secrets
import string

router = APIRouter()

@router.get("/pending-users", response_model=List[UserResponse])
def get_pending_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = db.query(User).filter(User.is_active == False).order_by(User.id.asc()).all()
    return users

@router.get("/users", response_model=List[UserResponse])
def get_users_list(
    search: str = None,
    role: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    from app.services.user import get_all_users
    return get_all_users(db, search, role)

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_admin(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    from app.services.user import create_user
    new_user = create_user(db, user_create)
    if not new_user:
         raise HTTPException(status_code=400, detail="Username already exists")
    
    # Auto-activate since admin created it
    new_user.is_active = True
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.put("/approve-user/{user_id}", response_model=UserResponse)
def approve_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user

@router.get("/password-resets", response_model=List[PasswordResetResponse])
def get_password_resets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(PasswordReset).filter(PasswordReset.status == "pending").all()

@router.post("/password-resets/{id}/reset")
def reset_user_password(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    reset_req = db.query(PasswordReset).filter(PasswordReset.id == id).first()
    if not reset_req or reset_req.status != "pending":
         raise HTTPException(status_code=404, detail="Request not found or already processed")
         
    # Generate random password
    chars = string.ascii_letters + string.digits + "!@#$%"
    temp_password = "".join(secrets.choice(chars) for _ in range(12))
    
    user = db.query(User).filter(User.id == reset_req.user_id).first()
    if user:
        user.hashed_password = get_password_hash(temp_password)
        
    reset_req.status = "processed"
    db.commit()
    
    return {"message": "Password reset successful", "temp_password": temp_password}
