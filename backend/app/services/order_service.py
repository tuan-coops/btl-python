from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.cart_item import CartItem
from app.models.enums import OrderStatus, PaymentMethod
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.user import User
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.order import (
    CheckoutRequest,
    OrderDetailResponse,
    OrderItemResponse,
    OrderListResponse,
    OrderSummaryResponse,
    ShippingSnapshotResponse,
)


class OrderService:
    def __init__(
        self,
        db: Session,
        order_repository: OrderRepository,
        cart_repository: CartRepository,
    ) -> None:
        self.db = db
        self.logger = get_logger(__name__)
        self.order_repository = order_repository
        self.cart_repository = cart_repository

    def _generate_order_code(self) -> str:
        while True:
            order_code = f"ORD-{uuid4().hex[:10].upper()}"
            if not self.order_repository.order_code_exists(order_code):
                return order_code

    def _serialize_item(self, item: OrderItem) -> OrderItemResponse:
        return OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product_name,
            unit_price=item.unit_price,
            quantity=item.quantity,
            line_total=item.line_total,
        )

    def _serialize_summary(self, order: Order) -> OrderSummaryResponse:
        return OrderSummaryResponse(
            id=order.id,
            order_code=order.order_code,
            status=order.status.value,
            payment_method=order.payment_method.value,
            subtotal=order.subtotal,
            shipping_fee=order.shipping_fee,
            discount_amount=order.discount_amount,
            total_amount=order.total_amount,
            created_at=order.created_at,
            items=[self._serialize_item(item) for item in order.items],
        )

    def checkout(self, current_user: User, payload: CheckoutRequest) -> OrderDetailResponse:
        cart = self.cart_repository.get_cart_by_user_id(current_user.id)
        if cart is None or not cart.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

        try:
            payment_method = PaymentMethod(payload.payment_method)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment method") from exc

        try:
            subtotal = Decimal("0")
            order_items: list[OrderItem] = []

            for cart_item in cart.items:
                product = cart_item.product
                if product is None or not product.is_active:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is not available")
                if cart_item.quantity > product.stock_quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Requested quantity exceeds available stock",
                    )

                line_total = cart_item.unit_price * cart_item.quantity
                subtotal += line_total
                product.stock_quantity -= cart_item.quantity
                order_items.append(
                    OrderItem(
                        product_id=cart_item.product_id,
                        product_name=cart_item.product_name,
                        unit_price=cart_item.unit_price,
                        quantity=cart_item.quantity,
                        line_total=line_total,
                    )
                )

            shipping_fee = Decimal("0")
            discount_amount = Decimal("0")
            total_amount = subtotal + shipping_fee - discount_amount

            order = Order(
                user_id=current_user.id,
                order_code=self._generate_order_code(),
                shipping_recipient_name=payload.recipient_name,
                shipping_phone=payload.phone,
                shipping_line1=payload.line1,
                shipping_line2=payload.line2,
                shipping_ward=payload.ward,
                shipping_district=payload.district,
                shipping_city=payload.city,
                shipping_province=payload.province,
                shipping_country=payload.country,
                customer_note=payload.note,
                subtotal=subtotal,
                shipping_fee=shipping_fee,
                discount_amount=discount_amount,
                total_amount=total_amount,
                payment_method=payment_method,
                status=OrderStatus.PENDING,
                items=order_items,
            )
            self.db.add(order)

            for cart_item in list(cart.items):
                self.db.delete(cart_item)

            self.db.commit()
            self.db.refresh(order)
            order = self.order_repository.get_user_order_by_id(current_user.id, order.id)
            self.logger.info("Order created: order_id=%s user_id=%s total=%s", order.id, current_user.id, order.total_amount)
            return OrderDetailResponse(
                **self._serialize_summary(order).model_dump(),
                shipping_address=ShippingSnapshotResponse(
                    recipient_name=order.shipping_recipient_name,
                    phone=order.shipping_phone,
                    line1=order.shipping_line1,
                    line2=order.shipping_line2,
                    ward=order.shipping_ward,
                    district=order.shipping_district,
                    city=order.shipping_city,
                    province=order.shipping_province,
                    country=order.shipping_country,
                ),
                note=order.customer_note,
            )
        except Exception:
            self.db.rollback()
            raise

    def list_orders(self, current_user: User, page: int, page_size: int) -> OrderListResponse:
        orders, total = self.order_repository.list_user_orders(current_user.id, page, page_size)
        return OrderListResponse(
            items=[self._serialize_summary(order) for order in orders],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_order_detail(self, current_user: User, order_id: int) -> OrderDetailResponse:
        order = self.order_repository.get_user_order_by_id(current_user.id, order_id)
        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return OrderDetailResponse(
            **self._serialize_summary(order).model_dump(),
            shipping_address=ShippingSnapshotResponse(
                recipient_name=order.shipping_recipient_name,
                phone=order.shipping_phone,
                line1=order.shipping_line1,
                line2=order.shipping_line2,
                ward=order.shipping_ward,
                district=order.shipping_district,
                city=order.shipping_city,
                province=order.shipping_province,
                country=order.shipping_country,
            ),
            note=order.customer_note,
        )
