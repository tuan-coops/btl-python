from sqlalchemy.orm import Session, joinedload

from app.models.category import Category
from app.models.product import Product


class SellerProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_products(
        self,
        *,
        category_id: int | None,
        pet_type: str | None,
        brand: str | None,
        is_active: bool | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Product], int]:
        query = self.db.query(Product).options(joinedload(Product.category), joinedload(Product.images))
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        if pet_type:
            query = query.filter(Product.pet_type == pet_type)
        if brand:
            query = query.filter(Product.brand.ilike(brand.strip()))
        if is_active is not None:
            query = query.filter(Product.is_active.is_(is_active))
        total = query.count()
        items = (
            query.order_by(Product.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def get_by_id(self, product_id: int) -> Product | None:
        return (
            self.db.query(Product)
            .options(joinedload(Product.category), joinedload(Product.images))
            .filter(Product.id == product_id)
            .first()
        )

    def get_by_slug(self, slug: str) -> Product | None:
        return self.db.query(Product).filter(Product.slug == slug).first()

    def get_by_sku(self, sku: str) -> Product | None:
        return self.db.query(Product).filter(Product.sku == sku).first()

    def get_category(self, category_id: int) -> Category | None:
        return self.db.query(Category).filter(Category.id == category_id).first()
