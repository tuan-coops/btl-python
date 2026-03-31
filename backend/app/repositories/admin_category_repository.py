from sqlalchemy.orm import Session

from app.models.category import Category


class AdminCategoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_categories(self, *, is_active: bool | None, page: int, page_size: int) -> tuple[list[Category], int]:
        query = self.db.query(Category)
        if is_active is not None:
            query = query.filter(Category.is_active.is_(is_active))
        total = query.count()
        items = (
            query.order_by(Category.name.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def get_by_id(self, category_id: int) -> Category | None:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_by_name(self, name: str) -> Category | None:
        return self.db.query(Category).filter(Category.name == name).first()

    def get_by_slug(self, slug: str) -> Category | None:
        return self.db.query(Category).filter(Category.slug == slug).first()
