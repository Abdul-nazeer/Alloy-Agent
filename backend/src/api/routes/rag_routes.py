"""
FastAPI Routes for RAG, Agent chat, and Document Upload.
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["RAG & Documents"])

# Upload directory
UPLOAD_DIR = Path(__file__).parent.parent.parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Document registry (in-memory for now - use DB in production)
_doc_registry: Dict[str, Dict] = {}


class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    context_used: bool


class DocumentInfo(BaseModel):
    doc_id: str
    doc_name: str
    filename: str
    chunk_count: int
    page_count: int
    file_size_kb: float
    status: str


@router.post("/v1/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Query the Alloy Agent for Decision Support using the new multi-agent system.
    """
    from backend.src.agents import chat
    
    try:
        result = chat(
            user_input=req.question,
            session_id=req.session_id or "default"
        )
        
        return ChatResponse(
            answer=result["response"],
            sources=[],
            context_used=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/upload", response_model=DocumentInfo)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF document for ingestion into the knowledge base.
    
    Pipeline:
    1. Validate PDF format
    2. Save to disk
    3. Extract text and chunk
    4. Generate embeddings
    5. Store in Qdrant vector database
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

    try:
        # Import PDF processing dependencies
        import fitz  # PyMuPDF
        from backend.src.rag.pdf_extractor import PDFExtractor
        from backend.src.rag.chunker import HierarchicalChunker
        from backend.src.rag.vector_store import get_vector_store
        
        logger.info(f"Processing {file.filename} ({file_size_kb:.1f}KB)")

        # Get page count
        doc = fitz.open(str(save_path))
        page_count = len(doc)
        doc.close()

        # Step 1: Extract text from PDF
        extractor = PDFExtractor(doc_id=doc_id)
        elements = extractor.extract(str(save_path))

        # Step 2: Chunk hierarchically
        chunker = HierarchicalChunker(max_tokens=500, overlap_tokens=50)
        chunks = chunker.chunk(elements)

        # Step 3: Get vector store and upsert chunks
        vector_store = get_vector_store()
        upserted_count = vector_store.upsert_chunks(chunks)

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

        logger.info(f"✓ Indexed {file.filename}: {len(chunks)} chunks, {upserted_count} vectors")
        
        return DocumentInfo(**doc_info)

    except Exception as e:
        logger.error(f"Failed to process {file.filename}: {e}", exc_info=True)
        save_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Processing failed: {str(e)}")


@router.get("/rag/documents", response_model=List[DocumentInfo])
async def list_documents():
    """List all indexed documents in the knowledge base."""
    # If registry is empty but Qdrant has data, rebuild from Qdrant
    if not _doc_registry:
        _rebuild_registry_from_qdrant()
    
    return [DocumentInfo(**v) for v in _doc_registry.values()]


def _rebuild_registry_from_qdrant():
    """Rebuild document registry from Qdrant metadata."""
    try:
        from backend.src.rag.vector_store import get_vector_store
        from pathlib import Path
        
        vector_store = get_vector_store()
        
        # Search paths for PDFs
        base_path = Path(__file__).parent.parent.parent.parent
        search_paths = [
            UPLOAD_DIR,
            base_path / "data" / "raw" / "manuals",
            base_path / "data" / "raw" / "kaggle" / "CMaps",
        ]
        
        # Scroll through all points to extract unique documents and count chunks
        docs_found = {}
        chunk_counts = {}
        offset = None
        
        logger.info("Rebuilding document registry from Qdrant...")
        
        while True:
            result = vector_store.client.scroll(
                collection_name=vector_store.collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            
            points, next_offset = result
            
            if not points:
                break
                
            for point in points:
                payload = point.payload
                doc_id = payload.get("doc_id")
                
                if not doc_id:
                    continue
                
                # Count chunks for this document
                chunk_counts[doc_id] = chunk_counts.get(doc_id, 0) + 1
                
                # Store document info from first chunk encountered
                if doc_id not in docs_found:
                    doc_name = payload.get("doc_name", "Unknown Document")
                    filename = f"{doc_name}.pdf"
                    
                    # Try to find the actual PDF file in search paths
                    file_path = None
                    file_size_kb = 0.0
                    
                    for search_dir in search_paths:
                        if not search_dir.exists():
                            continue
                        
                        # Try exact match first
                        for pattern in [f"{doc_name}.pdf", f"*{doc_name}*.pdf", f"{doc_id}_*.pdf"]:
                            matches = list(search_dir.glob(pattern))
                            if matches:
                                file_path = str(matches[0])
                                filename = matches[0].name
                                file_size_kb = matches[0].stat().st_size / 1024
                                break
                        
                        if file_path:
                            break
                    
                    # If still not found, use a placeholder path
                    if not file_path:
                        file_path = str(UPLOAD_DIR / f"{doc_id}_{filename}")
                    
                    docs_found[doc_id] = {
                        "doc_id": doc_id,
                        "doc_name": doc_name,
                        "filename": filename,
                        "file_path": file_path,
                        "chunk_count": 0,  # Will update below
                        "page_count": 0,
                        "file_size_kb": round(file_size_kb, 1),
                        "status": "indexed",
                    }
            
            if next_offset is None:
                break
            offset = next_offset
        
        # Update chunk counts
        for doc_id, count in chunk_counts.items():
            if doc_id in docs_found:
                docs_found[doc_id]["chunk_count"] = count
        
        # Update global registry
        _doc_registry.update(docs_found)
        
        logger.info(f"✓ Rebuilt registry from Qdrant: {len(docs_found)} documents, {sum(chunk_counts.values())} total chunks")
        
    except Exception as e:
        logger.error(f"Failed to rebuild registry from Qdrant: {e}", exc_info=True)


@router.get("/rag/pdf/{doc_id}")
async def serve_pdf(doc_id: str):
    """Serve the original PDF file for viewing/downloading."""
    from fastapi.responses import FileResponse
    from pathlib import Path
    
    if doc_id not in _doc_registry:
        # Try to rebuild registry and check again
        _rebuild_registry_from_qdrant()
        if doc_id not in _doc_registry:
            raise HTTPException(404, "Document not found")
    
    file_path = Path(_doc_registry[doc_id]["file_path"])
    
    if not file_path.exists():
        logger.error(f"PDF file not found: {file_path}")
        raise HTTPException(404, f"PDF file not found on disk: {file_path.name}")
    
    return FileResponse(
        str(file_path), 
        media_type="application/pdf",
        filename=_doc_registry[doc_id]["filename"]
    )


@router.get("/v1/health")
async def rag_health():
    """Check if RAG routes are operational"""
    return {"status": "healthy", "service": "RAG routes", "documents_indexed": len(_doc_registry)}
