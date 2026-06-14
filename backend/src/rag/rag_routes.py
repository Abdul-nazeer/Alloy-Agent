"""
FastAPI RAG API Routes

Endpoints:
  POST /api/rag/upload          → Upload PDF, extract, chunk, embed, store
  POST /api/rag/query           → Hybrid retrieve + LLM answer + citations
  GET  /api/rag/documents       → List indexed documents
  DELETE /api/rag/documents/{id} → Remove document
  GET  /api/rag/pdf/{doc_id}    → Serve PDF file for viewer
  GET  /api/rag/pdf/{doc_id}/page/{n}/image → Render page as image for viewer
"""

import os
import sys
import shutil
import hashlib
import logging
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import fitz  # PyMuPDF - for page image rendering

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "ingestion"))
sys.path.insert(0, str(Path(__file__).parent.parent / "retrieval"))
sys.path.insert(0, str(Path(__file__).parent.parent / "citation"))

from pdf_extractor import PDFExtractor
from chunker import HierarchicalChunker
from vector_store import VectorStoreManager
from retriever import HybridRetriever
from citation_builder import CitationBuilder

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/rag", tags=["RAG"])

# ── Storage ────────────────────────────────────────────────────────────────────
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)

# ── Singletons (initialized once per worker) ───────────────────────────────────
_vector_store: Optional[VectorStoreManager] = None
_retriever: Optional[HybridRetriever] = None
_citation_builder = CitationBuilder()


def get_vector_store() -> VectorStoreManager:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreManager()
    return _vector_store


def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever


# ── Models ─────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str
    doc_ids: Optional[list[str]] = None   # filter to specific docs
    top_k: int = 5
    model: str = "phi3"                    # "phi3" | "claude" | "openai"


class QueryResponse(BaseModel):
    answer: str
    answer_html: str
    citations: list[dict]
    sources: list[dict]
    query: str
    chunks_retrieved: int


class DocumentInfo(BaseModel):
    doc_id: str
    doc_name: str
    filename: str
    chunk_count: int
    page_count: int
    file_size_kb: float
    status: str


# ── Document metadata store (in-memory, replace with DB in prod) ───────────────
_doc_registry: dict[str, dict] = {}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=DocumentInfo)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    vs: VectorStoreManager = Depends(get_vector_store),
):
    """
    Upload a PDF. Pipeline:
    1. Save to disk
    2. Extract elements with bboxes (PDFExtractor)
    3. Chunk with hierarchy (HierarchicalChunker)
    4. Embed + upsert to Qdrant (VectorStoreManager)
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    # Generate stable doc_id from filename
    doc_id = hashlib.sha256(file.filename.encode()).hexdigest()[:12]
    save_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"

    # Save file
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    file_size_kb = len(content) / 1024

    # Get page count
    doc = fitz.open(str(save_path))
    page_count = len(doc)
    doc.close()

    # Run extraction + chunking + embedding in background for large files
    # For demo, run synchronously (add celery/background for >10MB)
    try:
        logger.info(f"Processing {file.filename} ({file_size_kb:.1f}KB, {page_count}p)")

        # Step 1: Extract with bboxes
        extractor = PDFExtractor(doc_id=doc_id)
        elements = extractor.extract(str(save_path))

        # Step 2: Chunk hierarchically
        chunker = HierarchicalChunker(max_tokens=400, overlap_tokens=60)
        chunks = chunker.chunk(elements)

        # Step 3: Embed + store
        upserted = vs.upsert_chunks(chunks)

        # Register document
        doc_info = {
            "doc_id": doc_id,
            "doc_name": Path(file.filename).stem,
            "filename": file.filename,
            "file_path": str(save_path),
            "chunk_count": len(chunks),
            "page_count": page_count,
            "file_size_kb": round(file_size_kb, 1),
            "status": "indexed",
        }
        _doc_registry[doc_id] = doc_info

        logger.info(f"Indexed {file.filename}: {len(chunks)} chunks, {upserted} vectors")
        return DocumentInfo(**doc_info)

    except Exception as e:
        logger.error(f"Failed to process {file.filename}: {e}", exc_info=True)
        save_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Processing failed: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    req: QueryRequest,
    retriever: HybridRetriever = Depends(get_retriever),
):
    """
    Hybrid RAG query:
    1. Retrieve top-k chunks (dense + sparse + rerank)
    2. Build citation-aware prompt
    3. Call LLM (Phi-3 or Claude)
    4. Parse citations → return answer + bbox data
    """
    if not req.query.strip():
        raise HTTPException(400, "Query cannot be empty")

    # Step 1: Retrieve
    chunks = retriever.retrieve(
        query=req.query,
        doc_ids=req.doc_ids,
        top_k=req.top_k,
    )

    if not chunks:
        return QueryResponse(
            answer="No relevant information found in the uploaded documents.",
            answer_html="No relevant information found in the uploaded documents.",
            citations=[],
            sources=[],
            query=req.query,
            chunks_retrieved=0,
        )

    # Step 2: Build prompt
    system_prompt, user_prompt = _citation_builder.build_full_prompt(req.query, chunks)

    # Step 3: Call LLM
    answer = await _call_llm(system_prompt, user_prompt, model=req.model)

    # Step 4: Parse citations
    cited = _citation_builder.parse_citations(answer, chunks)
    sources = _citation_builder.format_sources_list(cited.citations)

    return QueryResponse(
        answer=cited.answer,
        answer_html=cited.answer_html,
        citations=[{"index": c.index, "pages": c.page_nums, "bboxes": c.bboxes}
                   for c in cited.citations],
        sources=sources,
        query=req.query,
        chunks_retrieved=len(chunks),
    )


@router.get("/documents", response_model=list[DocumentInfo])
async def list_documents():
    """List all indexed documents."""
    return [DocumentInfo(**v) for v in _doc_registry.values()]


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    vs: VectorStoreManager = Depends(get_vector_store),
):
    if doc_id not in _doc_registry:
        raise HTTPException(404, "Document not found")

    # Remove from Qdrant
    vs.delete_document(doc_id)

    # Remove file
    info = _doc_registry.pop(doc_id)
    Path(info["file_path"]).unlink(missing_ok=True)

    return {"deleted": doc_id}


@router.get("/pdf/{doc_id}")
async def serve_pdf(doc_id: str):
    """Serve the original PDF for the frontend viewer."""
    if doc_id not in _doc_registry:
        raise HTTPException(404, "Document not found")
    file_path = _doc_registry[doc_id]["file_path"]
    return FileResponse(file_path, media_type="application/pdf")


@router.get("/pdf/{doc_id}/page/{page_num}/image")
async def render_page_image(doc_id: str, page_num: int, dpi: int = 150):
    """
    Render a specific PDF page as PNG.
    Frontend uses this to display pages with bbox overlays.
    DPI=150 → good quality at reasonable size (~200KB per page).
    """
    if doc_id not in _doc_registry:
        raise HTTPException(404, "Document not found")

    file_path = _doc_registry[doc_id]["file_path"]
    doc = fitz.open(file_path)

    if page_num < 1 or page_num > len(doc):
        raise HTTPException(400, f"Page {page_num} out of range (1-{len(doc)})")

    page = doc[page_num - 1]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img_bytes = pix.tobytes("png")
    doc.close()

    return StreamingResponse(
        iter([img_bytes]),
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/collection/info")
async def collection_info(vs: VectorStoreManager = Depends(get_vector_store)):
    return vs.get_collection_info()


# ── LLM Caller ─────────────────────────────────────────────────────────────────

async def _call_llm(system_prompt: str, user_prompt: str, model: str = "phi3") -> str:
    """
    Route to different LLM backends.
    phi3 → HuggingFace Inference API (your fine-tuned model)
    claude → Anthropic API
    """
    if model == "claude":
        return await _call_claude(system_prompt, user_prompt)
    else:
        return await _call_phi3(system_prompt, user_prompt)


async def _call_phi3(system_prompt: str, user_prompt: str) -> str:
    """Call fine-tuned Phi-3 via HuggingFace Inference API."""
    import httpx
    import os

    hf_token = os.getenv("HF_TOKEN")
    hf_model = os.getenv("HF_MODEL_ID", "your-username/alloy-agent-phi3")

    prompt = (
        f"<|system|>{system_prompt}<|end|>\n"
        f"<|user|>\n{user_prompt}<|end|>\n"
        f"<|assistant|>\n"
    )

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"https://api-inference.huggingface.co/models/{hf_model}",
            headers={"Authorization": f"Bearer {hf_token}"},
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 800,
                    "temperature": 0.1,
                    "return_full_text": False,
                },
            },
        )
        resp.raise_for_status()
        result = resp.json()
        if isinstance(result, list):
            return result[0].get("generated_text", "").strip()
        return str(result)


async def _call_claude(system_prompt: str, user_prompt: str) -> str:
    """Fallback to Claude Sonnet for high-quality answers."""
    import httpx
    import os

    api_key = os.getenv("ANTHROPIC_API_KEY")
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 1000,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            },
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]
