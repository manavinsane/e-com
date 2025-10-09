from app.models.order_model import Order
from app.models.user_model import User
from app.models.product_model import Product
from sqlmodel import Session, select, func
from fastapi import HTTPException
from typing import  Optional
from app.enums.enums import OrderStatus
from app.enums.enums import UserRoles


def create_order(session : Session , * , quantity : int , product_id : int, created_by : int)->Order:
    try:
        product = session.get(Product , product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if quantity<=0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

        if quantity>product.stock:
            raise HTTPException(status_code=400, detail="Not enough stock")

        product.stock -= quantity

        order = Order(product_id=product_id, quantity=quantity,created_by=created_by)

        session.add(product)
        session.add(order)
        session.commit()
        session.refresh(order)

        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_order(session:Session, id:int)->Order:
    try:
        order = session.get(Order, id)
    
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
    
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# def list_orders(session: Session, skip: int, limit: int, status: Optional[OrderStatus],current_user:int):
#     try:
#         user = session.get(User, current_user) #current_user
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
        
#         q = select(Order)
        
#         if user.user_role == "USER":
#             q = q.where(Order.created_by == user.id)
            
#         if status:
#             q = q.where(Order.status == status)

#         count_query = select(func.count()).select_from(q.subquery())
#         total_items = session.exec(count_query).one()

#         orders = session.exec(q.offset(skip).limit(limit)).all()

#         page = (skip // limit) + 1
#         total_pages = (total_items + limit - 1) // limit

#         return {
#             "data": orders,
#             "meta": {
#                 "total_items": total_items,
#                 "page": page,
#                 "per_page": limit,
#                 "total_pages": total_pages,
#                 "has_next": page < total_pages,
#                 "has_prev": page > 1
#             }
#         }

#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


def list_orders(session: Session, skip: int, limit: int, status: Optional[OrderStatus], current_user: int):
    try:
        user = session.get(User, current_user)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        q = select(Order)
        
        # Add debug prints
        print(f"User role: {user.user_role}")
        print(f"Status filter: {status}")
        
        if user.user_role == UserRoles.USER:
            q = q.where(Order.created_by == user.id)
            print(f"Applied USER filter for user_id: {user.id}")
            
        if status:
            q = q.where(Order.status == status)
            print(f"Applied status filter: {status}")

        # Print the query to see what SQL is generated
        print(f"Final query: {q}")

        count_query = select(func.count()).select_from(q.subquery())
        total_items = session.exec(count_query).one()

        orders = session.exec(q.offset(skip).limit(limit)).all()

        page = (skip // limit) + 1
        total_pages = (total_items + limit - 1) // limit

        return {
            "data": orders,
            "meta": {
                "total_items": total_items,
                "page": page,
                "per_page": limit,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def mark_order_paid(session:Session, id:int)->Order:
    try:
        order = session.get(Order, id)

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.status == "COMPLETED":
            return order

        order.status = "COMPLETED"
        session.add(order)
        session.commit()
        session.refresh(order)

        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def del_order(session:Session, id:int)->str:
    try:
        order = session.get(Order, id)

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.status == "COMPLETED":
            raise HTTPException(status_code=400, detail="Cannot delete paid order")

        product = session.get(Product, order.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        product.stock += order.quantity

        session.add(product)
        session.delete(order)
        session.commit()
        session.refresh(product)

        return {"detail": "Deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))