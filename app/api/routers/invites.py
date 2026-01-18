from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.api.deps_db import get_db
from app.core.security import hash_password
from app.models.invite import Invite
from app.models.user import User
from app.schemas.invite import (
    InviteCreateRequest,
    InviteCreateResponse,
    InviteAcceptRequest,
    InviteAcceptResponse,
)

router = APIRouter()


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@router.post("", response_model=InviteCreateResponse)
def create_invite(
    payload: InviteCreateRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> InviteCreateResponse:
    raw_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=payload.expires_hours)

    inv = Invite(
        tenant_id=admin.tenant_id,
        email=payload.email,
        role=payload.role,
        language=payload.language,
        token_hash=hash_token(raw_token),
        expires_at=expires_at,
        used_at=None,
        created_by=admin.id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    return InviteCreateResponse(
        id=inv.id,
        email=inv.email,
        expires_at=inv.expires_at,
        token=raw_token,
    )


@router.post("/accept", response_model=InviteAcceptResponse)
def accept_invite(payload: InviteAcceptRequest, db: Session = Depends(get_db)) -> InviteAcceptResponse:
    token_h = hash_token(payload.token)

    inv = db.scalar(select(Invite).where(Invite.token_hash == token_h))
    if not inv:
        raise HTTPException(status_code=400, detail="Invalid invite token")

    now = datetime.now(timezone.utc)

    if inv.used_at is not None:
        raise HTTPException(status_code=400, detail="Invite already used")

    # expires_at might be naive depending on DB; normalize check defensively
    expires_at = inv.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        raise HTTPException(status_code=400, detail="Invite expired")

    # Email already registered in this tenant?
    existing = db.scalar(
        select(User).where(User.tenant_id == inv.tenant_id, User.email == inv.email)
    )
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        tenant_id=inv.tenant_id,
        email=inv.email,
        password_hash=hash_password(payload.password),
        role=inv.role,
        language=inv.language,
        status="active",
    )
    db.add(user)

    inv.used_at = now

    db.commit()
    db.refresh(user)

    return InviteAcceptResponse(user_id=user.id, email=user.email)
