from app.models.product_model import Product
from sqlmodel import Session, select
from fastapi import HTTPException
from typing import List
from app.validators.product_validator import ProductCreate
from langchain.tools import tool
from app.db.database import get_session
import json


@tool("create_product_tool",return_direct=True)
def create_product(product_in:ProductCreate)->Product:
    """Create a product with given name description(optional) price and stock"""
    try:
            session_gen = get_session()
            session = next(session_gen)
            product = Product(**product_in.dict())  # <-- convert Pydantic -> ORM
            session.add(product)
            session.commit()
            session.refresh(product)
            return product.dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        try:
            next(session_gen)
        except StopIteration:
            pass

@tool("update_product_tool",return_direct=True)
def update_product(id :int ,**kwargs)->Product:
    """updates a product"""
    try:    
            session_gen = get_session()
            session = next(session_gen) 
            product = session.get(Product, id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            for key, value in kwargs.items():
                if value is not None:
                    setattr(product, key, value)
            session.add(product)
            session.commit()
            session.refresh(product)
            return product.dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        try:
            next(session_gen)
        except StopIteration:
            pass

@tool("get_product_tool",return_direct=True)
def get_product( id:int)->Product:
    """returns a product by id"""
    try:
            session_gen = get_session()
            session = next(session_gen)
            product = session.get(Product, id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            return product.dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        try:
            next(session_gen)
        except StopIteration:
            pass
@tool("list_products_tool",return_direct=True)
def list_products()->List[Product]:
    """returns a list of all products"""
    
    try:
        session_gen = get_session()
        session = next(session_gen)
        q = select(Product)
        products = session.exec(q).all()
        # breakpoint()
        return json.dumps([p.dict() for p in products])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        try:
            next(session_gen)
        except StopIteration:
            pass
@tool("delete_product_tool",return_direct=True)
def del_product(id : int )->None:
    """deletes a product by id"""
    try:
            session_gen = get_session()
            session = next(session_gen)
            product = session.get(Product, id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            session.delete(product)
            session.commit()
    except Exception as e:
        raise HTTPException(status_code=40, detail=str(e))
    finally:
        try:
            next(session_gen)
        except StopIteration:
            pass


LLM_TOOLS = [create_product, update_product, get_product,list_products,del_product]

# LLM_TOOLS = [create_product]