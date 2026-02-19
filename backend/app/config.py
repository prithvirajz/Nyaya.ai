"""
NyayaAI Configuration
=====================
Centralised settings loaded from environment variables via pydantic-settings.
All secrets and tunables are managed here.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Application-wide settings. Values are read from .env or environment."""

    # ── OpenRouter LLM ──────────────────────────────────────────────
    OPENROUTER_API_KEY: str = Field(default="", description="OpenRouter API key")
    OPENROUTER_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1/chat/completions",
        description="OpenRouter chat completions endpoint",
    )
    MODEL_NAME: str = Field(
        default="mistralai/mistral-7b-instruct",
        description="LLM model identifier on OpenRouter",
    )
    LLM_TEMPERATURE: float = Field(default=0.2, ge=0.0, le=1.0)
    LLM_MAX_TOKENS: int = Field(default=2048, ge=64, le=4096)

    # ── Embedding ───────────────────────────────────────────────────
    EMBEDDING_MODEL: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace sentence-transformer model for embeddings",
    )

    # ── RAG Tuning ──────────────────────────────────────────────────
    CHUNK_SIZE: int = Field(default=1000, ge=200, le=4000)
    CHUNK_OVERLAP: int = Field(default=200, ge=0, le=1000)
    TOP_K: int = Field(default=5, ge=1, le=20)

    # ── Paths ───────────────────────────────────────────────────────
    PDF_DIRECTORY: str = Field(
        default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pdfs"),
        description="Directory containing legal PDF files",
    )
    FAISS_INDEX_PATH: str = Field(
        default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "faiss_index"),
        description="Directory to persist the FAISS index",
    )
    FEEDBACK_FILE: str = Field(
        default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "feedback.jsonl"),
        description="Path to store user feedback",
    )

    # ── Security ────────────────────────────────────────────────────
    MAX_QUERY_LENGTH: int = Field(default=2000, ge=10, le=10000)
    MIN_QUERY_LENGTH: int = Field(default=5, ge=1, le=100)
    RATE_LIMIT: str = Field(
        default="10/minute",
        description="Rate limit per IP address (slowapi format)",
    )

    # ── CORS ────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "*"],
        description="Allowed CORS origins",
    )

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True


# ── Singleton ────────────────────────────────────────────────────────
settings = Settings()
