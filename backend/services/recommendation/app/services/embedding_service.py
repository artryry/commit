import asyncio
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

from config.settings import settings


class IEmbeddingEncoder(ABC):
    @abstractmethod
    async def encode_three(self, bio: str, search_for: str) -> Tuple[List[float], List[float], List[float]]:
        pass


@lru_cache(maxsize=1)
def _sentence_model() -> SentenceTransformer:
    return SentenceTransformer(settings.EMBEDDING_MODEL_NAME)


class EmbeddingEncoder(IEmbeddingEncoder):
    """Wraps sentence-transformers (blocking) so callers stay async."""

    @staticmethod
    def _combine(bio: str, search_for: str) -> str:
        b = (bio or "").strip()
        s = (search_for or "").strip()
        if b and s:
            return f"{b}\n\nsearch_for: {s}"
        return b or s or ""

    @staticmethod
    def _one(text: str) -> List[float]:
        text = (text or "").strip()
        if not text:
            return [0.0] * settings.EMBEDDING_DIM
        vec = _sentence_model().encode(text, normalize_embeddings=True)
        return np.asarray(vec, dtype=np.float32).tolist()

    async def encode_three(self, bio: str, search_for: str) -> Tuple[List[float], List[float], List[float]]:
        combined_text = self._combine(bio, search_for)

        def run() -> Tuple[List[float], List[float], List[float]]:
            return self._one(bio), self._one(search_for), self._one(combined_text)

        return await asyncio.to_thread(run)
