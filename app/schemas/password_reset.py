from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserResponse

class PasswordResetBase(BaseModel):
    email: str
    status: str

class PasswordResetResponse(PasswordResetBase):
    id: int
    user_id: int
    created_at: datetime
    user: UserResponse
    
    model_config = {"from_attributes": True}
