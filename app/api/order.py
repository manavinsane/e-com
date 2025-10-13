from app.models.order_model import Order
from app.models.user_model import User
from app.models.product_model import Product
from sqlmodel import Session, select, func
from fastapi import HTTPException
from typing import  Optional,List
from app.enums.enums import OrderStatus
from app.enums.enums import UserRoles
from datetime import datetime


def create_order(session : Session , * , quantity : int , product_id : int, created_by : int)->Order:
    try:
        user = session.get(User,created_by)
        userrole = user.user_role
        if userrole == UserRoles.ADMIN:
            product = session.get(Product , product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

            if quantity<=0:
                raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

            if quantity>product.stock:
                raise HTTPException(status_code=400, detail="Not enough stock")

            product.stock -= quantity

            order = Order(product_id=product_id, quantity=quantity,created_by_id=created_by)

            session.add(product)
            session.add(order)
            session.commit()
            session.refresh(order)

            return order

        raise HTTPException(status_code=400, detail="User is not an admin")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_order(session:Session, id:int, current_user:int)->Order:
    try:
        user = session.get(User, current_user)
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


def list_orders(session: Session, skip: int, limit: int, status: Optional[OrderStatus],date_from: Optional[str],date_to: Optional[str], current_user: int):
    try:
        user = session.get(User, current_user)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        q = select(Order)
        
        # Add debug prints
        print(f"User role: {user.user_role}")
        print(f"Status filter: {status}")
        print(f"Date from: {date_from}")
        print(f"Date to: {date_to}")
        
        if user.user_role == UserRoles.USER:
            q = q.where(Order.created_by == user.id)
            print(f"Applied USER filter for user_id: {user.id}")
            
        if status:
            q = q.where(Order.status == status)
            print(f"Applied status filter: {status}")

        date_from_dt = datetime.strptime(date_from, "%Y-%m-%d") if date_from else None
        date_to_dt = datetime.strptime(date_to, "%Y-%m-%d") if date_to else None

        if date_from_dt and date_to_dt:
 
            date_to_dt = date_to_dt.replace(hour=23, minute=59, second=59)
            q = q.where(Order.created_at.between(date_from_dt, date_to_dt))
            print(f"Applied date_from and date_to filter: {date_from_dt} to {date_to_dt}")
        elif date_from_dt:
            q = q.where(Order.created_at >= date_from_dt)
            print(f"Applied date_from filter: {date_from_dt}")
        elif date_to_dt:
            date_to_dt = date_to_dt.replace(hour=23, minute=59, second=59)
            q = q.where(Order.created_at <= date_to_dt)
            print(f"Applied date_to filter: {date_to_dt}")

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

# def list_user_order(session:Session,skip:int,limit:int ,id:int,current_user:int):
#     try:
#         user = session.get(User, current_user)

#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
        
#         if user.user_role == UserRoles.ADMIN:
#             query1 = select(Order).where(Order.created_by_id == id)

#             print(f"Final query: {query1}")
#         else:
#             raise HTTPException(status_code=400, detail="User is not an admin")
        
#         count_query = select(func.count()).select_from(query1.subquery())
#         total_items = session.exec(count_query).one()

#         orders = session.exec(query1.offset(skip).limit(limit)).all()
        

#         page = (skip // limit) + 1
#         total_pages = (total_items + limit - 1) // limit

#         orders = session.exec(query1).all()
        
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
    

def list_user_order(session: Session, skip: int, limit: int, id: int, current_user: int):
    user = session.get(User, current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.user_role != UserRoles.ADMIN:
        raise HTTPException(status_code=403, detail="User is not an admin")

    # Query orders for the specified user id
    query1 = select(Order).where(Order.created_by_id == id)

    # Total items for pagination
    count_query = select(func.count()).select_from(query1.subquery())
    total_items = session.exec(count_query).one()

    # Paginated results
    orders = session.exec(query1.offset(skip).limit(limit)).all()

    # Pagination meta
    page = (skip // limit) + 1
    total_pages = (total_items + limit - 1) // limit

    return {
        "data": orders,  # List[Order]
        "meta": {
            "total_items": total_items,
            "page": page,
            "per_page": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }

