from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str
    username: str
    dob: Optional[str] = None
    mobile_number: Optional[str] = None
    team_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str = "employee"

class UserResponse(UserBase):
    id: int
    is_active: bool
    role: str

    model_config = {"from_attributes": True}