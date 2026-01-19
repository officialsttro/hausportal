from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TicketBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)


class TicketCreate(TicketBase):
    unit_id: int


class TicketUpdateStatus(BaseModel):
    status: str = Field(min_length=1, max_length=20)


class TicketOut(BaseModel):
    id: int
    unit_id: int
    created_by: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
