from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.integrations.s3 import ensure_bucket_exists, get_s3_client, put_object
from app.models.document import Document


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build_object_key(*parts: str) -> str:
    # join ohne doppelte slashes
    clean = []
    for p in parts:
        p = (p or "").strip().strip("/")
        if p:
            clean.append(p)
    return "/".join(clean)


def create_document_and_upload(
    db: Session,
    *,
    tenant_id: int,
    uploaded_by: int,
    scope: str,
    property_id: int | None,
    unit_id: int | None,
    filename: str,
    content_type: str,
    data: bytes,
) -> Document:
    s3 = get_s3_client()
    ensure_bucket_exists(s3)

    scope_u = (scope or "").upper().strip()
    if scope_u not in ("PROPERTY", "UNIT"):
        raise ValueError("Invalid scope")

    if scope_u == "PROPERTY" and not property_id:
        raise ValueError("property_id required for PROPERTY scope")
    if scope_u == "UNIT" and not unit_id:
        raise ValueError("unit_id required for UNIT scope")

    safe_name = filename.replace("\\", "_").replace("/", "_").strip() or "upload.bin"

    if scope_u == "PROPERTY":
        key = build_object_key(f"tenant_{tenant_id}", "properties", str(property_id), f"{_utc_stamp()}_{safe_name}")
    else:
        key = build_object_key(f"tenant_{tenant_id}", "units", str(unit_id), f"{_utc_stamp()}_{safe_name}")

    put_object(s3, key=key, data=data, content_type=content_type or "application/octet-stream")

    doc = Document(
        tenant_id=tenant_id,
        scope=scope_u,
        property_id=property_id,
        unit_id=unit_id,
        uploaded_by=uploaded_by,
        filename=safe_name,
        content_type=content_type or "application/octet-stream",
        size_bytes=len(data),
        object_key=key,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_document_download_url(doc: Document, expires_seconds: int = 3600) -> str:
    s3 = get_s3_client()
    ensure_bucket_exists(s3)

    # SigV4 Presigned URL
    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": settings.minio_bucket, "Key": doc.object_key},
        ExpiresIn=expires_seconds,
    )


def delete_document_and_object(db: Session, doc: Document) -> None:
    s3 = get_s3_client()
    ensure_bucket_exists(s3)

    s3.delete_object(
        Bucket=settings.minio_bucket,
        Key=doc.object_key,
    )

    db.delete(doc)
    db.commit()
