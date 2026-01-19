from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


DocumentScope = Literal["PROPERTY", "UNIT"]


class DocumentOut(BaseModel):
    id: int
    scope: str
    property_id: Optional[int] = None
    unit_id: Optional[int] = None
    uploaded_by: int
    filename: str
    content_type: str
    size_bytes: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentPresignOut(BaseModel):
    id: int
    url: str


class DocumentListQuery(BaseModel):
    scope: Optional[DocumentScope] = None
    property_id: Optional[int] = None
    unit_id: Optional[int] = None
