from datetime import datetime
from pydantic import BaseModel


class InviteCreateRequest(BaseModel):
    email: str
    role: str = "RESIDENT"
    language: str = "de"
    expires_hours: int = 48


class InviteCreateResponse(BaseModel):
    id: int
    email: str
    expires_at: datetime
    token: str  # nur für DEV/Test (später per Email)


class InviteAcceptRequest(BaseModel):
    token: str
    password: str


class InviteAcceptResponse(BaseModel):
    user_id: int
    email: str
