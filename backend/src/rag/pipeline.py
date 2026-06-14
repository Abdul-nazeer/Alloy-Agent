"""
RAG Pipeline with Hybrid Search (Dense + Sparse + Reranking)

This replaces the old parent-child pipeline with a production-grade hybrid approach:
- Dense vectors (semantic similarity)
- Sparse vectors (BM25-style keyword matching)
- Cross-encoder reranking
- Citation tracking with bboxes

Usage:
    from backend.src.rag.pipeline import get_rag_pipeline
    
    rag = get_rag_pipeline()
    result = rag.query("motor overheating bearing failure")
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from backend.src.rag.retriever import HybridRetriever
from backend.src.rag.citation_builder import CitationBuilder
from backend.src.rag.config import QDRANT_URL, QDRANT_API_KEY

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Hybrid RAG pipeline with citations.
    
    Flow:
    1. Query → Hybrid Retriever (dense + sparse + rerank)
    2. Format context with citations [1], [2]
    3. Return context + sources with bbox metadata
    """
    
    def __init__(
        self,
        retriever: Optional[HybridRetriever] = None,
        citation_builder: Optional[CitationBuilder] = None,
    ):
        self.retriever = retriever or HybridRetriever(
            qdrant_url=QDRANT_URL,
            qdrant_api_key=QDRANT_API_KEY,
        )
        self.citation_builder = citation_builder or CitationBuilder()
        logger.info("Hybrid RAG Pipeline initialized")
    
    def query(
        self,
        question: str,
        *,
        top_k: int = 5,
        doc_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Full RAG query with hybrid search.
        
        Args:
            question: User query
            top_k: Number of chunks to return
            doc_ids: Optional filter to specific documents
        
        Returns:
            {
                "grounded": bool,
                "context": str,  # formatted with [1], [2] citations
                "sources": list,  # [{doc_name, pages, bboxes, ...}]
                "chunks": list,   # raw retrieved chunks
                "num_results": int,
                "refusal": str | None
            }
        """
        # 1. Retrieve with hybrid search
        chunks = self.retriever.retrieve(
            query=question,
            doc_ids=doc_ids,
            top_k=top_k
        )
        
        if not chunks:
            return self._refuse("No relevant information found in the knowledge base.")
        
        # 2. Build context with citations
        context = self.citation_builder.build_context_prompt(chunks)
        
        # 3. Extract source metadata
        sources = self._format_sources(chunks)
        
        return {
            "grounded": True,
            "context": context,
            "sources": sources,
            "chunks": chunks,  # for agents that need raw data
            "num_results": len(chunks),
            "refusal": None,
        }
    
    def query_with_llm_response(
        self,
        question: str,
        llm_answer: str,
        *,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Query + parse citations from LLM output.
        
        Use this when you have the LLM answer and want to attach
        citation metadata (bboxes, pages, etc.)
        
        Returns CitedAnswer with parsed citations
        """
        chunks = self.retriever.retrieve(
            query=question,
            top_k=top_k
        )
        
        if not chunks:
            return {
                "cited_answer": None,
                "refusal": "No relevant information found"
            }
        
        # Parse [1], [2] from LLM output
        cited_answer = self.citation_builder.parse_citations(llm_answer, chunks)
        
        return {
            "cited_answer": cited_answer,
            "refusal": None,
        }
    
    def _format_sources(self, chunks: list) -> List[Dict[str, Any]]:
        """Format chunks as source list for API response."""
        sources = []
        for chunk in chunks:
            sources.append({
                "index": chunk.citation_index,
                "doc_name": chunk.doc_name,
                "doc_id": chunk.doc_id,
                "section": chunk.section_heading,
                "pages": chunk.page_nums,
                "bboxes": chunk.bboxes,  # ← frontend uses for PDF highlighting
                "text_snippet": chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
                "score": round(chunk.score, 4),
                "rerank_score": round(chunk.rerank_score, 4),
            })
        return sources
    
    @staticmethod
    def _refuse(reason: str) -> Dict[str, Any]:
        return {
            "grounded": False,
            "context": "",
            "sources": [],
            "chunks": [],
            "num_results": 0,
            "refusal": reason,
        }


# ── Singleton ────────────────────────────────────────────────────────────────
_instance: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create singleton RAG pipeline."""
    global _instance
    if _instance is None:
        _instance = RAGPipeline()
    return _instance
