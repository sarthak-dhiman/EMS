from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.notification import NotificationLog, Notification
from app.models.user import User
from app.models.team import Team
import httpx
from pydantic import EmailStr
from fastapi import BackgroundTasks
import os
from datetime import datetime, timezone
import json
import logging
import asyncio
from app.core.sse import manager
import threading

logger = logging.getLogger("app_logger")

# No top-level email client config: import and build ConnectionConfig inside send_email_notification

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

        # Log attempt
        try:
            log_notification(db, user_id=user.id, type="EMAIL", status="ATTEMPT", payload=body)
        except Exception:
            logger.debug("Failed to write initial email attempt log")

        # Try to import fastapi_mail locally; if unavailable, fallback to mock logging
        try:
            from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
        except Exception:
            logger.info(f"fastapi_mail not installed; mocking email to {user.email}")
            log_notification(db, user_id=user.id, type="EMAIL", status="MOCK_SENT", payload=body)
            return

        # Build connection config
        conf = ConnectionConfig(
            MAIL_USERNAME = os.getenv("MAIL_USERNAME", "user@example.com"),
            MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "password"),
            MAIL_FROM = os.getenv("MAIL_FROM", "admin@ems-pro.com"),
            MAIL_PORT = int(os.getenv("MAIL_PORT", 587)),
            MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
            MAIL_STARTTLS = True,
            MAIL_SSL_TLS = False,
            USE_CREDENTIALS = True,
            VALIDATE_CERTS = False
        )

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
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        
        # Retry logic
        max_retries = int(os.getenv("WEBHOOK_MAX_RETRIES", "3"))
        base_delay = float(os.getenv("WEBHOOK_BASE_DELAY", "1.0"))

        last_error = None
        async with httpx.AsyncClient() as client:
            for attempt in range(1, max_retries + 1):
                try:
                    # Log attempt
                    try:
                        log_notification(db, team_id=team.id, type="WEBHOOK", status=f"ATTEMPT_{attempt}", payload=json.dumps(payload))
                    except Exception:
                        logger.debug("Failed to write webhook attempt log")

                    resp = await client.post(team.webhook_url, json=payload, timeout=5.0)
                    if resp.status_code < 400:
                        status = "SENT"
                        log_notification(db, team_id=team.id, type="WEBHOOK", status=status, payload=json.dumps(payload))
                        logger.info(f"Webhook {event} sent to {team.name} with status {status}")
                        return
                    else:
                        last_error = f"HTTP_{resp.status_code}"
                        logger.warning(f"Webhook attempt {attempt} got status {resp.status_code} for team {team.name}")
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"Webhook attempt {attempt} failed for team {team.name}: {e}")

                # Backoff before next attempt
                if attempt < max_retries:
                    await asyncio.sleep(base_delay * (2 ** (attempt - 1)))

        # All attempts failed
        final_status = f"FAILED_{last_error}" if last_error else "FAILED"
        log_notification(db, team_id=team_id, type="WEBHOOK", status=final_status, payload=json.dumps(payload), error=str(last_error))
        logger.error(f"Webhook {event} ultimately failed for team {team.name}: {last_error}")
    except Exception as e:
        logger.error(f"Webhook failed for team {team_id}: {e}")
        log_notification(db, team_id=team_id, type="WEBHOOK", status="FAILED", error=str(e), payload=json.dumps(data))
    finally:
        db.close()

async def broadcast_notification(user_id: int, payload: dict):
    await manager.broadcast(user_id, payload)

def create_in_app_notification(db: Session, user_id: int, title: str, message: str, background_tasks: BackgroundTasks = None):
    try:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        # Broadcast via SSE
        # Convert created_at to server local timezone for client display convenience
        try:
            local_ts = notif.created_at.astimezone()
        except Exception:
            # fallback: use original timestamp
            local_ts = notif.created_at

        payload = {
            "id": notif.id,
            "title": notif.title,
            "message": notif.message,
            "created_at": local_ts.isoformat(),
            "is_read": False
        }

        if background_tasks:
            background_tasks.add_task(broadcast_notification, user_id, payload)
        else:
            # If there's a running loop, schedule a task; otherwise run broadcast in a short-lived thread
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(manager.broadcast(user_id, payload))
            except RuntimeError:
                # No running event loop in this thread — run broadcast in a separate thread
                def _runner(u_id, pl):
                    try:
                        asyncio.run(manager.broadcast(u_id, pl))
                    except Exception as e:
                        logger.debug(f"Background broadcast failed: {e}")

                t = threading.Thread(target=_runner, args=(user_id, payload), daemon=True)
                t.start()

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
