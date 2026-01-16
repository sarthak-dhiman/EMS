from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserCreate
from app.dependencies import get_current_user

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
    
    users = db.query(User).filter(User.is_active == False).all()
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
