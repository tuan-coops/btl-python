from sqlalchemy.orm import Session, joinedload

from app.models.order import Order
from app.models.user import User


class AdminOrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_orders(
        self,
        *,
        status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Order], int]:
        query = (
            self.db.query(Order)
            .options(joinedload(Order.items), joinedload(Order.user).joinedload(User.role))
        )
        if status:
            query = query.filter(Order.status == status)
        total = query.count()
        items = (
            query.order_by(Order.created_at.desc(), Order.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def get_by_id(self, order_id: int) -> Order | None:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items), joinedload(Order.user).joinedload(User.role))
            .filter(Order.id == order_id)
            .first()
        )
