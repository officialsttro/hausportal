from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.api.deps_db import get_db
from app.models.property import Property
from app.models.unit import Unit
from app.models.user import User
from app.schemas.unit import UnitCreateRequest, UnitResponse

router = APIRouter()


@router.get("/by-property/{property_id}", response_model=list[UnitResponse])
def list_units_for_property(
    property_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # check property belongs to tenant
    prop = db.scalar(select(Property).where(Property.id == property_id, Property.tenant_id == user.tenant_id))
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    units = db.scalars(
        select(Unit).where(Unit.property_id == property_id, Unit.tenant_id == user.tenant_id).order_by(Unit.id)
    ).all()
    return units


@router.post("/by-property/{property_id}", response_model=UnitResponse)
def create_unit_for_property(
    property_id: int,
    payload: UnitCreateRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    prop = db.scalar(select(Property).where(Property.id == property_id, Property.tenant_id == admin.tenant_id))
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    unit = Unit(
        tenant_id=admin.tenant_id,
        property_id=property_id,
        label=payload.label,
    )
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit
