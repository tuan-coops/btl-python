from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.seller import (
    SellerCategoryCreateRequest,
    SellerCategoryListResponse,
    SellerCategoryResponse,
    SellerCategoryUpdateRequest,
    SellerDashboardResponse,
    SellerOrderDetailResponse,
    SellerOrderListResponse,
    SellerOrderStatusUpdateRequest,
    SellerProductCreateRequest,
    SellerProductListResponse,
    SellerProductResponse,
    SellerProductUpdateRequest,
    SellerUserListResponse,
)
from app.schemas.article import (
    SellerArticleCreateRequest,
    SellerArticleListResponse,
    SellerArticleResponse,
    SellerArticleUpdateRequest,
)
from app.services.seller_service import SellerService

router = APIRouter(prefix="/seller", tags=["seller"])


@router.get("/dashboard", response_model=SellerDashboardResponse)
def get_dashboard(
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerDashboardResponse:
    return SellerService(db).get_dashboard_stats()


@router.post("/categories", response_model=SellerCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: SellerCategoryCreateRequest,
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerCategoryResponse:
    return SellerService(db).create_category(payload)


@router.get("/categories", response_model=SellerCategoryListResponse)
def list_categories(
    is_active: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerCategoryListResponse:
    return SellerService(db).list_categories(is_active=is_active, page=page, page_size=page_size)


@router.get("/categories/{category_id}", response_model=SellerCategoryResponse)
def get_category(
    category_id: int,
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerCategoryResponse:
    return SellerService(db).get_category(category_id)


@router.patch("/categories/{category_id}", response_model=SellerCategoryResponse)
def update_category(
    category_id: int,
    payload: SellerCategoryUpdateRequest,
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerCategoryResponse:
    return SellerService(db).update_category(category_id, payload)


@router.delete("/categories/{category_id}", response_model=SellerCategoryResponse)
def delete_category(
    category_id: int,
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerCategoryResponse:
    return SellerService(db).delete_category(category_id)


@router.post("/products", response_model=SellerProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: SellerProductCreateRequest,
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerProductResponse:
    return SellerService(db).create_product(payload)


@router.get("/products", response_model=SellerProductListResponse)
def list_products(
    category_id: int | None = Query(default=None),
    pet_type: str | None = Query(default=None),
    brand: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerProductListResponse:
    return SellerService(db).list_products(
        category_id=category_id,
        pet_type=pet_type,
        brand=brand,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )


@router.get("/products/{product_id}", response_model=SellerProductResponse)
def get_product(
    product_id: int,
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerProductResponse:
    return SellerService(db).get_product(product_id)


@router.patch("/products/{product_id}", response_model=SellerProductResponse)
def update_product(
    product_id: int,
    payload: SellerProductUpdateRequest,
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerProductResponse:
    return SellerService(db).update_product(product_id, payload)


@router.delete("/products/{product_id}", response_model=SellerProductResponse)
def delete_product(
    product_id: int,
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerProductResponse:
    return SellerService(db).delete_product(product_id)


@router.get("/users", response_model=SellerUserListResponse)
def list_users(
    role: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerUserListResponse:
    return SellerService(db).list_users(role=role, is_active=is_active, page=page, page_size=page_size)


@router.get("/orders", response_model=SellerOrderListResponse)
def list_orders(
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerOrderListResponse:
    return SellerService(db).list_orders(status=status, page=page, page_size=page_size)


@router.get("/orders/{order_id}", response_model=SellerOrderDetailResponse)
def get_order(
    order_id: int,
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerOrderDetailResponse:
    return SellerService(db).get_order(order_id)


@router.patch("/orders/{order_id}/status", response_model=SellerOrderDetailResponse)
def update_order_status(
    order_id: int,
    payload: SellerOrderStatusUpdateRequest,
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerOrderDetailResponse:
    return SellerService(db).update_order_status(order_id, payload)


@router.post("/articles", response_model=SellerArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(
    payload: SellerArticleCreateRequest,
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerArticleResponse:
    return SellerService(db).create_article(payload)


@router.get("/articles", response_model=SellerArticleListResponse)
def list_articles(
    is_published: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerArticleListResponse:
    return SellerService(db).list_articles(is_published=is_published, page=page, page_size=page_size)


@router.get("/articles/{article_id}", response_model=SellerArticleResponse)
def get_article(
    article_id: int,
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerArticleResponse:
    return SellerService(db).get_article(article_id)


@router.patch("/articles/{article_id}", response_model=SellerArticleResponse)
def update_article(
    article_id: int,
    payload: SellerArticleUpdateRequest,
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerArticleResponse:
    return SellerService(db).update_article(article_id, payload)


@router.delete("/articles/{article_id}", response_model=SellerArticleResponse)
def delete_article(
    article_id: int,
    _: User = Depends(require_role("seller")),
    db: Session = Depends(get_db),
) -> SellerArticleResponse:
    return SellerService(db).delete_article(article_id)
