from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemCreateRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class CartItemUpdateRequest(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    unit_price: Decimal
    quantity: int
    line_total: Decimal
    primary_image: str | None


class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse]
    subtotal: Decimal
    total_quantity: int
