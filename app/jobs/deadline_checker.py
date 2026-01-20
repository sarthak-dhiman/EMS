import threading
import time
from datetime import datetime, timezone
from typing import Optional
from app.core.database import SessionLocal
from app.models.task import Task
from app.models.notification import Notification
from app.services.notification import create_in_app_notification
import logging
import os
from datetime import timedelta

logger = logging.getLogger(__name__)


def _check_deadlines_once(db):
    now = datetime.now(timezone.utc)
    # Overdue tasks
    overdue = db.query(Task).filter(Task.deadline != None).filter(Task.deadline < now).all()
    for task in overdue:
        # skip completed
        if getattr(task, "completed_at", None) or str(getattr(task, "status", "")).lower() == "completed":
            continue

        # Avoid duplicate notification: check existing notifications mentioning the task id
        exists = db.query(Notification).filter(Notification.user_id == task.user_id, Notification.message.like(f"%{task.title}%"), Notification.title.ilike("%overdue%") ).first()
        msg = f"Task overdue: {task.title}. Deadline was {task.deadline}"
        try:
            # notify assignee
            if task.user_id:
                if not exists:
                    create_in_app_notification(db, task.user_id, "Task Overdue", msg)

            # notify manager(s) and admins
            # Managers and admins are handled by task service's existing helpers; fallback: notify all admins
            from app.models.user import User
            admins = db.query(User).filter(User.role == "admin").all()
            for a in admins:
                create_in_app_notification(db, a.id, "Member Task Overdue", f"{task.title} overdue for user {task.user_id}")

            logger.info("Created overdue notification for task %s", task.id)
        except Exception as e:
            logger.exception("Failed to create overdue notifications: %s", e)

    # Approaching deadlines: within threshold hours but not yet overdue
    try:
        threshold_hours = int(os.getenv("DEADLINE_APPROACH_HOURS", "24"))
    except Exception:
        threshold_hours = 24

    window_end = now + timedelta(hours=threshold_hours)
    approaching = db.query(Task).filter(Task.deadline != None).filter(Task.deadline >= now).filter(Task.deadline <= window_end).all()
    for task in approaching:
        # skip completed
        if getattr(task, "completed_at", None) or str(getattr(task, "status", "")).lower() == "completed":
            continue

        # Skip if we've already created an approaching notification for this task recently
        exists_app = db.query(Notification).filter(Notification.user_id == task.user_id, Notification.title.ilike("%nearing%"), Notification.message.like(f"%{task.title}%")).first()
        try:
            msg = f"Task nearing deadline: {task.title}. Deadline at {task.deadline}"
            if task.user_id and not exists_app:
                create_in_app_notification(db, task.user_id, "Task Nearing Deadline", msg)

            # notify manager and admins as well
            from app.models.user import User
            if task.team_id:
                team = db.query(__import__("app.models.team", fromlist=["Team"]).Team).filter(__import__("app.models.team", fromlist=["Team"]).Team.id == task.team_id).first()
                if team and team.manager_id:
                    create_in_app_notification(db, team.manager_id, "Team Member Nearing Deadline", f"{task.title} is nearing deadline for member {task.user_id}")

            admins = db.query(User).filter(User.role == "admin").all()
            for a in admins:
                create_in_app_notification(db, a.id, "Member Nearing Deadline", f"{task.title} is nearing its deadline")
        except Exception as e:
            logger.exception("Failed to create approaching deadline notifications: %s", e)


def run_deadline_checker(interval_seconds: int = 300, stop_event: Optional[threading.Event] = None):
    """Run periodic deadline checks. Call from a background thread or startup event."""
    if stop_event is None:
        stop_event = threading.Event()

    db = SessionLocal()
    try:
        while not stop_event.is_set():
            _check_deadlines_once(db)
            stop_event.wait(interval_seconds)
    finally:
        db.close()


def start_in_thread(interval_seconds: int = 300):
    stop_event = threading.Event()
    t = threading.Thread(target=run_deadline_checker, args=(interval_seconds, stop_event), daemon=True)
    t.start()
    return stop_event
