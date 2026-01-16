from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Manager of the team
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    manager = relationship("User", foreign_keys=[manager_id], back_populates="managed_teams")
    
    # Members of the team
    members = relationship("User", foreign_keys="User.team_id", back_populates="team")
    
    # Tasks assigned to this team
    tasks = relationship("Task", back_populates="team")
