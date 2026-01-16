from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.subtask import SubTask
from app.models.task import Task
from app.schemas.task import SubTaskCreate, SubTaskResponse
from app.models.user import User
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/{task_id}/subtasks", response_model=SubTaskResponse)
def create_subtask(
    task_id: int,
    subtask: SubTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Permission check...
    
    new_subtask = SubTask(
        title=subtask.title,
        is_completed=subtask.is_completed,
        task_id=task_id
    )
    db.add(new_subtask)
    db.commit()
    db.refresh(new_subtask)
    return new_subtask

@router.put("/subtasks/{subtask_id}", response_model=SubTaskResponse)
def update_subtask(
    subtask_id: int,
    subtask_update: SubTaskCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subtask = db.query(SubTask).filter(SubTask.id == subtask_id).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")
        
    subtask.is_completed = subtask_update.is_completed
    subtask.title = subtask_update.title
    db.commit()
    db.refresh(subtask)
    return subtask

@router.delete("/subtasks/{subtask_id}")
def delete_subtask(
    subtask_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subtask = db.query(SubTask).filter(SubTask.id == subtask_id).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")
        
    db.delete(subtask)
    db.commit()
    return {"message": "Subtask deleted"}
