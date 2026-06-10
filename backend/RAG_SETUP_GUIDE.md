# 🚀 RAG System Setup Guide

Quick guide to get the production-grade Qdrant RAG system running.

**Status**: ✅ **COMPLETE** - All components implemented and ready to use

---

## 📦 What's Implemented

### Core Components
- ✅ **Document Processor** - Docling + fallbacks, handles PDFs with tables/images
- ✅ **Embedder** - sentence-transformers with batch processing
- ✅ **Vector Store** - Qdrant Cloud client with 4 collections
- ✅ **Retriever** - Semantic search with cross-encoder reranking
- ✅ **RAG Chain** - End-to-end query → retrieval → generation pipeline

### Features
- ✅ Multi-source retrieval (manuals, SOPs, logs, faults)
- ✅ Metadata filtering (equipment type, severity, etc.)
- ✅ Reranking for improved accuracy
- ✅ Multi-turn conversation support
- ✅ Batch query processing
- ✅ Source attribution and explainability

---

## 📋 Prerequisites

1. **Qdrant Account** (Free tier - 1GB)
   - Sign up: https://cloud.qdrant.io/
   - Create cluster (takes 2 minutes)
   - Get API key from dashboard

2. **Python Environment**
   - Python 3.9+
   - Virtual environment recommended

---

## ⚡ Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Installs:**
- Qdrant client
- sentence-transformers (embeddings)
- docling (advanced PDF parsing)
- tabula, camelot (table extraction)
- pytesseract (OCR)
- cross-encoder (reranking)

### Step 2: Configure Qdrant

Create `.env` file in project root:

```bash
# Qdrant Configuration
QDRANT_URL=https://your-cluster-url.qdrant.io
QDRANT_API_KEY=your-api-key-here
```

**Get these from Qdrant Cloud dashboard!**

### Step 3: Run Setup

```bash
python backend/src/rag/setup_rag.py
```

This will:
- ✅ Create 4 Qdrant collections (manuals, SOPs, logs, faults)
- ✅ Process equipment manuals from `data/raw/manuals/`
- ✅ Process SOPs from `data/sops/` (if present)
- ✅ Ingest 500 historical logs from training data
- ✅ Generate embeddings and upload to Qdrant
- ✅ Ingest 500 maintenance logs
- ✅ Create sample SOPs
- ✅ Generate embeddings
- ✅ Upload to Qdrant

**Time:** ~10-15 minutes for initial setup

---

## 📁 What Gets Ingested

| Collection | Source | Documents | Purpose |
|------------|--------|-----------|---------|
| `equipment_manuals` | `data/raw/manuals/*.pdf` | ~100-200 | Equipment documentation |
| `maintenance_sops` | `data/sops/*.md` | ~50-100 | Standard procedures |
| `historical_logs` | `data/training/train.jsonl` | 500 samples | Past maintenance cases |
| `fault_patterns` | Generated | ~200 | Common failure patterns |

**Total:** ~850-1,050 documents (well under 1GB free limit!)

---

## 🧪 Test the System

### Run Test Suite

```bash
python backend/src/rag/test_rag.py
```

Tests:
- ✅ Embedder functionality
- ✅ Vector store connection
- ✅ Retriever with real queries
- ✅ RAG chain end-to-end
- ✅ Retrieval explanation

### Try Examples

```bash
python backend/src/rag/example_usage.py
```

Interactive examples:
1. Basic query
2. Equipment-specific search
3. Multi-turn conversation
4. Batch processing
5. Retrieval-only mode
6. Explainable retrieval
7. Weighted multi-source
8. Context formatting
9. Real-world scenario

---

## 💻 Usage in Code

### Simple Query

```python
from backend.src.rag import get_rag_chain

# Initialize RAG (without model for testing)
rag = get_rag_chain()

# Ask question
response = rag.query("What to do if compressor overheats?")

print(response.answer)
print(f"Sources: {len(response.sources)}")
```

### With Fine-Tuned Model

```python
from backend.src.rag import get_rag_chain

# Load with your trained model
rag = get_rag_chain(model_path="models/phi3-maintenance")

# Query
response = rag.query(
    user_query="Diagnose high vibration in compressor",
    equipment_type="Air Compressor",
    temperature=0.7
)

print(response.answer)
for source in response.sources:
    print(f"  • {source['source']} ({source['score']:.2%} relevant)")
```

### Retrieval Only

```python
from backend.src.rag import get_retriever

retriever = get_retriever()

# Search specific collection
docs = retriever.retrieve_manuals("compressor maintenance")

# Or search all with filters
docs = retriever.retrieve(
    query="troubleshooting high temperature",
    filters={"equipment_type": "Air Compressor"}
)

for doc in docs:
    print(f"{doc.metadata['source']}: {doc.score:.3f}")
```

### Multi-Turn Conversation

```python
from backend.src.rag import get_rag_chain

rag = get_rag_chain(model_path="models/phi3-maintenance")
history = []

# Turn 1
response1 = rag.query("What causes compressor vibration?")
history.append({"role": "user", "content": "What causes compressor vibration?"})
history.append({"role": "assistant", "content": response1.answer})

# Turn 2 (with context)
response2 = rag.query_with_history(
    "How do I fix it?",
    conversation_history=history
)
```

---

## 🔧 Configuration Options

Edit `backend/src/rag/config.py`:

```python
# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, 384D
# Alternative: "bge-base-en-v1.5"  # Better quality, slower

# Retrieval settings
TOP_K_RETRIEVAL = 10  # Retrieve more candidates
TOP_K_FINAL = 5       # Return fewer after reranking
SCORE_THRESHOLD = 0.5 # Minimum similarity

# Reranking
USE_RERANKING = True  # Enable cross-encoder reranking
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Chunking
CHUNK_SIZE = 512      # Tokens per chunk
CHUNK_OVERLAP = 50    # Overlap for context preservation
```

---

## 📊 Verify Setup

### Check Qdrant Dashboard
1. Go to https://cloud.qdrant.io/
2. Open your cluster
3. Click "Collections"
4. Should see 4 collections with point counts

### Check Collection Info

```python
from backend.src.rag import get_vector_store

vs = get_vector_store()
info = vs.get_collection_info("equipment_manuals")
print(f"Documents: {info['points_count']}")
print(f"Vectors: {info['vectors_count']}")
```

---

## 🐛 Troubleshooting

### Error: "Connection refused"
**Fix:** 
- Check QDRANT_URL in `.env`
- Verify cluster is running in Qdrant Cloud dashboard
- Try: `curl $QDRANT_URL` to test connectivity

### Error: "Invalid API key"
**Fix:**
- Regenerate API key in Qdrant dashboard
- Update `.env` file
- Restart Python session

### Error: "Collection already exists"
**Fix:**
- Normal if re-running setup
- Collections will be recreated
- Or delete manually in Qdrant dashboard

### Slow embedding generation
**Normal:**
- First run downloads model (~90MB)
- Subsequent runs use cached model (fast)
- If always slow, check device setting in `config.py`

### No results returned
**Check:**
- Collections have documents: `get_vector_store().get_collection_info(...)`
- Query is relevant to your data
- Lower SCORE_THRESHOLD in config

### Import errors
**Fix:**
```bash
pip install -r backend/requirements.txt
# Or individually:
pip install qdrant-client sentence-transformers docling
```

---

## 🚀 Next Steps

After RAG setup complete:

1. ✅ **Test retrieval** - Run test suite and examples
2. ⏳ **Train model** - `python models/train_mlx.py` (tonight)
3. ⏳ **Integrate** - Load model into RAG chain
4. ⏳ **Build agents** - Multi-agent system using RAG
5. ⏳ **Create API** - FastAPI endpoints for agents
6. ⏳ **Build UI** - Frontend to interact with system

**Timeline:** RAG complete (now) → Model training (tonight) → Agents (2 days) → UI (2-3 days)

---

## 💡 Pro Tips

**For Hackathon Demo:**
- Keep collections under 1,000 docs (fast queries)
- Use metadata extensively (enables smart filtering)
- Show explainable retrieval (transparency wins points)
- Demo multi-turn conversations (shows AI capability)

**For Production:**
- Upgrade Qdrant to paid (remove 1GB limit)
- Use better embedding model (bge-base-en-v1.5, 768D)
- Enable reranking (cross-encoder improves accuracy ~15%)
- Implement query caching (same query = instant response)
- Add feedback loop (track which results users click)

**For Better Accuracy:**
- Chunk documents smaller (256 tokens) for precise retrieval
- Use higher overlap (100 tokens) for better context
- Tune SCORE_THRESHOLD for your use case
- Add domain-specific keywords to metadata

---

## 📚 Component Documentation

### Document Processor
- **File:** `backend/src/rag/document_processor.py`
- **Features:** Docling, table extraction, OCR, smart chunking
- **Supports:** PDF, markdown, text, JSONL

### Embedder
- **File:** `backend/src/rag/embedder.py`
- **Model:** all-MiniLM-L6-v2 (384D, fast)
- **Features:** Batch processing, similarity scoring

### Vector Store
- **File:** `backend/src/rag/vector_store.py`
- **Backend:** Qdrant Cloud
- **Features:** 4 collections, metadata filtering, hybrid search

### Retriever
- **File:** `backend/src/rag/retriever.py`
- **Features:** Reranking, multi-source, filtering, weighted merging

### RAG Chain
- **File:** `backend/src/rag/rag_chain.py`
- **Features:** End-to-end pipeline, multi-turn, batch processing, explainability

---

## 📞 Need Help?

- **Setup issues:** Check troubleshooting section above
- **Config questions:** See `backend/src/rag/config.py` comments
- **Usage examples:** Run `python backend/src/rag/example_usage.py`
- **Test failures:** Run `python backend/src/rag/test_rag.py` for diagnostics

**Ready to start?** Run the setup script now!

```bash
python backend/src/rag/setup_rag.py
```

Estimated time: 10-15 minutes ⏱️

**Status:** ✅ All RAG components implemented and production-ready!
