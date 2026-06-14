"""
Feedback Handler Service
Processes engineer corrections and indexes them into RAG with boost.
"""

import logging
import uuid
from typing import Dict, Any

from backend.src.services.logbook import get_logbook_service
from backend.src.rag.embedder import get_embedder
from backend.src.rag.vector_store import get_vector_store
from backend.src.rag.config import COLLECTION_CHUNKS

logger = logging.getLogger(__name__)


class FeedbackHandler:
    """Handle engineer feedback and improve RAG system."""
    
    def __init__(self):
        self.embedder = get_embedder()
        self.store = get_vector_store()
        self.logbook = get_logbook_service()
    
    def process_feedback(
        self,
        entry_id: str,
        verdict: str,
        actual_root_cause: str = None,
        action_taken: str = None,
        outcome: str = None,
        downtime_hours: float = None,
        engineer_notes: str = None
    ) -> Dict[str, Any]:
        """
        Process engineer feedback and index correction into RAG if incorrect.
        
        Corrections are stored with block_type='feedback_correction' and 
        receive 1.3× boost during retrieval (implemented in pipeline).
        """
        # 1. Store feedback in SQLite
        feedback_id = self.logbook.submit_feedback(
            entry_id=entry_id,
            verdict=verdict,
            actual_root_cause=actual_root_cause,
            action_taken=action_taken,
            outcome=outcome,
            downtime_hours=downtime_hours,
            engineer_notes=engineer_notes
        )
        
        # 2. If incorrect, index correction into Qdrant
        if verdict.lower() == 'incorrect' and actual_root_cause:
            self._index_correction(
                entry_id=entry_id,
                actual_root_cause=actual_root_cause,
                action_taken=action_taken or "",
                outcome=outcome or "",
                engineer_notes=engineer_notes or ""
            )
        
        return {
            "status": "success",
            "feedback_id": feedback_id,
            "correction_indexed": verdict.lower() == 'incorrect'
        }
    
    def _index_correction(
        self,
        entry_id: str,
        actual_root_cause: str,
        action_taken: str,
        outcome: str,
        engineer_notes: str
    ):
        """Index engineer correction into Qdrant."""
        # Get original logbook entry for context
        entry = self.logbook.get_entry(entry_id)
        
        if not entry:
            logger.warning(f"Entry {entry_id} not found, cannot index correction")
            return
        
        # Build correction text
        correction_text = (
            f"ENGINEER CORRECTION\n"
            f"Equipment: {entry['equipment_name']}\n"
            f"Original AI Diagnosis: {entry['root_cause']}\n\n"
            f"ACTUAL ROOT CAUSE (Engineer Verified):\n{actual_root_cause}\n\n"
            f"ACTION TAKEN:\n{action_taken}\n\n"
            f"OUTCOME:\n{outcome}\n\n"
            f"ENGINEER NOTES:\n{engineer_notes}\n\n"
            f"This correction was verified by maintenance engineer and should be "
            f"prioritized over generic manual text for similar failure patterns."
        )
        
        # Create chunk with feedback_correction type
        doc_id = f"feedback-{uuid.uuid4()}"
        chunk_id = f"{doc_id}-chunk-0"
        
        embedding = self.embedder.embed(correction_text)
        
        # Metadata includes special block_type for boost
        metadata = {
            "source": "engineer_feedback",
            "doc_type": "feedback_correction",
            "block_type": "feedback_correction",  # Key for 1.3× boost
            "entry_id": entry_id,
            "equipment_name": entry['equipment_name'],
            "original_diagnosis": entry['root_cause'],
            "verified_root_cause": actual_root_cause,
            "page_number": 1,
            "bbox": None
        }
        
        # Upsert into chunks collection
        from qdrant_client.models import PointStruct
        
        point = PointStruct(
            id=chunk_id,
            vector=embedding,
            payload={
                **metadata,
                "text": correction_text,
                "parent_doc_id": doc_id,
                "chunk_index": 0,
                "total_chunks": 1
            }
        )
        
        self.store.client.upsert(
            collection_name=COLLECTION_CHUNKS,
            points=[point]
        )
        
        logger.info(f"✓ Indexed correction for {entry_id} into RAG with feedback boost")


# Singleton
_handler: FeedbackHandler = None

def get_feedback_handler() -> FeedbackHandler:
    global _handler
    if _handler is None:
        _handler = FeedbackHandler()
    return _handler
