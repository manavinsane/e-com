from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import Optional
from app.enums.enums import OrderStatus
from app.db.database import get_session
# from app import crud, models, order_validator

from app.api import order as order_api
from app.models.order_model import Order
from app.validators.order_validator import OrderListResponse
from app.validators import order_validator

from app.api.user import get_current_user

router = APIRouter(prefix='/orders', tags=['orders'])


@router.get('/', response_model= OrderListResponse)
def list_orders(session: Session = Depends(get_session),
                current_user = Depends(get_current_user),
                skip: int = Query(0, ge=0), 
                limit: int = Query(10, ge=1),
                status: Optional[OrderStatus] = Query(None),
                date_from: Optional[str] = Query(None),
                date_to: Optional[str] = Query(None)):
    return order_api.list_orders(session,skip,limit,status,date_from,date_to,current_user)

@router.post('/', response_model=Order)
def create_order(order_in: order_validator.OrderCreate, session: Session = Depends(get_session),
                 current_user = Depends(get_current_user)):
    order = Order(**order_in.dict())
    return order_api.create_order(session, quantity=order.quantity, product_id=order.product_id,created_by=current_user)

@router.get('/{id}', response_model=Order)
def get_order(id: int, session: Session = Depends(get_session),
              current_user = Depends(get_current_user)):
    return order_api.get_order(session, id=id, current_user=current_user)

# @router.put('/{id}', response_model=models.Order)
# def update_order(id: int, order_update: order_validator.OrderUpdate, session: Session = Depends(get_session)):
#     return order.update_order(session, id=id, **order_update.dict())

@router.delete('/{id}', response_model=dict)
def delete_order(id: int, session: Session = Depends(get_session),
                 current_user = Depends(get_current_user)):
    return order_api.del_order(session, id=id)

@router.post('/{id}/paid', response_model=Order)
def mark_order_paid(id: int, session: Session = Depends(get_session),
                    current_user = Depends(get_current_user)):
    return order_api.mark_order_paid(session, id=id)

@router.get('/{id}/perticular-user', response_model=OrderListResponse)
def list_user_order(id: int,skip: int = Query(0, ge=0), limit: int = Query(10, ge=1) ,session: Session = Depends(get_session),
                    current_user = Depends(get_current_user)):
    return order_api.list_user_order(session, id=id,skip=skip,limit=limit, current_user=current_user)