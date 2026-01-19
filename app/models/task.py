from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, default="Open")
    priority = Column(String, default="Medium")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable if assigned to team but not specific user yet
    owner = relationship("User", back_populates="tasks")
    
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    team = relationship("Team", back_populates="tasks")
    
    subtasks = relationship("SubTask", back_populates="task", cascade="all, delete-orphan")
    
    deadline = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    history = relationship("TaskHistory", back_populates="task", cascade="all, delete-orphan")