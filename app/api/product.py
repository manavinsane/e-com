from app.models.product_model import Product
from sqlmodel import Session, select
from fastapi import HTTPException
from typing import List
from app.validators.product_validator import ProductCreate



def create_product(session:Session ,product_in:ProductCreate)->Product:
    try:
        product = Product(**product_in.dict())  # <-- convert Pydantic -> ORM
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def update_product(session:Session ,id :int ,**kwargs)->Product:
    try:    
        product = session.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        for key, value in kwargs.items():
            if value is not None:
                setattr(product, key, value)
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
def get_product(session:Session, id:int)->Product:
    try:
        product = session.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def list_products(session:Session)->List[Product]:
    # @TODO add pagination and search functionality. 
    try:
        q = select(Product)
        return session.exec(q).all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def del_product(session: Session, id : int )->None:
    try:
        product = session.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        session.delete(product)
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



