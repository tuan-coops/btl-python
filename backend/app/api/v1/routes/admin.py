from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import (
    AdminCategoryCreateRequest,
    AdminCategoryListResponse,
    AdminCategoryResponse,
    AdminCategoryUpdateRequest,
    AdminDashboardResponse,
    AdminOrderDetailResponse,
    AdminOrderListResponse,
    AdminOrderStatusUpdateRequest,
    AdminProductCreateRequest,
    AdminProductListResponse,
    AdminProductResponse,
    AdminProductUpdateRequest,
    AdminUserListResponse,
)
from app.schemas.article import (
    AdminArticleCreateRequest,
    AdminArticleListResponse,
    AdminArticleResponse,
    AdminArticleUpdateRequest,
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=AdminDashboardResponse)
def get_dashboard(
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminDashboardResponse:
    return AdminService(db).get_dashboard_stats()


@router.post("/categories", response_model=AdminCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: AdminCategoryCreateRequest,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminCategoryResponse:
    return AdminService(db).create_category(payload)


@router.get("/categories", response_model=AdminCategoryListResponse)
def list_categories(
    is_active: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminCategoryListResponse:
    return AdminService(db).list_categories(is_active=is_active, page=page, page_size=page_size)


@router.get("/categories/{category_id}", response_model=AdminCategoryResponse)
def get_category(
    category_id: int,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminCategoryResponse:
    return AdminService(db).get_category(category_id)


@router.patch("/categories/{category_id}", response_model=AdminCategoryResponse)
def update_category(
    category_id: int,
    payload: AdminCategoryUpdateRequest,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminCategoryResponse:
    return AdminService(db).update_category(category_id, payload)


@router.delete("/categories/{category_id}", response_model=AdminCategoryResponse)
def delete_category(
    category_id: int,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminCategoryResponse:
    return AdminService(db).delete_category(category_id)


@router.post("/products", response_model=AdminProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: AdminProductCreateRequest,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminProductResponse:
    return AdminService(db).create_product(payload)


@router.get("/products", response_model=AdminProductListResponse)
def list_products(
    category_id: int | None = Query(default=None),
    pet_type: str | None = Query(default=None),
    brand: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminProductListResponse:
    return AdminService(db).list_products(
        category_id=category_id,
        pet_type=pet_type,
        brand=brand,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )


@router.get("/products/{product_id}", response_model=AdminProductResponse)
def get_product(
    product_id: int,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminProductResponse:
    return AdminService(db).get_product(product_id)


@router.patch("/products/{product_id}", response_model=AdminProductResponse)
def update_product(
    product_id: int,
    payload: AdminProductUpdateRequest,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminProductResponse:
    return AdminService(db).update_product(product_id, payload)


@router.delete("/products/{product_id}", response_model=AdminProductResponse)
def delete_product(
    product_id: int,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminProductResponse:
    return AdminService(db).delete_product(product_id)


@router.get("/users", response_model=AdminUserListResponse)
def list_users(
    role: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminUserListResponse:
    return AdminService(db).list_users(role=role, is_active=is_active, page=page, page_size=page_size)


@router.get("/orders", response_model=AdminOrderListResponse)
def list_orders(
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminOrderListResponse:
    return AdminService(db).list_orders(status=status, page=page, page_size=page_size)


@router.get("/orders/{order_id}", response_model=AdminOrderDetailResponse)
def get_order(
    order_id: int,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminOrderDetailResponse:
    return AdminService(db).get_order(order_id)


@router.patch("/orders/{order_id}/status", response_model=AdminOrderDetailResponse)
def update_order_status(
    order_id: int,
    payload: AdminOrderStatusUpdateRequest,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminOrderDetailResponse:
    return AdminService(db).update_order_status(order_id, payload)


@router.post("/articles", response_model=AdminArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(
    payload: AdminArticleCreateRequest,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminArticleResponse:
    return AdminService(db).create_article(payload)


@router.get("/articles", response_model=AdminArticleListResponse)
def list_articles(
    is_published: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminArticleListResponse:
    return AdminService(db).list_articles(is_published=is_published, page=page, page_size=page_size)


@router.get("/articles/{article_id}", response_model=AdminArticleResponse)
def get_article(
    article_id: int,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminArticleResponse:
    return AdminService(db).get_article(article_id)


@router.patch("/articles/{article_id}", response_model=AdminArticleResponse)
def update_article(
    article_id: int,
    payload: AdminArticleUpdateRequest,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminArticleResponse:
    return AdminService(db).update_article(article_id, payload)


@router.delete("/articles/{article_id}", response_model=AdminArticleResponse)
def delete_article(
    article_id: int,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> AdminArticleResponse:
    return AdminService(db).delete_article(article_id)
