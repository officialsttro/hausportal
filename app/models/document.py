from datetime import datetime
from sqlalchemy import ForeignKey, String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)

    tenant_id: Mapped[int] = mapped_column(index=True)

    scope: Mapped[str] = mapped_column(String(20), index=True)
    property_id: Mapped[int | None] = mapped_column(
        ForeignKey("properties.id"), nullable=True, index=True
    )
    unit_id: Mapped[int | None] = mapped_column(
        ForeignKey("units.id"), nullable=True, index=True
    )

    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True
    )

    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer)

    # 🔑 DAS ist der Schlüssel in MinIO / S3
    object_key: Mapped[str] = mapped_column(String(1024), index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
