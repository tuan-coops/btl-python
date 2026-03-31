from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.cart_repository import CartRepository
from app.schemas.cart import CartItemCreateRequest, CartItemUpdateRequest, CartResponse
from app.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartResponse)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CartResponse:
    service = CartService(db, CartRepository(db))
    return service.get_cart(current_user)


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_cart_item(
    payload: CartItemCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CartResponse:
    service = CartService(db, CartRepository(db))
    return service.add_item(current_user, payload)


@router.patch("/items/{item_id}", response_model=CartResponse)
def update_cart_item(
    item_id: int,
    payload: CartItemUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CartResponse:
    service = CartService(db, CartRepository(db))
    return service.update_item(current_user, item_id, payload)


@router.delete("/items/{item_id}", response_model=CartResponse)
def delete_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CartResponse:
    service = CartService(db, CartRepository(db))
    return service.remove_item(current_user, item_id)
