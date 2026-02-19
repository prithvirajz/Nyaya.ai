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
from loguru import logger
from fastembed import TextEmbedding

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
    def model(self) -> TextEmbedding:
        """Lazy-load the embedding model on first access."""
        if self._model is None:
            logger.info(
                "Loading embedding model: {model}", model=settings.EMBEDDING_MODEL
            )
            # threads=None lets FastEmbed use all available CPU cores
            self._model = TextEmbedding(model_name=settings.EMBEDDING_MODEL, threads=None)
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
            
        # FastEmbed returns a generator of vectors, so we convert to list
        embeddings_generator = self.model.embed(texts)
        return [list(vec) for vec in embeddings_generator]

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
