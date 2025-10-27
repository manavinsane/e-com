from sqlmodel import SQLModel, Field, Enum as SqlEnum, Column, Relationship
from typing import Optional,List
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.enums.enums import UserRoles, SocialAccounts


class User(SQLModel, table=True):
    __tablename__ = 'users'

    # id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    # email : str = Field(index = True, unique=True, nullable=False)
    # username: str = Field(index=True, unique=True, nullable=False)
    # password:str = Field(nullable=False)
    # # email_verified: bool = Field(default=False)
    # # social_accounts: Optional[SocialAccounts] = Field(
    # #         sa_column=Column(SqlEnum(SocialAccounts, name="socialaccounts",
    # #         create_type=True,
    # #         default=None))
    # # )
    
    # is_active: bool = Field(default=True)
    # user_role: UserRoles = Field(
    #     sa_column=Column(SqlEnum(UserRoles, name="userroles", create_type=True)),
    #     default=UserRoles.USER
    # )
    # created_at: datetime = Field(default_factory= lambda: datetime.now(tz=timezone.utc))
    # updated_at: datetime = Field(default_factory= lambda: datetime.now(tz=timezone.utc))
    # orders : List["Order"] = Relationship(back_populates="created_by")
    
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
    orders : List["Order"] = Relationship(back_populates="created_by")