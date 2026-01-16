from sqlalchemy import Column, Integer, String , Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="employee")
    is_active = Column(Boolean, default=False)
    dob = Column(String, nullable=True) # Storing as string for simplicity, or Date
    mobile_number = Column(String, nullable=True)
    team_name = Column(String, nullable=True) # Legacy field, maybe deprecate in favor of team_id relationship
    
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    
    # Relationships
    team = relationship("Team", foreign_keys=[team_id], back_populates="members")
    managed_teams = relationship("Team", foreign_keys="Team.manager_id", back_populates="manager")

    tasks = relationship("Task", back_populates="owner")