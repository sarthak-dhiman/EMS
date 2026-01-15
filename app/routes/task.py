from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.task import TaskCreate, TaskResponse
from app.services.task import create_new_task, get_tasks_for_user
from app.models.user import User
from app.schemas.task import TaskUpdate 
from app.services.task import update_task_status, delete_task

router = APIRouter() 


from app.dependencies import get_current_user

# --- ROUTES ---

@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403, 
            detail="Only admins and managers can create tasks"
        )
    
    # If assignee is provided, use it. Otherwise, assign to self (or could error).
    # Assuming if not provided, it assigns to the creator (manager).
    assignee_id = task.user_id if task.user_id else current_user.id
    
    return create_new_task(db=db, task=task, user_id=assignee_id)

@router.get("/", response_model=List[TaskResponse])
def read_my_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_tasks_for_user(db=db, user_id=current_user.id)

@router.put("/{task_id}/status", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,  # We expect { "status": "done" }
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = update_task_status(db, task_id, task_update.status, current_user.id)

    if result == "Unauthorized":
        raise HTTPException(status_code=403, detail="You cannot edit another user's task")
    
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return result

@router.delete("/{task_id}")
def delete_my_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = delete_task(db, task_id, current_user.id)

    if result == "Unauthorized":
        raise HTTPException(status_code=403, detail="You cannot delete another user's task")
    
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task deleted successfully"}