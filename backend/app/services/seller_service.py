from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.article import Article
from app.models.category import Category
from app.models.enums import OrderStatus, PetType
from app.models.order import Order
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.user import User
from app.repositories.article_repository import ArticleRepository
from app.repositories.seller_category_repository import SellerCategoryRepository
from app.repositories.seller_order_repository import SellerOrderRepository
from app.repositories.seller_product_repository import SellerProductRepository
from app.repositories.seller_user_repository import SellerUserRepository
from app.schemas.seller import (
    SellerCategoryCreateRequest,
    SellerCategoryListResponse,
    SellerCategoryResponse,
    SellerCategoryUpdateRequest,
    SellerDashboardResponse,
    SellerOrderDetailResponse,
    SellerOrderListResponse,
    SellerOrderStatusUpdateRequest,
    SellerOrderSummaryResponse,
    SellerOrderUserResponse,
    SellerProductCreateRequest,
    SellerProductImageResponse,
    SellerProductListResponse,
    SellerProductResponse,
    SellerProductUpdateRequest,
    SellerUserListItemResponse,
    SellerUserListResponse,
)
from app.schemas.article import (
    SellerArticleCreateRequest,
    SellerArticleListResponse,
    SellerArticleResponse,
    SellerArticleUpdateRequest,
)
from app.schemas.order import OrderItemResponse, ShippingSnapshotResponse

ALLOWED_ORDER_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.SHIPPING, OrderStatus.CANCELLED},
    OrderStatus.SHIPPING: {OrderStatus.COMPLETED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
}


class SellerService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.logger = get_logger(__name__)
        self.category_repository = SellerCategoryRepository(db)
        self.product_repository = SellerProductRepository(db)
        self.user_repository = SellerUserRepository(db)
        self.order_repository = SellerOrderRepository(db)
        self.article_repository = ArticleRepository(db)

    def _serialize_category(self, category: Category) -> SellerCategoryResponse:
        return SellerCategoryResponse.model_validate(category)

    def _serialize_product(self, product: Product) -> SellerProductResponse:
        return SellerProductResponse(
            id=product.id,
            name=product.name,
            slug=product.slug,
            sku=product.sku,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            brand=product.brand,
            pet_type=product.pet_type.value,
            category_id=product.category_id,
            category_name=product.category.name,
            is_active=product.is_active,
            images=[
                SellerProductImageResponse(
                    id=image.id,
                    image_url=image.image_url,
                    alt_text=image.alt_text,
                    is_primary=image.is_primary,
                    sort_order=image.sort_order,
                )
                for image in product.images
            ],
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

    def _serialize_user(self, user: User) -> SellerUserListItemResponse:
        return SellerUserListItemResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            is_active=user.is_active,
            role=user.role.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def _serialize_order(self, order: Order) -> SellerOrderSummaryResponse:
        return SellerOrderSummaryResponse(
            id=order.id,
            order_code=order.order_code,
            status=order.status.value,
            payment_method=order.payment_method.value,
            subtotal=order.subtotal,
            shipping_fee=order.shipping_fee,
            discount_amount=order.discount_amount,
            total_amount=order.total_amount,
            created_at=order.created_at,
            user=SellerOrderUserResponse(
                id=order.user.id,
                full_name=order.user.full_name,
                email=order.user.email,
                phone=order.user.phone,
                role=order.user.role.name,
            ),
            items=[
                OrderItemResponse(
                    id=item.id,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    unit_price=item.unit_price,
                    quantity=item.quantity,
                    line_total=item.line_total,
                )
                for item in order.items
            ],
        )

    def list_categories(self, *, is_active: bool | None, page: int, page_size: int) -> SellerCategoryListResponse:
        categories, total = self.category_repository.list_categories(
            is_active=is_active,
            page=page,
            page_size=page_size,
        )
        return SellerCategoryListResponse(
            items=[self._serialize_category(category) for category in categories],
            total=total,
            page=page,
            page_size=page_size,
        )

    def create_category(self, payload: SellerCategoryCreateRequest) -> SellerCategoryResponse:
        if self.category_repository.get_by_name(payload.name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")
        if self.category_repository.get_by_slug(payload.slug):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category slug already exists")
        category = Category(
            name=payload.name,
            slug=payload.slug,
            description=payload.description,
            is_active=payload.is_active,
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return self._serialize_category(category)

    def get_category(self, category_id: int) -> SellerCategoryResponse:
        category = self.category_repository.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return self._serialize_category(category)

    def update_category(self, category_id: int, payload: SellerCategoryUpdateRequest) -> SellerCategoryResponse:
        category = self.category_repository.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        if payload.name and payload.name != category.name:
            existing = self.category_repository.get_by_name(payload.name)
            if existing and existing.id != category_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")
            category.name = payload.name
        if payload.slug and payload.slug != category.slug:
            existing = self.category_repository.get_by_slug(payload.slug)
            if existing and existing.id != category_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category slug already exists")
            category.slug = payload.slug
        if payload.description is not None:
            category.description = payload.description
        if payload.is_active is not None:
            category.is_active = payload.is_active
        self.db.commit()
        self.db.refresh(category)
        return self._serialize_category(category)

    def delete_category(self, category_id: int) -> SellerCategoryResponse:
        category = self.category_repository.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        category.is_active = False
        self.db.commit()
        self.db.refresh(category)
        return self._serialize_category(category)

    def _validate_category(self, category_id: int) -> Category:
        category = self.product_repository.get_category(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return category

    def _validate_pet_type(self, pet_type: str) -> PetType:
        try:
            return PetType(pet_type)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pet type") from exc

    def _apply_primary_image(self, product: Product, primary_image_url: str | None) -> None:
        if primary_image_url is None:
            return
        for image in product.images:
            image.is_primary = False
        existing = next((image for image in product.images if image.image_url == primary_image_url), None)
        if existing is not None:
            existing.is_primary = True
            existing.sort_order = 1
            return
        product.images.append(
            ProductImage(
                image_url=primary_image_url,
                alt_text=product.name,
                is_primary=True,
                sort_order=1,
            )
        )

    def list_products(
        self,
        *,
        category_id: int | None,
        pet_type: str | None,
        brand: str | None,
        is_active: bool | None,
        page: int,
        page_size: int,
    ) -> SellerProductListResponse:
        products, total = self.product_repository.list_products(
            category_id=category_id,
            pet_type=pet_type,
            brand=brand,
            is_active=is_active,
            page=page,
            page_size=page_size,
        )
        return SellerProductListResponse(
            items=[self._serialize_product(product) for product in products],
            total=total,
            page=page,
            page_size=page_size,
        )

    def create_product(self, payload: SellerProductCreateRequest) -> SellerProductResponse:
        self._validate_category(payload.category_id)
        if self.product_repository.get_by_slug(payload.slug):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product slug already exists")
        if self.product_repository.get_by_sku(payload.sku):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product SKU already exists")
        product = Product(
            category_id=payload.category_id,
            name=payload.name,
            slug=payload.slug,
            sku=payload.sku,
            description=payload.description,
            price=payload.price,
            stock_quantity=payload.stock_quantity,
            brand=payload.brand,
            pet_type=self._validate_pet_type(payload.pet_type),
            is_active=payload.is_active,
        )
        self._apply_primary_image(product, payload.primary_image_url)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        product = self.product_repository.get_by_id(product.id)
        return self._serialize_product(product)

    def get_product(self, product_id: int) -> SellerProductResponse:
        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return self._serialize_product(product)

    def update_product(self, product_id: int, payload: SellerProductUpdateRequest) -> SellerProductResponse:
        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if payload.category_id is not None:
            self._validate_category(payload.category_id)
            product.category_id = payload.category_id
        if payload.name is not None:
            product.name = payload.name
        if payload.slug is not None and payload.slug != product.slug:
            existing = self.product_repository.get_by_slug(payload.slug)
            if existing and existing.id != product_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product slug already exists")
            product.slug = payload.slug
        if payload.sku is not None and payload.sku != product.sku:
            existing = self.product_repository.get_by_sku(payload.sku)
            if existing and existing.id != product_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product SKU already exists")
            product.sku = payload.sku
        if payload.description is not None:
            product.description = payload.description
        if payload.price is not None:
            product.price = payload.price
        if payload.stock_quantity is not None:
            product.stock_quantity = payload.stock_quantity
        if payload.brand is not None:
            product.brand = payload.brand
        if payload.pet_type is not None:
            product.pet_type = self._validate_pet_type(payload.pet_type)
        if payload.is_active is not None:
            product.is_active = payload.is_active
        self._apply_primary_image(product, payload.primary_image_url)
        self.db.commit()
        self.db.refresh(product)
        product = self.product_repository.get_by_id(product.id)
        return self._serialize_product(product)

    def delete_product(self, product_id: int) -> SellerProductResponse:
        product = self.product_repository.get_by_id(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        product.is_active = False
        self.db.commit()
        self.db.refresh(product)
        product = self.product_repository.get_by_id(product.id)
        return self._serialize_product(product)

    def list_users(
        self,
        *,
        role: str | None,
        is_active: bool | None,
        page: int,
        page_size: int,
    ) -> SellerUserListResponse:
        users, total = self.user_repository.list_users(
            role=role,
            is_active=is_active,
            page=page,
            page_size=page_size,
        )
        return SellerUserListResponse(
            items=[self._serialize_user(user) for user in users],
            total=total,
            page=page,
            page_size=page_size,
        )

    def list_orders(self, *, status: str | None, page: int, page_size: int) -> SellerOrderListResponse:
        orders, total = self.order_repository.list_orders(status=status, page=page, page_size=page_size)
        return SellerOrderListResponse(
            items=[self._serialize_order(order) for order in orders],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_order(self, order_id: int) -> SellerOrderDetailResponse:
        order = self.order_repository.get_by_id(order_id)
        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        summary = self._serialize_order(order)
        return SellerOrderDetailResponse(
            **summary.model_dump(),
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

    def update_order_status(self, order_id: int, payload: SellerOrderStatusUpdateRequest) -> SellerOrderDetailResponse:
        order = self.order_repository.get_by_id(order_id)
        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        try:
            next_status = OrderStatus(payload.status)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order status") from exc
        if next_status not in ALLOWED_ORDER_TRANSITIONS[order.status]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order status transition")
        order.status = next_status
        self.db.commit()
        self.db.refresh(order)
        self.logger.info("Seller updated order status: order_id=%s status=%s", order.id, order.status.value)
        return self.get_order(order_id)

    def get_dashboard_stats(self) -> SellerDashboardResponse:
        now = datetime.now(UTC)
        month_start = datetime(now.year, now.month, 1, tzinfo=UTC)
        monthly_revenue = (
            self.db.query(func.coalesce(func.sum(Order.total_amount), 0))
            .filter(Order.status == OrderStatus.COMPLETED, Order.created_at >= month_start)
            .scalar()
        )
        return SellerDashboardResponse(
            total_users=self.db.query(func.count(User.id)).scalar() or 0,
            total_products=self.db.query(func.count(Product.id)).scalar() or 0,
            total_orders=self.db.query(func.count(Order.id)).scalar() or 0,
            pending_orders=self.db.query(func.count(Order.id)).filter(Order.status == OrderStatus.PENDING).scalar() or 0,
            low_stock_products=(
                self.db.query(func.count(Product.id))
                .filter(Product.stock_quantity <= settings.low_stock_threshold)
                .scalar()
                or 0
            ),
            monthly_revenue=monthly_revenue,
        )

    def list_articles(self, *, is_published: bool | None, page: int, page_size: int) -> SellerArticleListResponse:
        items, total = self.article_repository.list_all(
            is_published=is_published,
            page=page,
            page_size=page_size,
        )
        return SellerArticleListResponse(
            items=[SellerArticleResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def create_article(self, payload: SellerArticleCreateRequest) -> SellerArticleResponse:
        existing = self.article_repository.get_by_slug(payload.slug)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Article slug already exists")
        article = Article(
            title=payload.title,
            slug=payload.slug,
            summary=payload.summary,
            content=payload.content,
            is_published=payload.is_published,
            published_at=datetime.now(UTC) if payload.is_published else None,
        )
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return SellerArticleResponse.model_validate(article)

    def get_article(self, article_id: int) -> SellerArticleResponse:
        article = self.article_repository.get_by_id(article_id)
        if article is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        return SellerArticleResponse.model_validate(article)

    def update_article(self, article_id: int, payload: SellerArticleUpdateRequest) -> SellerArticleResponse:
        article = self.article_repository.get_by_id(article_id)
        if article is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        if payload.slug and payload.slug != article.slug:
            existing = self.article_repository.get_by_slug(payload.slug)
            if existing and existing.id != article_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Article slug already exists")
            article.slug = payload.slug
        if payload.title is not None:
            article.title = payload.title
        if payload.summary is not None:
            article.summary = payload.summary
        if payload.content is not None:
            article.content = payload.content
        if payload.is_published is not None:
            article.is_published = payload.is_published
            article.published_at = datetime.now(UTC) if payload.is_published else None
        self.db.commit()
        self.db.refresh(article)
        return SellerArticleResponse.model_validate(article)

    def delete_article(self, article_id: int) -> SellerArticleResponse:
        article = self.article_repository.get_by_id(article_id)
        if article is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        self.db.delete(article)
        self.db.commit()
        return SellerArticleResponse.model_validate(article)
