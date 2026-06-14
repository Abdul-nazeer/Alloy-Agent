"""
Qdrant vector store manager.

Handles:
- Collection creation with named vectors (dense + sparse for hybrid)
- Batch upsert of chunks
- HNSW config for production retrieval speed
"""

import os
import uuid
import logging
from typing import Optional
from dataclasses import asdict

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    HnswConfigDiff,
    OptimizersConfigDiff,
    SparseVectorParams,
    SparseIndexParams,
)
from sentence_transformers import SentenceTransformer

from backend.src.rag.chunker import Chunk
from backend.src.rag.config import QDRANT_URL, QDRANT_API_KEY, EMBEDDING_MODEL, VECTOR_SIZE

logger = logging.getLogger(__name__)

COLLECTION_NAME = "alloy_maintenance"  # Match Alloy-Agent naming
DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparse"
EMBEDDING_DIM = VECTOR_SIZE  # From config (384)
BATCH_SIZE = 64


class VectorStoreManager:
    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        collection_name: str = COLLECTION_NAME,
    ):
        url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")
        api_key = qdrant_api_key or os.getenv("QDRANT_API_KEY")

        self.client = QdrantClient(url=url, api_key=api_key, timeout=60)
        self.collection_name = collection_name
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        logger.info(f"Connected to Qdrant at {url}, collection={collection_name}")

    def ensure_collection(self):
        """Create collection if it doesn't exist."""
        existing = [c.name for c in self.client.get_collections().collections]
        if self.collection_name in existing:
            logger.info(f"Collection '{self.collection_name}' already exists")
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                DENSE_VECTOR_NAME: VectorParams(
                    size=EMBEDDING_DIM,
                    distance=Distance.COSINE,
                    hnsw_config=HnswConfigDiff(
                        m=16,              # connections per node
                        ef_construct=200,  # build quality
                        full_scan_threshold=10_000,
                    ),
                )
            },
            sparse_vectors_config={
                SPARSE_VECTOR_NAME: SparseVectorParams(
                    index=SparseIndexParams(on_disk=False)
                )
            },
            optimizers_config=OptimizersConfigDiff(
                indexing_threshold=20_000,
                memmap_threshold=50_000,
            ),
        )
        logger.info(f"Created collection '{self.collection_name}'")

    def upsert_chunks(self, chunks: list[Chunk]) -> int:
        """Embed and upsert chunks in batches. Returns count of upserted."""
        self.ensure_collection()
        total = 0

        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i : i + BATCH_SIZE]

            # Embed the context-enriched text
            texts = [c.text_for_embedding for c in batch]
            embeddings = self.embedder.encode(
                texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True
            )

            points = []
            for chunk, embedding in zip(batch, embeddings):
                payload = chunk.to_qdrant_payload()

                # Sparse vector via BM25-style term weights (simple TF approach)
                # For production, replace with SPLADE or BM42
                sparse_indices, sparse_values = self._build_sparse_vector(chunk.text)

                points.append(
                    PointStruct(
                        id=str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id)),
                        vector={
                            DENSE_VECTOR_NAME: embedding.tolist(),
                            SPARSE_VECTOR_NAME: {
                                "indices": sparse_indices,
                                "values": sparse_values,
                            },
                        },
                        payload=payload,
                    )
                )

            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True,
            )
            total += len(points)
            logger.info(f"Upserted batch {i//BATCH_SIZE + 1}: {total}/{len(chunks)} chunks")

        return total

    def _build_sparse_vector(self, text: str) -> tuple[list[int], list[float]]:
        """
        Simple TF-based sparse vector for hybrid search.
        Production: replace with SPLADE model for better recall.
        """
        import re
        from collections import Counter

        tokens = re.findall(r"\b[a-z]{3,}\b", text.lower())
        # Remove common stopwords
        stopwords = {
            "the", "and", "for", "are", "was", "with", "this", "that",
            "from", "have", "been", "will", "all", "but", "not", "they"
        }
        tokens = [t for t in tokens if t not in stopwords]

        if not tokens:
            return [0], [0.0]

        tf = Counter(tokens)
        total = len(tokens)

        # Use dict to avoid duplicate indices
        index_value_map = {}
        for token, count in tf.most_common(50):  # top-50 terms
            # Hash token to index space [0, 30000]
            idx = hash(token) % 30000
            tf_score = count / total
            # If collision, add scores (simple aggregation)
            if idx in index_value_map:
                index_value_map[idx] += tf_score
            else:
                index_value_map[idx] = tf_score

        # Convert to sorted lists (indices must be unique and sorted)
        sorted_items = sorted(index_value_map.items())
        indices = [idx for idx, _ in sorted_items]
        values = [float(val) for _, val in sorted_items]

        return indices, values

    def delete_document(self, doc_id: str):
        """Remove all chunks belonging to a document."""
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
            ),
        )
        logger.info(f"Deleted all chunks for doc_id={doc_id}")

    def get_collection_info(self) -> dict:
        info = self.client.get_collection(self.collection_name)
        return {
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": str(info.status),
        }
