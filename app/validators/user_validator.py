from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional
from datetime import datetime
from app.enums.enums import UserRoles

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str
    is_active: Optional[bool] = True
    user_role: Optional[UserRoles] = UserRoles.USER

    

class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

    @model_validator(mode="before")
    def check_username_or_email(cls, values):
        if not values.get("username") and not values.get("email"):
            raise ValueError("Either username or email must be provided")
        return values
    
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    access_token: Optional[str]
    refresh_token: Optional[str]
    created_at: datetime

# class UserLogin(BaseModel):
#     username: str
#     password: str
