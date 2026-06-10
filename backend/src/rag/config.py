"""
RAG System Configuration
Centralized config for Qdrant, embeddings, and retrieval settings
"""

import os
from pathlib import Path

# ============================================================================
# QDRANT CONFIGURATION
# ============================================================================

# Qdrant Connection
# Load from .env file (required)
from dotenv import load_dotenv
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Option 2: Local Qdrant (Docker)
# QDRANT_URL = "http://localhost:6333"
# QDRANT_API_KEY = None

# Collection names
COLLECTION_MANUALS = "equipment_manuals"
COLLECTION_SOPS = "maintenance_sops"
COLLECTION_LOGS = "historical_logs"
COLLECTION_FAULTS = "fault_patterns"

# Vector dimensions (all-MiniLM-L6-v2 = 384 dims)
VECTOR_SIZE = 384

# ============================================================================
# EMBEDDING CONFIGURATION
# ============================================================================

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
# Alternative: "bge-base-en-v1.5" (better quality, slower)

# Embedding device
EMBEDDING_DEVICE = "mps"  # For M1 Mac, use "cuda" for NVIDIA, "cpu" for CPU

# ============================================================================
# DOCUMENT PROCESSING
# ============================================================================

# Paths
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
RAW_MANUALS = DATA_DIR / "raw" / "manuals"
PROCESSED_DIR = DATA_DIR / "processed"
TRAINING_DATA = DATA_DIR / "training" / "train.jsonl"

# Chunking settings
CHUNK_SIZE = 512  # tokens
CHUNK_OVERLAP = 50  # tokens
MAX_CHUNKS_PER_DOC = 200  # Prevent huge documents

# ============================================================================
# RETRIEVAL CONFIGURATION
# ============================================================================

# Search settings
TOP_K_RETRIEVAL = 10  # Retrieve more, rerank to fewer
TOP_K_FINAL = 5  # Final results after reranking
SCORE_THRESHOLD = 0.5  # Minimum similarity score

# Reranking
USE_RERANKING = True
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Hybrid search weights
VECTOR_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3

# ============================================================================
# METADATA FILTERS
# ============================================================================

# Equipment types for filtering
EQUIPMENT_TYPES = [
    "Air Compressor",
    "Cooling Fan",
    "Rolling Mill",
    "Conveyor Motor",
    "Turbine",
    "Pump"
]

# Document types
DOC_TYPES = ["manual", "sop", "log", "fault"]

# Severity levels
SEVERITY_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# ============================================================================
# RAG CHAIN CONFIGURATION
# ============================================================================

# Context window for LLM
MAX_CONTEXT_LENGTH = 2048  # tokens

# Number of sources to cite
MAX_SOURCES = 3

# Temperature for generation (if using LLM API)
GENERATION_TEMPERATURE = 0.7

# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = "INFO"
LOG_QUERIES = True  # Log all queries for analysis

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if not QDRANT_URL:
        errors.append("QDRANT_URL not set")
    
    if QDRANT_URL.startswith("https://") and not QDRANT_API_KEY:
        errors.append("QDRANT_API_KEY required for Qdrant Cloud")
    
    if not DATA_DIR.exists():
        errors.append(f"Data directory not found: {DATA_DIR}")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True

# Export all config
__all__ = [
    'QDRANT_URL',
    'QDRANT_API_KEY',
    'COLLECTION_MANUALS',
    'COLLECTION_SOPS',
    'COLLECTION_LOGS',
    'COLLECTION_FAULTS',
    'VECTOR_SIZE',
    'EMBEDDING_MODEL',
    'EMBEDDING_DEVICE',
    'CHUNK_SIZE',
    'CHUNK_OVERLAP',
    'TOP_K_RETRIEVAL',
    'TOP_K_FINAL',
    'SCORE_THRESHOLD',
    'validate_config',
]
