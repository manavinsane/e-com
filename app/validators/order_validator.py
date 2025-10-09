from typing import Optional, List
from pydantic import BaseModel

class MetaData(BaseModel):
    total_items: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

class OrderCreate(BaseModel):
    product_id: int
    quantity: int

class OrderUpdate(BaseModel):
    id : int
    product_id: Optional[int]
    quantity: Optional[int]


class OrderRead(BaseModel):
    id: int
    product_id: int
    status: str
    quantity: int

    class Config:
        from_attributes = True  # needed for SQLModel -> Pydantic conversion

class OrderListResponse(BaseModel):
    data: List[OrderRead]
    meta: MetaData