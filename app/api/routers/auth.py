from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import verify_password
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_exp_minutes() -> int:
    # Robust: falls dein Settings-Objekt das Feld (noch) nicht hat,
    # nehmen wir 60 Minuten als Default.
    val = getattr(settings, "access_token_exp_minutes", 60)
    try:
        return int(val)
    except Exception:
        return 60


@router.post("/login")
def login(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email")
    password = payload.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="email and password required")

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=_token_exp_minutes())

    token = jwt.encode(
        {"sub": str(user.id), "iat": int(now.timestamp()), "exp": int(exp.timestamp())},
        settings.jwt_secret,
        algorithm="HS256",
    )

    return {"access_token": token, "token_type": "bearer"}
