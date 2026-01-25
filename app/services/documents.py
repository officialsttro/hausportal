from sqlalchemy.orm import Session

from app.models.document import Document
from app.core.config import settings
from app.integrations.s3 import get_s3_client


def delete_document_and_object(db: Session, doc: Document) -> None:
    s3 = get_s3_client()
    s3.delete_object(
        Bucket=settings.minio_bucket,
        Key=doc.object_key,
    )

    db.delete(doc)
    db.commit()
