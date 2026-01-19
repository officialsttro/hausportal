from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)

    name: Mapped[str] = mapped_column(String(200))
    street: Mapped[str] = mapped_column(String(200))
    postal_code: Mapped[str] = mapped_column(String(20))
    city: Mapped[str] = mapped_column(String(120))
