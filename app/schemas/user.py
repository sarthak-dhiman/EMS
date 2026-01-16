from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class UserBase(BaseModel):
    email: EmailStr
    username: str
    name: Optional[str] = None
    dob: Optional[date] = None
    mobile_number: Optional[str] = None
    team_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str = "employee"

class UserResponse(UserBase):
    id: int
    is_active: bool
    role: str
    dob: Optional[date] = None
    model_config = {"from_attributes": True}