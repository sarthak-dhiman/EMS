from pydantic import BaseModel
from typing import Optional


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "Medium" 


class TaskCreate(TaskBase):
    user_id: Optional[int] = None


class TaskUpdate(BaseModel):
    status: Optional[str] = None 

class TaskResponse(TaskBase):
    id: int
    status: str
    user_id: int

    class Config:
        from_attributes = True