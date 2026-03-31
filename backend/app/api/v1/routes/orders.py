from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.order import CheckoutRequest, OrderDetailResponse, OrderListResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/checkout", response_model=OrderDetailResponse)
def checkout(
    payload: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderDetailResponse:
    service = OrderService(db, OrderRepository(db), CartRepository(db))
    return service.checkout(current_user, payload)


@router.get("", response_model=OrderListResponse)
def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderListResponse:
    service = OrderService(db, OrderRepository(db), CartRepository(db))
    return service.list_orders(current_user, page, page_size)


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderDetailResponse:
    service = OrderService(db, OrderRepository(db), CartRepository(db))
    return service.get_order_detail(current_user, order_id)
