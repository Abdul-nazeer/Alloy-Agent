"""
Embedder: Convert text to vector embeddings
Uses sentence-transformers with local model for fast inference
"""

from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

from .config import EMBEDDING_MODEL, EMBEDDING_DEVICE, VECTOR_SIZE


class Embedder:
    """Text embedding generator using sentence-transformers"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL, device: str = EMBEDDING_DEVICE):
        """
        Initialize embedder with specified model
        
        Args:
            model_name: HuggingFace model name
            device: Device to run on ('cuda', 'mps', 'cpu')
        """
        self.model_name = model_name
        self.device = device
        
        print(f"Loading embedding model: {model_name}")
        print(f"Device: {device}")
        
        # Load model
        self.model = SentenceTransformer(model_name, device=device)
        
        # Verify dimensions
        self.dimension = self.model.get_sentence_embedding_dimension()
        assert self.dimension == VECTOR_SIZE, \
            f"Model dimension ({self.dimension}) doesn't match config ({VECTOR_SIZE})"
        
        print(f"✓ Embedder loaded: {self.dimension}D vectors")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Embed single text string
        
        Args:
            text: Input text
            
        Returns:
            List of floats (embedding vector)
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Embed multiple texts in batches
        
        Args:
            texts: List of input texts
            batch_size: Batch size for encoding
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()
    
    def embed_query(self, query: str) -> List[float]:
        """
        Embed query text (alias for embed_text for clarity)
        
        Args:
            query: Search query
            
        Returns:
            Query embedding vector
        """
        return self.embed_text(query)
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        emb1 = np.array(self.embed_text(text1))
        emb2 = np.array(self.embed_text(text2))
        
        # Cosine similarity
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "device": self.device,
            "max_seq_length": self.model.max_seq_length,
        }


# Singleton instance
_embedder_instance = None

def get_embedder() -> Embedder:
    """Get singleton embedder instance"""
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = Embedder()
    return _embedder_instance
