from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.team import Team
from app.models.user import User
from app.schemas.team import TeamCreate, TeamResponse, TeamUpdate
from app.schemas.user import UserResponse
from app.dependencies import get_current_user

from app.services.team import (
    create_team, get_team_by_name, get_all_teams, get_team_by_id,
    delete_team, assign_manager_to_team, add_members_to_team, get_user_team
)

router = APIRouter()

# --- Admin Endpoints ---

@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_new_team_route(
    team: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    existing_team = get_team_by_name(db, team.name)
    if existing_team:
        raise HTTPException(status_code=400, detail="Team name already exists")
    
    return create_team(db, team.name, team.description)

@router.get("/", response_model=List[TeamResponse])
def get_all_teams_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_all_teams(db)

@router.delete("/{team_id}")
def delete_team_route(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    team = get_team_by_id(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    delete_team(db, team)
    return {"message": "Team deleted"}

@router.put("/{team_id}/manager", response_model=TeamResponse)
def assign_manager_route(
    team_id: int,
    manager_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    team = get_team_by_id(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    updated_team = assign_manager_to_team(db, team, manager_id)
    if not updated_team:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated_team

@router.put("/{team_id}/members", response_model=TeamResponse)
def update_members_route(
    team_id: int,
    user_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Not authorized")
         
    team = get_team_by_id(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    success = add_members_to_team(db, team, user_ids)
    if not success:
        raise HTTPException(status_code=400, detail="One or more user IDs invalid")
        
    return team

@router.delete("/{team_id}/members/{user_id}", response_model=TeamResponse)
def remove_member_route(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Not authorized")
         
    team = get_team_by_id(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    from app.services.team import remove_member_from_team
    success = remove_member_from_team(db, team, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="User not in this team")
        
    return team

# --- Manager Endpoints ---

@router.get("/my-team", response_model=TeamResponse)
def get_my_team_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    team = get_user_team(db, current_user)
    if not team:
        raise HTTPException(status_code=404, detail="You are not part of any team")
    return team
