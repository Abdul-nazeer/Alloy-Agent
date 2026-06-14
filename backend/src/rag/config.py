"""
RAG Configuration — Single source of truth for all RAG settings.

Loads credentials from .env at project root.
Supports development (local Qdrant) and production (Qdrant Cloud).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Project paths ────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DATA_DIR = PROJECT_ROOT / "data"
RAW_MANUALS_DIR = DATA_DIR / "raw" / "manuals"
RAW_SOPS_DIR = DATA_DIR / "raw" / "sops"
TRAINING_DATA_PATH = DATA_DIR / "training" / "train.jsonl"
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# ── Environment ──────────────────────────────────────────────────────────────
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# ── Qdrant ───────────────────────────────────────────────────────────────────
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Parent-Child architecture — two collections per knowledge source
#   Parent: stores document-level metadata (no vectors)
#   Child:  stores chunk vectors, each linked to parent via parent_doc_id
COLLECTION_DOCUMENTS = os.getenv("QDRANT_COLLECTION_DOCS", "alloy_documents")
COLLECTION_CHUNKS = os.getenv("QDRANT_COLLECTION_CHUNKS", "alloy_chunks")

# Separate child collection for user uploads
COLLECTION_UPLOAD_CHUNKS = os.getenv("QDRANT_COLLECTION_UPLOADS", "alloy_upload_chunks")

# ── Knowledge Base ───────────────────────────────────────────────────────────
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
INCIDENTS_PATH = KNOWLEDGE_DIR / "incidents.json"
SPARE_PARTS_PATH = KNOWLEDGE_DIR / "spare_parts.csv"

VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dimension

# ── Embedding model ──────────────────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# ── Chunking ─────────────────────────────────────────────────────────────────
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
MAX_CHUNKS_PER_DOC = int(os.getenv("MAX_CHUNKS_PER_DOC", "300"))

# ── Retrieval ────────────────────────────────────────────────────────────────
TOP_K = int(os.getenv("TOP_K", "5"))
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "0.25"))
NEIGHBOR_EXPANSION = int(os.getenv("NEIGHBOR_EXPANSION", "1"))  # ±N neighboring chunks

# ── LLM Configuration ──────────────────────────────────────────────────────
# Supports: "ollama", "huggingface", "openai"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

# HuggingFace settings
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "CodeMasterAbdul/alloy-phi3-steel-maintenance")
HF_TOKEN = os.getenv("HF_TOKEN", "")

# Ollama settings (local, fast, offline!)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# OpenAI settings (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Generation parameters
GENERATION_MAX_TOKENS = int(os.getenv("GENERATION_MAX_TOKENS", "800"))  # Increased for detailed diagnostics
GENERATION_TEMPERATURE = float(os.getenv("GENERATION_TEMPERATURE", "0.3"))  # Lower for factual accuracy

# ── Domain (guardrails) ─────────────────────────────────────────────────────
ALLOWED_DOMAIN_KEYWORDS = [
    "maintenance", "equipment", "motor", "compressor", "bearing", "vibration",
    "temperature", "pressure", "torque", "rpm", "lubrication", "corrosion",
    "pump", "valve", "turbine", "conveyor", "mill", "roller", "fan", "cooling",
    "furnace", "steel", "alloy", "sensor", "fault", "failure", "diagnosis",
    "predictive", "inspection", "sop", "downtime", "spare", "repair",
    "overhaul", "alignment", "calibration", "hydraulic", "pneumatic",
    "electrical", "mechanical", "degradation", "wear", "fatigue", "crack",
    "leak", "overheating", "shutdown", "alert", "risk", "rul", "remaining",
    "useful", "life", "schedule", "plan", "priority", "recommendation",
]

EQUIPMENT_TYPES = [
    "Air Compressor", "Cooling Fan System", "Rolling Mill",
    "Conveyor Motor", "Turbine", "Pump", "Blast Furnace",
    "Heat Exchanger", "Hydraulic System",
]

SEVERITY_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def validate_config() -> bool:
    """Raise if critical config is missing."""
    errors = []
    if not QDRANT_URL:
        errors.append("QDRANT_URL is not set")
    if QDRANT_URL.startswith("https://") and not QDRANT_API_KEY:
        errors.append("QDRANT_API_KEY required for Qdrant Cloud")
    if errors:
        raise ValueError("Config errors:\n  • " + "\n  • ".join(errors))
    return True
