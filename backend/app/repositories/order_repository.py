from sqlalchemy.orm import Query, Session, joinedload

from app.models.order import Order


class OrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_user_orders(self, user_id: int, page: int, page_size: int) -> tuple[list[Order], int]:
        query: Query = (
            self.db.query(Order)
            .options(joinedload(Order.items))
            .filter(Order.user_id == user_id)
        )
        total = query.count()
        items = (
            query.order_by(Order.created_at.desc(), Order.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def get_user_order_by_id(self, user_id: int, order_id: int) -> Order | None:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items))
            .filter(Order.user_id == user_id, Order.id == order_id)
            .first()
        )

    def order_code_exists(self, order_code: str) -> bool:
        return self.db.query(Order.id).filter(Order.order_code == order_code).first() is not None
