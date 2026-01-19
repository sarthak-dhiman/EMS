from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

def create_new_task(db: Session, task: TaskCreate, user_id: int = None, team_id: int = None):
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
    return db_task

from app.models.user import User

def get_tasks_for_user(db: Session, user: User, status: str = None, priority: str = None, sort_by: str = None, order: str = "asc"):
    from sqlalchemy import desc, asc
    
    if user.role == 'admin':
        # Admin sees ALL tasks
        query = db.query(Task)
    else:
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

def update_task_with_history(db: Session, task: Task, updates: TaskUpdate, user: User):
    # Track changes
    changes = []
    
    if updates.status and updates.status != task.status:
        changes.append(("status", task.status, updates.status))
        task.status = updates.status
        if updates.status == "completed":
            task.completed_at = datetime.now()
        else:
            task.completed_at = None

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
                timestamp=datetime.utcnow()
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