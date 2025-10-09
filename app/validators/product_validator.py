from typing import Optional
from pydantic import BaseModel

class ProductCreate(BaseModel):
    name:str
    description : Optional[str] = None
    price : float = 0.0
    stock : int = 0

class ProductUpdate(BaseModel):
    name:Optional[str]
    description : Optional[str]
    price : Optional[float]
    stock : Optional[int]

class ProductRead(BaseModel):
    id : int
    name : str
    description : Optional[str]
    price : float
    stock : int