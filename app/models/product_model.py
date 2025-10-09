from sqlmodel import SQLModel, Field
from typing import Optional

class Product(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    name: str
    stock: int
    price: float = 0.0
    description: Optional[str] = Field(default=None)