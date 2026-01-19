from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserResponse
from app.schemas.task import TaskResponse

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(TeamBase):
    name: Optional[str] = None

class TeamResponse(TeamBase):
    id: int
    manager_id: Optional[int] = None
    created_at: datetime
    
    # We might want to return manager details or member counts in listings
    manager: Optional[UserResponse] = None
    members: List[UserResponse] = []
    tasks: List[TaskResponse] = []

    model_config = {"from_attributes": True}
