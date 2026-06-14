"""
RAG Package — Hybrid Search with Citations

Architecture:
- Dense vectors (semantic similarity)
- Sparse vectors (BM25-style keyword matching)
- Cross-encoder reranking
- Citation tracking with PDF bboxes

Collections:
  alloy_maintenance — Single collection with named vectors (dense + sparse)

Modules:
  config, pdf_extractor, chunker, vector_store, retriever,
  citation_builder, pipeline, ingest
"""

from .config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    VECTOR_SIZE,
    EMBEDDING_MODEL,
    HF_MODEL_ID,
    HF_TOKEN,
    TOP_K,
    SCORE_THRESHOLD,
    UPLOADS_DIR,
    validate_config,
)
from .pipeline import RAGPipeline, get_rag_pipeline
from .retriever import HybridRetriever
from .vector_store import VectorStoreManager
from .citation_builder import CitationBuilder

__all__ = [
    "QDRANT_URL", "QDRANT_API_KEY", "VECTOR_SIZE", "EMBEDDING_MODEL",
    "HF_MODEL_ID", "HF_TOKEN", "TOP_K", "SCORE_THRESHOLD",
    "UPLOADS_DIR", "validate_config",
    "RAGPipeline", "get_rag_pipeline",
    "HybridRetriever",
    "VectorStoreManager",
    "CitationBuilder",
]

__version__ = "4.0.0-hybrid"
