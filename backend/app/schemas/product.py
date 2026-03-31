from decimal import Decimal

from pydantic import BaseModel


class ProductImageResponse(BaseModel):
    id: int
    image_url: str
    alt_text: str | None
    is_primary: bool
    sort_order: int


class ProductListItemResponse(BaseModel):
    id: int
    name: str
    slug: str
    price: Decimal
    stock_quantity: int
    brand: str | None
    pet_type: str
    category: str
    primary_image: str | None


class ProductListResponse(BaseModel):
    items: list[ProductListItemResponse]
    total: int
    page: int
    page_size: int


class ProductDetailResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    price: Decimal
    stock_quantity: int
    brand: str | None
    pet_type: str
    category: str
    images: list[ProductImageResponse]
