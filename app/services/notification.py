from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.notification import NotificationLog, Notification
from app.models.user import User
from app.models.team import Team
import httpx
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
import os
from datetime import datetime
import json
import logging

logger = logging.getLogger("app_logger")

# --- Config ---
# Ensure these are in .env or defaulting here
conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "user@example.com"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "password"),
    MAIL_FROM = os.getenv("MAIL_FROM", "admin@ems-pro.com"),
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = False # For dev
)

async def send_email_notification(db_session: Session, user_id: int, subject: str, body: str):
    # We use a new session if possible or the provided one
    # For background tasks, it's safer to use user_id and fetch fresh
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found for email notification")
            return

        if not user.email_notifications:
            logger.info(f"Email notifications disabled for user {user.username}")
            return

        # Check if we have real credentials
        if not os.getenv("MAIL_USERNAME"):
            logger.info(f"[MOC EMAIL] To: {user.email} | Subject: {subject}")
            log_notification(db, user_id=user.id, type="EMAIL", status="MOCK_SENT", payload=body)
            return

        message = MessageSchema(
            subject=subject,
            recipients=[user.email],
            body=body,
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        log_notification(db, user_id=user.id, type="EMAIL", status="SENT", payload=body)
        logger.info(f"Email sent successfully to {user.email}")
    except Exception as e:
        logger.error(f"Email failed to {user_id}: {e}")
        log_notification(db, user_id=user_id, type="EMAIL", status="FAILED", error=str(e), payload=body)
    finally:
        db.close()

async def send_webhook_notification(db_session: Session, team_id: int, event: str, data: dict):
    db = SessionLocal()
    try:
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team or not team.webhook_url:
            return

        payload = {
            "event": event,
            "team": team.name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(team.webhook_url, json=payload, timeout=5.0)
            status = "SENT" if resp.status_code < 400 else f"FAILED_{resp.status_code}"
            
        log_notification(db, team_id=team.id, type="WEBHOOK", status=status, payload=json.dumps(payload))
        logger.info(f"Webhook {event} sent to {team.name} with status {status}")
    except Exception as e:
        logger.error(f"Webhook failed for team {team_id}: {e}")
        log_notification(db, team_id=team_id, type="WEBHOOK", status="FAILED", error=str(e), payload=json.dumps(data))
    finally:
        db.close()

def create_in_app_notification(db: Session, user_id: int, title: str, message: str):
    try:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message
        )
        db.add(notif)
        db.commit()
        return notif
    except Exception as e:
        logger.error(f"Failed to create in-app notification: {e}")
        db.rollback()
        return None

def log_notification(db: Session, user_id: int = None, team_id: int = None, type: str = "", status: str = "", payload: str = "", error: str = None):
    # Ensure we use the provided session correctly
    try:
        log = NotificationLog(
            user_id=user_id,
            team_id=team_id,
            type=type,
            status=status,
            payload=payload[:5000] if payload else None,
            error_message=error
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log notification: {e}")
        if db: db.rollback()
