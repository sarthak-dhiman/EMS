from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class SubTask(Base):
    __tablename__ = "subtasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", back_populates="subtasks")
