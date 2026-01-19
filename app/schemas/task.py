from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None 


class TaskCreate(TaskBase):
    user_id: Optional[int] = None
    team_id: Optional[int] = None
    priority: Optional[str] = "medium"
    deadline: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None 
    priority: Optional[str] = None
    team_id: Optional[int] = None
    user_id: Optional[int] = None
    deadline: Optional[datetime] = None


class SubTaskBase(BaseModel):
    title: str = Field(..., min_length=1)
    is_completed: bool = False

class SubTaskCreate(SubTaskBase):
    pass

class SubTaskResponse(SubTaskBase):
    id: int
    task_id: int
    model_config = {"from_attributes": True}


class TaskResponse(TaskBase):
    id: int
    status: str
    priority: str
    user_id: Optional[int] = None
    team_id: Optional[int] = None
    deadline: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    subtasks: List[SubTaskResponse] = []
    
    model_config = {"from_attributes": True} #the purpose of this is “You can read data from ORM objects, not just dicts.” as pydantic needs dict , sqlachemy returns objects