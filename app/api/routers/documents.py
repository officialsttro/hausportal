from __future__ import annotations

from datetime import datetime
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.integrations.s3 import ensure_bucket_exists, get_s3_client, put_object
from app.models.document import Document
from app.models.user import User

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("")
def upload_document(
    scope: str = Form(...),
    property_id: int | None = Form(None),
    unit_id: int | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Basic Validation
    if scope not in ("PROPERTY", "UNIT"):
        raise HTTPException(status_code=422, detail="scope must be PROPERTY or UNIT")

    if scope == "PROPERTY" and not property_id:
        raise HTTPException(status_code=422, detail="property_id is required for scope PROPERTY")

    if scope == "UNIT" and not unit_id:
        raise HTTPException(status_code=422, detail="unit_id is required for scope UNIT")

    data = file.file.read()
    size = len(data)

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    safe_name = (file.filename or "file").replace("/", "_")
    if scope == "PROPERTY":
        object_key = f"tenant_{user.tenant_id}/properties/{property_id}/{ts}_{safe_name}"
    else:
        object_key = f"tenant_{user.tenant_id}/units/{unit_id}/{ts}_{safe_name}"

    s3 = get_s3_client()
    ensure_bucket_exists(s3)
    bucket = settings.minio_bucket

    try:
        put_object(
            s3,
            key=object_key,
            data=data,
            content_type=file.content_type or "application/octet-stream",
        )
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

    doc = Document(
        tenant_id=user.tenant_id,
        scope=scope,
        property_id=property_id,
        unit_id=unit_id,
        uploaded_by=user.id,
        filename=file.filename or "file",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=size,
        object_key=object_key,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "id": doc.id,
        "scope": doc.scope,
        "property_id": doc.property_id,
        "unit_id": doc.unit_id,
        "uploaded_by": doc.uploaded_by,
        "filename": doc.filename,
        "content_type": doc.content_type,
        "size_bytes": doc.size_bytes,
        "created_at": doc.created_at,
    }


@router.get("")
def list_documents(
    scope: str | None = Query(None, pattern="^(PROPERTY|UNIT)$"),
    property_id: int | None = Query(None, ge=1),
    unit_id: int | None = Query(None, ge=1),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Document).filter(Document.tenant_id == user.tenant_id)

    if scope:
        q = q.filter(Document.scope == scope)

    # property_id nur sinnvoll bei PROPERTY
    if property_id is not None:
        if scope == "UNIT":
            # explizit UNIT + property_id macht keinen Sinn -> leer
            return []
        q = q.filter(Document.property_id == property_id)

    # unit_id nur sinnvoll bei UNIT
    if unit_id is not None:
        if scope == "PROPERTY":
            # explizit PROPERTY + unit_id macht keinen Sinn -> leer
            return []
        q = q.filter(Document.unit_id == unit_id)

    docs = q.order_by(Document.id.desc()).all()

    return [
        {
            "id": d.id,
            "scope": d.scope,
            "property_id": d.property_id,
            "unit_id": d.unit_id,
            "uploaded_by": d.uploaded_by,
            "filename": d.filename,
            "content_type": d.content_type,
            "size_bytes": d.size_bytes,
            "created_at": d.created_at,
        }
        for d in docs
    ]


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.tenant_id == user.tenant_id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not getattr(doc, "object_key", None):
        raise HTTPException(status_code=500, detail="Document has no object_key")

    s3 = get_s3_client()
    ensure_bucket_exists(s3)

    bucket = settings.minio_bucket
    try:
        url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket, "Key": doc.object_key},
            ExpiresIn=600,
        )
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"id": doc.id, "url": url}
