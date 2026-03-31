from decimal import Decimal

from sqlalchemy.orm import Query, Session, joinedload

from app.models.category import Category
from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_active_query(self) -> Query:
        return (
            self.db.query(Product)
            .options(joinedload(Product.category), joinedload(Product.images))
            .filter(Product.is_active.is_(True))
        )

    def list_products(
        self,
        *,
        search: str | None,
        category_id: int | None,
        pet_type: str | None,
        brand: str | None,
        price_min: Decimal | None,
        price_max: Decimal | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Product], int]:
        query = self._base_active_query()

        if search:
            query = query.filter(Product.name.ilike(f"%{search.strip()}%"))
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        if pet_type:
            query = query.filter(Product.pet_type == pet_type)
        if brand:
            query = query.filter(Product.brand.ilike(brand.strip()))
        if price_min is not None:
            query = query.filter(Product.price >= price_min)
        if price_max is not None:
            query = query.filter(Product.price <= price_max)

        total = query.count()
        items = (
            query.order_by(Product.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def get_product_by_id(self, product_id: int) -> Product | None:
        return self._base_active_query().filter(Product.id == product_id).first()
