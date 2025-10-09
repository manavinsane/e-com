from sqlmodel import SQLModel, Field, Enum as SqlEnum, Column
from typing import Optional
from datetime import datetime
from app.enums.enums import UserRoles


class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: Optional[int] = Field(primary_key=True)
    email : str = Field(index = True, unique=True, nullable=False)
    username: str = Field(index=True, unique=True, nullable=False)
    password:str = Field(nullable=False)
    is_active: bool = Field(default=True)
    user_role: UserRoles = Field(
        sa_column=Column(SqlEnum(UserRoles, name="userroles", create_type=True)),
        default=UserRoles.USER
    )
    access_token: Optional[str] = Field(default=None)
    refresh_token: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)