from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CheckoutRequest(BaseModel):
    recipient_name: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=1, max_length=20)
    line1: str = Field(min_length=1, max_length=255)
    line2: str | None = Field(default=None, max_length=255)
    ward: str | None = Field(default=None, max_length=100)
    district: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    province: str = Field(min_length=1, max_length=100)
    country: str = Field(default="Vietnam", min_length=1, max_length=100)
    payment_method: str
    note: str | None = None


class OrderItemResponse(BaseModel):
    id: int
    product_id: int | None
    product_name: str
    unit_price: Decimal
    quantity: int
    line_total: Decimal


class OrderSummaryResponse(BaseModel):
    id: int
    order_code: str
    status: str
    payment_method: str
    subtotal: Decimal
    shipping_fee: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    created_at: datetime
    items: list[OrderItemResponse]


class OrderListResponse(BaseModel):
    items: list[OrderSummaryResponse]
    total: int
    page: int
    page_size: int


class ShippingSnapshotResponse(BaseModel):
    recipient_name: str
    phone: str
    line1: str
    line2: str | None
    ward: str | None
    district: str | None
    city: str | None
    province: str
    country: str


class OrderDetailResponse(OrderSummaryResponse):
    shipping_address: ShippingSnapshotResponse
    note: str | None
