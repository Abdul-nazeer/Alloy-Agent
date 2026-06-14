"""
PDF Ingestion Pipeline - Hybrid RAG System

Workflow:
1. Extract PDFs with bbox tracking (pdf_extractor.py)
2. Hierarchical chunking with context (chunker.py)
3. Embed chunks (dense + sparse vectors)
4. Upsert to Qdrant with hybrid search support

Usage:
    python -m backend.src.rag.ingest
    python -m backend.src.rag.ingest --force  # re-ingest all
"""

import logging
from pathlib import Path
import argparse

from backend.src.rag.config import RAW_MANUALS_DIR, QDRANT_URL, QDRANT_API_KEY
from backend.src.rag.pdf_extractor import PDFExtractor
from backend.src.rag.chunker import chunk_elements
from backend.src.rag.vector_store import VectorStoreManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main ingestion pipeline."""
    parser = argparse.ArgumentParser(description="Ingest PDFs into hybrid RAG system")
    parser.add_argument("--force", action="store_true", help="Re-ingest all documents")
    parser.add_argument("--pdf", type=str, help="Ingest single PDF file")
    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("🔧 ALLOY AGENT - PDF INGESTION PIPELINE (Hybrid RAG)")
    logger.info("=" * 80)

    # Initialize vector store
    logger.info(f"Connecting to Qdrant: {QDRANT_URL[:50]}...")
    vs_manager = VectorStoreManager(
        qdrant_url=QDRANT_URL,
        qdrant_api_key=QDRANT_API_KEY,
        collection_name="alloy_maintenance"
    )
    vs_manager.ensure_collection()
    
    # Get PDFs to process
    if args.pdf:
        pdf_files = [Path(args.pdf)]
    else:
        pdf_files = list(RAW_MANUALS_DIR.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {RAW_MANUALS_DIR}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    logger.info("-" * 80)
    
    total_chunks = 0
    
    for pdf_path in pdf_files:
        logger.info(f"\n📄 Processing: {pdf_path.name}")
        logger.info("-" * 80)
        
        try:
            # Step 1: Extract with bbox tracking
            logger.info("  [1/3] Extracting elements...")
            extractor = PDFExtractor()
            elements = extractor.extract(str(pdf_path))
            logger.info(f"    ✓ Extracted {len(elements)} elements")
            
            if not elements:
                logger.warning(f"    ⚠️  No elements extracted from {pdf_path.name}")
                continue
            
            # Step 2: Hierarchical chunking
            logger.info("  [2/3] Chunking with context...")
            chunks = chunk_elements(elements, max_tokens=400, overlap_tokens=60)
            logger.info(f"    ✓ Created {len(chunks)} chunks")
            
            if not chunks:
                logger.warning(f"    ⚠️  No chunks created from {pdf_path.name}")
                continue
            
            # Step 3: Upsert to Qdrant (dense + sparse)
            logger.info("  [3/3] Upserting to vector store...")
            count = vs_manager.upsert_chunks(chunks)
            logger.info(f"    ✓ Upserted {count} chunks")
            
            total_chunks += count
            
        except Exception as e:
            logger.error(f"  ✗ Failed to process {pdf_path.name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("✅ INGESTION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"  Total chunks indexed: {total_chunks}")
    logger.info(f"  Collection: alloy_maintenance")
    
    # Show collection stats
    try:
        info = vs_manager.get_collection_info()
        logger.info(f"  Vector count: {info['vectors_count']}")
        logger.info(f"  Points count: {info['points_count']}")
        logger.info(f"  Status: {info['status']}")
    except Exception as e:
        logger.warning(f"  Could not fetch collection info: {e}")
    
    logger.info("=" * 80)
    logger.info("\n💡 Next steps:")
    logger.info("  1. Test retrieval: python test_hybrid_rag.py")
    logger.info("  2. Start API: python -m uvicorn backend.src.api.main:app --reload")
    logger.info("  3. Query: POST http://localhost:8000/api/v1/chat")


if __name__ == "__main__":
    main()
