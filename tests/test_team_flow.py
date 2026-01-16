import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.team import Team
from app.core.security import get_password_hash

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_teams.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_team_flow():
    # 1. Create Admin
    db = TestingSessionLocal()
    admin_user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_active=True
    )
    db.add(admin_user)
    db.commit()
    
    # 2. Create Manager
    manager_user = User(
        email="manager@example.com",
        username="manager",
        hashed_password=get_password_hash("manager123"),
        role="manager",
        is_active=True
    )
    db.add(manager_user)
    db.commit()

    # 3. Create Employee (User A)
    user_a = User(
        email="usera@example.com",
        username="usera",
        hashed_password=get_password_hash("user123"),
        role="employee",
        is_active=True
    )
    db.add(user_a)
    db.commit()
    db.close()

    # Login as Admin
    res = client.post("/auth/login", data={"username": "admin", "password": "admin123"})
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 4. Admin creates Team
    res = client.post("/teams/", json={"name": "Alpha Team", "description": "The A Team"}, headers=admin_headers)
    assert res.status_code == 201
    team_id = res.json()["id"]

    # 5. Admin assigns Manager to Team
    # We need manager ID.
    db = TestingSessionLocal()
    manager_id = db.query(User).filter(User.username == "manager").first().id
    user_a_id = db.query(User).filter(User.username == "usera").first().id
    db.close()

    res = client.put(f"/teams/{team_id}/manager?manager_id={manager_id}", headers=admin_headers)
    assert res.status_code == 200

    # 6. Admin assigns User A to Team
    res = client.put(f"/teams/{team_id}/members", json=[user_a_id], headers=admin_headers)
    assert res.status_code == 200

    # Login as Manager
    res = client.post("/auth/login", data={"username": "manager", "password": "manager123"})
    manager_token = res.json()["access_token"]
    manager_headers = {"Authorization": f"Bearer {manager_token}"}

    # 7. Manager views My Team
    res = client.get("/teams/my-team", headers=manager_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Alpha Team"

    # 8. Manager assigns task to User A
    res = client.post("/tasks/", json={
        "title": "Fix Bug", 
        "description": "Urgent",
        "user_id": user_a_id,
        "team_id": team_id
    }, headers=manager_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Fix Bug"
    
    # 9. Manager fails to assign task to non-team member
    # Create another user outside using DB directly for speed
    db = TestingSessionLocal()
    user_b = User(email="b@e.com", username="b", hashed_password="x", role="employee", is_active=True)
    db.add(user_b)
    db.commit()
    user_b_id = user_b.id
    db.close()

    res = client.post("/tasks/", json={
        "title": "Bad Assign", 
        "user_id": user_b_id,
        "team_id": team_id
    }, headers=manager_headers)
    assert res.status_code == 403
