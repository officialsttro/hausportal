from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.api.deps_db import get_db
from app.models.user import User
from app.models.unit import Unit
from app.models.user_unit import UserUnit
from app.schemas.user_unit import UserUnitAssignRequest

router = APIRouter()


@router.post("/assign")
def assign_user_to_unit(
    payload: UserUnitAssignRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    # user must be in same tenant
    user = db.scalar(select(User).where(User.id == payload.user_id, User.tenant_id == admin.tenant_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # unit must be in same tenant
    unit = db.scalar(select(Unit).where(Unit.id == payload.unit_id, Unit.tenant_id == admin.tenant_id))
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    existing = db.scalar(select(UserUnit).where(UserUnit.user_id == payload.user_id, UserUnit.unit_id == payload.unit_id))
    if existing:
        return {"status": "already_assigned"}

    link = UserUnit(user_id=payload.user_id, unit_id=payload.unit_id, relation_type=payload.relation_type)
    db.add(link)
    db.commit()
    return {"status": "assigned"}
