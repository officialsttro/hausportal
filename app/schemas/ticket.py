from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TicketCreate(BaseModel):
    unit_id: int
    title: str
    description: str


class TicketUpdate(BaseModel):
    # Admin darf aktuell nur Status ändern (kannst du später erweitern)
    status: Optional[str] = None


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: str
    language: str
    status: str


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    unit_id: int
    created_by: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    # neu: User-Infos für Frontend
    created_by_user: Optional[UserPublic] = None
