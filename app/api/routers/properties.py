from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.api.deps_db import get_db
from app.models.property import Property
from app.models.user import User
from app.schemas.property import PropertyCreateRequest, PropertyResponse

router = APIRouter()


@router.get("", response_model=list[PropertyResponse])
def list_properties(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.scalars(select(Property).where(Property.tenant_id == user.tenant_id).order_by(Property.id)).all()
    return rows


@router.post("", response_model=PropertyResponse)
def create_property(
    payload: PropertyCreateRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    prop = Property(
        tenant_id=admin.tenant_id,
        name=payload.name,
        street=payload.street,
        postal_code=payload.postal_code,
        city=payload.city,
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prop = db.scalar(select(Property).where(Property.id == property_id, Property.tenant_id == user.tenant_id))
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop
