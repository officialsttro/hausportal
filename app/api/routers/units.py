from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.unit import Unit
from app.models.user import User

router = APIRouter(prefix="/units", tags=["units"])


@router.get("")
def list_units(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(Unit)
        .filter(Unit.tenant_id == user.tenant_id)
        .order_by(Unit.label)
        .all()
    )
