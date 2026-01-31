from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Relationship zum Ersteller (User)
    creator = relationship("User", foreign_keys=[created_by])

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(2000))
    status: Mapped[str] = mapped_column(String(20), default="OPEN")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.utcnow, onupdate=datetime.utcnow
    )
