from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.tickets import TicketCreate, TicketOut, TicketUpdateStatus

router = APIRouter(prefix="/tickets", tags=["tickets"])

ALLOWED_STATUSES = {"OPEN", "IN_PROGRESS", "DONE"}


@router.get("", response_model=List[TicketOut])
def list_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[str] = Query(default=None),
    unit_id: Optional[int] = Query(default=None),
    q: Optional[str] = Query(default=None, description="search in title/description"),
):
    stmt = select(Ticket).where(Ticket.tenant_id == current_user.tenant_id)

    if status:
        stmt = stmt.where(Ticket.status == status)

    if unit_id:
        stmt = stmt.where(Ticket.unit_id == unit_id)

    if q:
        like = f"%{q}%"
        stmt = stmt.where((Ticket.title.ilike(like)) | (Ticket.description.ilike(like)))

    stmt = stmt.order_by(Ticket.id.desc())

    return list(db.execute(stmt).scalars().all())


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket or ticket.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("", response_model=TicketOut)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = Ticket(
        tenant_id=current_user.tenant_id,
        unit_id=payload.unit_id,
        created_by=current_user.id,
        title=payload.title,
        description=payload.description,
        status="OPEN",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.patch("/{ticket_id}", response_model=TicketOut)
def update_ticket_status(
    ticket_id: int,
    payload: TicketUpdateStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")

    ticket = db.get(Ticket, ticket_id)
    if not ticket or ticket.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = payload.status
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket
