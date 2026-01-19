from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.models.team import Team
from app.models.user import User

def create_team(db: Session, name: str, description: str = None) -> Team:
    new_team = Team(name=name, description=description)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team

def get_team_by_name(db: Session, name: str) -> Optional[Team]:
    return db.query(Team).filter(Team.name == name).first()

def get_all_teams(db: Session) -> List[Team]:
    return db.query(Team).options(joinedload(Team.members), joinedload(Team.manager)).order_by(Team.id.asc()).all()

def get_team_by_id(db: Session, team_id: int) -> Optional[Team]:
    return db.query(Team).filter(Team.id == team_id).options(joinedload(Team.members), joinedload(Team.tasks), joinedload(Team.manager)).first()

def delete_team(db: Session, team: Team):
    db.delete(team)
    db.commit()

def assign_manager_to_team(db: Session, team: Team, manager_id: int) -> Optional[Team]:
    user = db.query(User).filter(User.id == manager_id).first()
    if not user:
        return None
    
    team.manager_id = manager_id
    user.team_id = team.id
    db.commit()
    db.refresh(team)
    return team

def add_members_to_team(db: Session, team: Team, user_ids: List[int]) -> bool:
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    if len(users) != len(user_ids):
        return False
        
    for user in users:
        user.team_id = team.id
        
    db.commit()
    db.refresh(team)
    return True

def get_user_team(db: Session, user: User) -> Optional[Team]:
    team_query = db.query(Team).options(joinedload(Team.members), joinedload(Team.tasks))
    
    if user.team_id:
        return team_query.filter(Team.id == user.team_id).first()
    
    managed_team = team_query.filter(Team.manager_id == user.id).first()
    if managed_team:
        return managed_team
        
    return None

def remove_member_from_team(db: Session, team: Team, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.team_id != team.id:
        return False
        
    user.team_id = None
    if team.manager_id == user.id:
        team.manager_id = None
        
    db.commit()
    db.refresh(team)
    return True
