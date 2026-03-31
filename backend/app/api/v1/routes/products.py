from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductDetailResponse, ProductListResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
def list_products(
    search: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    pet_type: str | None = Query(default=None),
    brand: str | None = Query(default=None),
    price_min: Decimal | None = Query(default=None, ge=0),
    price_max: Decimal | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ProductListResponse:
    service = ProductService(ProductRepository(db))
    return service.list_products(
        search=search,
        category_id=category_id,
        pet_type=pet_type,
        brand=brand,
        price_min=price_min,
        price_max=price_max,
        page=page,
        page_size=page_size,
    )


@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductDetailResponse:
    service = ProductService(ProductRepository(db))
    product = service.get_product_detail(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product
