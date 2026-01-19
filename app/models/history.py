from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class TaskHistory(Base):
    __tablename__ = "task_history"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False) # e.g., "created", "status_change", "reassigned"
    
    field_changed = Column(String, nullable=True) # e.g., "status"
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.now)
    
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Who performed the action
    
    task = relationship("Task", back_populates="history")
    user = relationship("User") 
