from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.notification import NotificationResponse
from app.models.notification import Notification
from app.models.user import User
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from app.core.security import SECRET_KEY, ALGORITHM
from app.services.user import get_user_by_email

from app.core.sse import manager
from fastapi.responses import StreamingResponse
import asyncio
import json
from pydantic import BaseModel
from app.dependencies import get_current_user


class NotificationPreferences(BaseModel):
    email_notifications: bool

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
def get_my_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rows = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()

    # Convert created_at to server local timezone before returning so clients see local times
    results = []
    for n in rows:
        try:
            local_ts = n.created_at.astimezone()
        except Exception:
            local_ts = n.created_at

        results.append({
            "id": n.id,
            "user_id": n.user_id,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": local_ts
        })

    return results

@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notif = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notif.is_read = True
    db.commit()
    return {"status": "success"}

@router.put("/read-all")
def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read == False).update({Notification.is_read: True})
    db.commit()
    return {"status": "success"}


@router.get("/preferences")
def get_preferences(current_user: User = Depends(get_current_user)):
    return {"email_notifications": current_user.email_notifications}


@router.put("/preferences")
def update_preferences(prefs: NotificationPreferences, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.email_notifications = bool(prefs.email_notifications)
    db.commit()
    return {"status": "success", "email_notifications": user.email_notifications}

@router.get("/stream")
async def stream_notifications(request: Request, db: Session = Depends(get_db)):
    """
    SSE Endpoint for real-time notifications.
    Supports `Authorization: Bearer <token>` header and legacy `?token=` query param for compatibility.
    """

    # Prefer Authorization header
    auth = request.headers.get("authorization")
    token = None
    if auth and auth.lower().startswith("bearer "):
        token = auth.split(None, 1)[1].strip()
    # Fallback to legacy ?token= param
    if not token:
        token = request.query_params.get("token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token error: {str(e)}")

    user = get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    user_id = user.id
        
    async def event_generator():
        queue = await manager.connect(int(user_id))
        try:
            while True:
                # Wait for message or client disconnect
                if await request.is_disconnected():
                    break
                    
                try:
                    # Wait for 1 second for a message, then yield a keep-alive comment
                    # This allows us to check for disconnection
                    message = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield {
                        "event": "message",
                        "data": json.dumps(message)
                    }
                except asyncio.TimeoutError:
                    # Keep-alive
                    yield {"event": "ping", "data": "pong"}
                    
        finally:
            await manager.disconnect(int(user_id), queue)

    # Attempt to use EventSourceResponse if available, otherwise fall back to StreamingResponse
    try:
        from sse_starlette.sse import EventSourceResponse
        return EventSourceResponse(event_generator())
    except Exception:
        try:
            from starlette.responses import EventSourceResponse
            return EventSourceResponse(event_generator())
        except Exception:
            async def sse_wrapper():
                async for item in event_generator():
                    if isinstance(item, dict):
                        ev = item.get("event")
                        data = item.get("data")
                        if ev == "ping":
                            yield f": {data}\n\n"
                        else:
                            yield f"event: {ev}\n"
                            for line in str(data).splitlines():
                                yield f"data: {line}\n"
                            yield "\n"

            return StreamingResponse(sse_wrapper(), media_type="text/event-stream")
