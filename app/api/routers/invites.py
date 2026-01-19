from datetime import datetime, timedelta, timezone
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.invite import Invite
from app.models.user import User
from app.core.security import hash_password

router = APIRouter(prefix="/invites", tags=["invites"])


@router.post("")
def create_invite(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")

    email = payload.get("email")
    role = payload.get("role")
    language = payload.get("language", "de")
    expires_hours = payload.get("expires_hours", 48)

    if not email or not role:
        raise HTTPException(status_code=400, detail="email and role required")

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=int(expires_hours))

    invite = Invite(
        tenant_id=user.tenant_id,
        email=email,
        role=role,
        language=language,
        token=token,
        expires_at=expires_at,
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)

    return {
        "id": invite.id,
        "email": invite.email,
        "expires_at": invite.expires_at,
        "token": invite.token,
    }


@router.post("/accept")
def accept_invite(payload: dict, db: Session = Depends(get_db)):
    token = payload.get("token")
    password = payload.get("password")

    if not token or not password:
        raise HTTPException(status_code=400, detail="token and password required")

    invite = db.query(Invite).filter(Invite.token == token).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    now = datetime.now(timezone.utc)
    if invite.expires_at < now:
        raise HTTPException(status_code=400, detail="Invite expired")

    # check if user already exists
    existing = db.query(User).filter(User.email == invite.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        tenant_id=invite.tenant_id,
        email=invite.email,
        role=invite.role,
        language=invite.language,
        password_hash=hash_password(password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"user_id": new_user.id, "email": new_user.email}
