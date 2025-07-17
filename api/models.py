from database import Base
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class VisitorModel(Base):
    __tablename__ = "visitors"
    __table_args__ = {"extend_existing": True}
    id: Mapped[int] = mapped_column(primary_key=True)
    ref_code: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    telegram_id: Mapped[str] = mapped_column(Integer, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc)
    )
    inviter_id: Mapped[int] = mapped_column(Integer, ForeignKey("inviters.id"))
