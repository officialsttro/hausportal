from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id"), index=True)

    label: Mapped[str] = mapped_column(String(80))
