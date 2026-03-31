from sqlalchemy.orm import Session, joinedload

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product


class CartRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_cart_by_user_id(self, user_id: int) -> Cart | None:
        return (
            self.db.query(Cart)
            .options(
                joinedload(Cart.items).joinedload(CartItem.product).joinedload(Product.images),
            )
            .filter(Cart.user_id == user_id)
            .first()
        )

    def create_cart(self, user_id: int) -> Cart:
        cart = Cart(user_id=user_id)
        self.db.add(cart)
        self.db.flush()
        return cart

    def get_or_create_cart(self, user_id: int) -> Cart:
        cart = self.get_cart_by_user_id(user_id)
        if cart is None:
            cart = self.create_cart(user_id)
        return cart

    def get_cart_item(self, item_id: int, user_id: int) -> CartItem | None:
        return (
            self.db.query(CartItem)
            .join(Cart, CartItem.cart_id == Cart.id)
            .options(joinedload(CartItem.product).joinedload(Product.images))
            .filter(CartItem.id == item_id, Cart.user_id == user_id)
            .first()
        )
