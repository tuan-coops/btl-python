from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HealthCheckLog(Base):
    __tablename__ = "health_check_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="ok", nullable=False)
