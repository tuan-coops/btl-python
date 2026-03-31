from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_categories(self) -> list[Category]:
        return (
            self.db.query(Category)
            .filter(Category.is_active.is_(True))
            .order_by(Category.name.asc())
            .all()
        )
