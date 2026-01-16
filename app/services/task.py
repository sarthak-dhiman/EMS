from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

def create_new_task(db: Session, task: TaskCreate, user_id: int = None, team_id: int = None):
    # We map the Pydantic schema to the Database Model
    db_task = Task(
        title=task.title,
        description=task.description,
        user_id=user_id,
        team_id=team_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks_for_user(db: Session, user_id: int):
    # Only return tasks that belong to this specific user
    return db.query(Task).filter(Task.user_id == user_id).all()


def update_task_status(db: Session, task_id: int, status: str, user_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return None
        

    if task.user_id != user_id:
        return "Unauthorized"

    
    task.status = status
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task_id: int, user_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return None
        
    
    if task.user_id != user_id:
        return "Unauthorized"

   
    db.delete(task)
    db.commit()
    return True