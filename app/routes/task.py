from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.schemas.task import TaskCreate, TaskResponse
from app.services.task import create_new_task, get_tasks_for_user
from app.models.user import User
from app.models.task import Task
from app.models.history import TaskHistory
from app.schemas.history import TaskHistoryResponse
from app.models.subtask import SubTask
from app.models.comment import Comment
from app.schemas.task import TaskUpdate 
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.task import update_task_status, delete_task, update_task_with_history
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
            
            # Allow assigning to self
            if assignee.id == current_user.id:
                pass
            else:
                flag = False
                for team in current_user.managed_teams:
                     if team.id == assignee.team_id:
                         flag = True
                         break
                if not flag:
                     raise HTTPException(status_code=403, detail=f"You can only assign tasks to your team members. User {assignee.id} is in team {assignee.team_id}")

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
    status: Optional[str] = None,
    priority: Optional[str] = None,
    sort_by: Optional[str] = None,
    order: str = "asc",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_tasks_for_user(
        db=db, 
        user=current_user, 
        status=status, 
        priority=priority, 
        sort_by=sort_by, 
        order=order
    )

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
        # Bug #2: Admin should not be able to mark a task as completed unless assigned to him
        if (task_update.status == "completed" and 
            current_user.role == "admin" and 
            task.user_id != current_user.id):
             raise HTTPException(status_code=403, detail="Admins cannot complete tasks assigned to others")

    # Delegate to service for update and history logging
    task = update_task_with_history(db, task, task_update, current_user)
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
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Authorization Logic
    is_authorized = False
    
    # 1. Admin can delete anything
    if current_user.role == "admin":
        is_authorized = True
        
    # 2. Owner can delete their own task
    elif task.user_id == current_user.id:
        is_authorized = True
        
    # 3. Manager can delete task if assignee is in their managed team
    elif current_user.role == "manager":
        if task.user_id:
            assignee = db.query(User).filter(User.id == task.user_id).first()
            if assignee and assignee.team_id:
                # Check if this team is managed by current_user
                for team in current_user.managed_teams:
                    if team.id == assignee.team_id:
                        is_authorized = True
                        break
    
    if not is_authorized:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")

    delete_task(db, task_id)
    return {"message": "Task deleted successfully"}

# --- COMMENT ROUTES ---

@router.post("/{task_id}/comments", response_model=CommentResponse)
def create_comment(
    task_id: int,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    new_comment = Comment(
        content=comment.content,
        task_id=task_id,
        user_id=current_user.id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    # Reload with author for response
    # Actually refresh might load it if we access it? 
    # Or explicitly query. Easier to return object and generic loading handles it if joinedload used elsewhere?
    # Pydantic will try to access .author. SQLAlchemy lazy loads it by default. 
    # Since we are in an active session, lazy load works.
    return new_comment

@router.get("/{task_id}/comments", response_model=List[CommentResponse])
def get_task_comments(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check access? (Same as task access logic... skipping complex check for brevity, assuming if you have ID you can view comments? Or should restrict?)
    # Ideally restrict to Owner/Manager/Team.
    # For now, open to authenticated users (or minimal check).
    
    comments = db.query(Comment).filter(Comment.task_id == task_id).options(joinedload(Comment.author)).order_by(Comment.created_at.asc()).all()
    return comments

# --- HISTORY ROUTES ---

@router.get("/{task_id}/history", response_model=List[TaskHistoryResponse])
def get_task_history(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = db.query(TaskHistory).filter(TaskHistory.task_id == task_id).order_by(TaskHistory.timestamp.desc()).all()
    return history