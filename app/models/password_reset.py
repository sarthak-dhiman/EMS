from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    email = Column(String, index=True)
    status = Column(String, default="pending") # pending, processed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
