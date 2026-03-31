from sqlalchemy.orm import Session, joinedload

from app.models.user import User


class AdminUserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_users(
        self,
        *,
        role: str | None,
        is_active: bool | None,
        page: int,
        page_size: int,
    ) -> tuple[list[User], int]:
        query = self.db.query(User).options(joinedload(User.role))
        if role:
            query = query.join(User.role).filter_by(name=role)
        if is_active is not None:
            query = query.filter(User.is_active.is_(is_active))
        total = query.count()
        items = (
            query.order_by(User.created_at.desc(), User.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total
