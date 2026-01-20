from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.models.task import Task

router = APIRouter()


@router.get("/tasks-per-user")
def tasks_per_user(db: Session = Depends(get_db)):
    # Returns a simple list of user id, username, task_count
    results = db.query(User.id, User.username).all()
    data = []
    for u in results:
        count = db.query(Task).filter(Task.user_id == u.id).count()
        data.append({"user_id": u.id, "username": u.username, "task_count": count})
    return data


@router.get("/workload-distribution")
def workload_distribution(db: Session = Depends(get_db)):
    # Return tasks grouped by team and by user counts
    teams = db.execute("SELECT id, name FROM teams").fetchall()
    team_data = []
    for t in teams:
        task_count = db.query(Task).filter(Task.team_id == t.id).count()
        team_data.append({"team_id": t.id, "team_name": t.name, "task_count": task_count})

    # Top 10 busiest users
    users = db.query(User.id, User.username).all()
    user_load = []
    for u in users:
        c = db.query(Task).filter(Task.user_id == u.id).count()
        user_load.append({"user_id": u.id, "username": u.username, "task_count": c})
    user_load = sorted(user_load, key=lambda x: x["task_count"], reverse=True)[:10]

    return {"teams": team_data, "top_users": user_load}
