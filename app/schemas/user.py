from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Any
from datetime import date

class UserBase(BaseModel):
    email: EmailStr
    username: str
    name: Optional[str] = None
    dob: Optional[date] = None
    mobile_number: Optional[str] = None
    team_name: Optional[str] = None
    team_id: Optional[int] = None

class UserCreate(UserBase):
    password: str
    role: str = "employee"

class UserResponse(UserBase):
    id: int
    is_active: bool
    role: str
    dob: Optional[date] = None
    
    # We want team_name to reflect the actual team logic
    # We can use the property display_team_name from the model
    
    model_config = {"from_attributes": True}

    @field_validator("team_name", mode="before", check_fields=False)
    def populate_team_name(cls, v, info):
        # If we are validating from an ORM object, check for display_team_name
        # Note: Pydantic v2 validation context is tricky.
        # But wait, if we define the field as computing from an alias?
        return v
        
    # Better: Use a custom getter via property method in a separate schema if tricky, 
    # but simplest Pydantic V2 way for ORM properties:
    # Just rely on the fact that if 'team_name' matches a property on the model, it is used.
    # BUT UserBase has 'team_name' which matches the COLUMN 'team_name'.
    # Pydantic prefers the attribute. The ORM has both (column and property).
    # We want the property logic.
    # So we should tell Pydantic to read 'display_team_name' for the 'team_name' field.
    
    team_name: Optional[str] = Field(None, validation_alias="display_team_name")
