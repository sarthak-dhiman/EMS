from sqlalchemy import Column, Integer, String , Boolean, ForeignKey, Date
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
    email_notifications = Column(Boolean, default=True, nullable=False)
    dob = Column(Date, nullable=True) 
    mobile_number = Column(String, nullable=True)
    team_name = Column(String, nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    
    # Relationships
    team = relationship("Team", foreign_keys=[team_id], back_populates="members")
    managed_teams = relationship("Team", foreign_keys="Team.manager_id", back_populates="manager")

    tasks = relationship("Task", back_populates="owner")

    @property
    def display_team_name(self):
        return self.team.name if self.team else self.team_name