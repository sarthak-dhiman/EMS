import requests

BASE_URL = "http://127.0.0.1:8000"

def login_admin():
    # Use existing admin
    email = "admin@ems.com"
    password = "password123"
    
    # Login
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    if resp.status_code != 200:
        print("Login failed", resp.text)
        return None
    return resp.json()["access_token"]

def reproduce():
    token = login_admin()
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create Team
    team_resp = requests.post(f"{BASE_URL}/teams/", json={"name": "Test Team 405"}, headers=headers)
    if team_resp.status_code == 400: # Already exists
        # Get team ID?
        teams = requests.get(f"{BASE_URL}/teams/", headers=headers).json()
        target_team = next((t for t in teams if t["name"] == "Test Team 405"), None)
        team_id = target_team["id"]
    else:
        team_id = team_resp.json()["id"]
        
    # 3. Create User to Add
    user_email = "victim_405@example.com"
    requests.post(f"{BASE_URL}/auth/register", json={
        "email": user_email, "username": "victim405", "password": "password", "role": "employee"
    })
    # We need to get this user's ID. Admin can list users.
    users = requests.get(f"{BASE_URL}/admin/users", headers=headers).json()
    target_user = next((u for u in users if u["email"] == user_email), None)
    
    if not target_user:
        print("Could not find user")
        return

    user_id = target_user["id"]
    
    # 4. Try to Add Member (PUT)
    print(f"Attempting PUT /teams/{team_id}/members with body [{user_id}]")
    resp = requests.put(f"{BASE_URL}/teams/{team_id}/members", json=[user_id], headers=headers)
    
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    reproduce()
