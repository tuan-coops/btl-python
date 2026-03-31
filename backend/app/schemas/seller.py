from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.order import OrderItemResponse, ShippingSnapshotResponse


class PageMetaResponse(BaseModel):
    total: int
    page: int
    page_size: int


class SellerDashboardResponse(BaseModel):
    total_users: int
    total_products: int
    total_orders: int
    pending_orders: int
    low_stock_products: int
    monthly_revenue: Decimal


class SellerCategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=120)
    description: str | None = None
    is_active: bool = True


class SellerCategoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    slug: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    is_active: bool | None = None


class SellerCategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SellerCategoryListResponse(PageMetaResponse):
    items: list[SellerCategoryResponse]


class SellerProductCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    sku: str = Field(min_length=1, max_length=100)
    description: str | None = None
    price: Decimal = Field(ge=0)
    stock_quantity: int = Field(ge=0)
    brand: str | None = Field(default=None, max_length=100)
    pet_type: str
    category_id: int
    is_active: bool = True
    primary_image_url: str | None = None


class SellerProductUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=255)
    sku: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    brand: str | None = Field(default=None, max_length=100)
    pet_type: str | None = None
    category_id: int | None = None
    is_active: bool | None = None
    primary_image_url: str | None = None


class SellerProductImageResponse(BaseModel):
    id: int
    image_url: str
    alt_text: str | None
    is_primary: bool
    sort_order: int


class SellerProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    sku: str
    description: str | None
    price: Decimal
    stock_quantity: int
    brand: str | None
    pet_type: str
    category_id: int
    category_name: str
    is_active: bool
    images: list[SellerProductImageResponse]
    created_at: datetime
    updated_at: datetime


class SellerProductListResponse(PageMetaResponse):
    items: list[SellerProductResponse]


class SellerUserListItemResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str | None
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime


class SellerUserListResponse(PageMetaResponse):
    items: list[SellerUserListItemResponse]


class SellerOrderUserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str | None
    role: str


class SellerOrderSummaryResponse(BaseModel):
    id: int
    order_code: str
    status: str
    payment_method: str
    subtotal: Decimal
    shipping_fee: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    created_at: datetime
    user: SellerOrderUserResponse
    items: list[OrderItemResponse]


class SellerOrderListResponse(PageMetaResponse):
    items: list[SellerOrderSummaryResponse]


class SellerOrderDetailResponse(SellerOrderSummaryResponse):
    shipping_address: ShippingSnapshotResponse
    note: str | None


class SellerOrderStatusUpdateRequest(BaseModel):
    status: str
