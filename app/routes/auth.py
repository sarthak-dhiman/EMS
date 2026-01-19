from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user import create_user, get_user_by_email, delete_user, get_user_by_username_or_email
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import verify_password, create_access_token
from app.dependencies import get_current_user
from app.models.user import User
from datetime import timedelta
from pydantic import BaseModel, EmailStr
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.password_reset import PasswordReset

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_create: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    # Check username
    existing_user_username = get_user_by_username_or_email(db, user_create.username)
    if existing_user_username and existing_user_username.username == user_create.username:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    new_user = create_user(db, user_create)
    return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username_or_email(db, form_data.username) # OAuth2 form uses 'username', not 'email'
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    
    return {"access_token": access_token, "token_type": "Bearer"}

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, request.email)
    if not user:
        # Return success to avoid enumeration
        return {"message": "If this email is registered, a password reset request has been submitted."}
    
    # Check for existing pending request
    existing = db.query(PasswordReset).filter(PasswordReset.user_id == user.id, PasswordReset.status == "pending").first()
    if existing:
         return {"message": "Request already pending."}

    new_request = PasswordReset(user_id=user.id, email=user.email)
    db.add(new_request)
    db.commit()
    return {"message": "Password reset request submitted."}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.delete("/{user_id}")
def delete_user_account(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not enough permissions. Only admins can delete users."
        )

    result = delete_user(db, user_id)
    
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted successfully"}