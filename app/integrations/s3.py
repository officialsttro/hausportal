from __future__ import annotations

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import settings


def get_s3_client():
    # Wichtig: MinIO Presigned URLs brauchen i.d.R. SigV4 => signature_version="s3v4"
    return boto3.client(
        "s3",
        endpoint_url=settings.minio_endpoint,
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        region_name="us-east-1",
        config=Config(signature_version="s3v4"),
    )


def ensure_bucket_exists(s3):
    bucket = settings.minio_bucket
    try:
        s3.head_bucket(Bucket=bucket)
    except ClientError:
        s3.create_bucket(Bucket=bucket)


def put_object(s3, key: str, data: bytes, content_type: str = "application/octet-stream"):
    bucket = settings.minio_bucket
    s3.put_object(Bucket=bucket, Key=key, Body=data, ContentType=content_type)
