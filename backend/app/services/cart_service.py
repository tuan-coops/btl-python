from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.user import User
from app.repositories.cart_repository import CartRepository
from app.schemas.cart import CartItemCreateRequest, CartItemResponse, CartItemUpdateRequest, CartResponse


def _primary_image_url(product: Product | None) -> str | None:
    if product is None or not product.images:
        return None
    primary = next((image for image in product.images if image.is_primary), None)
    return primary.image_url if primary else product.images[0].image_url


class CartService:
    def __init__(self, db: Session, repository: CartRepository) -> None:
        self.db = db
        self.repository = repository

    def _serialize_item(self, item: CartItem) -> CartItemResponse:
        line_total = item.unit_price * item.quantity
        return CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product_name,
            unit_price=item.unit_price,
            quantity=item.quantity,
            line_total=line_total,
            primary_image=_primary_image_url(item.product),
        )

    def _serialize_cart(self, cart: Cart) -> CartResponse:
        items = [self._serialize_item(item) for item in cart.items]
        subtotal = sum((item.line_total for item in items), start=Decimal("0"))
        total_quantity = sum(item.quantity for item in items)
        return CartResponse(
            id=cart.id,
            items=items,
            subtotal=subtotal,
            total_quantity=total_quantity,
        )

    def get_cart(self, current_user: User) -> CartResponse:
        cart = self.repository.get_or_create_cart(current_user.id)
        self.db.commit()
        cart = self.repository.get_cart_by_user_id(current_user.id)
        return self._serialize_cart(cart)

    def add_item(self, current_user: User, payload: CartItemCreateRequest) -> CartResponse:
        cart = self.repository.get_or_create_cart(current_user.id)
        product = (
            self.db.query(Product)
            .filter(Product.id == payload.product_id, Product.is_active.is_(True))
            .first()
        )
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if product.stock_quantity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is out of stock")

        existing_item = next((item for item in cart.items if item.product_id == product.id), None)
        new_quantity = payload.quantity if existing_item is None else existing_item.quantity + payload.quantity
        if new_quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity exceeds available stock",
            )

        if existing_item is None:
            cart.items.append(
                CartItem(
                    product_id=product.id,
                    product_name=product.name,
                    unit_price=product.price,
                    quantity=payload.quantity,
                )
            )
        else:
            existing_item.quantity = new_quantity

        self.db.commit()
        cart = self.repository.get_cart_by_user_id(current_user.id)
        return self._serialize_cart(cart)

    def update_item(self, current_user: User, item_id: int, payload: CartItemUpdateRequest) -> CartResponse:
        item = self.repository.get_cart_item(item_id, current_user.id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
        if item.product is None or not item.product.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is not available")
        if payload.quantity > item.product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity exceeds available stock",
            )

        item.quantity = payload.quantity
        self.db.commit()
        cart = self.repository.get_cart_by_user_id(current_user.id)
        return self._serialize_cart(cart)

    def remove_item(self, current_user: User, item_id: int) -> CartResponse:
        item = self.repository.get_cart_item(item_id, current_user.id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

        self.db.delete(item)
        self.db.commit()
        cart = self.repository.get_cart_by_user_id(current_user.id)
        if cart is None:
            cart = self.repository.create_cart(current_user.id)
            self.db.commit()
            cart = self.repository.get_cart_by_user_id(current_user.id)
        return self._serialize_cart(cart)
