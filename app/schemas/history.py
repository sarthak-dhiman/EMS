from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskHistoryResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    action: str
    field_changed: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    timestamp: datetime
    
    # Optional author info
    user_username: Optional[str] = None # Or Author object

    model_config = {"from_attributes": True}
