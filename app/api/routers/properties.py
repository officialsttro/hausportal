from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.property import Property
from app.models.user import User

router = APIRouter(prefix="/properties", tags=["properties"])


@router.get("")
def list_properties(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(Property)
        .filter(Property.tenant_id == user.tenant_id)
        .order_by(Property.id.asc())
        .all()
    )


@router.post("")
def create_property(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")

    name = payload.get("name")
    street = payload.get("street")
    postal_code = payload.get("postal_code")
    city = payload.get("city")

    if not name or not street or not postal_code or not city:
        raise HTTPException(status_code=400, detail="name, street, postal_code, city required")

    prop = Property(
        tenant_id=user.tenant_id,
        name=name,
        street=street,
        postal_code=postal_code,
        city=city,
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return {
        "id": prop.id,
        "name": prop.name,
        "street": prop.street,
        "postal_code": prop.postal_code,
        "city": prop.city,
    }
