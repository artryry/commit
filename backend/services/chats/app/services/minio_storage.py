import logging
from urllib.parse import urlparse

from minio import Minio

from config import cfg

logger = logging.getLogger(__name__)


class ChatImageStorage:
    """Deletes objects from the same MinIO bucket profiles use (`storage_key` paths)."""

    def __init__(self) -> None:
        self._bucket = cfg.STORAGE_BUCKET
        parsed = urlparse(cfg.STORAGE_ENDPOINT)
        host = parsed.hostname or "localhost"
        port = parsed.port or 9000
        endpoint = f"{host}:{port}"
        secure = cfg.STORAGE_USE_SSL or parsed.scheme == "https"
        self._client = Minio(
            endpoint,
            access_key=cfg.STORAGE_ACCESS_KEY,
            secret_key=cfg.STORAGE_SECRET_KEY,
            secure=secure,
        )

    def remove_keys(self, keys: list[str]) -> None:
        for key in keys:
            try:
                self._client.remove_object(self._bucket, key)
            except Exception:
                logger.warning("failed to remove object %s", key, exc_info=True)
