from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin, get_db
from app.models.document import Document
from app.models.user import User
from app.services.documents import (
    create_document_and_upload,
    delete_document_and_object,
    get_document_download_url,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
def list_documents(
    scope: str | None = None,
    property_id: int | None = None,
    unit_id: int | None = None,
    published_only: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # MVP: Admin sieht alles im Tenant. (Resident-Filter später sauber.)
    q = db.query(Document).filter(Document.tenant_id == user.tenant_id)

    if scope:
        q = q.filter(Document.scope == scope.upper())
    if property_id:
        q = q.filter(Document.property_id == property_id)
    if unit_id:
        q = q.filter(Document.unit_id == unit_id)

    if published_only:
        q = q.filter(Document.published_at.isnot(None))

    return q.order_by(Document.created_at.desc()).all()


@router.post("", dependencies=[Depends(require_admin)])
async def upload_document(
    scope: str = Form(...),
    property_id: int | None = Form(None),
    unit_id: int | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        doc = create_document_and_upload(
            db,
            tenant_id=user.tenant_id,
            uploaded_by=user.id,
            scope=scope,
            property_id=property_id,
            unit_id=unit_id,
            filename=file.filename or "upload.bin",
            content_type=file.content_type or "application/octet-stream",
            data=data,
        )
        # Upload ist erstmal Entwurf (published_at bleibt NULL)
        return doc
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{document_id}/publish", dependencies=[Depends(require_admin)])
def publish_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    doc = db.get(Document, document_id)
    if not doc or doc.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.published_at is not None:
        # idempotent: bereits published
        return doc

    doc.published_at = datetime.utcnow()
    doc.published_by = user.id

    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    doc = db.get(Document, document_id)
    if not doc or doc.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Document not found")

    # MVP: Zugriffskontrolle für Residents kommt als nächster Schritt
    url = get_document_download_url(doc)
    return {"url": url}


@router.delete("/{document_id}", dependencies=[Depends(require_admin)])
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    delete_document_and_object(db, doc)
    return {"status": "deleted"}
