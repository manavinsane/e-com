from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from app.enums.enums import OrderStatus
from sqlmodel import Relationship

class Order(SQLModel, table=True):
    
    id: Optional[int] = Field(primary_key=True)
    created_by_id: int = Field(foreign_key="users.id")
    product_id: int
    quantity: int
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional["User"] = Relationship(back_populates="orders")


