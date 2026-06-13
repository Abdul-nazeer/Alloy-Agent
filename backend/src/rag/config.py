"""
RAG System Configuration
Centralized config for Qdrant, embeddings, and retrieval settings
Supports both local development and production deployment
"""

import os
from pathlib import Path

# ============================================================================
# ENVIRONMENT DETECTION
# ============================================================================

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development | production
IS_PRODUCTION = ENVIRONMENT == "production"

# ============================================================================
# QDRANT CONFIGURATION
# ============================================================================

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Production: Qdrant Cloud (free 1GB cluster)
# Development: Local Qdrant (Docker)
if IS_PRODUCTION:
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    if not QDRANT_URL or not QDRANT_API_KEY:
        raise ValueError("Production mode requires QDRANT_URL and QDRANT_API_KEY in environment")
else:
    # Local development with Docker Qdrant
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = None

print(f"🔧 Environment: {ENVIRONMENT}")
print(f"📍 Qdrant URL: {QDRANT_URL}")

# Collection names (parent-child architecture)
COLLECTION_DOCUMENTS = "documents"  # Parent: full document metadata
COLLECTION_CHUNKS = "chunk"         # Child: searchable text chunks (matches Qdrant UI)

# Vector dimensions (all-MiniLM-L6-v2 = 384 dims)
VECTOR_SIZE = 384

# ============================================================================
# EMBEDDING CONFIGURATION
# ============================================================================

# Embedding model (lightweight, fast, good quality)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# Note: Model auto-downloads on first run (~80MB)

# Embedding device detection
import torch
if torch.cuda.is_available():
    EMBEDDING_DEVICE = "cuda"
elif torch.backends.mps.is_available():
    EMBEDDING_DEVICE = "mps"  # Apple Silicon
else:
    EMBEDDING_DEVICE = "cpu"

print(f"💻 Embedding device: {EMBEDDING_DEVICE}")

# ============================================================================
# DOCUMENT PROCESSING
# ============================================================================

# Paths (relative to project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_MANUALS = DATA_DIR / "raw" / "manuals"
RAW_SOPS = DATA_DIR / "raw" / "sops"
PROCESSED_DIR = DATA_DIR / "processed"
TRAINING_DATA = DATA_DIR / "training" / "train.jsonl"

# Create directories if they don't exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Chunking settings
CHUNK_SIZE = 512  # tokens (~2000 characters)
CHUNK_OVERLAP = 50  # tokens overlap for context
MAX_CHUNKS_PER_DOC = 200  # Prevent huge documents

# ============================================================================
# RETRIEVAL CONFIGURATION
# ============================================================================

# Search settings
TOP_K_RETRIEVAL = 10  # Retrieve more, rerank to fewer
TOP_K_FINAL = 5  # Final results after reranking
SCORE_THRESHOLD = 0.5  # Minimum similarity score (0-1)

# Reranking (improves relevance)
USE_RERANKING = True
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# ============================================================================
# LLM CONFIGURATION (HuggingFace)
# ============================================================================

# Fine-tuned model on HuggingFace
LLM_MODEL = "abdul-nazeer/alloy-agent-phi3-maintenance"
HF_TOKEN = os.getenv("HF_TOKEN")  # Optional, increases rate limit

# Generation settings
MAX_CONTEXT_LENGTH = 2048  # tokens for RAG context
GENERATION_TEMPERATURE = 0.7
GENERATION_MAX_TOKENS = 400
GENERATION_TOP_P = 0.9

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
    "Pump",
    "Blast Furnace",
    "Heat Exchanger",
    "Hydraulic System"
]

# Document types
DOC_TYPES = ["manual", "sop", "log", "fault"]

# Severity levels
SEVERITY_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# ============================================================================
# CACHING (Production Only)
# ============================================================================

ENABLE_CACHE = IS_PRODUCTION
CACHE_TTL = 3600  # seconds (1 hour)

# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = "INFO" if IS_PRODUCTION else "DEBUG"
LOG_QUERIES = True  # Log all queries for analysis

# ============================================================================
# RATE LIMITING (Production Only)
# ============================================================================

if IS_PRODUCTION:
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 500
else:
    RATE_LIMIT_PER_MINUTE = None
    RATE_LIMIT_PER_HOUR = None

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if not QDRANT_URL:
        errors.append("QDRANT_URL not set")
    
    if IS_PRODUCTION and QDRANT_URL.startswith("https://") and not QDRANT_API_KEY:
        errors.append("QDRANT_API_KEY required for Qdrant Cloud in production")
    
    if not DATA_DIR.exists():
        errors.append(f"Data directory not found: {DATA_DIR}")
    
    if errors:
        raise ValueError(f"❌ Configuration errors:\n  - " + "\n  - ".join(errors))
    
    print("✓ Configuration validated")
    return True

# Export all config
__all__ = [
    'ENVIRONMENT',
    'IS_PRODUCTION',
    'QDRANT_URL',
    'QDRANT_API_KEY',
    'COLLECTION_DOCUMENTS',
    'COLLECTION_CHUNKS',
    'VECTOR_SIZE',
    'EMBEDDING_MODEL',
    'EMBEDDING_DEVICE',
    'CHUNK_SIZE',
    'CHUNK_OVERLAP',
    'TOP_K_RETRIEVAL',
    'TOP_K_FINAL',
    'SCORE_THRESHOLD',
    'LLM_MODEL',
    'HF_TOKEN',
    'validate_config',
]
