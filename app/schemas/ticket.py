from datetime import datetime
from pydantic import BaseModel


class TicketCreate(BaseModel):
    unit_id: int
    title: str
    description: str


class TicketOut(BaseModel):
    id: int
    tenant_id: int
    unit_id: int
    created_by: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TicketStatusUpdate(BaseModel):
    status: str
