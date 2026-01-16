from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.task import Task
from app.models.subtask import SubTask
from app.models.team import Team
from app.core.security import get_password_hash
from passlib.context import CryptContext

from sqlalchemy import text

# Try to drop tables with cascade to handle circular dependencies
with engine.connect() as connection:
    connection.execute(text("DROP TABLE IF EXISTS tasks CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS teams CASCADE"))
    connection.commit()

Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # Configuration for seeding
    TEAMS_CONFIG = [
        {"name": "Engineering", "description": "Software Development Team"},
        {"name": "Marketing", "description": "Sales and Marketing Team"},
        {"name": "Design", "description": "UI/UX Design Team"},
    ]
    
    USERS_CONFIG = [
        # Admin
        {"email": "admin@ems.com", "username": "admin", "role": "admin", "team": None},
        
        # Engineering
        {"email": "eng.manager@ems.com", "username": "eng_manager", "role": "manager", "team": "Engineering"},
        {"email": "alice@ems.com", "username": "alice", "role": "employee", "team": "Engineering"},
        {"email": "bob@ems.com", "username": "bob", "role": "employee", "team": "Engineering"},
        
        # Marketing
        {"email": "mkt.manager@ems.com", "username": "mkt_manager", "role": "manager", "team": "Marketing"},
        {"email": "charlie@ems.com", "username": "charlie", "role": "employee", "team": "Marketing"},
        
        # Design
        {"email": "design.manager@ems.com", "username": "design_manager", "role": "manager", "team": "Design"},
        {"email": "dave@ems.com", "username": "dave", "role": "employee", "team": "Design"},
    ]
    
    common_password = "password123"
    hashed_password = get_password_hash(common_password)
    
    report_lines = []
    logins_output = ["--- EMS CREDENTIALS ---"]

    try:
        # 1. Create Teams
        teams_map = {} # name -> id
        print("Seeding Teams...")
        for t_conf in TEAMS_CONFIG:
            team = db.query(Team).filter(Team.name == t_conf["name"]).first()
            if not team:
                team = Team(name=t_conf["name"], description=t_conf["description"])
                db.add(team)
                db.commit()
                db.refresh(team)
                print(f"   Created Team: {team.name}")
            else:
                print(f"   Team exists: {team.name}")
            teams_map[team.name] = team

        # 2. Create Users
        print("\nSeeding Users...")
        users_map = {} # username -> user object
        
        for u_conf in USERS_CONFIG:
            user = db.query(User).filter(User.email == u_conf["email"]).first()
            if not user:
                user = User(
                    email=u_conf["email"],
                    username=u_conf["username"],
                    hashed_password=hashed_password,
                    role=u_conf["role"],
                    is_active=True,
                    team_id=teams_map[u_conf["team"]].id if u_conf["team"] else None
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"   Created User: {user.username} ({user.role})")
            else:
                # Update team if needed
                if u_conf["team"] and user.team_id != teams_map[u_conf["team"]].id:
                    user.team_id = teams_map[u_conf["team"]].id
                    db.commit()
                print(f"   User exists: {user.username}")
            
            users_map[user.username] = user
            
            # Add to logins file
            logins_output.append(f"\nUser: {user.username}")
            logins_output.append(f"Email: {user.email}")
            logins_output.append(f"Role: {user.role}")
            logins_output.append(f"Team: {u_conf['team'] or 'None'}")
            logins_output.append(f"Password: {common_password}")
            logins_output.append("-" * 20)

        # 3. Assign Managers to Teams
        print("\nAssigning Managers...")
        for u_conf in USERS_CONFIG:
            if u_conf["role"] == "manager" and u_conf["team"]:
                team = teams_map[u_conf["team"]]
                manager = users_map[u_conf["username"]]
                if team.manager_id != manager.id:
                    team.manager_id = manager.id
                    db.commit()
                    print(f"   Assigned {manager.username} as manager of {team.name}")

        # 4. Create Tasks
        print("\nSeeding Tasks...")
        TASKS_CONFIG = [
            # Engineering Tasks
            {"title": "Setup CI/CD", "status": "In Progress", "team": "Engineering", "user": "alice"},
            {"title": "Database Migration", "status": "Open", "team": "Engineering", "user": None}, # Unassigned team task
            {"title": "Frontend Revamp", "status": "Done", "team": "Engineering", "user": "bob"},
            
            # Marketing Tasks
            {"title": "Q1 Campaign", "status": "Open", "team": "Marketing", "user": "charlie"},
            {"title": "Social Media Plan", "status": "In Progress", "team": "Marketing", "user": None},
            
            # Design Tasks
            {"title": "Logo Redesign", "status": "Open", "team": "Design", "user": "dave"},
        ]

        for t_conf in TASKS_CONFIG:
            # Check if task exists (simple check by title for this seeder)
            exists = db.query(Task).filter(Task.title == t_conf["title"]).first()
            if not exists:
                team = teams_map[t_conf["team"]]
                user_id = users_map[t_conf["user"]].id if t_conf["user"] else None
                
                new_task = Task(
                    title=t_conf["title"],
                    description=f"Task for {t_conf['team']}",
                    priority="Medium",
                    status=t_conf["status"],
                    team_id=team.id,
                    user_id=user_id
                )
                db.add(new_task)
                db.commit()
                print(f"   Created Task: {new_task.title} -> {t_conf['team']} ({t_conf['user'] or 'Unassigned'})")

        # Write logins file
        with open("logins.txt", "w") as f:
            f.write("\n".join(logins_output))
        
        print("\nSeeding Complete!")
        print("Credentials saved to logins.txt")

    except Exception as e:
        print(f"Error seeding DB: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()