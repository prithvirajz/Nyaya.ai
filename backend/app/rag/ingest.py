"""
NyayaAI – PDF Ingestion Pipeline
===================================
Loads legal PDFs, cleans text, chunks, attaches metadata, and builds a FAISS index.

Usage (from backend/ directory):
    python -m app.rag.ingest
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import faiss
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger
from pypdf import PdfReader

# Ensure the backend root is on sys.path when run as a script
_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.config import settings
from app.services.embedding_service import embedding_service

# ── Filename convention ──────────────────────────────────────────────────
# Expected filename format: <Law>__<Section>__<Category>.pdf
# Example: IPC__Section-302__Criminal.pdf
# If the filename doesn't follow this convention, defaults are used.


def _parse_filename_metadata(filepath: str) -> Dict[str, str]:
    """
    Extract metadata from the PDF filename using the convention:
        <Law>__<Section>__<Category>.pdf

    Falls back to sensible defaults when the convention isn't followed.
    """
    basename = Path(filepath).stem  # remove .pdf
    parts = basename.split("__")

    return {
        "law": parts[0].replace("-", " ").replace("_", " ") if len(parts) >= 1 else "Unknown",
        "section": parts[1].replace("-", " ").replace("_", " ") if len(parts) >= 2 else "",
        "category": parts[2].replace("-", " ").replace("_", " ") if len(parts) >= 3 else "General",
        "source": Path(filepath).name,
    }


def _clean_text(text: str) -> str:
    """
    Clean extracted PDF text:
    - Remove excessive whitespace
    - Remove page numbers and common headers/footers
    - Normalise Unicode
    """
    # Remove common page-number patterns
    text = re.sub(r"\n\s*Page\s+\d+\s*(of\s+\d+)?\s*\n", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"\n\s*-\s*\d+\s*-\s*\n", "\n", text)

    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse spaces (but keep newlines)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def load_pdfs(pdf_dir: str | None = None) -> List[Tuple[str, str]]:
    """
    Load all PDFs from the given directory.

    Returns:
        List of (filepath, full_text) tuples.
    """
    pdf_dir = pdf_dir or settings.PDF_DIRECTORY
    pdf_path = Path(pdf_dir)

    if not pdf_path.exists():
        logger.warning("PDF directory does not exist: {dir}. Creating it.", dir=pdf_dir)
        pdf_path.mkdir(parents=True, exist_ok=True)
        return []

    pdf_files = sorted(pdf_path.glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found in {dir}", dir=pdf_dir)
        return []

    results = []
    for pdf_file in pdf_files:
        try:
            reader = PdfReader(str(pdf_file))
            pages_text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            full_text = "\n\n".join(pages_text)
            cleaned = _clean_text(full_text)
            if cleaned:
                results.append((str(pdf_file), cleaned))
                logger.info("Loaded PDF: {file} ({n} chars)", file=pdf_file.name, n=len(cleaned))
            else:
                logger.warning("PDF yielded no text: {file}", file=pdf_file.name)
        except Exception as exc:
            logger.error("Failed to load PDF {file}: {err}", file=pdf_file.name, err=exc)

    return results


def chunk_documents(
    documents: List[Tuple[str, str]],
) -> Tuple[List[str], List[Dict[str, str]]]:
    """
    Split documents into chunks and generate metadata for each chunk.

    Returns:
        (texts, metadatas) – parallel lists of chunk texts and their metadata dicts.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    all_texts: List[str] = []
    all_metadatas: List[Dict[str, str]] = []

    for filepath, text in documents:
        base_meta = _parse_filename_metadata(filepath)
        chunks = splitter.split_text(text)
        for chunk in chunks:
            all_texts.append(chunk)
            all_metadatas.append(base_meta.copy())

    logger.info("Total chunks created: {n}", n=len(all_texts))
    return all_texts, all_metadatas


def build_faiss_index(
    texts: List[str],
    metadatas: List[Dict[str, str]],
    index_path: str | None = None,
) -> None:
    """
    Generate embeddings and build a FAISS index, persisting it to disk.

    Saves:
        - index.faiss   – the FAISS flat index
        - texts.npy     – numpy array of chunk texts
        - metadatas.npy – numpy array of metadata dicts
    """
    index_path = index_path or settings.FAISS_INDEX_PATH
    out_dir = Path(index_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Generating embeddings for {n} chunks...", n=len(texts))
    embeddings = embedding_service.embed_texts(texts)
    embeddings_np = np.array(embeddings, dtype="float32")

    # Build FAISS index (Flat L2 — exact search, fine for < 100k chunks)
    dimension = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)

    # Persist
    faiss.write_index(index, str(out_dir / "index.faiss"))
    np.save(str(out_dir / "texts.npy"), np.array(texts, dtype=object))
    np.save(str(out_dir / "metadatas.npy"), np.array(metadatas, dtype=object))

    logger.info(
        "FAISS index saved to {path} ({n} vectors, dim={d})",
        path=index_path,
        n=index.ntotal,
        d=dimension,
    )


def run_ingestion(pdf_dir: str | None = None, index_path: str | None = None) -> None:
    """End-to-end ingestion: load → chunk → embed → index."""
    logger.info("Starting PDF ingestion pipeline...")
    documents = load_pdfs(pdf_dir)
    if not documents:
        logger.warning("No documents to ingest. Add PDFs to the data/pdfs/ directory.")
        return

    texts, metadatas = chunk_documents(documents)
    build_faiss_index(texts, metadatas, index_path)
    logger.info("Ingestion complete ✓")


# ── CLI entry point ──────────────────────────────────────────────────────
if __name__ == "__main__":
    run_ingestion()
