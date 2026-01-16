import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db, Base, engine
from app.models.user import User
from app.models.team import Team
from app.core.security import get_password_hash

client = TestClient(app)

# --- Fixtures ---
@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def admin_token(test_db):
    # Create Admin
    admin = User(
        username="admin_test",
        email="admin_test@ems.com",
        hashed_password=get_password_hash("password"),
        role="admin",
        is_active=True
    )
    test_db.add(admin)
    test_db.commit()
    
    response = client.post("/auth/login", data={"username": "admin_test", "password": "password"})
    return response.json()["access_token"]

# --- Tests ---

def test_create_user_admin(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "username": "new_employee",
        "email": "new_employee@ems.com",
        "password": "password123",
        "role": "employee"
    }
    
    response = client.post("/admin/users", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "new_employee"
    assert data["is_active"] == True
    assert data["role"] == "employee"

def test_team_member_management(admin_token, test_db):
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 1. Create Team
    team_payload = {"name": "Test Team 1", "description": "Desc"}
    res_team = client.post("/teams/", json=team_payload, headers=headers)
    assert res_team.status_code == 201
    team_id = res_team.json()["id"]
    
    # 2. Create User to be Member
    user_payload = {
        "username": "team_member_1",
        "email": "tm1@ems.com",
        "password": "password",
        "role": "employee"
    }
    res_user = client.post("/admin/users", json=user_payload, headers=headers)
    user_id = res_user.json()["id"]
    
    # 3. Add Member
    res_add = client.put(f"/teams/{team_id}/members", json=[user_id], headers=headers)
    assert res_add.status_code == 200
    
    # Verify Member added
    # Since we can't easily check via GET /teams list deep structure in one go without looping, 
    # we can try fetching the team by ID if that endpoint exists or checking DB
    team = test_db.query(Team).filter(Team.id == team_id).first()
    assert len(team.members) == 1
    assert team.members[0].id == user_id
    
    # 4. Remove Member
    res_del = client.delete(f"/teams/{team_id}/members/{user_id}", headers=headers)
    assert res_del.status_code == 200
    
    # Verify Member removed
    test_db.refresh(team)
    assert len(team.members) == 0
