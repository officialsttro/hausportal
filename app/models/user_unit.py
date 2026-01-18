from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserUnit(Base):
    __tablename__ = "user_units"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), primary_key=True)

    # "TENANT" oder "OWNER" (Mieter/Eigentümer)
    relation_type: Mapped[str] = mapped_column(String(20), nullable=False, default="TENANT")
