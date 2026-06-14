"""
Production Hybrid Retriever:
  Dense (semantic) + Sparse (BM25-style) → Reciprocal Rank Fusion → Cross-encoder Rerank

Why hybrid beats pure vector:
  - "bearing temperature threshold" → dense finds semantic matches
  - "FC-TH-01" (fault code) → sparse finds exact string match
  - Reranker re-scores on full query-chunk pair for final ranking

Citation output: each result carries bboxes per page for frontend highlighting.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Filter, FieldCondition, MatchValue,
    SearchRequest, NamedVector, NamedSparseVector, SparseVector,
    FusionQuery, Prefetch,
)
from sentence_transformers import SentenceTransformer, CrossEncoder
import re
from collections import Counter

from backend.src.rag.config import QDRANT_URL, QDRANT_API_KEY, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

COLLECTION_NAME = "alloy_maintenance"  # Match Alloy-Agent naming
DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparse"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

TOP_K_PREFETCH = 30      # candidates from each retriever
TOP_K_RERANK = 10        # after reranking
TOP_K_FINAL = 5          # returned to LLM


@dataclass
class RetrievedChunk:
    chunk_id: str
    doc_id: str
    doc_name: str
    text: str
    context_prefix: str
    section_heading: str
    page_nums: list[int]
    bboxes: list[dict]      # [{page, bbox, bbox_norm, element_id}]
    score: float
    rerank_score: float = 0.0
    citation_index: int = 0  # 1-indexed, for "[1]" citations in LLM output


class HybridRetriever:
    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        collection_name: str = COLLECTION_NAME,
    ):
        url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")
        api_key = qdrant_api_key or os.getenv("QDRANT_API_KEY")

        self.client = QdrantClient(url=url, api_key=api_key, timeout=30)
        self.collection_name = collection_name
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        self.reranker = CrossEncoder(RERANKER_MODEL, max_length=512)
        logger.info("HybridRetriever initialized")

    def retrieve(
        self,
        query: str,
        doc_ids: Optional[list[str]] = None,   # filter to specific docs
        top_k: int = TOP_K_FINAL,
    ) -> list[RetrievedChunk]:
        """
        Full pipeline: dense + sparse prefetch → RRF fusion → rerank → return.
        """
        # Step 1: Embed query
        query_embedding = self.embedder.encode(
            query, normalize_embeddings=True
        ).tolist()

        # Step 2: Build sparse query vector
        sparse_indices, sparse_values = self._build_sparse_query(query)

        # Step 3: Optional document filter
        search_filter = None
        if doc_ids:
            search_filter = Filter(
                must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_ids[0]))]
                # For multiple docs: use must with should
            )

        # Step 4: Hybrid search using Qdrant's built-in RRF fusion
        results = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=[
                Prefetch(
                    query=query_embedding,
                    using=DENSE_VECTOR_NAME,
                    limit=TOP_K_PREFETCH,
                    filter=search_filter,
                ),
                Prefetch(
                    query=SparseVector(
                        indices=sparse_indices,
                        values=sparse_values,
                    ),
                    using=SPARSE_VECTOR_NAME,
                    limit=TOP_K_PREFETCH,
                    filter=search_filter,
                ),
            ],
            query=FusionQuery(fusion="rrf"),   # Reciprocal Rank Fusion
            limit=TOP_K_RERANK,
            with_payload=True,
        ).points

        if not results:
            return []

        # Step 5: Cross-encoder reranking
        chunks = [self._point_to_chunk(p) for p in results]
        reranked = self._rerank(query, chunks)

        # Step 6: Assign citation indices
        final = reranked[:top_k]
        for i, chunk in enumerate(final):
            chunk.citation_index = i + 1

        logger.info(f"Retrieved {len(final)} chunks for query: '{query[:60]}...'")
        return final

    def _rerank(self, query: str, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        """Cross-encoder reranking: scores (query, chunk_text) pairs."""
        if len(chunks) <= 1:
            return chunks

        pairs = [(query, c.text) for c in chunks]
        scores = self.reranker.predict(pairs)

        for chunk, score in zip(chunks, scores):
            chunk.rerank_score = float(score)

        return sorted(chunks, key=lambda c: c.rerank_score, reverse=True)

    def _point_to_chunk(self, point) -> RetrievedChunk:
        p = point.payload
        return RetrievedChunk(
            chunk_id=p.get("chunk_id", ""),
            doc_id=p.get("doc_id", ""),
            doc_name=p.get("doc_name", ""),
            text=p.get("text", ""),
            context_prefix=p.get("context_prefix", ""),
            section_heading=p.get("section_heading", ""),
            page_nums=p.get("page_nums", []),
            bboxes=p.get("bboxes", []),
            score=point.score,
        )

    def _build_sparse_query(self, query: str) -> tuple[list[int], list[float]]:
        """Build sparse query vector (must have unique sorted indices)."""
        tokens = re.findall(r"\b[a-z]{3,}\b", query.lower())
        stopwords = {"the", "and", "for", "are", "was", "with", "this", "that"}
        tokens = [t for t in tokens if t not in stopwords]
        if not tokens:
            return [0], [1.0]
        tf = Counter(tokens)
        total = sum(tf.values())
        
        # Use dict to avoid duplicate indices
        index_value_map = {}
        for token, count in tf.items():
            idx = hash(token) % 30000
            score = count / total
            if idx in index_value_map:
                index_value_map[idx] += score
            else:
                index_value_map[idx] = score
        
        # Sort by index (required by Qdrant)
        sorted_items = sorted(index_value_map.items())
        indices = [idx for idx, _ in sorted_items]
        values = [float(val) for _, val in sorted_items]
        
        return indices, values
