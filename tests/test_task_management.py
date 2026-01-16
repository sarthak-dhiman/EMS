import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db, Base, engine
from app.models.user import User
from app.models.task import Task
from app.core.security import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

import uuid

@pytest.fixture(scope="module")
def manager_token(test_db):
    unique_id = str(uuid.uuid4())[:8]
    username = f"manager_{unique_id}"
    email = f"mgr_{unique_id}@ems.com"
    
    user = User(username=username, email=email, hashed_password=get_password_hash("password"), role="manager", is_active=True)
    test_db.add(user)
    test_db.commit()
    response = client.post("/auth/login", data={"username": username, "password": "password"})
    return response.json()["access_token"]

def test_task_lifecycle_with_subtasks(manager_token, test_db):
    headers = {"Authorization": f"Bearer {manager_token}"}
    
    # 1. Create Task
    task_payload = {"title": "Main Task", "description": "Desc"}
    res_task = client.post("/tasks/", json=task_payload, headers=headers)
    assert res_task.status_code == 200
    task_id = res_task.json()["id"]
    
    # 2. Add Subtask
    res_sub = client.post(f"/tasks/{task_id}/subtasks", json={"title": "Subtask 1"}, headers=headers)
    assert res_sub.status_code == 200
    subtask_id = res_sub.json()["id"]
    
    # 3. Verify Subtask in Task
    res_get = client.get("/tasks/", headers=headers)
    task_data = [t for t in res_get.json() if t["id"] == task_id][0]
    assert len(task_data["subtasks"]) == 1
    assert task_data["subtasks"][0]["title"] == "Subtask 1"
    
    # 4. Toggle Subtask
    res_toggle = client.put(f"/tasks/subtasks/{subtask_id}", json={"title": "Subtask 1", "is_completed": True}, headers=headers)
    assert res_toggle.status_code == 200
    assert res_toggle.json()["is_completed"] == True
    
    # 5. Update Task Details (Change Title)
    res_update = client.put(f"/tasks/{task_id}", json={"title": "Renamed Task"}, headers=headers)
    assert res_update.status_code == 200
    
    # 6. Verify Updates
    res_get_2 = client.get("/tasks/", headers=headers)
    task_data_2 = [t for t in res_get_2.json() if t["id"] == task_id][0]
    assert task_data_2["title"] == "Renamed Task"
    assert task_data_2["subtasks"][0]["is_completed"] == True
    
    # 7. Delete Subtask
    res_del = client.delete(f"/tasks/subtasks/{subtask_id}", headers=headers)
    assert res_del.status_code == 200
    
    res_get_3 = client.get("/tasks/", headers=headers)
    task_data_3 = [t for t in res_get_3.json() if t["id"] == task_id][0]
    assert len(task_data_3["subtasks"]) == 0
