import json
import logging
import uuid
from io import BytesIO
from urllib.parse import urlparse

from minio import Minio
from minio.error import S3Error

from config import cfg

logger = logging.getLogger(__name__)

_CONTENT_TYPE_EXT = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


def _anonymous_get_object_policy(bucket: str) -> str:
    """S3/MinIO policy: allow unauthenticated HTTP GET on object URLs."""
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket}/*"],
                },
            ],
        },
        separators=(",", ":"),
    )


def _minio_netloc(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    if parsed.netloc:
        return parsed.netloc
    return endpoint.replace("http://", "").replace("https://", "").split("/")[0]


class ChatImageStorage:
    def __init__(self) -> None:
        self._client = Minio(
            _minio_netloc(cfg.STORAGE_ENDPOINT),
            access_key=cfg.STORAGE_ACCESS_KEY,
            secret_key=cfg.STORAGE_SECRET_KEY,
            secure=cfg.STORAGE_USE_SSL,
        )
        self._bucket = cfg.STORAGE_BUCKET
        self._ensure_bucket()
        self._ensure_anonymous_read_policy()

    def _ensure_anonymous_read_policy(self) -> None:
        if not cfg.STORAGE_ANONYMOUS_READ:
            return
        try:
            self._client.set_bucket_policy(self._bucket, _anonymous_get_object_policy(self._bucket))
            logger.info("minio anonymous GetObject policy set bucket=%s", self._bucket)
        except S3Error:
            logger.exception("minio set_bucket_policy failed bucket=%s", self._bucket)
            raise

    def _ensure_bucket(self) -> None:
        try:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
                logger.info("minio created bucket=%s", self._bucket)
        except S3Error:
            logger.exception("minio bucket_exists/make_bucket failed bucket=%s", self._bucket)
            raise

    def upload_chat_image(self, data: bytes, content_type: str) -> str:
        ext = _CONTENT_TYPE_EXT.get(content_type)
        if ext is None:
            raise ValueError(f"unsupported image content type: {content_type}")
        key = f"chats/{uuid.uuid4().hex}.{ext}"
        stream = BytesIO(data)
        try:
            self._client.put_object(
                self._bucket,
                key,
                stream,
                length=len(data),
                content_type=content_type,
            )
        except S3Error as e:
            logger.exception("minio put_object failed key=%s", key)
            raise RuntimeError("failed to store chat image") from e
        return key

    def remove_keys(self, keys: list[str]) -> None:
        if not keys:
            return
        errors: list[str] = []
        for key in keys:
            try:
                self._client.remove_object(self._bucket, key)
            except S3Error as e:
                logger.warning("minio remove_object failed key=%s: %s", key, e)
                errors.append(key)
        if errors:
            raise RuntimeError(f"failed to remove some objects: {errors}")
