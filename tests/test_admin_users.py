import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.core.security import get_password_hash

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_admin_users.db"
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

def test_admin_users_flow():
    # 1. Create Users
    db = TestingSessionLocal()
    admin = User(email="admin@e.com", username="admin", hashed_password=get_password_hash("pass"), role="admin", is_active=True)
    manager = User(email="mgr@e.com", username="manager", hashed_password=get_password_hash("pass"), role="manager", is_active=True)
    emp = User(email="emp@e.com", username="employee", hashed_password=get_password_hash("pass"), role="employee", is_active=True)
    db.add_all([admin, manager, emp])
    db.commit()
    db.close()

    # Login as Admin
    res = client.post("/auth/login", data={"username": "admin", "password": "pass"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get All Users
    res = client.get("/admin/users", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 3

    # 3. Search for "emp"
    res = client.get("/admin/users?search=emp", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["username"] == "employee"

    # 4. Filter by Role "manager"
    res = client.get("/admin/users?role=manager", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["role"] == "manager"

    # 5. Combined Search & Filter
    res = client.get("/admin/users?search=mgr&role=manager", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1

    # 5b. Search by ID (assuming admin has ID 1)
    res = client.get("/admin/users?search=1", headers=headers)
    assert res.status_code == 200
    # Might have multiple if digits are in username, but ID 1 should be there
    users = res.json()
    assert any(u["id"] == 1 for u in users)

    # 6. Test Unauthorized Access
    # Login as Manager (cannot access /admin/users)
    res = client.post("/auth/login", data={"username": "manager", "password": "pass"})
    mgr_token = res.json()["access_token"]
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}

    res = client.get("/admin/users", headers=mgr_headers)
    assert res.status_code == 403
