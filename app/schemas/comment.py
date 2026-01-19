from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class UserSummary(BaseModel):
    id: int
    username: str

class CommentResponse(CommentBase):
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    author: Optional[UserSummary] = None
    
    model_config = {"from_attributes": True}
