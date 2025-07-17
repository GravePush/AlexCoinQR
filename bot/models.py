from database import Base
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column


class InviterModel(Base):
    __tablename__ = "inviters"
    __table_args__ = {"extend_existing": True}
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, nullable=False)
    ref_code: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc)
    )
    expire_time: Mapped[int] = mapped_column(Integer, default=30)
    click_count: Mapped[int] = mapped_column(Integer)
