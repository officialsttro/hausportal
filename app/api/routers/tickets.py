from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_admin, get_db
from app.models.ticket import Ticket
from app.models.unit import Unit
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketOut

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _apply_owner_filter(q, user: User):
    return q.filter(Ticket.created_by == user.id)


def _is_ticket_owned_by_user(ticket: Ticket, user: User) -> bool:
    return ticket.created_by == user.id


def _with_creator(q):
    return q.options(joinedload(Ticket.creator))


@router.get("", response_model=list[TicketOut])
def list_tickets(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = _with_creator(db.query(Ticket)).filter(Ticket.tenant_id == user.tenant_id)

    if user.role != "ADMIN":
        q = _apply_owner_filter(q, user)

    tickets = q.all()

    out: list[TicketOut] = []
    for t in tickets:
        d = TicketOut.model_validate(t).model_dump()
        d["created_by_user"] = t.creator
        out.append(TicketOut.model_validate(d))
    return out


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ticket = _with_creator(db.query(Ticket)).filter(Ticket.id == ticket_id).first()
    if not ticket or ticket.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if user.role != "ADMIN" and not _is_ticket_owned_by_user(ticket, user):
        raise HTTPException(status_code=403, detail="Forbidden")

    d = TicketOut.model_validate(ticket).model_dump()
    d["created_by_user"] = ticket.creator
    return TicketOut.model_validate(d)


@router.post("", response_model=TicketOut)
def create_ticket(
    data: TicketCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    unit = db.get(Unit, data.unit_id)
    if not unit or unit.tenant_id != user.tenant_id:
        raise HTTPException(status_code=400, detail="Invalid unit_id")

    ticket = Ticket(
        tenant_id=user.tenant_id,
        unit_id=data.unit_id,
        title=data.title,
        description=data.description,
        status="OPEN",
        created_by=user.id,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    ticket = _with_creator(db.query(Ticket)).filter(Ticket.id == ticket.id).first()
    d = TicketOut.model_validate(ticket).model_dump()
    d["created_by_user"] = ticket.creator if ticket else None
    return TicketOut.model_validate(d)


@router.patch("/{ticket_id}", response_model=TicketOut, dependencies=[Depends(require_admin)])
def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    db: Session = Depends(get_db),
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(ticket, k, v)

    db.commit()
    db.refresh(ticket)

    ticket = _with_creator(db.query(Ticket)).filter(Ticket.id == ticket_id).first()
    d = TicketOut.model_validate(ticket).model_dump()
    d["created_by_user"] = ticket.creator if ticket else None
    return TicketOut.model_validate(d)


@router.delete("/{ticket_id}", dependencies=[Depends(require_admin)])
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()
    return {"status": "deleted", "id": ticket_id}
