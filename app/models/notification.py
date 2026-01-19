from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from datetime import datetime
from app.core.database import Base

class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Optional if team notification
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True) # Optional if user notification
    
    type = Column(String, nullable=False) # EMAIL, WEBHOOK
    status = Column(String, nullable=False) # SENT, FAILED
    payload = Column(Text, nullable=True) # JSON payload or message body
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
