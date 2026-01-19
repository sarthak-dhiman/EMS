from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from fastapi import BackgroundTasks
from app.services.notification import send_email_notification, send_webhook_notification, create_in_app_notification
from app.models.team import Team 

def create_new_task(db: Session, task: TaskCreate, background_tasks: BackgroundTasks = None, user_id: int = None, team_id: int = None):
    # We map the Pydantic schema to the Database Model
    db_task = Task(
        title=task.title,
        description=task.description,
        user_id=user_id,
        team_id=team_id,
        priority=task.priority,
        deadline=task.deadline
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Trigger Notification
    # 1. Email to Assignee
    try:
        if db_task.user_id:
            user = db.query(User).filter(User.id == db_task.user_id).first()
            if user and background_tasks:
                 # Pass the async function to background tasks
                 background_tasks.add_task(
                     send_email_notification, 
                     None, # Dummy session, function creates its own
                     user.id, 
                     f"New Task Assigned: {db_task.title}", 
                     f"<p>You have been assigned a new task: <b>{db_task.title}</b></p><p>Description: {db_task.description}</p>"
                 )
            
            # 2. In-App Notification (Synchronous since we are already in service)
            create_in_app_notification(db, user.id, "New Task Assigned", f"You have been assigned: {db_task.title}")
    except Exception as e:
        print(f"Notification Error: {e}")

    return db_task

from app.models.user import User

def get_tasks_for_user(db: Session, user: User, status: str = None, priority: str = None, sort_by: str = None, order: str = "asc"):
    from sqlalchemy import desc, asc
    
    if user.role == 'admin':
        # Admin sees ALL tasks
        query = db.query(Task)
    elif user.role == 'manager':
        # Manager should see tasks assigned to themselves, tasks assigned to teams they manage,
        # and tasks assigned to members of teams they manage.
        from app.models.team import Team
        from sqlalchemy import or_

        # Query managed teams using current DB session (robust even if user object is detached)
        managed_team_ids = [t.id for t in db.query(Team).filter(Team.manager_id == user.id).all()]

        # Gather member user ids for those teams
        member_ids = []
        if managed_team_ids:
            members = db.query(User).filter(User.team_id.in_(managed_team_ids)).all()
            member_ids = [m.id for m in members]

        conditions = [Task.user_id == user.id]
        if managed_team_ids:
            conditions.append(Task.team_id.in_(managed_team_ids))
        if member_ids:
            conditions.append(Task.user_id.in_(member_ids))

        query = db.query(Task).filter(or_(*conditions))
    else:
        # Regular employee: only tasks assigned to them
        query = db.query(Task).filter(Task.user_id == user.id)
    
    if status:
        query = query.filter(Task.status.ilike(status))
    if priority:
        query = query.filter(Task.priority.ilike(priority))
        
    if sort_by:
        if sort_by == "deadline":
            col = Task.deadline
        elif sort_by == "priority":
            col = Task.priority
        elif sort_by == "created_at":
            col = Task.id
        else:
            col = Task.id
            
        if order == "desc":
             query = query.order_by(desc(col))
        else:
             query = query.order_by(asc(col))
    else:
        query = query.order_by(Task.id.desc())

    return query.all()


def update_task_status(db: Session, task_id: int, status: str, user_id: int):
    # This seems unused now or legacy?
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task: return None
    if task.user_id != user_id: return "Unauthorized"
    task.status = status
    db.commit()
    return task

from datetime import datetime
from app.models.history import TaskHistory

def update_task_with_history(db: Session, task: Task, updates: TaskUpdate, user: User, background_tasks: BackgroundTasks = None):
    # Track changes
    changes = []
    
    if updates.status and updates.status != task.status:
        changes.append(("status", task.status, updates.status))
        task.status = updates.status
        if updates.status == "completed":
            task.completed_at = datetime.now()
        else:
            task.completed_at = None
            
        # Trigger Webhook if Team has URL
        if task.team_id and background_tasks:
            team = db.query(Team).filter(Team.id == task.team_id).first()
            if team and team.webhook_url:
                payload = {
                    "task_id": task.id,
                    "title": task.title,
                    "old_status": changes[-1][1],
                    "new_status": updates.status,
                    "updated_by": user.username
                }
                background_tasks.add_task(send_webhook_notification, None, task.team_id, "task_status_updated", payload)
                
                # In-App Notification to Assignee
                if task.user_id:
                    create_in_app_notification(db, task.user_id, "Task Status Updated", f"Task '{task.title}' status changed to {updates.status}")

                # SPECIAL COMPLETION NOTIFICATIONS
                if updates.status == "completed":
                    # 1. Get all Admins
                    admins = db.query(User).filter(User.role == "admin").all()
                    
                    # 2. Get Team Manager
                    manager = None
                    if task.team_id:
                        team = db.query(Team).filter(Team.id == task.team_id).first()
                        if team and team.manager_id:
                            manager = db.query(User).filter(User.id == team.manager_id).first()

                    # Notification Targets
                    targets = set()
                    
                    if user.role == "employee":
                        # Send to Admins and Manager
                        for a in admins: targets.add(a.id)
                        if manager: targets.add(manager.id)
                    elif user.role == "manager":
                        # Send to Admins
                        for a in admins: targets.add(a.id)
                    
                    # Remove self from targets
                    if user.id in targets:
                        targets.remove(user.id)
                        
                    for target_id in targets:
                        create_in_app_notification(
                            db, 
                            target_id, 
                            "Task Completed", 
                            f"{user.username} has completed the task: {task.title}"
                        )

    if updates.priority and updates.priority != task.priority:
        # Employee Restriction: cannot change priority
        if user.role == "employee":
             pass # Ignore priority change
        else:
            changes.append(("priority", task.priority, updates.priority))
            task.priority = updates.priority

    if updates.title and updates.title != task.title:
        changes.append(("title", task.title, updates.title))
        task.title = updates.title
        
    if updates.description is not None and updates.description != task.description:
        changes.append(("description", "old_desc", "new_desc")) 
        task.description = updates.description
        
    if updates.deadline and updates.deadline != task.deadline:
         changes.append(("deadline", str(task.deadline), str(updates.deadline)))
         task.deadline = updates.deadline
         
    if updates.team_id and updates.team_id != task.team_id:
        changes.append(("team_id", str(task.team_id), str(updates.team_id)))
        task.team_id = updates.team_id
        
    if updates.user_id is not None and updates.user_id != task.user_id:
        # Restriction: Only Admin/Manager can reassign? 
        # For now, rely on route logic or basic role check. 
        # Employee shouldn't reassign usually.
        if user.role == "employee":
             pass
        else:
            changes.append(("user_id", str(task.user_id), str(updates.user_id)))
            task.user_id = updates.user_id

    # Commit changes and logs
    if changes:
        for field, old, new in changes:
            history = TaskHistory(
                task_id=task.id,
                user_id=user.id,
                action="update",
                field_changed=field,
                old_value=str(old) if old else None,
                new_value=str(new) if new else None,
                timestamp=datetime.now()
            )
            db.add(history)
            
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return None
        
    db.delete(task)
    db.commit()
    return True