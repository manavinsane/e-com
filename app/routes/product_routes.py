from fastapi import APIRouter, Depends, HTTPException

from app.validators import product_validator
from app.api import product as product_api

from app.models.product_model import Product

from typing import List


router = APIRouter(prefix='/products', tags=['products'])

@router.post('/',response_model = Product)
def create_product(product_in : product_validator.ProductCreate):
    return product_api.create_product(product_in)   

@router.get('/',response_model = List[product_validator.ProductRead])
def get_products():
    return product_api.list_products()

@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int):
    product = product_api.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=Product)
def update_product(product_id: int, product_update: product_validator.ProductUpdate):
    return product_api.update_product(product_id, **product_update.dict())

@router.delete("/{product_id}")
def delete_product(product_id: int):
    product_api.del_product(product_id)
    return {"detail": "Deleted"}