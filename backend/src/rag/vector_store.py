"""
Vector Store: Qdrant client wrapper
Handles connection, collection management, and CRUD operations
"""

from typing import List, Dict, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue,
    SearchRequest, ScoredPoint
)
import uuid

from .config import (
    QDRANT_URL, QDRANT_API_KEY, VECTOR_SIZE,
    COLLECTION_MANUALS, COLLECTION_SOPS,
    COLLECTION_LOGS, COLLECTION_FAULTS
)


class VectorStore:
    """Qdrant vector database client"""
    
    def __init__(self, url: str = QDRANT_URL, api_key: str = QDRANT_API_KEY):
        """
        Initialize Qdrant client
        
        Args:
            url: Qdrant server URL
            api_key: API key for Qdrant Cloud (optional for local)
        """
        self.url = url
        self.api_key = api_key
        
        print(f"Connecting to Qdrant: {url}")
        
        # Connect to Qdrant
        if api_key:
            self.client = QdrantClient(url=url, api_key=api_key)
        else:
            self.client = QdrantClient(url=url)
        
        print("✓ Connected to Qdrant")
    
    def create_collection(self, collection_name: str, vector_size: int = VECTOR_SIZE):
        """
        Create a new collection
        
        Args:
            collection_name: Name of collection
            vector_size: Dimension of vectors
        """
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE  # Cosine similarity
                )
            )
            print(f"✓ Created collection: {collection_name}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"  Collection {collection_name} already exists")
            else:
                raise
    
    def delete_collection(self, collection_name: str):
        """Delete a collection"""
        self.client.delete_collection(collection_name=collection_name)
        print(f"✓ Deleted collection: {collection_name}")
    
    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists"""
        collections = self.client.get_collections().collections
        return any(c.name == collection_name for c in collections)
    
    def add_documents(
        self,
        collection_name: str,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to collection
        
        Args:
            collection_name: Target collection
            texts: Document texts
            embeddings: Document embeddings
            metadatas: Optional metadata dicts
            ids: Optional custom IDs
            
        Returns:
            List of document IDs
        """
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        # Add text to metadata
        for i, text in enumerate(texts):
            metadatas[i]['text'] = text
        
        # Create points
        points = [
            PointStruct(
                id=id_,
                vector=embedding,
                payload=metadata
            )
            for id_, embedding, metadata in zip(ids, embeddings, metadatas)
        ]
        
        # Upload to Qdrant
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )
        
        print(f"✓ Added {len(points)} documents to {collection_name}")
        return ids
    
    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.0,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[ScoredPoint]:
        """
        Search for similar documents
        
        Args:
            collection_name: Collection to search
            query_vector: Query embedding
            limit: Max results
            score_threshold: Minimum similarity score
            filter_dict: Metadata filters
            
        Returns:
            List of search results with scores
        """
        # Build filter
        query_filter = None
        if filter_dict:
            conditions = []
            for key, value in filter_dict.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            query_filter = Filter(must=conditions)
        
        # Search
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter
        )
        
        return results
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics"""
        info = self.client.get_collection(collection_name=collection_name)
        return {
            "name": collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status,
        }
    
    def initialize_collections(self):
        """Create all required collections"""
        collections = [
            COLLECTION_MANUALS,
            COLLECTION_SOPS,
            COLLECTION_LOGS,
            COLLECTION_FAULTS
        ]
        
        for collection in collections:
            self.create_collection(collection)
        
        print(f"✓ Initialized {len(collections)} collections")


# Singleton instance
_vector_store_instance = None

def get_vector_store() -> VectorStore:
    """Get singleton vector store instance"""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance
