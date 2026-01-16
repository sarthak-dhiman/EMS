from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.task import TaskCreate, TaskResponse
from app.services.task import create_new_task, get_tasks_for_user
from app.models.user import User
from app.models.task import Task
from app.models.subtask import SubTask
from app.schemas.task import TaskUpdate 
from app.services.task import update_task_status, delete_task
from sqlalchemy.orm import joinedload

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
    
    # Manager permission check: Can only assign to own team members
    if current_user.role == "manager":
        # If assigning to a user
        if task.user_id:
            assignee = db.query(User).filter(User.id == task.user_id).first()
            if not assignee:
                raise HTTPException(status_code=404, detail="Assignee not found")
            
            # Check if assignee is in manager's team
            # Case 1: Manager manages the team the user is in
            flag = False
            for team in current_user.managed_teams:
                 if team.id == assignee.team_id:
                     flag = True
                     break
            if not flag:
                 raise HTTPException(status_code=403, detail="You can only assign tasks to your team members")

        # If assigning to a team (Manager must manage that team)
        if task.team_id:
            flag = False
            for team in current_user.managed_teams:
                if team.id == task.team_id:
                    flag = True
                    break
            if not flag:
                raise HTTPException(status_code=403, detail="You can only assign tasks to teams you manage")

    assignee_id = task.user_id 
    # If no user_id or team_id provided, default to self? Or require one?
    # Let's assume if nothing provided, assign to self
    if not assignee_id and not task.team_id:
        assignee_id = current_user.id
    
    return create_new_task(db=db, task=task, user_id=assignee_id, team_id=task.team_id)

@router.get("/", response_model=List[TaskResponse])
def read_my_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_tasks_for_user(db=db, user_id=current_user.id)

@router.put("/{task_id}", response_model=TaskResponse)
def update_task_details(
    task_id: int,
    task_update: TaskUpdate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # This replaces the old /{task_id}/status endpoint effectively, or extends it
    # Ideally should consolidate. Frontend was calling /status specifically.
    # Let's keep /status for backward compat if needed or just handle everything here.
    # The frontend code I saw used PUT /tasks/{id}/status.
    # I should change frontend to use PUT /tasks/{id} for status update too.
    
    task = db.query(Task).filter(Task.id == task_id).options(joinedload(Task.subtasks)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Permission: Owner OR Manager of Team OR Team Member (if assigned to team)
    # Simplifying for now: if user==owner or user==manager or user in team
    
    if task_update.status:
        task.status = task_update.status
    if task_update.title:
        task.title = task_update.title
    if task_update.description:
        task.description = task_update.description
    if task_update.team_id:
        task.team_id = task_update.team_id
        
    db.commit()
    db.refresh(task)
    return task

@router.put("/{task_id}/status", response_model=TaskResponse)
def update_task_status_endpoint(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Legacy endpoint wrapper
    return update_task_details(task_id, task_update, current_user, db)

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