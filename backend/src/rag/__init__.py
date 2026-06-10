"""
RAG (Retrieval-Augmented Generation) System

Core components for knowledge retrieval:
- Embedder: Convert text to vectors
- Vector Store: Qdrant client for semantic search
- Document Processor: Process PDFs and documents
"""

from .embedder import Embedder, get_embedder
from .vector_store import VectorStore, get_vector_store
from .document_processor import DocumentProcessor, get_document_processor
from .config import (
    COLLECTION_MANUALS,
    COLLECTION_SOPS,
    COLLECTION_LOGS,
    COLLECTION_FAULTS,
    validate_config,
)

__all__ = [
    'Embedder',
    'get_embedder',
    'VectorStore',
    'get_vector_store',
    'DocumentProcessor',
    'get_document_processor',
    'COLLECTION_MANUALS',
    'COLLECTION_SOPS',
    'COLLECTION_LOGS',
    'COLLECTION_FAULTS',
    'validate_config',
]

__version__ = '1.0.0'
