import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.schemas.user import UserResponse
from datetime import date

class MockTeam:
    def __init__(self, name):
        self.name = name

class MockUser:
    def __init__(self, id, username, email, team_name, is_active, role, team=None, dob=None, mobile_number=None, team_id=None):
        self.id = id
        self.username = username
        self.email = email
        self.team_name = team_name # The column value (might be old/None)
        self.is_active = is_active
        self.role = role
        self.team = team
        self.dob = dob
        self.mobile_number = mobile_number
        self.team_id = team_id

    @property
    def display_team_name(self):
        return self.team.name if self.team else self.team_name

def test_schema():
    # Case 1: Has team relationship
    user_with_team = MockUser(
        id=1, username="u1", email="u1@e.com", team_name="OldName", is_active=True, role="emp",
        team=MockTeam("NewTeam")
    )
    resp = UserResponse.model_validate(user_with_team)
    print(f"Case 1 (With Team Rel): {resp.team_name}")
    if resp.team_name != "NewTeam":
        print("FAIL Case 1")
    
    # Case 2: No relationship, falls back to column
    user_no_rel = MockUser(
        id=2, username="u2", email="u2@e.com", team_name="Fallback", is_active=True, role="emp",
        team=None
    )
    resp2 = UserResponse.model_validate(user_no_rel)
    print(f"Case 2 (No Rel): {resp2.team_name}")
    if resp2.team_name != "Fallback":
        print("FAIL Case 2")

if __name__ == "__main__":
    test_schema()
