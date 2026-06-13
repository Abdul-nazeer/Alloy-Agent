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
    COLLECTION_DOCUMENTS, COLLECTION_CHUNKS
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
            self.client = QdrantClient(
                url=url,
                api_key=api_key,
                timeout=60,
                verify=True,
                https=True
            )
        else:
            self.client = QdrantClient(url=url, timeout=60)
        
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
            error_msg = str(e).lower()
            if "already exists" in error_msg:
                print(f"  Collection {collection_name} already exists")
            elif "forbidden" in error_msg or "403" in error_msg:
                # Qdrant Cloud free tier blocks API collection creation
                print(f"  ⚠️  Cannot create collection via API (Qdrant Cloud restriction)")
                print(f"  Checking if {collection_name} already exists...")
                if self.collection_exists(collection_name):
                    print(f"  ✓ Collection {collection_name} exists, continuing...")
                else:
                    print(f"  ❌ Collection {collection_name} does not exist")
                    print(f"  Please create it manually in Qdrant UI:")
                    print(f"     1. Go to https://cloud.qdrant.io/")
                    print(f"     2. Create collection '{collection_name}'")
                    print(f"     3. Vector size: {vector_size}, Distance: Cosine")
                    raise Exception(f"Collection '{collection_name}' must be created manually in Qdrant UI")
            else:
                raise
    
    def delete_collection(self, collection_name: str):
        """Delete a collection"""
        self.client.delete_collection(collection_name=collection_name)
        print(f"✓ Deleted collection: {collection_name}")
    
    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists"""
        try:
            # Try to get collection info - if it exists, no error
            self.client.get_collection(collection_name=collection_name)
            return True
        except:
            return False
    
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
        """Create parent-child collections"""
        collections = [COLLECTION_DOCUMENTS, COLLECTION_CHUNKS]
        
        for collection in collections:
            self.create_collection(collection)
        
        print(f"✓ Initialized {len(collections)} collections (parent-child architecture)")
    
    def add_document_with_chunks(
        self,
        document_id: str,
        document_metadata: Dict[str, Any],
        chunks_data: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        Add parent document and its child chunks
        
        Args:
            document_id: Unique document ID
            document_metadata: Document-level metadata
            chunks_data: List of dicts with 'text', 'embedding', 'metadata'
            
        Returns:
            Dict with 'document_id' and 'chunk_ids'
        """
        # Add child chunks with full parent metadata embedded
        chunk_ids = []
        chunk_points = []
        
        for i, chunk_data in enumerate(chunks_data):
            chunk_id = f"{document_id}_chunk_{i}"
            chunk_ids.append(chunk_id)
            
            # Combine parent metadata with chunk metadata
            chunk_metadata = {
                # Parent document metadata
                **document_metadata,
                'parent_document_id': document_id,
                'num_chunks': len(chunks_data),
                # Chunk-specific metadata
                **chunk_data['metadata'],
                'chunk_index': i,
                'chunk_id': chunk_id,
                'text': chunk_data['text']
            }
            
            chunk_point = PointStruct(
                id=chunk_id,
                vector=chunk_data['embedding'],
                payload=chunk_metadata
            )
            chunk_points.append(chunk_point)
        
        # Upload all chunks
        self.client.upsert(
            collection_name=COLLECTION_CHUNKS,
            points=chunk_points
        )
        
        print(f"✓ Added document {document_id} with {len(chunk_ids)} chunks")
        
        return {
            'document_id': document_id,
            'chunk_ids': chunk_ids
        }
    
    def search_with_parent_context(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.0,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search chunks and return with parent document context
        
        Returns list of dicts with:
        - chunk_text: The matched chunk text
        - chunk_score: Similarity score
        - parent_document_id: Parent document ID
        - document_type: Type of source document
        - source: Source information for citation
        - full_metadata: Complete chunk payload including parent info
        """
        # Search chunks (they contain full parent metadata)
        chunk_results = self.search(
            collection_name=COLLECTION_CHUNKS,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            filter_dict=filter_dict
        )
        
        # Format results with parent context (already in chunk metadata)
        results = []
        for chunk in chunk_results:
            results.append({
                'chunk_text': chunk.payload.get('text', ''),
                'chunk_score': chunk.score,
                'parent_document_id': chunk.payload.get('parent_document_id', ''),
                'document_type': chunk.payload.get('document_type', 'unknown'),
                'equipment_type': chunk.payload.get('equipment_type', ''),
                'source': chunk.payload.get('source', ''),
                'chunk_index': chunk.payload.get('chunk_index', 0),
                'full_metadata': chunk.payload
            })
        
        return results


# Singleton instance
_vector_store_instance = None

def get_vector_store() -> VectorStore:
    """Get singleton vector store instance"""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance
