"""
NyayaAI – Embedding Service
=============================
Singleton wrapper around a sentence-transformer model for generating embeddings.
Uses all-MiniLM-L6-v2 (384-dimensional, fast, free).
"""

from __future__ import annotations

import threading
from typing import List

from loguru import logger
from sentence_transformers import SentenceTransformer

from app.config import settings


class EmbeddingService:
    """
    Thread-safe singleton that lazily loads the sentence-transformer model.
    This avoids loading the model at import time and saves memory when not needed.
    """

    _instance: EmbeddingService | None = None
    _lock = threading.Lock()

    def __new__(cls) -> EmbeddingService:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._model = None
        return cls._instance

    @property
    def model(self) -> SentenceTransformer:
        """Lazy-load the embedding model on first access."""
        if self._model is None:
            logger.info(
                "Loading embedding model: {model}", model=settings.EMBEDDING_MODEL
            )
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully.")
        return self._model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of strings to embed.

        Returns:
            List of embedding vectors (each is a list of floats).
        """
        if not texts:
            return []
        embeddings = self.model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Generate an embedding for a single query string.

        Args:
            query: The query text to embed.

        Returns:
            A single embedding vector as a list of floats.
        """
        return self.embed_texts([query])[0]


# ── Module-level convenience instance ────────────────────────────────────
embedding_service = EmbeddingService()
