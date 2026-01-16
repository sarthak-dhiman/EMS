import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.user import User

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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

def test_registration_flow():
    # 1. Register a new user
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "dob": "1990-01-01",
            "mobile_number": "1234567890",
            "team_name": "Engineering"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["is_active"] == False
    user_id = data["id"]

    # 2. Try to login (should fail because inactive)
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "password123"},
    )
    assert response.status_code == 401
    assert "pending admin approval" in response.json()["detail"]

    # 3. Admin Login (need to create an admin first)
    db = TestingSessionLocal()
    from app.core.security import get_password_hash
    admin_user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_active=True
    )
    db.add(admin_user)
    db.commit()
    db.close()

    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    admin_token = response.json()["access_token"]

    # 4. Admin sees pending user
    response = client.get(
        "/admin/pending-users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 1
    assert users[0]["username"] == "testuser"

    # 5. Admin approves user
    response = client.put(
        f"/admin/approve-user/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_active"] == True

    # 6. User login again (should succeed)
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

    # 7. Test login with email
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
